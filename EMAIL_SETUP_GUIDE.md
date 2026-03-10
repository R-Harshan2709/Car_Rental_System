# Email Configuration Setup Guide

## Overview

The car rental system uses Flask-Mail to send approval and rejection emails to customers. To enable email functionality, you need to configure the email credentials.

## Gmail SMTP Setup (Recommended)

### Step 1: Enable 2-Factor Authentication

1. Go to your Google Account: https://myaccount.google.com
2. Click on "Security" in the left sidebar
3. Enable "2-Step Verification"

### Step 2: Generate App Password

1. In Google Account, go to Security
2. Find "App passwords" (only appears if 2FA is enabled)
3. Select "Mail" and "Windows Computer" (or your OS)
4. Generate an App Password (16 characters)
5. Copy this password - you'll need it next

### Step 3: Set Environment Variables

Create a `.env` file in the root of your car_rental_system directory:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-char-app-password
MAIL_DEFAULT_SENDER=noreply@carrental.com
```

### Step 4: Load Environment Variables in app.py

Modify `app.py` to load the `.env` file:

```python
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from flask import Flask, render_template, redirect, url_for
from config import Config
# ... rest of imports
```

### Step 5: Install python-dotenv

```bash
pip install python-dotenv
```

Add it to `requirements.txt`:

```
python-dotenv>=0.21.0
```

## Alternative Email Providers

### Outlook/Hotmail SMTP

```
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### SendGrid SMTP

```
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your-sendgrid-api-key
```

## Testing Email Configuration

### Test in Python Console

```python
from flask import Flask
from config import Config
from utils.email_service import send_approval_email
import os

# Set environment variables
os.environ['MAIL_USERNAME'] = 'your-email@gmail.com'
os.environ['MAIL_PASSWORD'] = 'your-app-password'

# Create Flask app
app = Flask(__name__)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@carrental.com')

from utils.email_service import mail, init_mail
init_mail(app)

with app.app_context():
    result = send_approval_email(
        customer_email='test@example.com',
        customer_name='Test Customer',
        car_brand='Tesla',
        car_model='Model 3',
        rental_id=123,
        start_date='2025-12-01',
        end_date='2025-12-05',
        total_price=5000.00
    )
    print(f"Email sent: {result}")
```

## Troubleshooting

### Error: "SMTPAuthenticationError"

- Check your email and password are correct
- Make sure 2FA is enabled for Gmail
- Verify you're using an "App Password" not your regular password
- Check if less secure apps access is enabled (if not using app password)

### Error: "Connection refused"

- Verify MAIL_SERVER and MAIL_PORT are correct
- Check your firewall/antivirus isn't blocking SMTP
- Ensure TLS is enabled (MAIL_USE_TLS=True)

### Emails sent but not received

- Check spam/junk folder
- Verify recipient email is correct in database
- Check the application logs for errors (printed to console)

### Error: "SMTPServerDisconnected"

- SMTP connection timeout - may be network issue
- Try setting timeout in Flask-Mail config
- Consider using a dedicated email service

## Email Service Improvements Made

The email service now includes:

- ✓ Error logging to console
- ✓ Try-catch blocks for exception handling
- ✓ Debug information showing SMTP configuration
- ✓ Boolean return values to indicate success/failure
- ✓ Generic `send_email()` function for code reuse

## Email Events

### Approval Email

Sent when admin clicks "Approve" on a rental request. Contains:

- Booking ID
- Car details (brand, model)
- Rental dates
- Total price
- Encouragement to proceed with booking

### Rejection Email

Sent when admin clicks "Reject" on a rental request. Contains:

- Booking ID
- Car details
- Support contact encouragement

## Security Notes

⚠️ **IMPORTANT**:

- Never commit `.env` file to version control
- Add `.env` to `.gitignore`
- Use app-specific passwords, not account passwords
- Consider using a dedicated email service for production
- Implement rate limiting to prevent email spam abuse

## Production Recommendations

For production deployments:

1. Use a dedicated email service (SendGrid, Mailgun, AWS SES)
2. Implement email queue system for better reliability
3. Add email templates with proper formatting
4. Monitor email delivery rates
5. Implement bounce handling
6. Set up email analytics

## Next Steps

1. Configure your email credentials
2. Test the email service using the console test above
3. Test the admin approval feature
4. Check customer email for approval notification
5. Monitor console logs for any errors
