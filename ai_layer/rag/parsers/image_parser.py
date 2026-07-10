import uuid
from typing import List
from PIL import Image

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

from ai_layer.rag.interfaces.parser import BaseParser
from ai_layer.rag.models import Document, SourceType
from ai_layer.rag.utils.cleaning import clean_text

class TrOCRSingleton:
    """
    Singleton pattern to ensure the TrOCR model is only loaded into memory once.
    This saves significant RAM and startup time when parsing multiple images.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TrOCRSingleton, cls).__new__(cls)
            cls._instance.processor = None
            cls._instance.model = None
            cls._instance._load_model()
        return cls._instance
        
    def _load_model(self):
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library is not installed. Run `pip install transformers`")
            
        print("Loading TrOCR model into memory (Singleton)...")
        # Using a base printed model, can be swapped for handwritten if needed.
        model_id = "microsoft/trocr-base-printed"
        self.processor = TrOCRProcessor.from_pretrained(model_id)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_id)
        print("TrOCR model loaded successfully.")

    def extract_text(self, image: Image.Image) -> str:
        """
        Runs OCR on the given image and returns the extracted text.
        """
        pixel_values = self.processor(image, return_tensors="pt").pixel_values
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return generated_text


class ImageParser(BaseParser):
    """
    Parser for Image files using TrOCR (Transformers OCR).
    Extracts text from scanned documents or photos.
    """
    
    def __init__(self):
        # Initialize or get the singleton instance of TrOCR
        self.ocr_engine = TrOCRSingleton()
        
    def parse(self, file_path: str, source_type: SourceType, knowledge_item_id: str) -> List[Document]:
        if source_type != SourceType.IMAGE:
            raise ValueError(f"ImageParser expects SourceType.IMAGE, got {source_type}")
            
        try:
            image = Image.open(file_path).convert("RGB")
            raw_text = self.ocr_engine.extract_text(image)
            
            cleaned_text = clean_text(raw_text)
            
            if cleaned_text:
                metadata = {
                    "file_path": file_path,
                    "resolution": image.size,
                    "ocr_model": "microsoft/trocr-base-printed"
                }
                
                document = Document(
                    id=str(uuid.uuid4()),
                    knowledge_item_id=knowledge_item_id,
                    text_content=cleaned_text,
                    metadata=metadata,
                    page_content=None
                )
                return [document]
            
            return []
            
        except Exception as e:
            raise RuntimeError(f"Error parsing Image file {file_path}: {str(e)}")
