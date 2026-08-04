import fitz  # PyMuPDF
from utils.logger import get_logger

logger = get_logger("PDFParser")

class PDFParser:
    @staticmethod
    def extract_text(file_path_or_bytes) -> str:
        """
        Extracts raw clean text from a PDF file path or binary buffer.
        Handles multi-column resume layout cleanly.
        """
        text = ""
        try:
            if isinstance(file_path_or_bytes, str):
                doc = fitz.open(file_path_or_bytes)
            else:
                doc = fitz.open(stream=file_path_or_bytes, filetype="pdf")

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                # Sort blocks chronologically for natural reading flow
                text += page.get_text("text", sort=True) + "\n"
            
            logger.info("PDF text extraction completed successfully.")
            return text.strip()
        except Exception as e:
            logger.error(f"Error parsing PDF file: {str(e)}")
            return ""