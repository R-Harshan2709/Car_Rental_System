from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from datetime import datetime
import os
from config import Config

def generate_receipt(rental_data, payment_data, car_data, user_data, driver_data):
    """
    Generate a professional PDF receipt for a car rental
    
    Args:
        rental_data: dict with rental information
        payment_data: dict with payment information
        car_data: dict with car information
        user_data: dict with user information
        driver_data: dict with driver information
    
    Returns:
        str: Path to the generated PDF file
    """
    # Create filename
    receipt_filename = f"receipt_{rental_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    receipt_path = os.path.join(Config.RECEIPT_FOLDER, receipt_filename)
    
    # Create PDF document
    doc = SimpleDocTemplate(receipt_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    normal_style.fontSize = 10
    
    # Title
    title = Paragraph("CAR RENTAL RECEIPT", title_style)
    story.append(title)
    
    # Receipt info
    receipt_info = [
        ['Receipt Number:', f"#{payment_data['id']:06d}"],
        ['Date:', datetime.now().strftime('%B %d, %Y')],
        ['Booking ID:', f"#{rental_data['id']:06d}"]
    ]
    
    receipt_table = Table(receipt_info, colWidths=[2*inch, 4*inch])
    receipt_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
    ]))
    story.append(receipt_table)
    story.append(Spacer(1, 20))
    
    # Customer Information
    story.append(Paragraph("Customer Information", heading_style))
    customer_info = [
        ['Name:', user_data['username']],
        ['Email:', user_data['email']],
    ]
    customer_table = Table(customer_info, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
    ]))
    story.append(customer_table)
    story.append(Spacer(1, 20))
    
    # Rental Details
    story.append(Paragraph("Rental Details", heading_style))
    rental_info = [
        ['Car:', f"{car_data['brand']} {car_data['model']} ({car_data['year']})"],
        ['Start Date:', rental_data['start_date']],
        ['End Date:', rental_data['end_date']],
        ['Daily Rate:', f"₹{car_data['price_per_day']:.2f}"],
    ]
    rental_table = Table(rental_info, colWidths=[2*inch, 4*inch])
    rental_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
    ]))
    story.append(rental_table)
    story.append(Spacer(1, 20))
    
    # Driver Information
    story.append(Paragraph("Assigned Driver", heading_style))
    driver_info = [
        ['Driver Name:', driver_data['name']],
        ['Phone Number:', driver_data['phone']],
        ['License:', driver_data['license_number']],
    ]
    driver_table = Table(driver_info, colWidths=[2*inch, 4*inch])
    driver_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('PADDING', (10, 8), (10, 8), 10),
    ]))
    story.append(driver_table)
    story.append(Spacer(1, 30))
    
    # Payment Summary
    story.append(Paragraph("Payment Summary", heading_style))
    payment_info = [
        ['Subtotal:', f"₹{rental_data['total_price']:.2f}"],
        ['Tax (10%):', f"₹{rental_data['total_price'] * 0.1:.2f}"],
        ['Total Amount:', f"₹{payment_data['amount']:.2f}"],
        ['Payment Status:', 'PAID']
    ]
    payment_table = Table(payment_info, colWidths=[4*inch, 2*inch])
    payment_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -2), 'Helvetica-Bold'),
        ('FONTNAME', (0, -2), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6b7280')),
        ('LINEABOVE', (0, -2), (-1, -2), 2, colors.HexColor('#2563eb')),
        ('FONTSIZE', (0, -2), (-1, -1), 12),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#059669')),
    ]))
    story.append(payment_table)
    story.append(Spacer(1, 40))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#9ca3af'),
        alignment=TA_CENTER
    )
    footer_text = """
    <para align=center>
    Thank you for choosing our car rental service!<br/>
    For any questions or concerns, please contact us at support@carrental.com<br/>
    <b>This is an electronically generated receipt and does not require a signature.</b>
    </para>
    """
    story.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(story)
    
    return receipt_filename
