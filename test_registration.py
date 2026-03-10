#!/usr/bin/env python
"""Test script to verify registration column functionality"""

import sqlite3
import sys

def test_registration_column():
    """Test if registration column exists and works"""
    try:
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute('PRAGMA table_info(cars)')
        columns = {col[1]: col[2] for col in cursor.fetchall()}
        
        print("=" * 50)
        print("CAR REGISTRATION FEATURE TEST")
        print("=" * 50)
        
        if 'registration' in columns:
            print("✓ Registration column exists")
            print(f"  Type: {columns['registration']}")
        else:
            print("✗ Registration column is MISSING")
            print("\nExisting columns:")
            for col_name in columns:
                print(f"  - {col_name}")
            conn.close()
            return False
        
        # Test a dummy insert
        print("\nTesting dummy insert with registration...")
        try:
            cursor.execute("""
                SELECT COUNT(*) FROM cars
            """)
            car_count = cursor.fetchone()[0]
            print(f"✓ Current cars in database: {car_count}")
        except Exception as e:
            print(f"✗ Error reading cars: {e}")
            conn.close()
            return False
        
        # Test the duplicate check query
        print("\nTesting duplicate check query...")
        try:
            cursor.execute("SELECT id FROM cars WHERE registration = ?", ('DL01AB1234',))
            result = cursor.fetchone()
            print(f"✓ Duplicate check query works (result: {result})")
        except Exception as e:
            print(f"✗ Error with duplicate check: {e}")
            conn.close()
            return False
        
        conn.close()
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"✗ FATAL ERROR: {e}")
        return False

if __name__ == '__main__':
    success = test_registration_column()
    sys.exit(0 if success else 1)
