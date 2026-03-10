import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'owner', 'customer')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cars table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price_per_day REAL NOT NULL,
            description TEXT,
            image_path TEXT,
            status TEXT DEFAULT 'available' CHECK(status IN ('available', 'rented', 'maintenance')),
            approval_status TEXT DEFAULT 'pending' CHECK(approval_status IN ('pending', 'approved', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')
    
    # Drivers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS drivers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            license_number TEXT UNIQUE NOT NULL,
            availability_status TEXT DEFAULT 'available' CHECK(availability_status IN ('available', 'assigned')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Rentals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rentals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            driver_id INTEGER,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'cancelled')),
            approval_status TEXT DEFAULT 'pending' CHECK(approval_status IN ('pending', 'approved', 'rejected')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (car_id) REFERENCES cars(id),
            FOREIGN KEY (driver_id) REFERENCES drivers(id)
        )
    ''')
    
    # Payments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rental_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            receipt_path TEXT,
            FOREIGN KEY (rental_id) REFERENCES rentals(id)
        )
    ''')
    
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE role = 'admin'")
    if not cursor.fetchone():
        admin_password = generate_password_hash('admin123')
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            ('admin', 'admin@carrental.com', admin_password, 'admin')
        )
    
    # Create some sample drivers
    cursor.execute("SELECT COUNT(*) FROM drivers")
    if cursor.fetchone()[0] == 0:
        sample_drivers = [
            ('John Smith', '+1-555-0101', 'DL123456'),
            ('Maria Garcia', '+1-555-0102', 'DL234567'),
            ('David Chen', '+1-555-0103', 'DL345678'),
            ('Sarah Johnson', '+1-555-0104', 'DL456789'),
            ('Michael Brown', '+1-555-0105', 'DL567890')
        ]
        cursor.executemany(
            "INSERT INTO drivers (name, phone, license_number) VALUES (?, ?, ?)",
            sample_drivers
        )
    
    conn.commit()
    conn.close()

def migrate_db():
    """Run database migrations"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Check if approval_status column exists in rentals table
        cursor.execute("PRAGMA table_info(rentals)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'approval_status' not in columns:
            # Add approval_status column
            cursor.execute("""
                ALTER TABLE rentals 
                ADD COLUMN approval_status TEXT DEFAULT 'pending' 
                CHECK(approval_status IN ('pending', 'approved', 'rejected'))
            """)
            conn.commit()
            print("Migration: Added approval_status column to rentals table")
        
        # Check if payment_status column exists in payments table
        cursor.execute("PRAGMA table_info(payments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'payment_status' not in columns:
            # Add payment_status column
            cursor.execute("""
                ALTER TABLE payments 
                ADD COLUMN payment_status TEXT DEFAULT 'pending' 
                CHECK(payment_status IN ('pending', 'completed', 'failed'))
            """)
            conn.commit()
            print("Migration: Added payment_status column to payments table")
        
        # Check if registration column exists in cars table
        cursor.execute("PRAGMA table_info(cars)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'registration' not in columns:
            # Add registration column for vehicle identification
            # Note: Cannot use UNIQUE constraint in ALTER TABLE with existing data
            cursor.execute("""
                ALTER TABLE cars 
                ADD COLUMN registration TEXT
            """)
            conn.commit()
            print("Migration: Added registration column to cars table")
            
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

# Helper functions
def create_user(username, email, password, role):
    """Create a new user"""
    conn = get_db()
    cursor = conn.cursor()
    password_hash = generate_password_hash(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_user_by_username(username):
    """Get user by username"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Get user by ID"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def verify_password(user, password):
    """Verify user password"""
    return check_password_hash(user['password_hash'], password)

def get_available_driver():
    """Get an available driver"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM drivers WHERE availability_status = 'available' LIMIT 1")
    driver = cursor.fetchone()
    conn.close()
    return driver

def update_driver_status(driver_id, status, cursor=None, conn=None):
    """Update driver availability status
    
    Args:
        driver_id: ID of the driver to update
        status: New availability status
        cursor: Optional existing cursor to use (for transaction handling)
        conn: Optional existing connection to use (for transaction handling)
    """
    close_conn = False
    if cursor is None or conn is None:
        conn = get_db()
        cursor = conn.cursor()
        close_conn = True
    
    cursor.execute("UPDATE drivers SET availability_status = ? WHERE id = ?", (status, driver_id))
    
    if close_conn:
        conn.commit()
        conn.close()

def approve_rental(rental_id):
    """Approve a rental and send approval email"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get rental and customer details
    cursor.execute("""
        SELECT r.*, u.email, u.username, c.brand, c.model
        FROM rentals r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
        WHERE r.id = ?
    """, (rental_id,))
    rental = cursor.fetchone()
    
    if rental:
        # Update rental status
        cursor.execute("UPDATE rentals SET approval_status = 'approved' WHERE id = ?", (rental_id,))
        conn.commit()
        
        # Send approval email
        try:
            from utils.email_service import send_approval_email
            email_sent = send_approval_email(
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
                print(f"✓ Approval email sent to {rental['email']}")
            else:
                print(f"✗ Failed to send approval email to {rental['email']}")
        except Exception as e:
            print(f"✗ Error sending approval email: {str(e)}")
    
    conn.close()

def reject_rental(rental_id):
    """Reject a rental and send rejection email"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get rental and customer details
    cursor.execute("""
        SELECT r.*, u.email, u.username, c.brand, c.model
        FROM rentals r
        JOIN users u ON r.user_id = u.id
        JOIN cars c ON r.car_id = c.id
        WHERE r.id = ?
    """, (rental_id,))
    rental = cursor.fetchone()
    
    if rental:
        # Update rental status
        cursor.execute("UPDATE rentals SET approval_status = 'rejected' WHERE id = ?", (rental_id,))
        conn.commit()
        
        # Send rejection email
        try:
            from utils.email_service import send_rejection_email
            email_sent = send_rejection_email(
                customer_email=rental['email'],
                customer_name=rental['username'],
                car_brand=rental['brand'],
                car_model=rental['model'],
                rental_id=rental['id']
            )
            if email_sent:
                print(f"✓ Rejection email sent to {rental['email']}")
            else:
                print(f"✗ Failed to send rejection email to {rental['email']}")
        except Exception as e:
            print(f"✗ Error sending rejection email: {str(e)}")
    
    conn.close()

def get_rental_payment(rental_id):
    """Get payment details for a rental"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM payments WHERE rental_id = ?", (rental_id,))
    payment = cursor.fetchone()
    conn.close()
    return payment

def update_payment_status(payment_id, status):
    """Update payment status"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE payments SET payment_status = ? WHERE id = ?", (status, payment_id))
    conn.commit()
    conn.close()

def get_pending_payments(user_id):
    """Get all pending payments for a user"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.*, r.*, c.brand, c.model
        FROM payments p
        JOIN rentals r ON p.rental_id = r.id
        JOIN cars c ON r.car_id = c.id
        WHERE r.user_id = ? AND p.payment_status = 'pending'
    """, (user_id,))
    payments = cursor.fetchall()
    conn.close()
    return payments
