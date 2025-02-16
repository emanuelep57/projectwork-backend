import cloudinary
import cloudinary.uploader
from flask import current_app


def configure_cloudinary():
    cloudinary.config(
        cloud_name="dj5udxse6",
        api_key="642297578711331",
        api_secret="ZuOtUlULKB2ryltlbZwtq-saaGU",
        secure=True,
    )


def upload_pdf_to_cloudinary(pdf_buffer, filename):
    try:
        # Ensure Cloudinary is configured
        configure_cloudinary()

        # Reset buffer position
        pdf_buffer.seek(0)

        # Upload PDF to Cloudinary
        upload_result = cloudinary.uploader.upload(
            pdf_buffer,
            resource_type='raw',  # Use 'raw' for non-image files
            folder='pdf_biglietti',  # Optional: organize uploads in a folder
            public_id=filename.replace('.pdf', ''),  # Remove .pdf extension for public_id
            unique_filename=False,
            overwrite=True
        )

        # Return the secure URL of the uploaded file
        return upload_result['secure_url']

    except Exception as e:
        current_app.logger.error(f"Cloudinary upload error: {str(e)}")
        raise
