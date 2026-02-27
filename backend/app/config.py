import os
from pathlib import Path


class Settings:
    APP_NAME: str = "Secure LLM Gateway"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # File handling
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MODEL_OUTPUT_DIR: str = os.getenv("MODEL_OUTPUT_DIR", "./models")
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))

    # Supported file types
    ALLOWED_EXTENSIONS: set = {".csv", ".txt", ".pdf", ".docx", ".png", ".jpg", ".jpeg"}

    # PII detection thresholds
    PII_CONFIDENCE_THRESHOLD: float = float(os.getenv("PII_CONFIDENCE_THRESHOLD", "0.7"))
    HIGH_RISK_THRESHOLD: float = float(os.getenv("HIGH_RISK_THRESHOLD", "0.8"))

    def __init__(self):
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.MODEL_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)


settings = Settings()
