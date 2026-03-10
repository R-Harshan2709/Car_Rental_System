# Car Rental System

A full-stack web application for managing car rentals with three distinct user roles: Admin, Car Owner, and Customer.

## Features

### Admin
- Dashboard with system statistics
- Approve/reject car listings
- Manage users and drivers
- View all rentals and transactions

### Car Owner
- Add and manage car listings
- View rental history for owned cars
- Track revenue from rentals
- Edit car details

### Customer
- Browse available cars with filters
- Rent cars with automatic driver assignment
- View rental history
- Download PDF receipts with booking details

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite3
- **PDF Generation**: ReportLab
- **Frontend**: HTML, CSS (Modern Dark Theme), JavaScript
- **Image Handling**: Pillow

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd "d:\Project Sample\car_rental_system"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**:
   ```bash
   python app.py
   ```

2. **Access the application**:
   Open your browser and navigate to: `http://localhost:5000`

## Default Credentials

**Admin Account**:
- Username: `admin`
- Password: `admin123`

## Usage Guide

### For Customers

1. Register a new account (select "Rent cars" role)
2. Login with your credentials
3. Browse available cars
4. Select a car and choose rental dates
5. Complete the rental (driver will be auto-assigned)
6. Download your PDF receipt from "My Rentals"

### For Car Owners

1. Register a new account (select "List my cars" role)
2. Login with your credentials
3. Add a new car with details and image
4. Wait for admin approval
5. Once approved, your car will be available for rent
6. View rentals and revenue in your dashboard

### For Admins

1. Login with admin credentials
2. Review pending car approvals
3. Approve or reject car listings
4. Manage users and drivers
5. Monitor all rentals and system statistics

## Project Structure

```
car_rental_system/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models.py              # Database models and functions
├── requirements.txt       # Python dependencies
├── routes/
│   ├── auth.py           # Authentication routes
│   ├── admin.py          # Admin routes
│   ├── owner.py          # Car owner routes
│   └── customer.py       # Customer routes
├── templates/
│   ├── base.html         # Base template
│   ├── auth/             # Login and registration pages
│   ├── admin/            # Admin dashboard and pages
│   ├── owner/            # Car owner pages
│   └── customer/         # Customer pages
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── main.js       # JavaScript functionality
│   ├── uploads/          # Car images (auto-created)
│   └── receipts/         # PDF receipts (auto-created)
└── utils/
    └── pdf_generator.py  # PDF receipt generation
```

## Features in Detail

### PDF Receipt Generation
- Professional receipts with all rental details
- Driver information (name, phone, license)
- Payment breakdown with tax calculation
- Unique booking ID for each rental

### Automatic Driver Assignment
- System automatically assigns available drivers
- Driver details included in receipts
- Driver availability tracking

### Car Approval Workflow
1. Car owner submits car listing
2. Admin reviews and approves/rejects
3. Only approved cars appear in customer browse page

### Image Upload
- Support for PNG, JPG, JPEG, GIF formats
- Maximum file size: 5MB
- Images stored in `static/uploads/cars/`

## Database Schema

- **users**: User accounts with roles (admin, owner, customer)
- **cars**: Car listings with approval status
- **drivers**: Driver pool for rental assignments
- **rentals**: Rental transactions
- **payments**: Payment records with receipt paths

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Role-based access control
- CSRF protection (Flask built-in)

## Future Enhancements

- Email notifications
- Real payment gateway integration
- Advanced search and filtering
- Rating and review system
- Mobile app version

## License

This project is for educational purposes.

## Support

For issues or questions, please contact the development team.
