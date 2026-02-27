from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.model_service import ModelService
from app.schemas.request_schemas import PromptRequest
from app.schemas.response_schemas import PromptResponse

router = APIRouter()
model_service = ModelService()


@router.post("/train", response_model=PromptResponse)
async def train_model(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """Accept a CSV file and a user prompt, train a model, and return a .pkl file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    try:
        result = await model_service.train_from_prompt(file, prompt)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")
