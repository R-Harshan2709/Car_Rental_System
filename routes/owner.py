from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import role_required
from models import get_db
from werkzeug.utils import secure_filename
from config import Config
import os

owner_bp = Blueprint('owner', __name__, url_prefix='/owner')

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@owner_bp.route('/dashboard')
@role_required('owner')
def dashboard():
    """Car owner dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    owner_id = session['user_id']
    
    # Get owner's cars
    cursor.execute("SELECT COUNT(*) FROM cars WHERE owner_id = ?", (owner_id,))
    total_cars = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cars WHERE owner_id = ? AND approval_status = 'approved'", (owner_id,))
    approved_cars = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cars WHERE owner_id = ? AND approval_status = 'pending'", (owner_id,))
    pending_cars = cursor.fetchone()[0]
    
    # Get rentals of owner's cars
    cursor.execute("""
        SELECT COUNT(*) FROM rentals r
        JOIN cars c ON r.car_id = c.id
        WHERE c.owner_id = ? AND r.status = 'active'
    """, (owner_id,))
    active_rentals = cursor.fetchone()[0]
    
    # Get revenue
    cursor.execute("""
        SELECT SUM(p.amount) FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        JOIN cars c ON r.car_id = c.id
        WHERE c.owner_id = ?
    """, (owner_id,))
    total_revenue = cursor.fetchone()[0] or 0
    
    # Get completed rentals count
    cursor.execute("""
        SELECT COUNT(*) FROM rentals r
        JOIN cars c ON r.car_id = c.id
        WHERE c.owner_id = ? AND r.status = 'completed'
    """, (owner_id,))
    completed_rentals = cursor.fetchone()[0]
    
    # Get monthly revenue (current month)
    cursor.execute("""
        SELECT SUM(p.amount) FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        JOIN cars c ON r.car_id = c.id
        WHERE c.owner_id = ? AND strftime('%Y-%m', p.payment_date) = strftime('%Y-%m', 'now')
    """, (owner_id,))
    monthly_revenue = cursor.fetchone()[0] or 0
    
    # Get average revenue per rental
    if completed_rentals > 0:
        average_rental = total_revenue / completed_rentals
    else:
        average_rental = 0
    
    # Get pending payments (from active/pending rentals without payment)
    cursor.execute("""
        SELECT SUM(r.total_price) FROM rentals r
        JOIN cars c ON r.car_id = c.id
        WHERE c.owner_id = ? AND r.status IN ('active', 'pending') 
        AND r.approval_status = 'approved'
        AND NOT EXISTS (SELECT 1 FROM payments WHERE rental_id = r.id)
    """, (owner_id,))
    pending_payments = cursor.fetchone()[0] or 0
    
    # Get active rental value (total price of active rentals)
    cursor.execute("""
        SELECT SUM(r.total_price) FROM rentals r
        JOIN cars c ON r.car_id = c.id
        WHERE c.owner_id = ? AND r.status = 'active' AND r.approval_status = 'approved'
    """, (owner_id,))
    active_rental_value = cursor.fetchone()[0] or 0
    
    conn.close()
    
    stats = {
        'total_cars': total_cars,
        'approved_cars': approved_cars,
        'pending_cars': pending_cars,
        'active_rentals': active_rentals,
        'total_revenue': total_revenue,
        'completed_rentals': completed_rentals,
        'monthly_revenue': monthly_revenue,
        'average_rental': average_rental,
        'pending_payments': pending_payments,
        'active_rental_value': active_rental_value
    }
    
    return render_template('owner/dashboard.html', stats=stats)

@owner_bp.route('/cars/add', methods=['GET', 'POST'])
@role_required('owner')
def add_car():
    """Add a new car"""
    if request.method == 'POST':
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        registration = request.form.get('registration')
        price_per_day = request.form.get('price_per_day')
        description = request.form.get('description')
        
        # Validation
        if not all([brand, model, year, registration, price_per_day]):
            flash('Please fill in all required fields.', 'danger')
            return render_template('owner/add_car.html')
        
        # Validate registration format (Indian: LLDDLLDDDD)
        import re
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$', registration):
            flash('Invalid registration format. Use format: DL01AB1234 (State code + 2 digits + 2 letters + 4 digits).', 'danger')
            return render_template('owner/add_car.html')
        
        # Check if registration already exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM cars WHERE registration = ?", (registration,))
        if cursor.fetchone():
            flash('This registration number is already registered in the system!', 'danger')
            conn.close()
            return render_template('owner/add_car.html')
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_path = f"uploads/cars/{filename}"
        
        # Insert car
        cursor.execute("""
            INSERT INTO cars (owner_id, brand, model, year, registration, price_per_day, description, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session['user_id'], brand, model, year, registration, price_per_day, description, image_path))
        
        conn.commit()
        conn.close()
        
        flash('Car added successfully! Waiting for admin approval.', 'success')
        return redirect(url_for('owner.my_cars'))
    
    return render_template('owner/add_car.html')

