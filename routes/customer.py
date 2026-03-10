from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, jsonify
from routes.auth import login_required
from models import get_db, get_available_driver, update_driver_status, get_rental_payment, update_payment_status
from utils.pdf_generator import generate_receipt
from config import Config
from datetime import datetime
import os
import json

customer_bp = Blueprint('customer', __name__, url_prefix='/customer')

@customer_bp.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    user_id = session['user_id']
    
    # Get customer statistics
    cursor.execute("SELECT COUNT(*) FROM rentals WHERE user_id = ?", (user_id,))
    total_rentals = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rentals WHERE user_id = ? AND status = 'active'", (user_id,))
    active_rentals = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(total_price) FROM rentals WHERE user_id = ?", (user_id,))
    total_spent = cursor.fetchone()[0] or 0
    
    # Get recent rentals
    cursor.execute("""
        SELECT r.*, c.brand, c.model, c.image_path, d.name as driver_name, d.phone as driver_phone
        FROM rentals r
        JOIN cars c ON r.car_id = c.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
        LIMIT 3
    """, (user_id,))
    recent_rentals = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'total_rentals': total_rentals,
        'active_rentals': active_rentals,
        'total_spent': total_spent
    }
    
    return render_template('customer/dashboard.html', stats=stats, recent_rentals=recent_rentals)

@customer_bp.route('/cars')
@login_required
def browse_cars():
    """Browse available cars"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get filters
    brand = request.args.get('brand', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    
    # Build query
    query = "SELECT * FROM cars WHERE approval_status = 'approved' AND status = 'available'"
    params = []
    
    if brand:
        query += " AND brand LIKE ?"
        params.append(f"%{brand}%")
    
    if min_price:
        query += " AND price_per_day >= ?"
        params.append(min_price)
    
    if max_price:
        query += " AND price_per_day <= ?"
        params.append(max_price)
    
    query += " ORDER BY created_at DESC"
    
    cursor.execute(query, params)
    cars = cursor.fetchall()
    
    conn.close()
    
    return render_template('customer/browse_cars.html', cars=cars)

@customer_bp.route('/cars/<int:car_id>')
@login_required
def car_details(car_id):
    """View car details"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, u.username as owner_name 
        FROM cars c
        JOIN users u ON c.owner_id = u.id
        WHERE c.id = ?
    """, (car_id,))
    car = cursor.fetchone()
    
    conn.close()
    
    if not car:
        flash('Car not found.', 'danger')
        return redirect(url_for('customer.browse_cars'))
    
    return render_template('customer/car_details.html', car=car)

@customer_bp.route('/rent/<int:car_id>', methods=['POST'])
@login_required
def rent_car(car_id):
    """Rent a car"""
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    if not all([start_date, end_date]):
        flash('Please provide both start and end dates.', 'danger')
        return redirect(url_for('customer.car_details', car_id=car_id))
    
    # Parse dates
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start >= end:
            flash('End date must be after start date.', 'danger')
            return redirect(url_for('customer.car_details', car_id=car_id))
        
        if start < datetime.now():
            flash('Start date cannot be in the past.', 'danger')
            return redirect(url_for('customer.car_details', car_id=car_id))
        
        days = (end - start).days
    except ValueError:
        flash('Invalid date format.', 'danger')
        return redirect(url_for('customer.car_details', car_id=car_id))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Get car details
    cursor.execute("SELECT * FROM cars WHERE id = ? AND status = 'available' AND approval_status = 'approved'", (car_id,))
    car = cursor.fetchone()
    
    if not car:
        flash('Car is not available for rent.', 'danger')
        conn.close()
        return redirect(url_for('customer.browse_cars'))
    
    # Calculate total price
    total_price = car['price_per_day'] * days
    
    # Get available driver
    driver = get_available_driver()
    
    if not driver:
        flash('No drivers available at the moment. Please try again later.', 'warning')
        conn.close()
        return redirect(url_for('customer.car_details', car_id=car_id))
    
    # Create rental
    cursor.execute("""
        INSERT INTO rentals (user_id, car_id, driver_id, start_date, end_date, total_price)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (session['user_id'], car_id, driver['id'], start_date, end_date, total_price))
    
    rental_id = cursor.lastrowid
    
    # Update car status
    cursor.execute("UPDATE cars SET status = 'rented' WHERE id = ?", (car_id,))
    
    # Update driver status (using same transaction)
    update_driver_status(driver['id'], 'assigned', cursor, conn)
    
    # Create payment (simulated - add 10% tax)
    payment_amount = total_price * 1.1
    cursor.execute("""
        INSERT INTO payments (rental_id, amount)
        VALUES (?, ?)
    """, (rental_id, payment_amount))
    
    payment_id = cursor.lastrowid
    
    conn.commit()
    
    # Get rental data for PDF
    cursor.execute("SELECT * FROM rentals WHERE id = ?", (rental_id,))
    rental = cursor.fetchone()
    
    cursor.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    payment = cursor.fetchone()
    
    cursor.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],))
    user = cursor.fetchone()
    
    conn.close()
    
    # Generate PDF receipt
    try:
        receipt_filename = generate_receipt(
            rental_data=dict(rental),
            payment_data=dict(payment),
            car_data=dict(car),
            user_data=dict(user),
            driver_data=dict(driver)
        )
        
        # Update payment with receipt path
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE payments SET receipt_path = ? WHERE id = ?", (receipt_filename, payment_id))
        conn.commit()
        conn.close()
        
        flash('Car rented successfully! Your receipt has been generated.', 'success')
    except Exception as e:
        flash(f'Car rented successfully, but receipt generation failed: {str(e)}', 'warning')
    
    return redirect(url_for('customer.rentals'))

