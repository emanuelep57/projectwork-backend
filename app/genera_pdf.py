import os
from flask import Blueprint, current_app
from flask_login import current_user
import requests
import io
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.platypus import PageBreak
from reportlab.lib.units import inch
from reportlab.lib.colors import black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image as ReportlabImage
from reportlab.lib.enums import TA_CENTER

def create_pdf_styles():
    """Create custom PDF styles for the ticket."""
    styles = getSampleStyleSheet()

    # Only add the style if it doesn't already exist
    if 'CustomTitle' not in styles:
        styles.add(ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=black,
            alignment=TA_CENTER
        ))

    if 'CustomSubtitle' not in styles:
        styles.add(ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=black,
            alignment=TA_CENTER
        ))

    return styles


def generate_qr_code(data, box_size=10):
    """Generate a QR code for the ticket."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


def download_image(url):
    """Download image from URL and return as bytes."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return io.BytesIO(response.content)
    except Exception as e:
        current_app.logger.error(f"Failed to download image: {e}")
        return None


def genera_biglietto_pdf(tickets_info, order_id):
    """
    Generate PDF for multiple tickets in a single document.

    Args:
        tickets_info (list): List of tuples containing ticket details.
        order_id (int): ID of the order for the title.

    Returns:
        BytesIO: PDF buffer.
    """
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Create styles
    styles = create_pdf_styles()

    # Collect all story elements
    story = []

    # Logo path (ensure this path is correct)
    logo_path = "/home/emanuele/project_work/react-shadcn/public/images/logo_pegasus.webp"

    print(f"Tickets info length: {len(tickets_info)}")
    for item in tickets_info:
        print(f"Ticket: {item[0].id}, Film: {item[1].titolo}")

    if not tickets_info:
        current_app.logger.error("No ticket information provided")
        raise ValueError("Empty ticket information")

    for ticket, film, proiezione, sala, posto in tickets_info:
        page_content = []

        # Add logo if exists
        if os.path.exists(logo_path):
            try:
                logo = ReportlabImage(logo_path, width=1.5 * inch, height=1.5 * inch)
                logo.hAlign = 'RIGHT'
                page_content.append(logo)
            except Exception as e:
                current_app.logger.error(f"Error loading logo: {e}")

        # Add film poster
        if film.url_copertina:
            poster_image = download_image(film.url_copertina)
            if poster_image:
                try:
                    poster = ReportlabImage(poster_image, width=3 * inch, height=4 * inch)
                    poster.hAlign = 'CENTER'
                    page_content.append(poster)
                except Exception as e:
                    current_app.logger.error(f"Error loading poster image: {e}")

        # Generate QR code
        qr_data = f"Ticket ID: {ticket.id}, Film: {film.titolo}, Date: {proiezione.data_ora}"
        qr_img = generate_qr_code(qr_data)
        qr_image = ReportlabImage(qr_img, width=1.5 * inch, height=1.5 * inch)
        qr_image.hAlign = 'CENTER'

        # Add ticket details
        guest_name = f"{ticket.nome_ospite or current_user.nome} {ticket.cognome_ospite or current_user.cognome}"

        page_content.extend([
            Paragraph(f"Order ID: {order_id} - CINEMA PEGASUS", styles['CustomTitle']),
            Paragraph(f"Film: {film.titolo}", styles['CustomSubtitle']),
            Paragraph(f"Date: {proiezione.data_ora.strftime('%d/%m/%Y')}", styles['CustomSubtitle']),
            Paragraph(f"Time: {proiezione.data_ora.strftime('%H:%M')}", styles['CustomSubtitle']),
            Paragraph(f"Room: {sala.nome}", styles['CustomSubtitle']),
            qr_image,
            Paragraph(f"Name: {guest_name}", styles['CustomSubtitle']),
            Paragraph(f"Seat: {posto.fila}{posto.numero}", styles['CustomSubtitle']),
        ])

        # Add page content to the story
        story.extend(page_content)
        story.append(PageBreak())

    # Build PDF
    try:
        doc.build(story)
    except Exception as e:
        current_app.logger.error(f"Error building PDF: {e}")

    buffer.seek(0)
    buffer_content = buffer.getvalue()
    current_app.logger.info(f"PDF Buffer Size: {len(buffer_content)} bytes")

    if len(buffer_content) == 0:
        current_app.logger.error("Generated PDF is empty")
        raise ValueError("PDF generation failed - empty document")

    return buffer
