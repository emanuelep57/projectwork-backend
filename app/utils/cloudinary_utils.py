import os

import cloudinary
import cloudinary.uploader
from flask import current_app


def configure_cloudinary():
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
        secure=True,
    )


def upload_pdf_to_cloudinary(pdf_buffer, filename):
    try:
        # configurazione cloudinary
        configure_cloudinary()

        # Reset buffer
        pdf_buffer.seek(0)

        # Upload PDF su Cloudinary
        upload_result = cloudinary.uploader.upload(
            pdf_buffer,
            resource_type='raw',  # 'raw' per file che non sono immagini
            folder='pdf_biglietti',
            public_id=filename.replace('.pdf', ''),  # Rimozione dell'estensione .pdf
            unique_filename=False,
            overwrite=True
        )

        # URL del file caricato
        return upload_result['secure_url']

    except Exception as e:
        current_app.logger.error(f"Cloudinary error: {str(e)}")
        raise