@customer_bp.route('/rentals')
@login_required
def rentals():
    """View rental history"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.*, c.brand, c.model, c.image_path, d.name as driver_name, d.phone as driver_phone,
               p.receipt_path, p.payment_status, p.amount, p.id as payment_id
        FROM rentals r
        JOIN cars c ON r.car_id = c.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        LEFT JOIN payments p ON p.rental_id = r.id
        WHERE r.user_id = ?
        ORDER BY r.created_at DESC
    """, (session['user_id'],))
    
    user_rentals = cursor.fetchall()
    
    conn.close()
    
    return render_template('customer/rentals.html', rentals=user_rentals, config=Config)

@customer_bp.route('/receipt/<int:rental_id>')
@login_required
def view_receipt(rental_id):
    """View/download receipt"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.receipt_path FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        WHERE r.id = ? AND r.user_id = ?
    """, (rental_id, session['user_id']))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result or not result['receipt_path']:
        flash('Receipt not found.', 'danger')
        return redirect(url_for('customer.rentals'))
    
    receipt_path = os.path.join(Config.RECEIPT_FOLDER, result['receipt_path'])
    
    if not os.path.exists(receipt_path):
        flash('Receipt file not found.', 'danger')
        return redirect(url_for('customer.rentals'))
    
    return send_file(receipt_path, as_attachment=True, download_name=result['receipt_path'])

@customer_bp.route('/payment/<int:rental_id>')
@login_required
def payment(rental_id):
    """Payment page for a rental"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get rental and payment details
    cursor.execute("""
        SELECT r.*, p.id as payment_id, p.amount, p.payment_status, c.brand, c.model
        FROM rentals r
        JOIN payments p ON p.rental_id = r.id
        JOIN cars c ON r.car_id = c.id
        WHERE r.id = ? AND r.user_id = ?
    """, (rental_id, session['user_id']))
    
    rental = cursor.fetchone()
    conn.close()
    
    if not rental:
        flash('Rental not found.', 'danger')
        return redirect(url_for('customer.rentals'))
    
    return render_template('customer/payment.html', rental=rental)

@customer_bp.route('/process-payment/<int:rental_id>', methods=['POST'])
@login_required
def process_payment(rental_id):
    """Process payment for a rental"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get payment details
    cursor.execute("""
        SELECT p.id, p.amount FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        WHERE r.id = ? AND r.user_id = ?
    """, (rental_id, session['user_id']))
    
    payment = cursor.fetchone()
    
    if not payment:
        conn.close()
        return jsonify({'success': False, 'message': 'Payment not found'}), 404
    
    # Get payment method
    payment_method = request.form.get('payment_method', '').strip()
    
    if not payment_method:
        conn.close()
        flash('Please select a payment method.', 'danger')
        return redirect(url_for('customer.payment', rental_id=rental_id))
    
    # Validate payment method
    valid_methods = ['upi', 'card', 'netbanking', 'wallet']
    if payment_method not in valid_methods:
        conn.close()
        flash('Invalid payment method selected.', 'danger')
        return redirect(url_for('customer.payment', rental_id=rental_id))
    
    # If card method, validate card details
    if payment_method == 'card':
        card_number = request.form.get('card_number', '').replace(' ', '')
        card_holder = request.form.get('card_holder', '').strip()
        expiry_date = request.form.get('expiry_date', '').strip()
        cvv = request.form.get('cvv', '').strip()
        
        # Validate card fields
        if not card_number or len(card_number) != 16 or not card_number.isdigit():
            conn.close()
            flash('Invalid card number. Must be 16 digits.', 'danger')
            return redirect(url_for('customer.payment', rental_id=rental_id))
        
        if not card_holder or len(card_holder.strip()) == 0:
            conn.close()
            flash('Cardholder name is required.', 'danger')
            return redirect(url_for('customer.payment', rental_id=rental_id))
        
        if not expiry_date or len(expiry_date) != 5 or '/' not in expiry_date:
            conn.close()
            flash('Invalid expiry date. Use MM/YY format.', 'danger')
            return redirect(url_for('customer.payment', rental_id=rental_id))
        
        if not cvv or len(cvv) < 3 or len(cvv) > 4 or not cvv.isdigit():
            conn.close()
            flash('Invalid CVV. Must be 3-4 digits.', 'danger')
            return redirect(url_for('customer.payment', rental_id=rental_id))
    
    # Log payment method for demo purposes
    payment_method_log = f"{payment_method.upper()} payment processed"
    if payment_method == 'card':
        card_last_4 = request.form.get('card_number', '').replace(' ', '')[-4:]
        payment_method_log += f" (Card ending in {card_last_4})"
    
    print(f"✓ {payment_method_log} for Rental #{rental_id}")
    
    # Simulate payment processing (In production, integrate with actual payment gateway)
    # For demo, we'll mark as completed
    try:
        update_payment_status(payment['id'], 'completed')
        
        # Get rental for flash message
        cursor.execute("SELECT * FROM rentals WHERE id = ?", (rental_id,))
        rental_data = cursor.fetchone()
        
        conn.close()
        
        flash(f'✓ Payment successful via {payment_method.upper()}! Your rental is confirmed.', 'success')
        return redirect(url_for('customer.rentals'))
    except Exception as e:
        conn.close()
        print(f"✗ Error processing payment: {str(e)}")
        flash('Payment processing failed. Please try again.', 'danger')
        return redirect(url_for('customer.payment', rental_id=rental_id))

