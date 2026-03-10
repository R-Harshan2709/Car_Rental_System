#!/usr/bin/env python
"""Test the add car registration validation"""

import re

def test_registration_format():
    """Test registration format validation"""
    
    valid_registrations = [
        'DL01AB1234',
        'MH02CD5678',
        'KA03EF9012',
        'UP04GH3456',
        'TN05IJ7890',
        'RJ06KL1234',
        'GJ07MN5678',
        'WB08OP9012'
    ]
    
    invalid_registrations = [
        'dl01ab1234',  # lowercase
        'DL1AB1234',   # only 1 digit in district
        'DL01A1234',   # only 1 letter in sequential  
        'DL01AB123',   # only 3 digits in serial
        'DL-01-AB-1234',  # hyphens
        'DL 01 AB 1234',  # spaces
        'DL0A1B1234',  # wrong order
        '01DLABCD1234'  # wrong order
    ]
    
    pattern = r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$'
    
    print("=" * 60)
    print("REGISTRATION FORMAT VALIDATION TEST")
    print("=" * 60)
    
    print("\n✓ VALID REGISTRATIONS:")
    all_valid = True
    for reg in valid_registrations:
        matches = bool(re.match(pattern, reg))
        status = "✓" if matches else "✗"
        print(f"  {status} {reg}")
        if not matches:
            all_valid = False
    
    print("\n✗ INVALID REGISTRATIONS (should NOT match):")
    all_invalid = True
    for reg in invalid_registrations:
        matches = bool(re.match(pattern, reg))
        status = "✓" if not matches else "✗"
        print(f"  {status} {reg} - {'rejected' if not matches else 'INCORRECTLY ACCEPTED'}")
        if matches:
            all_invalid = False
    
    print("\n" + "=" * 60)
    if all_valid and all_invalid:
        print("✓ ALL FORMAT VALIDATION TESTS PASSED")
    else:
        print("✗ SOME TESTS FAILED")
    print("=" * 60)
    
    return all_valid and all_invalid

if __name__ == '__main__':
    test_registration_format()
