import csv
from io import StringIO
from pathlib import Path

from fastapi import UploadFile

from app.config import settings
from app.privacy.ocr_engine import OCREngine

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}
ocr_engine = OCREngine()


async def parse_uploaded_file(file: UploadFile) -> str:
    """Parse an uploaded file and return its text content."""
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")

    content_bytes = await file.read()

    if ext in IMAGE_EXTENSIONS:
        return ocr_engine.extract_text_from_bytes(content_bytes)

    if ext == ".csv":
        return _parse_csv(content_bytes.decode("utf-8"))

    if ext == ".txt":
        return content_bytes.decode("utf-8")

    if ext == ".pdf":
        return _parse_pdf(content_bytes)

    if ext == ".docx":
        return _parse_docx(content_bytes)

    raise ValueError(f"No parser available for: {ext}")


def _parse_csv(text: str) -> str:
    """Flatten CSV content into a single text string."""
    reader = csv.reader(StringIO(text))
    rows = [" ".join(row) for row in reader]
    return "\n".join(rows)


def _parse_pdf(content_bytes: bytes) -> str:
    """Extract text from PDF bytes."""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=content_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except ImportError:
        raise ValueError("PDF parsing requires PyMuPDF. Install with: pip install PyMuPDF")


def _parse_docx(content_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    try:
        from io import BytesIO
        from docx import Document
        doc = Document(BytesIO(content_bytes))
        return "\n".join(p.text for p in doc.paragraphs)
    except ImportError:
        raise ValueError("DOCX parsing requires python-docx. Install with: pip install python-docx")
