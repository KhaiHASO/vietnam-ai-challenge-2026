import uuid
import fitz  # PyMuPDF
from typing import List
from ai_layer.rag.interfaces.parser import BaseParser
from ai_layer.rag.models import Document, SourceType
from ai_layer.rag.utils.cleaning import clean_text

class PDFParser(BaseParser):
    """
    Parser for PDF files using PyMuPDF.
    Extracts text page by page.
    """
    
    def parse(self, file_path: str, source_type: SourceType, knowledge_item_id: str) -> List[Document]:
        if source_type != SourceType.PDF:
            raise ValueError(f"PDFParser expects SourceType.PDF, got {source_type}")
            
        documents = []
        try:
            # Open the PDF file
            doc = fitz.open(file_path)
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                raw_text = page.get_text("text")
                
                # Clean the extracted text
                cleaned_text = clean_text(raw_text)
                
                # Only create a document if there's text (skip empty pages/scanned images without OCR)
                if cleaned_text:
                    metadata = {
                        "page_number": page_num + 1,
                        "total_pages": total_pages,
                        "file_path": file_path
                    }
                    
                    document = Document(
                        id=str(uuid.uuid4()),
                        knowledge_item_id=knowledge_item_id,
                        text_content=cleaned_text,
                        metadata=metadata,
                        page_content=None
                    )
                    documents.append(document)
            
            doc.close()
            return documents
            
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF file {file_path}: {str(e)}")
