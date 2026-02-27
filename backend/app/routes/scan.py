from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.privacy_service import PrivacyService
from app.schemas.response_schemas import ScanResponse
from app.utils.file_parser import parse_uploaded_file

router = APIRouter()
privacy_service = PrivacyService()


@router.post("/upload", response_model=ScanResponse)
async def scan_file(file: UploadFile = File(...)):
    """Upload a document, image, or CSV to scan for PII."""
    try:
        content = await parse_uploaded_file(file)
        result = privacy_service.scan_and_mask(content, file.filename)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.post("/text", response_model=ScanResponse)
async def scan_text(text: str):
    """Scan raw text for PII."""
    result = privacy_service.scan_and_mask(text, source="direct_input")
    return result
