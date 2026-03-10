# Email Configuration Setup

The car rental system now includes email notifications for rental approvals and rejections. Follow these steps to set up email functionality.

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication

1. Go to your Google Account (myaccount.google.com)
2. Select Security on the left
3. Enable 2-Step Verification

### Step 2: Create an App Password

1. Go to Google Account Security settings
2. Find "App passwords" (this option only appears if 2FA is enabled)
3. Select Mail and Windows Computer (or appropriate device)
4. Google will generate a 16-character password

### Step 3: Set Environment Variables

Create a `.env` file in the project root directory or set these environment variables:

```
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-16-character-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

## Other Email Providers

### Outlook/Hotmail

```
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### Yahoo Mail

```
MAIL_SERVER=smtp.mail.yahoo.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@yahoo.com
MAIL_PASSWORD=your-password
```

## Installation

Install the required package:

```bash
pip install -r requirements.txt
```

## Features

- **Approval Email**: Sent when admin approves a rental
- **Rejection Email**: Sent when admin rejects a rental
- **HTML and Plain Text**: Emails include both formats
- **Detailed Information**: Includes booking ID, car details, dates, and pricing

## Testing Locally

For development/testing without sending actual emails, you can:

1. Check the console output for email content
2. Use a service like Mailtrap (mailtrap.io) for free testing
3. Mock the email service in tests

## Troubleshooting

- **Authentication Error**: Verify your app password is correct (not your regular Gmail password)
- **Connection Error**: Check firewall settings and ensure port 587 is not blocked
- **Email Not Sent**: Check application logs for error messages
- **TLS Error**: Ensure MAIL_USE_TLS is set to True for port 587

## Security Notes

- Never commit `.env` file with real credentials
- Use app-specific passwords, not your actual Gmail password
- Consider using environment variable management tools in production
