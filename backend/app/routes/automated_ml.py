from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.services.model_service import ModelService

router = APIRouter()
model_service = ModelService()


@router.post("/automated-ml")
async def automated_ml(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """
    Accept a sanitized CSV dataset and a natural language prompt,
    then automatically configure, train, and evaluate an ML model.

    The prompt should describe the ML objective, e.g.:
    - "Classify the species column"
    - "Predict the price column using regression"
    - "Categorize churn, optimize accuracy"
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted")

    try:
        result = await model_service.train_from_prompt(file, prompt)

        return {
            "status": "success",
            "model_summary": {
                "model_id": result["model_id"],
                "model_name": result["model_name"],
                "task_type": result["task_type"],
                "target_column": result["target_column"],
            },
            "evaluation_metrics": result["metrics"],
            "predictions": result["predictions"],
            "dataset_summary": result["dataset_summary"],
            "download_url": f"/api/model/download/{result['model_id']}",
            "message": result["message"],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Automated ML failed: {str(e)}")
