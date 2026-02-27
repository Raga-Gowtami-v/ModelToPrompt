from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class Detection(BaseModel):
    type: str
    value: str
    start: int
    end: int
    confidence: float
    detector: str


class RiskResult(BaseModel):
    score: float
    level: str
    breakdown: Dict[str, Any]
    total_detections: int = 0


class ScanResponse(BaseModel):
    source: str
    original_length: int
    masked_text: str
    detections: List[Detection]
    risk: RiskResult


class PromptResponse(BaseModel):
    model_id: str
    task_type: str
    target_column: str
    model_name: str = ""
    metrics: Dict[str, Any] = {}
    predictions: List[Dict[str, Any]] = []
    dataset_summary: Dict[str, Any] = {}
    model_path: str
    message: str


class PIIReport(BaseModel):
    total_detections: int
    detections: List[Detection]


class SanitizeResponse(BaseModel):
    status: str
    filename: str
    sanitized_content: str
    original_length: int
    pii_report: PIIReport
    risk_summary: RiskResult


class ModelSummary(BaseModel):
    model_id: str
    model_name: str
    task_type: str
    target_column: str


class DatasetSummary(BaseModel):
    total_rows: int
    train_rows: int
    test_rows: int
    features: List[str]


class AutoMLResponse(BaseModel):
    status: str
    model_summary: ModelSummary
    evaluation_metrics: Dict[str, float]
    predictions: List[Dict[str, Any]]
    dataset_summary: DatasetSummary
    download_url: str
    message: str
