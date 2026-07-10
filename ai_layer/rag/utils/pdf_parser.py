import fitz  # PyMuPDF
import logging

logger = logging.getLogger(__name__)

class PDFParser:
    @staticmethod
    def parse(file_bytes: bytes) -> str:
        """
        Parses a PDF file from bytes and extracts its text.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            raise ValueError(f"Lỗi khi đọc file PDF: {str(e)}")
