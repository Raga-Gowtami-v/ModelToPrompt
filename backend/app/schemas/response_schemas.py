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
    detection_reason: str = ""
    target_column: str
    model_name: str = ""
    selected_model: str = ""
    selected_metric: str = ""
    primary_score: float = 0.0
    train_primary_score: Optional[float] = None
    generalization_gap: Optional[float] = None
    adjusted_score: Optional[float] = None
    metrics: Dict[str, Any] = {}
    all_model_metrics: List[Dict[str, Any]] = []
    feature_importance: Optional[List[Dict[str, Any]]] = None
    predictions: List[Dict[str, Any]] = []
    train_rows: int = 0
    test_rows: int = 0
    evaluation_method: str = "80-20 Train-Test Split"
    dataset_summary: Dict[str, Any] = {}
    model_path: str
    warning: Optional[str] = None
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
    cross_validation_used: bool = False
    evaluation_method: str = "80-20 Train-Test Split"
    features: List[str]


class AutoMLResponse(BaseModel):
    status: str
    model_summary: ModelSummary
    detection_reason: str = ""
    evaluation_metrics: Dict[str, Any]
    all_model_metrics: List[Dict[str, Any]] = []
    selected_metric: str = ""
    primary_score: float = 0.0
    feature_importance: Optional[List[Dict[str, Any]]] = None
    train_rows: int = 0
    test_rows: int = 0
    evaluation_method: str = "80-20 Train-Test Split"
    predictions: List[Dict[str, Any]]
    dataset_summary: DatasetSummary
    warning: Optional[str] = None
    download_url: str
    message: str
