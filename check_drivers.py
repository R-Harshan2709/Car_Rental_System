import sqlite3

conn = sqlite3.connect('car_rental.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check if drivers table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='drivers'")
table_exists = cursor.fetchone()

if table_exists:
    print("✓ Drivers table exists")
    
    # Check drivers
    cursor.execute('SELECT * FROM drivers')
    drivers = cursor.fetchall()
    print(f'\nTotal drivers: {len(drivers)}')
    
    if len(drivers) > 0:
        print('\nDriver List:')
        for driver in drivers:
            print(f'  ID: {driver["id"]}, Name: {driver["name"]}, License: {driver["license_number"]}, Phone: {driver["phone"]}, Status: {driver["availability_status"]}')
    else:
        print('\n⚠ No drivers found in database!')
else:
    print('✗ Drivers table does not exist!')

conn.close()
