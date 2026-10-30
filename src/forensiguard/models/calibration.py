"""Probability calibration for forensic confidence estimation."""

from typing import Union
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


class ForensiCalibrator:
    """
    Calibrates raw model probabilities to ensure empirical probabilities match observed frequencies,
    which is essential for forensic defensibility.
    """

    def __init__(self, method: str = "sigmoid") -> None:
        self.method = method
        self.calibrator = LogisticRegression() if method == "sigmoid" else IsotonicRegression(out_of_bounds="clip")
        self.is_fitted = False

    def fit(self, uncalibrated_probs: np.ndarray, y_true: np.ndarray) -> "ForensiCalibrator":
        X = uncalibrated_probs.reshape(-1, 1)
        self.calibrator.fit(X, y_true)
        self.is_fitted = True
        return self

    def predict_proba(self, uncalibrated_probs: np.ndarray) -> np.ndarray:
        if not self.is_fitted:
            return uncalibrated_probs
        X = uncalibrated_probs.reshape(-1, 1)
        if self.method == "sigmoid":
            calibrated = self.calibrator.predict_proba(X)[:, 1]
        else:
            calibrated = self.calibrator.predict(X.ravel())
        return np.clip(calibrated, 0.0, 1.0)
