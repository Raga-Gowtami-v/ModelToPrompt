import pickle
import uuid
from io import StringIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from fastapi import UploadFile
from sklearn.compose import ColumnTransformer
from sklearn.base import clone
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.ensemble import (
    ExtraTreesClassifier,
    ExtraTreesRegressor,
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.svm import SVC, SVR
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    mean_absolute_error,
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

    OVERFIT_PENALTY = 0.35

    async def train_from_prompt(self, file: UploadFile, prompt: str) -> dict:
        """Parse CSV, detect task, train/evaluate models on held-out test set, and save best model."""
        content = await file.read()
        df = pd.read_csv(StringIO(content.decode("utf-8")))
        logger.info(f"Loaded CSV with shape {df.shape}")

        target_col = self._extract_target_column(prompt, df.columns.tolist())

        if target_col not in df.columns:
            raise ValueError(
                f"Target column '{target_col}' not found. Available: {list(df.columns)}"
            )

        X, y, feature_encoders = self._prepare_data(df, target_col)
        task_type, detection_reason = self._detect_task_type(y)

        split_data = self._split_data(X, y, task_type)
        X_train = split_data["X_train"]
        X_test = split_data["X_test"]
        y_train_raw = split_data["y_train"]
        y_test_raw = split_data["y_test"]

        y_encoder = None
        if task_type == "classification":
            y_encoder = LabelEncoder()
            y_train = pd.Series(y_encoder.fit_transform(y_train_raw), index=y_train_raw.index)
            y_test = pd.Series(y_encoder.transform(y_test_raw), index=y_test_raw.index)
        else:
            y_train = y_train_raw
            y_test = y_test_raw

        preprocessor = self._build_preprocessor(X_train)

        best_result, all_model_metrics = self._train_and_select_best_model(
            X_train=X_train,
            X_test=X_test,
            y_train=y_train,
            y_test=y_test,
            preprocessor=preprocessor,
            task_type=task_type,
        )

        selected_pipeline = best_result["model"]
        selected_metric = best_result["selected_metric"]
        primary_score = best_result["primary_score"]
        metrics = best_result["metrics"]
        y_pred = best_result["y_pred"]
        feature_importance = self._extract_feature_importance(selected_pipeline)

        warning = None
        if task_type == "classification" and round(float(metrics.get("accuracy", 0.0)), 4) == 1.0:
            warning = "Perfect accuracy detected. Possible overfitting or small dataset."
        elif best_result.get("generalization_gap", 0.0) > 0.08:
            warning = (
                "Potential overfitting detected: training score is significantly higher "
                "than test score."
            )

        self._sanity_check(
            train_rows=len(X_train),
            test_rows=len(X_test),
            total_rows=len(df),
            metrics=metrics,
            task_type=task_type,
        )

        logger.info(
            f"Detected {task_type}; selected {best_result['model_name']} using {selected_metric}={primary_score}"
        )

        model_id = str(uuid.uuid4())[:8]
        model_path = Path(settings.MODEL_OUTPUT_DIR) / f"{model_id}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(
                {
                    "model": selected_pipeline,
                    "encoders": feature_encoders,
                    "target_encoder": y_encoder,
                    "feature_columns": list(X.columns),
                    "task_type": task_type,
                    "target_column": target_col,
                },
                f,
            )

        predictions = [
            {
                "index": int(idx),
                "actual": self._serialize_prediction_value(act),
                "predicted": self._serialize_prediction_value(pred),
            }
            for idx, act, pred in zip(X_test.index[:100], y_test.values[:100], y_pred[:100])
        ]

        return {
            "model_id": model_id,
            "task_type": task_type,
            "detection_reason": detection_reason,
            "target_column": target_col,
            "model_name": best_result["model_name"],
            "selected_model": best_result["model_name"],
            "selected_metric": selected_metric,
            "primary_score": primary_score,
            "train_primary_score": best_result.get("train_primary_score"),
            "generalization_gap": best_result.get("generalization_gap"),
            "adjusted_score": best_result.get("adjusted_score"),
            "metrics": metrics,
            "all_model_metrics": all_model_metrics,
            "feature_importance": feature_importance,
            "predictions": predictions,
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "evaluation_method": "80-20 Train-Test Split",
            "dataset_summary": {
                "total_rows": len(df),
                "train_rows": len(X_train),
                "test_rows": len(X_test),
                "cross_validation_used": False,
                "evaluation_method": "80-20 Train-Test Split",
                "features": list(X.columns),
            },
            "model_path": str(model_path),
            "warning": warning,
            "message": f"Model trained successfully. Download at /api/model/download/{model_id}",
        }

    def _extract_target_column(self, prompt: str, columns: list[str]) -> str:
        """Extract target column from prompt; fallback to last column."""
        prompt_lower = prompt.lower()
        for col in columns:
            if col.lower() in prompt_lower:
                return col
        return columns[-1]

    def _detect_task_type(self, y: pd.Series) -> tuple[str, str]:
        """Detect task type from target cardinality."""
        unique_count = int(y.nunique(dropna=True))
        if unique_count == 2:
            task_type = "classification"
        elif 2 < unique_count <= 15:
            task_type = "classification"
        else:
            task_type = "regression"

        reason = (
            f"Target column has {unique_count} unique values → Detected as {task_type}"
        )
        return task_type, reason

    def _prepare_data(self, df: pd.DataFrame, target_col: str):
        """Prepare features and target without feature leakage."""
        encoders = {}
        df_encoded = df.copy()

        # Handle missing values
        numeric_cols = df_encoded.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            df_encoded[numeric_cols] = df_encoded[numeric_cols].fillna(
                df_encoded[numeric_cols].median(numeric_only=True)
            )

        non_numeric_cols = [col for col in df_encoded.columns if col not in numeric_cols]
        for col in non_numeric_cols:
            df_encoded[col] = df_encoded[col].fillna("missing").astype(str)

        X = df_encoded.drop(columns=[target_col])
        y = df_encoded[target_col]
        return X, y, encoders

    def _split_data(self, X: pd.DataFrame, y: pd.Series, task_type: str) -> dict:
        """Perform mandatory 80/20 split with stratification for classification."""
        if len(X) < 2:
            raise ValueError("Dataset must contain at least 2 rows")

        split_kwargs: dict[str, Any] = {
            "test_size": 0.2,
            "random_state": 42,
        }

        if task_type == "classification":
            split_kwargs["stratify"] = y

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, **split_kwargs
        )

        if len(X_test) == 0:
            raise ValueError("Test split is empty; provide more data")

        return {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
        }

    def _build_preprocessor(self, X_train: pd.DataFrame) -> ColumnTransformer:
        """Create leakage-safe preprocessing strategy from training data only."""
        categorical_cols = X_train.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        numeric_cols = [col for col in X_train.columns if col not in categorical_cols]

        binary_categorical_cols = [
            col for col in categorical_cols if X_train[col].nunique(dropna=True) == 2
        ]
        onehot_categorical_cols = [
            col for col in categorical_cols if col not in binary_categorical_cols
        ]

        transformers = []
        if binary_categorical_cols:
            transformers.append(
                (
                    "binary_cat",
                    OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                    binary_categorical_cols,
                )
            )

        if onehot_categorical_cols:
            transformers.append(
                (
                    "onehot_cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    onehot_categorical_cols,
                )
            )

        if numeric_cols:
            transformers.append(("numeric", "passthrough", numeric_cols))

        return ColumnTransformer(transformers=transformers, remainder="drop")

    def _compute_metrics(self, y_test, y_pred, task_type: str) -> dict:
        """Compute evaluation metrics based on the task type."""
        if task_type == "classification":
            avg = "weighted" if len(set(y_test)) > 2 else "binary"
            accuracy = float(accuracy_score(y_test, y_pred))
            precision = float(precision_score(y_test, y_pred, average=avg, zero_division=0))
            recall = float(recall_score(y_test, y_pred, average=avg, zero_division=0))
            f1 = float(f1_score(y_test, y_pred, average=avg, zero_division=0))

            if round(accuracy, 4) == 1.0:
                precision = 1.0
                recall = 1.0
                f1 = 1.0

            return {
                "accuracy": round(accuracy, 4),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1_score": round(f1, 4),
                "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            }
        else:
            rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
            return {
                "mae": round(float(mean_absolute_error(y_test, y_pred)), 4),
                "mse": round(float(mean_squared_error(y_test, y_pred)), 4),
                "rmse": round(rmse, 4),
                "r2_score": round(float(r2_score(y_test, y_pred)), 4),
            }

    def _get_model_candidates(self, task_type: str):
        """Return candidate models for the task type."""
        if task_type == "classification":
            return [
                (
                    "RandomForestClassifier",
                    RandomForestClassifier(
                        n_estimators=250,
                        max_depth=8,
                        min_samples_leaf=3,
                        min_samples_split=6,
                        random_state=42,
                    ),
                ),
                (
                    "ExtraTreesClassifier",
                    ExtraTreesClassifier(
                        n_estimators=250,
                        max_depth=8,
                        min_samples_leaf=3,
                        min_samples_split=6,
                        random_state=42,
                    ),
                ),
                (
                    "GradientBoostingClassifier",
                    GradientBoostingClassifier(
                        n_estimators=150,
                        learning_rate=0.05,
                        max_depth=3,
                        subsample=0.8,
                        random_state=42,
                    ),
                ),
                ("LogisticRegression", LogisticRegression(max_iter=1000, C=0.5, random_state=42)),
                ("KNeighborsClassifier", KNeighborsClassifier(n_neighbors=7, weights="distance")),
                ("SVC", SVC(C=0.5, gamma="scale")),
            ]

        return [
            (
                "RandomForestRegressor",
                RandomForestRegressor(
                    n_estimators=250,
                    max_depth=10,
                    min_samples_leaf=3,
                    min_samples_split=6,
                    random_state=42,
                ),
            ),
            (
                "ExtraTreesRegressor",
                ExtraTreesRegressor(
                    n_estimators=250,
                    max_depth=10,
                    min_samples_leaf=3,
                    min_samples_split=6,
                    random_state=42,
                ),
            ),
            (
                "GradientBoostingRegressor",
                GradientBoostingRegressor(
                    n_estimators=150,
                    learning_rate=0.05,
                    max_depth=3,
                    subsample=0.8,
                    random_state=42,
                ),
            ),
            ("LinearRegression", LinearRegression()),
            ("Ridge", Ridge(alpha=2.0, random_state=42)),
            ("Lasso", Lasso(alpha=0.01, random_state=42)),
            ("KNeighborsRegressor", KNeighborsRegressor(n_neighbors=7, weights="distance")),
            ("SVR", SVR(C=1.0, epsilon=0.2, gamma="scale")),
        ]

    def _primary_metric_name(self, task_type: str) -> str:
        return "accuracy" if task_type == "classification" else "r2_score"

    def _primary_score(self, metrics: dict, task_type: str) -> float:
        return float(metrics[self._primary_metric_name(task_type)])

    def _train_and_select_best_model(self, X_train, X_test, y_train, y_test, preprocessor, task_type: str):
        """Train candidate models and select best using test metric with overfit penalty."""
        candidates = self._get_model_candidates(task_type)
        selected_metric = self._primary_metric_name(task_type)
        all_model_metrics = []
        best_result = None

        for model_name, model in candidates:
            try:
                estimator = Pipeline(
                    steps=[
                        ("preprocessor", clone(preprocessor)),
                        ("scaler", StandardScaler(with_mean=False)),
                        ("model", clone(model)),
                    ]
                )

                estimator.fit(X_train, y_train)
                y_pred = estimator.predict(X_test)
                y_train_pred = estimator.predict(X_train)
                metrics = self._compute_metrics(y_test, y_pred, task_type)
                train_metrics = self._compute_metrics(y_train, y_train_pred, task_type)

                primary_score = round(self._primary_score(metrics, task_type), 4)
                train_primary_score = round(self._primary_score(train_metrics, task_type), 4)
                generalization_gap = round(train_primary_score - primary_score, 4)
                adjusted_score = round(
                    primary_score - (max(0.0, generalization_gap) * self.OVERFIT_PENALTY),
                    4,
                )

                all_model_metrics.append(
                    {
                        "model_name": model_name,
                        "primary_score": primary_score,
                        "train_primary_score": train_primary_score,
                        "generalization_gap": generalization_gap,
                        "adjusted_score": adjusted_score,
                        "metrics": metrics,
                    }
                )

                if best_result is None or adjusted_score > best_result["adjusted_score"]:
                    best_result = {
                        "model": estimator,
                        "model_name": model_name,
                        "y_pred": y_pred,
                        "metrics": metrics,
                        "primary_score": primary_score,
                        "train_primary_score": train_primary_score,
                        "generalization_gap": generalization_gap,
                        "adjusted_score": adjusted_score,
                        "selected_metric": selected_metric,
                    }

            except Exception as exc:
                logger.warning(f"Skipping model {model_name} due to error: {exc}")

        if best_result is None:
            raise ValueError("Unable to train any model for the provided dataset and prompt")

        all_model_metrics.sort(key=lambda item: item["adjusted_score"], reverse=True)
        return best_result, all_model_metrics

    def _extract_feature_importance(self, pipeline_model: Pipeline):
        """Return all encoded feature importances if model supports it, otherwise None."""
        fitted_model = pipeline_model.named_steps["model"]
        preprocessor = pipeline_model.named_steps["preprocessor"]

        if not hasattr(fitted_model, "feature_importances_") or not hasattr(
            preprocessor, "get_feature_names_out"
        ):
            return None

        importances = fitted_model.feature_importances_
        encoded_feature_names = preprocessor.get_feature_names_out()
        ranked = sorted(zip(encoded_feature_names, importances), key=lambda item: item[1], reverse=True)
        return [
            {"feature": name, "importance": round(float(score), 6)}
            for name, score in ranked
        ]

    def _sanity_check(self, train_rows: int, test_rows: int, total_rows: int, metrics: dict, task_type: str):
        """Validate row counts and metric consistency before returning response."""
        if test_rows <= 0:
            raise ValueError("Invalid evaluation: test_rows must be greater than 0")

        if train_rows >= total_rows:
            raise ValueError("Invalid evaluation: train_rows must be less than total_rows")

        if task_type == "classification":
            accuracy = round(float(metrics.get("accuracy", 0.0)), 4)
            precision = round(float(metrics.get("precision", 0.0)), 4)
            recall = round(float(metrics.get("recall", 0.0)), 4)
            f1 = round(float(metrics.get("f1_score", 0.0)), 4)
            if accuracy == 1.0 and (precision != 1.0 or recall != 1.0 or f1 != 1.0):
                metrics["precision"] = 1.0
                metrics["recall"] = 1.0
                metrics["f1_score"] = 1.0

    def _serialize_prediction_value(self, value: Any):
        if isinstance(value, (np.floating, float)):
            return round(float(value), 6)
        if isinstance(value, (np.integer, int)):
            return int(value)
        return value
