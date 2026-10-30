"""Supervised XGBoost classifier for filesystem metadata anti-forensics."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
import shap
from xgboost import XGBClassifier


class MetadataClassifier:
    """
    Gradient-boosted decision tree classifier (XGBoost) trained on engineered
    metadata features augmented with clean-baseline anomaly scores.
    """

    def __init__(
        self,
        n_estimators: int = 120,
        max_depth: int = 4,
        learning_rate: float = 0.05,
        subsample: float = 0.85,
        colsample_bytree: float = 0.85,
        random_state: int = 42,
    ) -> None:
        self.feature_names: List[str] = []
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            random_state=random_state,
            eval_metric="logloss",
            n_jobs=-1,
        )
        self.explainer: Optional[shap.TreeExplainer] = None
        self.is_fitted = False

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: Union[np.ndarray, pd.Series],
        eval_set: Optional[List[Tuple[pd.DataFrame, Any]]] = None,
    ) -> "MetadataClassifier":
        """
        Fits XGBoost model and initializes SHAP TreeExplainer.
        """
        self.feature_names = list(X_train.columns)
        self.model.fit(
            X_train,
            y_train,
            eval_set=eval_set,
            verbose=False,
        )
        self.explainer = shap.TreeExplainer(self.model)
        self.is_fitted = True
        return self

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Returns 2D array of class probabilities [P(clean), P(manipulated)]."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predict_proba.")
        return self.model.predict_proba(X[self.feature_names])

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Returns binary prediction (0 = clean, 1 = manipulated)."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before predict.")
        return self.model.predict(X[self.feature_names])

    def get_feature_importances(self) -> Dict[str, float]:
        """Returns gain-based feature importances."""
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted to get importances.")
        imps = self.model.feature_importances_
        return {name: float(imp) for name, imp in zip(self.feature_names, imps)}

    def explain_sample(self, X_row: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Computes local SHAP attributions for a single sample row.
        Returns a sorted list of contributing features with values and SHAP scores.
        """
        if self.explainer is None:
            self.explainer = shap.TreeExplainer(self.model)

        row_df = X_row[self.feature_names]
        shap_values = self.explainer.shap_values(row_df)

        if isinstance(shap_values, list):
            # Binary classification case in older shap versions
            vals = shap_values[1][0]
        elif len(shap_values.shape) == 2:
            vals = shap_values[0]
        else:
            vals = shap_values[0]

        contributions = []
        for name, val, shap_val in zip(self.feature_names, row_df.values[0], vals):
            contributions.append({
                "feature": name,
                "value": float(val),
                "shap_value": float(shap_val),
                "direction": "suspicious" if shap_val > 0 else "benign",
            })

        # Sort by absolute SHAP contribution descending
        contributions.sort(key=lambda x: abs(x["shap_value"]), reverse=True)
        return contributions

    def save(self, path: Union[str, Path]) -> None:
        """Saves fitted classifier to disk."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "model": self.model,
            "feature_names": self.feature_names,
            "is_fitted": self.is_fitted,
        }, path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "MetadataClassifier":
        """Loads fitted classifier from disk."""
        data = joblib.load(path)
        obj = cls()
        obj.model = data["model"]
        obj.feature_names = data["feature_names"]
        obj.is_fitted = data["is_fitted"]
        obj.explainer = shap.TreeExplainer(obj.model)
        return obj
