"""SHAP-based explainability and natural language forensic interpretations."""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "delta_mtime_ctime": "Time interval between modification and metadata change (mtime - ctime)",
    "delta_atime_mtime": "Time interval between access and modification (atime - mtime)",
    "delta_atime_ctime": "Time interval between access and metadata change (atime - ctime)",
    "is_chronology_inverted": "Chronological inversion indicator (mtime precedes ctime)",
    "mtime_zero_subseconds": "Zero fractional subsecond precision on modification timestamp",
    "ctime_zero_subseconds": "Zero fractional subsecond precision on metadata change timestamp",
    "atime_zero_subseconds": "Zero fractional subsecond precision on access timestamp",
    "mtime_round_minute": "Modification timestamp aligned to exact minute boundary",
    "mtime_round_hour": "Modification timestamp aligned to exact hour boundary",
    "folder_mtime_deviation_zscore": "Z-score deviation from sibling files in parent directory",
    "folder_mtime_diff_median": "Absolute temporal difference from directory median timestamp",
    "file_size_bytes": "File payload size in bytes",
    "clean_anomaly_score": "Isolation Forest deviation from clean filesystem baseline",
}


def generate_natural_language_explanation(feature_contributions: List[Dict[str, Any]]) -> List[str]:
    """
    Translates mathematical SHAP feature attributions into defensible,
    investigator-readable statements.
    """
    explanations: List[str] = []

    for item in feature_contributions:
        feat = item["feature"]
        val = item["value"]
        shap_val = item["shap_value"]
        direction = item["direction"]

        if abs(shap_val) < 0.02:
            continue

        sign_str = f"+{shap_val:.3f}" if shap_val > 0 else f"{shap_val:.3f}"

        if feat == "is_chronology_inverted" and val > 0.5:
            explanations.append(
                f"[CRITICAL ANOMALY] Modification timestamp predates creation/metadata change "
                f"(chronology inversion, SHAP: {sign_str}). Natural write activity updates ctime after or alongside mtime."
            )
        elif feat == "mtime_zero_subseconds" and val > 0.5:
            explanations.append(
                f"[TIMING ARTIFACT] Modification timestamp exhibits zero subsecond precision "
                f"(subsecond = 0.000s, SHAP: {sign_str}). High-resolution filesystems retain microsecond noise; "
                f"exact zeroing is characteristic of rudimentary timestomping utilities."
            )
        elif feat == "folder_mtime_deviation_zscore" and abs(val) > 2.0:
            explanations.append(
                f"[CONTEXTUAL OUTLIER] File timestamp is {val:.2f} standard deviations away from "
                f"neighboring files in the directory (SHAP: {sign_str}), suggesting isolated backdating/forward-dating."
            )
        elif feat == "clean_anomaly_score" and val > 0.6:
            explanations.append(
                f"[BASELINE DIVERGENCE] Anomaly component scored file at {val:.2f} (SHAP: {sign_str}) "
                f"relative to normal unmanipulated filesystem distributions."
            )
        elif feat == "delta_mtime_ctime" and val < -60:
            hours = abs(val) / 3600.0
            explanations.append(
                f"[TEMPORAL GAP] Modification time is {hours:.1f} hours older than metadata change time "
                f"(SHAP: {sign_str})."
            )
        elif feat == "mtime_round_hour" and val > 0.5:
            explanations.append(
                f"[ROUND TIMESTAMP] Modification timestamp falls on an exact hour boundary (SHAP: {sign_str}), "
                f"suggesting manual timestamp assignment."
            )
        else:
            desc = FEATURE_DESCRIPTIONS.get(feat, feat)
            verb = "pushed toward suspicious" if shap_val > 0 else "supported benign classification"
            explanations.append(f"{desc} (observed: {val:.2f}, SHAP: {sign_str}) {verb}.")

    if not explanations:
        explanations.append("All extracted metadata metrics remain within typical benign baseline thresholds.")

    return explanations
