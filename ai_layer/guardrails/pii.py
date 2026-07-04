import re
from typing import Dict, Tuple

class PIIScanner:
    def __init__(self):
        # Phone pattern (Vietnamese formats: 09xx, 03xx, 08xx, 07xx, 05xx, +84, etc.)
        self.phone_pattern = re.compile(
            r'(?:\+84|0)(?:\s*\d{3}\s*\d{3}\s*\d{3}|\s*\d{2}\s*\d{3}\s*\d{4}|\s*\d{9,10})'
        )
        # Email pattern
        self.email_pattern = re.compile(
            r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        )
        # Citizen Identity Card (CCCD - 12 digits, or old CMND - 9 digits)
        self.cccd_pattern = re.compile(
            r'\b\d{9}\b|\b\d{12}\b'
        )

    def scan_and_redact(self, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Scans text for PII, replaces them with placeholders, and returns the redacted text 
        along with the mapping of placeholders -> original values (to restore them for tools).
        """
        redacted_text = text
        mapping = {}
        
        # Redact Emails
        emails = self.email_pattern.findall(text)
        for idx, email in enumerate(emails):
            placeholder = f"[REDACTED_EMAIL_{idx}]"
            mapping[placeholder] = email
            redacted_text = redacted_text.replace(email, placeholder)
            
        # Redact Phones
        phones = self.phone_pattern.findall(redacted_text)
        for idx, phone in enumerate(phones):
            # Clean spaces for unique mapping key
            clean_phone = phone.strip()
            placeholder = f"[REDACTED_PHONE_{idx}]"
            mapping[placeholder] = clean_phone
            redacted_text = redacted_text.replace(phone, placeholder)
            
        # Redact CCCD
        cccds = self.cccd_pattern.findall(redacted_text)
        for idx, cccd in enumerate(cccds):
            placeholder = f"[REDACTED_CCCD_{idx}]"
            mapping[placeholder] = cccd
            redacted_text = redacted_text.replace(cccd, placeholder)
            
        return redacted_text, mapping

    def restore_pii(self, text: str, mapping: Dict[str, str]) -> str:
        """
        Restores redacted PII in a text (e.g. before calling database APIs).
        """
        restored_text = text
        for placeholder, original in mapping.items():
            restored_text = restored_text.replace(placeholder, original)
        return restored_text
