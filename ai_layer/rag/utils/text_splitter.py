import logging
from typing import List

logger = logging.getLogger(__name__)

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
    """
    Split text into chunks using RecursiveCharacterTextSplitter.
    Fallback to simple paragraph splitting if langchain is not available.
    """
    if not text or not text.strip():
        return []
        
    if LANGCHAIN_AVAILABLE:
        try:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            chunks = splitter.split_text(text)
            logger.info(f"Split text into {len(chunks)} chunks using RecursiveCharacterTextSplitter")
            return chunks
        except Exception as e:
            logger.error(f"Error using RecursiveCharacterTextSplitter: {e}")
            # Fallback to naive splitting
            pass
            
    # Fallback naive implementation
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [text.strip()]
    
    logger.info(f"Split text into {len(paragraphs)} chunks using naive splitter (fallback)")
    return paragraphs
