from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from app.config import settings

router = APIRouter()


@router.get("/download/{model_id}")
async def download_model(model_id: str):
    """Download a trained model (.pkl file) by its ID."""
    model_path = Path(settings.MODEL_OUTPUT_DIR) / f"{model_id}.pkl"
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")
    return FileResponse(
        path=str(model_path),
        filename=f"{model_id}.pkl",
        media_type="application/octet-stream",
    )


@router.get("/list")
async def list_models():
    """List all available trained models."""
    model_dir = Path(settings.MODEL_OUTPUT_DIR)
    models = [
        {"id": f.stem, "filename": f.name, "size_bytes": f.stat().st_size}
        for f in model_dir.glob("*.pkl")
    ]
    return {"models": models}
