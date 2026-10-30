"""Evaluation metrics computation for security-critical forensic triage."""

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def compute_security_metrics(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    threshold: float = 0.5,
) -> Dict[str, Any]:
    """
    Computes security-oriented forensic metrics with special emphasis on False Positive Rate.
    """
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob).astype(float)
    y_pred = (y_prob >= threshold).astype(int)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    # Rates
    fpr = float(fp / max(fp + tn, 1))
    fnr = float(fn / max(fn + tp, 1))
    tpr = float(tp / max(tp + fn, 1))
    tnr = float(tn / max(tn + fp, 1))

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.5

    brier = float(brier_score_loss(y_true, y_prob))

    # Calculate operational operating thresholds: Recall at fixed low FPR (1% and 5%)
    fpr_arr, tpr_arr, thresh_arr = roc_curve(y_true, y_prob)
    rec_at_1pct_fpr = 0.0
    rec_at_5pct_fpr = 0.0

    for f, t in zip(fpr_arr, tpr_arr):
        if f <= 0.01:
            rec_at_1pct_fpr = max(rec_at_1pct_fpr, float(t))
        if f <= 0.05:
            rec_at_5pct_fpr = max(rec_at_5pct_fpr, float(t))

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "roc_auc": roc_auc,
        "pr_auc": pr_auc,
        "brier_score": brier,
        "false_positive_rate": fpr,
        "false_negative_rate": fnr,
        "true_positive_rate": tpr,
        "true_negative_rate": tnr,
        "recall_at_1pct_fpr": rec_at_1pct_fpr,
        "recall_at_5pct_fpr": rec_at_5pct_fpr,
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "sample_count": len(y_true),
    }
