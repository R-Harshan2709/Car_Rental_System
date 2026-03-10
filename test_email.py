#!/usr/bin/env python3
"""
Email Configuration Tester
Run this script to verify that your email setup is working correctly.
"""

import os
import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("Car Rental System - Email Configuration Tester")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking Environment Variables:")
    print("-" * 60)
    
    required_vars = [
        'MAIL_SERVER',
        'MAIL_PORT',
        'MAIL_USE_TLS',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    env_config = {}
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive data
            if var == 'MAIL_PASSWORD':
                display_value = '*' * len(value)
            else:
                display_value = value
            print(f"  ✓ {var}: {display_value}")
            env_config[var] = value
        else:
            print(f"  ✗ {var}: NOT SET")
    
    # Check config file
    print("\n2. Checking config.py:")
    print("-" * 60)
    try:
        from config import Config
        print(f"  MAIL_SERVER: {Config.MAIL_SERVER}")
        print(f"  MAIL_PORT: {Config.MAIL_PORT}")
        print(f"  MAIL_USE_TLS: {Config.MAIL_USE_TLS}")
        print(f"  MAIL_USERNAME: {Config.MAIL_USERNAME}")
        print(f"  MAIL_PASSWORD: {'*' * len(Config.MAIL_PASSWORD) if Config.MAIL_PASSWORD else 'NOT SET'}")
        
        # Check if using defaults
        if Config.MAIL_USERNAME == 'your-email@gmail.com':
            print("\n  ⚠️  WARNING: Using default MAIL_USERNAME placeholder!")
        if Config.MAIL_PASSWORD == 'your-app-password':
            print("  ⚠️  WARNING: Using default MAIL_PASSWORD placeholder!")
    except Exception as e:
        print(f"  ✗ Error reading config: {e}")
        return False
    
    # Test Flask-Mail
    print("\n3. Testing Flask-Mail Installation:")
    print("-" * 60)
    try:
        from flask_mail import Mail
        print("  ✓ Flask-Mail is installed")
    except ImportError:
        print("  ✗ Flask-Mail is NOT installed")
        print("    Run: pip install Flask-Mail")
        return False
    
    # Test connection
    print("\n4. Testing Email Connection:")
    print("-" * 60)
    try:
        from flask import Flask
        from config import Config
        from utils.email_service import mail, init_mail
        
        app = Flask(__name__)
        init_mail(app)
        
        with app.app_context():
            # Try to connect
            try:
                # This will attempt to send a test email
                from flask_mail import Message
                msg = Message(
                    subject='Test - Car Rental System',
                    recipients=[Config.MAIL_USERNAME],
                    body='This is a test email from the Car Rental System.',
                    html='<p>This is a <strong>test email</strong> from the Car Rental System.</p>'
                )
                mail.send(msg)
                print(f"  ✓ Test email sent successfully to {Config.MAIL_USERNAME}")
                print("    Check your inbox (and spam folder) for the test email")
                return True
            except Exception as e:
                print(f"  ✗ Failed to send test email: {str(e)}")
                print("\n  Possible solutions:")
                print("  1. Check your email credentials are correct")
                print("  2. Ensure Gmail 2FA is enabled and using App Password")
                print("  3. Check firewall/antivirus isn't blocking SMTP")
                print("  4. Verify MAIL_SERVER and MAIL_PORT are correct")
                return False
    except Exception as e:
        print(f"  ✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_email_config()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ Email configuration is working correctly!")
        print("  Admin approvals will now send emails to customers.")
    else:
        print("✗ Email configuration needs attention")
        print("  See EMAIL_SETUP_GUIDE.md for detailed instructions")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
