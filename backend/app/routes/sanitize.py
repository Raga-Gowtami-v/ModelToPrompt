from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from app.services.privacy_service import PrivacyService
from app.utils.file_parser import parse_uploaded_file

router = APIRouter()
privacy_service = PrivacyService()


@router.post("/sanitize")
async def sanitize(
    file: UploadFile = File(...),
    mode: Optional[str] = Form("redact"),
):
    """
    Detect and eliminate PII from a document, dataset, or image.

    Accepts: text files, CSV files, images (JPEG/PNG).
    Returns: masked/sanitized content, PII extraction report, risk score summary.
    """
    try:
        # Parse the uploaded file (handles text, CSV, images via OCR)
        content = await parse_uploaded_file(file)

        # Run PII detection and masking
        result = privacy_service.scan_and_mask(content, source=file.filename)

        return {
            "status": "success",
            "filename": file.filename,
            "sanitized_content": result["masked_text"],
            "original_length": result["original_length"],
            "pii_report": {
                "total_detections": len(result["detections"]),
                "detections": result["detections"],
            },
            "risk_summary": result["risk"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sanitization failed: {str(e)}")
