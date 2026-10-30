"""Unit tests for models: Anomaly Detector, XGBoost Classifier, CNN, and Late Fusion."""

import numpy as np
import pandas as pd
import pytest
import torch

from forensiguard.features.metadata_features import FEATURE_NAMES
from forensiguard.models.anomaly_detector import MetadataAnomalyDetector
from forensiguard.models.fusion import FUSION_FEATURE_NAMES, LateFusionMetaClassifier
from forensiguard.models.image_cnn import SRNetLite
from forensiguard.models.metadata_classifier import MetadataClassifier


def test_anomaly_detector_training_and_scoring():
    rng = np.random.RandomState(42)
    # Baseline normal data
    X_clean = pd.DataFrame(rng.normal(0, 1, size=(100, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
    detector = MetadataAnomalyDetector(random_state=42)
    detector.fit(X_clean)

    # Anomaly vector (extreme outlier)
    X_anomaly = pd.DataFrame(rng.normal(15, 1, size=(5, len(FEATURE_NAMES))), columns=FEATURE_NAMES)
    scores = detector.score_samples(X_anomaly)

    assert len(scores) == 5
    assert np.all(scores > 0.5), "Severe outliers must receive high anomaly scores"


def test_metadata_classifier_and_shap():
    rng = np.random.RandomState(42)
    cols = FEATURE_NAMES + ["clean_anomaly_score"]
    X = pd.DataFrame(rng.normal(0, 1, size=(80, len(cols))), columns=cols)
    y = np.array([0] * 40 + [1] * 40)

    clf = MetadataClassifier(n_estimators=10, random_state=42)
    clf.fit(X, y)

    probs = clf.predict_proba(X)
    assert probs.shape == (80, 2)

    explanations = clf.explain_sample(X.iloc[[0]])
    assert len(explanations) == len(cols)
    assert "feature" in explanations[0]
    assert "shap_value" in explanations[0]


def test_srnet_lite_cnn_forward():
    model = SRNetLite()
    dummy_input = torch.randn(2, 1, 128, 128)
    logits = model(dummy_input)
    assert logits.shape == (2, 2)


def test_late_fusion_fit_and_predict():
    rng = np.random.RandomState(42)
    X = pd.DataFrame(rng.uniform(0, 1, size=(60, len(FUSION_FEATURE_NAMES))), columns=FUSION_FEATURE_NAMES)
    y_bin = np.array([0] * 30 + [1] * 30)
    y_tech = np.array([0] * 30 + [1] * 10 + [2] * 10 + [3] * 10)

    fusion = LateFusionMetaClassifier(random_state=42)
    fusion.fit(X, y_bin, y_tech)

    result = fusion.predict_fusion(X.iloc[[0]])
    assert "manipulation_probability" in result
    assert "is_manipulated" in result
    assert "attributed_technique" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
