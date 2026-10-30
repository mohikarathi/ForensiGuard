"""Late-fusion meta-classifier combining metadata and image modalities with technique attribution."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold

from forensiguard.data.schema import ID_TO_TECHNIQUE, TECHNIQUE_TO_ID, ManipulationType


FUSION_FEATURE_NAMES: List[str] = [
    "p_metadata",
    "p_image",
    "has_image_modality",
    "signature_mismatch",
    "anomaly_score",
    "shannon_entropy",
    "lsb_pair_pval",
]


class LateFusionMetaClassifier:
    """
    Transparent, explainable stacked late-fusion classifier.
    Combines calibrated outputs from Modality 1 (Metadata) and Modality 2 (Image/Binary).
    Outputs overall manipulation probability, confidence, and technique-level attribution.
    """

    def __init__(self, c_param: float = 1.0, random_state: int = 42) -> None:
        self.c_param = c_param
        self.random_state = random_state
        # Binary meta-classifier: Clean vs Manipulated
        self.binary_meta = LogisticRegression(
            C=self.c_param,
            random_state=self.random_state,
            max_iter=1000,
            class_weight="balanced",
        )
        # Multi-class attribution meta-classifier
        self.attribution_meta = LogisticRegression(
            C=self.c_param,
            random_state=self.random_state,
            max_iter=1000,
            class_weight="balanced",
        )
        self.feature_names = FUSION_FEATURE_NAMES
        self.decision_threshold = 0.50
        self.is_fitted = False

    def fit(
        self,
        X_fusion: pd.DataFrame,
        y_binary: np.ndarray,
        y_technique: np.ndarray,
    ) -> "LateFusionMetaClassifier":
        """
        Fits both binary manipulation detector and multi-class technique attributor.
        Input X_fusion must be derived from leakage-safe OOF predictions or training split.
        """
        X_mat = X_fusion[self.feature_names].values
        self.binary_meta.fit(X_mat, y_binary)
        self.attribution_meta.fit(X_mat, y_technique)
        self.is_fitted = True
        return self

    def predict_proba(self, X_fusion: pd.DataFrame) -> np.ndarray:
        """Returns 2D class probabilities [P(clean), P(manipulated)]."""
        if not self.is_fitted:
            raise RuntimeError("Fusion model must be fitted before predict_proba.")
        return self.binary_meta.predict_proba(X_fusion[self.feature_names].values)

    def predict(self, X_fusion: pd.DataFrame, threshold: Optional[float] = None) -> np.ndarray:
        """Returns binary predictions based on decision threshold."""
        thresh = threshold if threshold is not None else self.decision_threshold
        probs = self.predict_proba(X_fusion)[:, 1]
        return (probs >= thresh).astype(int)

    def predict_fusion(self, X_fusion: pd.DataFrame, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Runs complete multimodal inference.
        Returns dictionary containing:
        - manipulation_prob: float in [0, 1]
        - is_manipulated: bool
        - attributed_technique: str
        - attribution_probs: Dict[str, float]
        - confidence: float in [0, 1]
        - feature_contributions: Dict[str, float]
        """
        if not self.is_fitted:
            raise RuntimeError("Fusion model must be fitted before predict_fusion.")

        thresh = threshold if threshold is not None else self.decision_threshold
        X_mat = X_fusion[self.feature_names].values

        # Binary manipulation probability
        bin_probs = self.binary_meta.predict_proba(X_mat)
        p_manip = float(bin_probs[0, 1])
        is_manip = bool(p_manip >= thresh)

        # Multi-class attribution
        attr_probs = self.attribution_meta.predict_proba(X_mat)[0]
        classes = self.attribution_meta.classes_
        attr_dict = {
            ID_TO_TECHNIQUE.get(int(c), str(c)): float(prob)
            for c, prob in zip(classes, attr_probs)
        }

        # Determine most likely technique
        # If binary prediction says clean, attribute to clean unless strong specific signal
        if not is_manip and "clean" in attr_dict and attr_dict["clean"] >= 0.40:
            top_technique = "clean"
        else:
            # Pick non-clean highest if manipulated, else highest overall
            non_clean_candidates = {k: v for k, v in attr_dict.items() if k != "clean"}
            if non_clean_candidates and is_manip:
                top_technique = max(non_clean_candidates.items(), key=lambda item: item[1])[0]
            else:
                top_technique = max(attr_dict.items(), key=lambda item: item[1])[0]

        # Confidence: distance from decision boundary normalized
        margin = abs(p_manip - 0.5) * 2.0  # [0, 1]
        top_attr_p = attr_dict.get(top_technique, 0.5)
        confidence = float(np.clip(0.6 * margin + 0.4 * top_attr_p, 0.0, 1.0))

        # Linear contributions from logistic regression weights
        weights = self.binary_meta.coef_[0]
        intercept = self.binary_meta.intercept_[0]
        contributions = {
            feat: float(w * val)
            for feat, w, val in zip(self.feature_names, weights, X_mat[0])
        }

        return {
            "manipulation_probability": p_manip,
            "is_manipulated": is_manip,
            "attributed_technique": top_technique,
            "attribution_probabilities": attr_dict,
            "confidence": confidence,
            "intercept": float(intercept),
            "linear_contributions": contributions,
        }

    def save(self, path: Union[str, Path]) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "binary_meta": self.binary_meta,
            "attribution_meta": self.attribution_meta,
            "feature_names": self.feature_names,
            "is_fitted": self.is_fitted,
            "decision_threshold": self.decision_threshold,
        }, path)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "LateFusionMetaClassifier":
        data = joblib.load(path)
        obj = cls()
        obj.binary_meta = data["binary_meta"]
        obj.attribution_meta = data["attribution_meta"]
        obj.feature_names = data["feature_names"]
        obj.is_fitted = data["is_fitted"]
        obj.decision_threshold = data.get("decision_threshold", 0.50)
        return obj

