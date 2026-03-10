# Car Registration Number Feature

## Overview

A mandatory car registration/number field has been added to the car rental system to ensure proper vehicle identification and prevent duplicate vehicle registrations.

## Changes Made

### 1. Database Migration (`models.py`)

- Added migration in `migrate_db()` function to create `registration` column in `cars` table
- Column is `TEXT UNIQUE` to prevent duplicate registrations
- Automatically runs when the app starts

```sql
ALTER TABLE cars ADD COLUMN registration TEXT UNIQUE
```

### 2. Add Car Form (`templates/owner/add_car.html`)

- Added mandatory **Car Registration/Number** input field at the top
- Format: Indian vehicle registration plate format
- Pattern: `LLDDLLDDDD` (2 letters + 2 digits + 2 letters + 4 digits)
- Example: `DL01AB1234`

### 3. Edit Car Form (`templates/owner/edit_car.html`)

- Added **Car Registration/Number** input field
- Shows existing registration value
- Can be updated during edit

### 4. Backend Validation (`routes/owner.py`)

#### Add Car Function

```python
# Validates registration format using regex
# Checks for duplicates in database
# Returns specific error messages for invalid input
```

#### Edit Car Function

```python
# Same validation as add_car
# Allows updates but prevents duplicate registration numbers
# Excludes current car from duplicate check
```

### 5. Display Updates

- **my_cars.html**: Shows registration number on owner's car listing
- **browse_cars.html**: Shows registration number in customer's car browse view
- **car_details.html**: Displays registration in detailed car view
- **pending_cars.html**: Shows registration for admin approval review

## Validation Rules

### Format Validation

- **Pattern**: `[A-Z]{2}\d{2}[A-Z]{2}\d{4}`
- **Requirements**:
  - 2 uppercase letters (State Code)
  - 2 digits (District Code)
  - 2 uppercase letters (Sequential)
  - 4 digits (Serial Number)

### Examples of Valid Registrations

- `DL01AB1234` - Delhi
- `MH02CD5678` - Maharashtra
- `KA03EF9012` - Karnataka
- `UP04GH3456` - Uttar Pradesh
- `TN05IJ7890` - Tamil Nadu

### Examples of Invalid Registrations

- `dl01ab1234` - Lowercase not allowed
- `DL1AB1234` - Only 1 digit in district code
- `DL01A1234` - Only 1 letter in sequential
- `DL01AB123` - Only 3 digits in serial
- `DL-01-AB-1234` - Hyphens not allowed
- `DL 01 AB 1234` - Spaces not allowed

### Uniqueness Validation

- System prevents adding cars with duplicate registration numbers
- Error message: "This registration number is already registered in the system!"

## Error Messages

| Scenario                 | Message                                                                                               |
| ------------------------ | ----------------------------------------------------------------------------------------------------- |
| Registration field empty | "Please fill in all required fields."                                                                 |
| Invalid format           | "Invalid registration format. Use format: DL01AB1234 (State code + 2 digits + 2 letters + 4 digits)." |
| Duplicate registration   | "This registration number is already registered in the system!"                                       |

## User Experience Flow

### Adding a New Car (Owner)

1. Click "Add New Car" button
2. Enter Car Registration (required) - e.g., `DL01AB1234`
3. Fill Brand, Model, Year, Price, Description
4. Upload car image (optional)
5. Click "Add Car"
6. System validates format and uniqueness
7. Car added and awaits admin approval

### Editing a Car (Owner)

1. Click "Edit" on a car in "My Cars"
2. Registration field is pre-filled with existing value
3. Can update registration if new value doesn't exist
4. Make other updates as needed
5. Click "Update Car"
6. System validates and saves

### Browsing Cars (Customer)

1. View car cards showing registration number
2. Click car to see full details
3. Registration displayed on car details page
4. Proceed with booking

### Admin Approval

1. Admin sees registration number on pending cars
2. Can verify vehicle details against registration
3. Approve or reject listing

## Indian Vehicle Registration Format Guide

```
Example Registration: DL01AB1234

DL    = State Code (2 letters)
01    = District Code (2 digits)
AB    = Sequential Letters (2 letters)
1234  = Serial Number (4 digits)
```

### Common Indian State Codes

- **AN** - Andaman and Nicobar Islands
- **AP** - Andhra Pradesh
- **AR** - Arunachal Pradesh
- **AS** - Assam
- **BR** - Bihar
- **CG** - Chhattisgarh
- **CH** - Chandigarh
- **CT** - Chhattisgarh
- **DD** - Daman and Diu
- **DL** - Delhi
- **DN** - Dadra and Nagar Haveli
- **GA** - Goa
- **GJ** - Gujarat
- **HR** - Haryana
- **HP** - Himachal Pradesh
- **JK** - Jammu and Kashmir
- **JH** - Jharkhand
- **KA** - Karnataka
- **KL** - Kerala
- **LD** - Lakshadweep
- **MH** - Maharashtra
- **ML** - Meghalaya
- **MN** - Manipur
- **MP** - Madhya Pradesh
- **MZ** - Mizoram
- **NL** - Nagaland
- **OD** - Odisha
- **PB** - Punjab
- **PY** - Puducherry
- **RJ** - Rajasthan
- **SK** - Sikkim
- **TG** - Telangana
- **TN** - Tamil Nadu
- **TR** - Tripura
- **UP** - Uttar Pradesh
- **UT** - Uttarakhand
- **WB** - West Bengal

## Files Modified

1. `models.py` - Added database migration
2. `routes/owner.py` - Updated add_car and edit_car functions
3. `templates/owner/add_car.html` - Added registration input field
4. `templates/owner/edit_car.html` - Added registration input field
5. `templates/owner/my_cars.html` - Display registration number
6. `templates/customer/browse_cars.html` - Display registration number
7. `templates/customer/car_details.html` - Display registration number
8. `templates/admin/pending_cars.html` - Display registration number

## Benefits

✅ **Proper Vehicle Identification** - Each car uniquely identified by registration  
✅ **Prevent Duplicates** - System prevents same car being registered twice  
✅ **Legal Compliance** - Follows Indian vehicle registration standards  
✅ **Better Admin Review** - Admins can verify real vehicle details  
✅ **Track Vehicle Records** - Easy to maintain vehicle history  
✅ **Improved Security** - Reduces fraudulent listings  
✅ **Enhanced Trust** - Customers can see official registration numbers

## Testing Checklist

- [ ] Owner can add a car with valid registration
- [ ] Owner cannot add car with invalid format
- [ ] Owner cannot add duplicate registration
- [ ] Owner can edit car and update registration
- [ ] Customer can see registration in car listings
- [ ] Admin can see registration in pending approvals
- [ ] Database stores registration correctly
- [ ] Registration displays on all relevant pages

## Future Enhancements

- [ ] Integration with SARTHI (Vehicle Registration Database)
- [ ] Real-time registration verification API
- [ ] Support for international vehicle formats
- [ ] QR code integration for vehicle details
- [ ] Vehicle theft/blacklist checking
- [ ] Historical registration tracking

## Support & Troubleshooting

### Registration format validation fails:

1. Check format matches: `LLDDLLDDDD`
2. Use uppercase letters only
3. Verify state code is correct
4. Check for typos in numbers
5. Ensure no duplicate in system

### Database migration issues:

1. Migration runs automatically on app startup
2. Check `migrate_db()` is called in app initialization
3. Verify database file permissions
4. Check database schema with: `PRAGMA table_info(cars)`
