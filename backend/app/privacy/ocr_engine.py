from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image


class OCREngine:
    """Extract text from images using Tesseract OCR."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text(self, image_path: str) -> str:
        """Extract text from an image file."""
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        image = Image.open(path)
        text = pytesseract.image_to_string(image)
        return text.strip()

    def extract_text_from_bytes(self, image_bytes: bytes) -> str:
        """Extract text from image bytes."""
        from io import BytesIO
        image = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
