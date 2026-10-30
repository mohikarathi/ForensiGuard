"""Unsupervised anomaly detection trained strictly on clean forensic metadata."""

from pathlib import Path
from typing import Optional, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler


class MetadataAnomalyDetector:
    """
    Learns normal baseline of filesystem metadata exclusively from verified clean artifacts.
    Outputs an anomaly score S in [0, 1], where higher values indicate deviation.
    """

    def __init__(
        self,
        contamination: float = 0.05,
        n_estimators: int = 150,
        random_state: int = 42
    ) -> None:
        self.contamination = contamination
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.model = IsolationForest(
            contamination=self.contamination,
            n_estimators=self.n_estimators,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.is_fitted = False

    def fit(self, X_clean: Union[np.ndarray, pd.DataFrame]) -> "MetadataAnomalyDetector":
        """
        Fits scaler and Isolation Forest strictly on clean training data.
        Target leakage guard: MUST NOT be called on mixed or test data.
        """
        if isinstance(X_clean, pd.DataFrame):
            X_mat = X_clean.values
        else:
            X_mat = np.asarray(X_clean)

        X_scaled = self.scaler.fit_transform(X_mat)
        self.model.fit(X_scaled)
        self.is_fitted = True
        return self

    def score_samples(self, X: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Computes anomaly score in [0, 1], with 0 = normal and 1 = extreme anomaly.
        """
        if not self.is_fitted:
            raise RuntimeError("AnomalyDetector must be fitted before scoring.")

        if isinstance(X, pd.DataFrame):
            X_mat = X.values
        else:
            X_mat = np.asarray(X)

        X_scaled = self.scaler.transform(X_mat)
        # raw decision_function: lower means more abnormal
        raw_scores = self.model.decision_function(X_scaled)
        # Normalize to [0, 1] range inverted (higher = more anomalous)
        # Typically raw_score ranges around [-0.5, 0.5]
        normalized = 1.0 / (1.0 + np.exp(raw_scores * 5.0))
        return np.clip(normalized, 0.0, 1.0)

    def save(self, path: Union[str, Path]) -> None:
        """Saves fitted detector to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"scaler": self.scaler, "model": self.model, "is_fitted": self.is_fitted}, path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "MetadataAnomalyDetector":
        """Loads fitted detector from disk."""
        data = joblib.load(path)
        obj = cls()
        obj.scaler = data["scaler"]
        obj.model = data["model"]
        obj.is_fitted = data["is_fitted"]
        return obj
