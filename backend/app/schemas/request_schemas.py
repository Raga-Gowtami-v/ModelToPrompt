from pydantic import BaseModel
from typing import Optional


class ScanRequest(BaseModel):
    text: str
    source: Optional[str] = "direct_input"


class PromptRequest(BaseModel):
    prompt: str
    target_column: Optional[str] = None
    task_type: Optional[str] = None  # "classification" or "regression"
