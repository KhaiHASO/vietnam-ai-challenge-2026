import re
import unicodedata

def clean_text(raw_text: str) -> str:
    """
    Cleans and normalizes text extracted from documents.
    - Normalizes Unicode characters.
    - Removes non-printable characters.
    - Replaces multiple whitespace/newlines with a single space or newline.
    - Trims leading/trailing whitespace.
    """
    if not raw_text:
        return ""
        
    # 1. Normalize Unicode (NFC is generally best for Vietnamese)
    text = unicodedata.normalize('NFC', raw_text)
    
    # 2. Remove non-printable characters except for newlines and tabs
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t"))
    
    # 3. Replace multiple spaces with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    
    # 4. Replace multiple newlines with a maximum of two newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # 5. Trim leading and trailing whitespace
    return text.strip()
