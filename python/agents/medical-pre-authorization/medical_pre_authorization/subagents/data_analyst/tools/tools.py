from google.cloud import storage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from datetime import datetime
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import io
import logging
import warnings
import os

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


warnings.filterwarnings("ignore")
STORAGE_BUCKET = os.getenv("REPORT_STORAGE_BUCKET")
logger = logging.getLogger(__name__)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
REPORT_DOCUMENT_FILE_NAME = f"pre_authorization_report_{timestamp}.pdf"


def store_pdf(pdf_text: str) -> str:
    """Writes text to a PDF file, then uploads it to Google Cloud Storage.
    Args:
        pdf_text: The text to write to the PDF.
    """
    pdf_buffer = None  # Initialize to None for finally block
    try:
        pdf_buffer = io.BytesIO()

        # Use SimpleDocTemplate for handling complex layouts, text wrapping, and page breaks
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Add the text to the story, handling paragraphs and line breaks
        # We'll split the text by double newlines to treat them as separate paragraphs
        # and then add each paragraph to the story.
        for paragraph_text in pdf_text.split("\n\n"):
            if paragraph_text.strip():
                p = Paragraph(
                    paragraph_text.strip().replace("\n", "<br/>"), styles["Normal"]
                )
                story.append(p)
                # The explicit Spacer line below was removed to reduce excessive blank lines.
                story.append(Spacer(1, 0.05 * letter[1]))

        doc.build(story)

        pdf_buffer.seek(0)  # Reset buffer to start

        # Upload the PDF to GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(STORAGE_BUCKET)
        blob = bucket.blob(REPORT_DOCUMENT_FILE_NAME)

        blob.upload_from_file(pdf_buffer, content_type="application/pdf")

        logger.info(
            f"Successfully uploaded PDF to gs://{STORAGE_BUCKET}/{REPORT_DOCUMENT_FILE_NAME}"
        )
        return f"Successfully uploaded PDF to gs://{STORAGE_BUCKET}/{REPORT_DOCUMENT_FILE_NAME}"

    except Exception as e:
        logger.error(f"Error writing text to PDF and uploading: {e}")
        raise
    finally:
        if pdf_buffer:
            pdf_buffer.close()
