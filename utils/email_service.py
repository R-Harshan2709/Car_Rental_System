from flask_mail import Mail, Message
from config import Config

mail = Mail()

def init_mail(app):
    """Initialize mail with Flask app"""
    app.config['MAIL_SERVER'] = Config.MAIL_SERVER
    app.config['MAIL_PORT'] = Config.MAIL_PORT
    app.config['MAIL_USE_TLS'] = Config.MAIL_USE_TLS
    app.config['MAIL_USERNAME'] = Config.MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = Config.MAIL_PASSWORD
    app.config['MAIL_DEFAULT_SENDER'] = Config.MAIL_DEFAULT_SENDER
    mail.init_app(app)

def send_email(subject, recipients, body, html_body):
    """Generic email sending function with error handling"""
    try:
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html_body
        )
        mail.send(msg)
        print(f"✓ Email sent successfully to {recipients}")
        return True
    except Exception as e:
        print(f"✗ Error sending email: {str(e)}")
        print(f"  MAIL_SERVER: {Config.MAIL_SERVER}")
        print(f"  MAIL_PORT: {Config.MAIL_PORT}")
        print(f"  MAIL_USERNAME: {Config.MAIL_USERNAME}")
        return False

def send_approval_email(customer_email, customer_name, car_brand, car_model, rental_id, start_date, end_date, total_price):
    """Send approval email to customer"""
    subject = f"✓ Rental Approved - Car Rental System"
    
    body = f"""
Dear {customer_name},

Great news! Your rental request has been APPROVED by our admin team.

Rental Details:
================
Booking ID: #{rental_id}
Car: {car_brand} {car_model}
Start Date: {start_date}
End Date: {end_date}
Total Price: ₹{total_price:.2f}

You can now proceed with your booking. Please log in to your account to view more details and download your receipt.

Thank you for choosing our car rental service!

Best regards,
Car Rental System Team
"""

    html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #3b82f6, #2563eb); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 20px; border-radius: 0 0 8px 8px; }}
        .approval-badge {{ display: inline-block; background: #10b981; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; }}
        .details {{ background: #f0f9ff; padding: 15px; border-left: 4px solid #3b82f6; margin: 20px 0; border-radius: 5px; }}
        .detail-item {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #2563eb; }}
        .footer {{ text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
        a {{ color: #3b82f6; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Rental Approved!</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{customer_name}</strong>,</p>
            
            <p>Great news! Your rental request has been <span class="approval-badge">✓ APPROVED</span> by our admin team.</p>
            
            <div class="details">
                <h3 style="margin-top: 0; color: #2563eb;">Rental Details</h3>
                <div class="detail-item">
                    <span class="label">Booking ID:</span> #{rental_id}
                </div>
                <div class="detail-item">
                    <span class="label">Car:</span> {car_brand} {car_model}
                </div>
                <div class="detail-item">
                    <span class="label">Start Date:</span> {start_date}
                </div>
                <div class="detail-item">
                    <span class="label">End Date:</span> {end_date}
                </div>
                <div class="detail-item">
                    <span class="label">Total Price:</span> <span style="color: #10b981; font-weight: bold;">₹{total_price:.2f}</span>
                </div>
            </div>
            
            <p>You can now proceed with your booking. Please log in to your account to view more details and download your receipt.</p>
            
            <p style="color: #666; font-size: 14px;">If you have any questions, please don't hesitate to contact our support team.</p>
            
            <div class="footer">
                <p>Thank you for choosing our car rental service!</p>
                <p>Car Rental System Team</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    return send_email(subject, [customer_email], body, html_body)

def send_trip_completion_email(customer_email, customer_name, car_brand, car_model, rental_id, start_date, end_date, total_price):
    """Send trip completion verification email to customer"""
    subject = f"✓ Trip Completed - Car Rental System"
    
    body = f"""
Dear {customer_name},

Your rental trip has been completed and verified by our admin team.

Trip Details:
================
Booking ID: #{rental_id}
Car: {car_brand} {car_model}
Start Date: {start_date}
End Date: {end_date}
Total Price: ₹{total_price:.2f}

Status: COMPLETED ✓

Thank you for using our car rental service. We hope you had a great experience. Please feel free to rent with us again!

Best regards,
Car Rental System Team
"""

    html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 20px; border-radius: 0 0 8px 8px; }}
        .completion-badge {{ display: inline-block; background: #10b981; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; }}
        .details {{ background: #f0fdf4; padding: 15px; border-left: 4px solid #10b981; margin: 20px 0; border-radius: 5px; }}
        .detail-item {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #059669; }}
        .footer {{ text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Trip Completed!</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{customer_name}</strong>,</p>
            
            <p>Your rental trip has been <span class="completion-badge">✓ COMPLETED</span> and verified by our admin team.</p>
            
            <div class="details">
                <h3 style="margin-top: 0; color: #059669;">Trip Details</h3>
                <div class="detail-item">
                    <span class="label">Booking ID:</span> #{rental_id}
                </div>
                <div class="detail-item">
                    <span class="label">Car:</span> {car_brand} {car_model}
                </div>
                <div class="detail-item">
                    <span class="label">Start Date:</span> {start_date}
                </div>
                <div class="detail-item">
                    <span class="label">End Date:</span> {end_date}
                </div>
                <div class="detail-item">
                    <span class="label">Total Price:</span> <span style="color: #10b981; font-weight: bold;">₹{total_price:.2f}</span>
                </div>
                <div class="detail-item">
                    <span class="label">Status:</span> <span style="color: #10b981; font-weight: bold;">COMPLETED ✓</span>
                </div>
            </div>
            
            <p style="color: #666; font-size: 14px;">Thank you for using our car rental service. We hope you had a great experience with us!</p>
            
            <p style="color: #666; font-size: 14px;">If you have any questions or feedback, please don't hesitate to contact our support team.</p>
            
            <div class="footer">
                <p>We look forward to serving you again in the future!</p>
                <p>Car Rental System Team</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    return send_email(subject, [customer_email], body, html_body)
def send_rejection_email(customer_email, customer_name, car_brand, car_model, rental_id):
    """Send rejection email to customer"""
    subject = f"✗ Rental Request Rejected - Car Rental System"
    
    body = f"""
Dear {customer_name},

We regret to inform you that your rental request has been REJECTED by our admin team.

Rental Details:
================
Booking ID: #{rental_id}
Car: {car_brand} {car_model}

If you have any questions or would like more information about the rejection, please contact our support team.

Thank you for your interest in our car rental service.

Best regards,
Car Rental System Team
"""

    html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background: #f9f9f9; border-radius: 8px; }}
        .header {{ background: linear-gradient(135deg, #ef4444, #dc2626); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background: white; padding: 20px; border-radius: 0 0 8px 8px; }}
        .rejection-badge {{ display: inline-block; background: #ef4444; color: white; padding: 10px 15px; border-radius: 5px; font-weight: bold; margin-bottom: 20px; }}
        .details {{ background: #fef2f2; padding: 15px; border-left: 4px solid #ef4444; margin: 20px 0; border-radius: 5px; }}
        .detail-item {{ margin: 10px 0; }}
        .label {{ font-weight: bold; color: #dc2626; }}
        .footer {{ text-align: center; margin-top: 20px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✗ Rental Request Rejected</h1>
        </div>
        <div class="content">
            <p>Dear <strong>{customer_name}</strong>,</p>
            
            <p>We regret to inform you that your rental request has been <span class="rejection-badge">✗ REJECTED</span> by our admin team.</p>
            
            <div class="details">
                <h3 style="margin-top: 0; color: #dc2626;">Rental Details</h3>
                <div class="detail-item">
                    <span class="label">Booking ID:</span> #{rental_id}
                </div>
                <div class="detail-item">
                    <span class="label">Car:</span> {car_brand} {car_model}
                </div>
            </div>
            
            <p style="color: #666; font-size: 14px;">If you have any questions or would like more information about the rejection, please contact our support team.</p>
            
            <div class="footer">
                <p>Thank you for your interest in our car rental service.</p>
                <p>Car Rental System Team</p>
            </div>
        </div>
    </div>
</body>
</html>
"""

    return send_email(subject, [customer_email], body, html_body)
