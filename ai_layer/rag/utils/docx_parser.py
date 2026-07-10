import zipfile
import xml.etree.ElementTree as ET
import io
import logging

logger = logging.getLogger(__name__)

class DocxParser:
    @staticmethod
    def parse(file_content: bytes) -> str:
        """
        Parses text from a .docx file without requiring external dependencies like python-docx.
        """
        try:
            with zipfile.ZipFile(io.BytesIO(file_content)) as docx:
                content = docx.read('word/document.xml')
                
            tree = ET.fromstring(content)
            
            # The namespace for Word XML
            namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            
            paragraphs = []
            for p in tree.findall('.//w:p', namespaces):
                texts = [node.text for node in p.findall('.//w:t', namespaces) if node.text]
                if texts:
                    paragraphs.append(''.join(texts))
                    
            return '\n\n'.join(paragraphs)
            
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            raise ValueError(f"Could not parse DOCX file: {e}")
