from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.auth import role_required
from models import get_db, approve_rental, reject_rental
from utils.email_service import send_trip_completion_email
from config import Config

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    """Admin dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
    total_customers = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'owner'")
    total_owners = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cars WHERE approval_status = 'approved'")
    total_cars = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cars WHERE approval_status = 'pending'")
    pending_cars = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM rentals WHERE status = 'active'")
    active_rentals = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(amount) FROM payments")
    total_revenue = cursor.fetchone()[0] or 0
    
    # Get completed rentals count
    cursor.execute("SELECT COUNT(*) FROM rentals WHERE status = 'completed'")
    completed_rentals = cursor.fetchone()[0]
    
    # Get monthly revenue (current month)
    cursor.execute("""
        SELECT SUM(p.amount) FROM payments p
        WHERE strftime('%Y-%m', p.payment_date) = strftime('%Y-%m', 'now')
    """)
    monthly_revenue = cursor.fetchone()[0] or 0
    
    # Get average revenue per rental
    if completed_rentals > 0:
        average_rental = total_revenue / completed_rentals
    else:
        average_rental = 0
    
    # Get pending payments (from active/pending rentals without payment)
    cursor.execute("""
        SELECT SUM(r.total_price) FROM rentals r
        WHERE r.status IN ('active', 'pending') 
        AND r.approval_status = 'approved'
        AND NOT EXISTS (SELECT 1 FROM payments WHERE rental_id = r.id)
    """)
    pending_payments = cursor.fetchone()[0] or 0
    
    # Get active rental value (total price of active rentals)
    cursor.execute("""
        SELECT SUM(r.total_price) FROM rentals r
        WHERE r.status = 'active' AND r.approval_status = 'approved'
    """)
    active_rental_value = cursor.fetchone()[0] or 0
    
    # Get recent rentals
    cursor.execute("""
        SELECT r.*, u.username, c.brand, c.model 
        FROM rentals r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
        ORDER BY r.created_at DESC
        LIMIT 5
    """)
    recent_rentals = cursor.fetchall()
    
    conn.close()
    
    stats = {
        'total_customers': total_customers,
        'total_owners': total_owners,
        'total_cars': total_cars,
        'pending_cars': pending_cars,
        'active_rentals': active_rentals,
        'total_revenue': total_revenue,
        'completed_rentals': completed_rentals,
        'monthly_revenue': monthly_revenue,
        'average_rental': average_rental,
        'pending_payments': pending_payments,
        'active_rental_value': active_rental_value
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_rentals=recent_rentals)

@admin_bp.route('/cars/pending')
@role_required('admin')
def pending_cars():
    """View pending car approvals"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.*, u.username as owner_name 
        FROM cars c
        JOIN users u ON c.owner_id = u.id
        WHERE c.approval_status = 'pending'
        ORDER BY c.created_at DESC
    """)
    cars = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/pending_cars.html', cars=cars)

@admin_bp.route('/cars/approve/<int:car_id>', methods=['POST'])
@role_required('admin')
def approve_car(car_id):
    """Approve a car"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE cars SET approval_status = 'approved' WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()
    
    flash('Car approved successfully!', 'success')
    return redirect(url_for('admin.pending_cars'))

@admin_bp.route('/cars/reject/<int:car_id>', methods=['POST'])
@role_required('admin')
def reject_car(car_id):
    """Reject a car"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE cars SET approval_status = 'rejected' WHERE id = ?", (car_id,))
    conn.commit()
    conn.close()
    
    flash('Car rejected.', 'info')
    return redirect(url_for('admin.pending_cars'))

@admin_bp.route('/users')
@role_required('admin')
def users():
    """View all users"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
    all_users = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/rentals')
@role_required('admin')
def rentals():
    """View all rentals"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT r.*, u.username, c.brand, c.model, d.name as driver_name
        FROM rentals r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
        LEFT JOIN drivers d ON r.driver_id = d.id
        ORDER BY r.created_at DESC
    """)
    all_rentals = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/rentals.html', rentals=all_rentals, config=Config)

@admin_bp.route('/rentals/approve/<int:rental_id>', methods=['POST'])
@role_required('admin')
def approve_rental_route(rental_id):
    """Approve a rental"""
    approve_rental(rental_id)
    flash('Rental approved successfully!', 'success')
    return redirect(url_for('admin.rentals'))

@admin_bp.route('/rentals/reject/<int:rental_id>', methods=['POST'])
@role_required('admin')
def reject_rental_route(rental_id):
    """Reject a rental"""
    reject_rental(rental_id)
    flash('Rental rejected.', 'info')
    return redirect(url_for('admin.rentals'))

@admin_bp.route('/rentals/end-trip/<int:rental_id>', methods=['POST'])
@role_required('admin')
def end_trip(rental_id):
    """End an active rental trip"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get rental details
    cursor.execute("""
        SELECT r.*, u.email, u.username, c.brand, c.model
        FROM rentals r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
        WHERE r.id = ?
    """, (rental_id,))
    rental = cursor.fetchone()
    
    if not rental:
        flash('Rental not found.', 'danger')
        conn.close()
        return redirect(url_for('admin.rentals'))
    
    if rental['status'] != 'active':
        flash('This rental is not active.', 'info')
        conn.close()
        return redirect(url_for('admin.rentals'))
    
    # Update rental status to 'completed'
    cursor.execute("UPDATE rentals SET status = 'completed' WHERE id = ?", (rental_id,))
    conn.commit()
    conn.close()
    
    # Send trip completion email to customer
    email_sent = send_trip_completion_email(
        customer_email=rental['email'],
        customer_name=rental['username'],
        car_brand=rental['brand'],
        car_model=rental['model'],
        rental_id=rental['id'],
        start_date=rental['start_date'],
        end_date=rental['end_date'],
        total_price=rental['total_price']
    )
    
    if email_sent:
        flash(f'Trip ended and verification email sent to {rental["username"]}', 'success')
    else:
        flash(f'Trip ended but failed to send verification email to {rental["username"]}', 'warning')
    
    return redirect(url_for('admin.rentals'))

@admin_bp.route('/drivers')
@role_required('admin')
def drivers():
    """View and manage drivers"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all drivers with their rental and car information
    cursor.execute("""
        SELECT 
            d.*,
            r.id as rental_id,
            r.status as rental_status,
            r.start_date,
            r.end_date,
            c.brand,
            c.model,
            c.registration,
            u.username as customer_name
        FROM drivers d
        LEFT JOIN rentals r ON d.id = r.driver_id AND r.status IN ('pending', 'active')
        LEFT JOIN cars c ON r.car_id = c.id
        LEFT JOIN users u ON r.user_id = u.id
        ORDER BY d.name
    """)
    all_drivers = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin/drivers.html', drivers=all_drivers)
