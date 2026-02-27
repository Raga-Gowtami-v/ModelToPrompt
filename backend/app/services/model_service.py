import pickle
import uuid
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from fastapi import UploadFile
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    mean_squared_error,
    r2_score,
)

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ModelService:
    """Train ML models from CSV data based on user prompts."""

    TASK_KEYWORDS = {
        "classify": "classification",
        "classification": "classification",
        "predict class": "classification",
        "categorize": "classification",
        "regression": "regression",
        "predict": "regression",
        "forecast": "regression",
        "estimate": "regression",
    }

    async def train_from_prompt(self, file: UploadFile, prompt: str) -> dict:
        """Parse the CSV, interpret the prompt, train a model, and save as .pkl."""
        # Read CSV
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode("utf-8")))
        logger.info(f"Loaded CSV with shape {df.shape}")

        # Parse prompt to determine target column and task type
        target_col, task_type = self._parse_prompt(prompt, df.columns.tolist())

        if target_col not in df.columns:
            raise ValueError(
                f"Target column '{target_col}' not found. Available: {list(df.columns)}"
            )

        # Prepare data
        X, y, encoders = self._prepare_data(df, target_col, task_type)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Select and train model
        model = self._select_model(task_type)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        logger.info(f"Model trained, generating metrics...")

        # Compute detailed metrics
        metrics = self._compute_metrics(y_test, y_pred, task_type)

        # Save as .pkl
        model_id = str(uuid.uuid4())[:8]
        model_path = Path(settings.MODEL_OUTPUT_DIR) / f"{model_id}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(
                {"model": model, "encoders": encoders, "feature_columns": list(X.columns)},
                f,
            )

        # Build predictions list (limited to first 100 rows)
        predictions = [
            {"index": int(idx), "actual": float(act), "predicted": float(pred)}
            for idx, act, pred in zip(X_test.index[:100], y_test.values[:100], y_pred[:100])
        ]

        return {
            "model_id": model_id,
            "task_type": task_type,
            "target_column": target_col,
            "model_name": type(model).__name__,
            "metrics": metrics,
            "predictions": predictions,
            "dataset_summary": {
                "total_rows": len(df),
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "features": list(X.columns),
            },
            "model_path": str(model_path),
            "message": f"Model trained successfully. Download at /api/model/download/{model_id}",
        }

    def _parse_prompt(self, prompt: str, columns: list) -> tuple:
        """Extract target column and task type from user prompt."""
        prompt_lower = prompt.lower()

        # Detect task type
        task_type = "classification"  # default
        for keyword, task in self.TASK_KEYWORDS.items():
            if keyword in prompt_lower:
                task_type = task
                break

        # Detect target column from prompt
        target_col = None
        for col in columns:
            if col.lower() in prompt_lower:
                target_col = col
                break

        if target_col is None:
            # Default to last column
            target_col = columns[-1]

        return target_col, task_type

    def _prepare_data(self, df: pd.DataFrame, target_col: str, task_type: str):
        """Prepare features and target, encoding categoricals."""
        encoders = {}
        df_encoded = df.copy()

        for col in df_encoded.columns:
            if df_encoded[col].dtype == "object":
                le = LabelEncoder()
                df_encoded[col] = le.fit_transform(df_encoded[col].astype(str))
                encoders[col] = le

        # Handle missing values
        df_encoded = df_encoded.fillna(df_encoded.median(numeric_only=True))

        X = df_encoded.drop(columns=[target_col])
        y = df_encoded[target_col]
        return X, y, encoders

    def _compute_metrics(self, y_test, y_pred, task_type: str) -> dict:
        """Compute evaluation metrics based on the task type."""
        if task_type == "classification":
            avg = "weighted" if len(set(y_test)) > 2 else "binary"
            return {
                "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
                "precision": round(float(precision_score(y_test, y_pred, average=avg, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, y_pred, average=avg, zero_division=0)), 4),
                "f1_score": round(float(f1_score(y_test, y_pred, average=avg, zero_division=0)), 4),
            }
        else:
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            return {
                "rmse": round(rmse, 4),
                "r2_score": round(float(r2_score(y_test, y_pred)), 4),
            }

    def _select_model(self, task_type: str):
        """Select an appropriate model based on the task type."""
        if task_type == "classification":
            return RandomForestClassifier(n_estimators=100, random_state=42)
        else:
            return RandomForestRegressor(n_estimators=100, random_state=42)
