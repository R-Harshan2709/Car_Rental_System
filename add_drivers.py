import sqlite3

conn = sqlite3.connect('car_rental.db')
cursor = conn.cursor()

# First, let's set some existing drivers to 'available' status
print("Updating existing drivers to 'available' status...")
cursor.execute("UPDATE drivers SET availability_status = 'available' WHERE id IN (1, 2, 3)")
conn.commit()
print("✓ Updated drivers 1, 2, and 3 to available status")

# Add more drivers with 'available' status
new_drivers = [
    ('Rajesh Kumar', 'DL01AB1234', '+91-98765-43210'),
    ('Priya Sharma', 'DL02CD5678', '+91-98765-43211'),
    ('Amit Patel', 'DL03EF9012', '+91-98765-43212'),
    ('Sneha Reddy', 'DL04GH3456', '+91-98765-43213'),
    ('Vikram Singh', 'DL05IJ7890', '+91-98765-43214'),
    ('Anita Verma', 'DL06KL2345', '+91-98765-43215'),
    ('Rohan Gupta', 'DL07MN6789', '+91-98765-43216'),
    ('Kavita Desai', 'DL08OP1234', '+91-98765-43217'),
]

print("\nAdding new drivers...")
for name, license, phone in new_drivers:
    try:
        cursor.execute("""
            INSERT INTO drivers (name, license_number, phone, availability_status)
            VALUES (?, ?, ?, 'available')
        """, (name, license, phone))
        print(f"✓ Added driver: {name}")
    except sqlite3.IntegrityError:
        print(f"⚠ Driver {name} already exists (skipped)")

conn.commit()

# Show all available drivers
cursor.execute("SELECT * FROM drivers WHERE availability_status = 'available'")
available_drivers = cursor.fetchall()

print(f"\n{'='*60}")
print(f"Total Available Drivers: {len(available_drivers)}")
print(f"{'='*60}")

for driver in available_drivers:
    print(f"ID: {driver[0]}, Name: {driver[1]}, License: {driver[2]}, Phone: {driver[3]}")

conn.close()
print("\n✓ Driver setup completed successfully!")