@owner_bp.route('/cars/my-cars')
@role_required('owner')
def my_cars():
    """View owner's cars"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM cars WHERE owner_id = ? ORDER BY created_at DESC", (session['user_id'],))
    cars = cursor.fetchall()
    
    conn.close()
    
    return render_template('owner/my_cars.html', cars=cars)

@owner_bp.route('/cars/edit/<int:car_id>', methods=['GET', 'POST'])
@role_required('owner')
def edit_car(car_id):
    """Edit car details"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute("SELECT * FROM cars WHERE id = ? AND owner_id = ?", (car_id, session['user_id']))
    car = cursor.fetchone()
    
    if not car:
        flash('Car not found or you do not have permission to edit it.', 'danger')
        conn.close()
        return redirect(url_for('owner.my_cars'))
    
    if request.method == 'POST':
        brand = request.form.get('brand')
        model = request.form.get('model')
        year = request.form.get('year')
        registration = request.form.get('registration')
        price_per_day = request.form.get('price_per_day')
        description = request.form.get('description')
        
        # Validation
        if not all([brand, model, year, registration, price_per_day]):
            flash('Please fill in all required fields.', 'danger')
            conn.close()
            return render_template('owner/edit_car.html', car=car)
        
        # Validate registration format
        import re
        if not re.match(r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$', registration):
            flash('Invalid registration format. Use format: DL01AB1234.', 'danger')
            conn.close()
            return render_template('owner/edit_car.html', car=car)
        
        # Check if registration already exists (excluding current car)
        cursor.execute("SELECT id FROM cars WHERE registration = ? AND id != ?", (registration, car_id))
        if cursor.fetchone():
            flash('This registration number is already registered in the system!', 'danger')
            conn.close()
            return render_template('owner/edit_car.html', car=car)
        
        cursor.execute("""
            UPDATE cars 
            SET brand = ?, model = ?, year = ?, registration = ?, price_per_day = ?, description = ?
            WHERE id = ?
        """, (brand, model, year, registration, price_per_day, description, car_id))
        
        conn.commit()
        conn.close()
        
        flash('Car updated successfully!', 'success')
        return redirect(url_for('owner.my_cars'))
    
    conn.close()
    return render_template('owner/edit_car.html', car=car)

@owner_bp.route('/cars/delete/<int:car_id>', methods=['POST'])
@role_required('owner')
def delete_car(car_id):
    """Delete a car"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Verify ownership
    cursor.execute("SELECT * FROM cars WHERE id = ? AND owner_id = ?", (car_id, session['user_id']))
    car = cursor.fetchone()
    
    if not car:
        flash('Car not found or you do not have permission to delete it.', 'danger')
        conn.close()
        return redirect(url_for('owner.my_cars'))
    
    # Check if car has active rentals
    cursor.execute("SELECT COUNT(*) FROM rentals WHERE car_id = ? AND status = 'active'", (car_id,))
    active_rentals = cursor.fetchone()[0]
    
    if active_rentals > 0:
        flash('Cannot delete car with active rentals. Please wait until all rentals are completed.', 'danger')
        conn.close()
        return redirect(url_for('owner.my_cars'))
    
    # Delete the car
    cursor.execute("DELETE FROM cars WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()
    
    flash('Car deleted successfully!', 'success')
    return redirect(url_for('owner.my_cars'))

@owner_bp.route('/rentals')
@role_required('owner')
def rentals():
    """View rentals of owner's cars"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.*, u.username, c.brand, c.model, d.name as driver_name
        FROM rentals r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        WHERE c.owner_id = ?
        ORDER BY r.created_at DESC
    """, (session['user_id'],))
    
    owner_rentals = cursor.fetchall()
    
    conn.close()
    
    return render_template('owner/rentals.html', rentals=owner_rentals, config=Config)
