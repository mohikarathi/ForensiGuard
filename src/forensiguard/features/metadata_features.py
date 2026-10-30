"""Feature extraction engineering from filesystem metadata."""

from datetime import datetime, timezone
import math
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


FEATURE_NAMES: List[str] = [
    "delta_mtime_ctime",
    "delta_atime_mtime",
    "delta_atime_ctime",
    "is_chronology_inverted",
    "mtime_zero_subseconds",
    "ctime_zero_subseconds",
    "atime_zero_subseconds",
    "mtime_round_minute",
    "mtime_round_hour",
    "folder_mtime_deviation_zscore",
    "folder_mtime_diff_median",
    "file_size_bytes",
]


def extract_metadata_features_dict(meta: Dict[str, Any], folder_context: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
    """
    Computes numerical metadata features from raw extracted metadata attributes.
    """
    mtime = float(meta.get("mtime", 0.0))
    atime = float(meta.get("atime", 0.0))
    ctime = float(meta.get("ctime", 0.0))
    file_size = float(meta.get("file_size_bytes", 0))

    # Subseconds
    mtime_sub = float(meta.get("mtime_subsecond", 0.0))
    ctime_sub = float(meta.get("ctime_subsecond", 0.0))
    atime_sub = float(meta.get("atime_subsecond", 0.0))

    # Time differences (seconds)
    delta_m_c = mtime - ctime
    delta_a_m = atime - mtime
    delta_a_c = atime - ctime

    # Chronology checks: normally on file creation/write, mtime >= ctime (or near identical)
    # Timestomping mtime into the past often results in mtime < ctime
    is_inverted = 1.0 if delta_m_c < -1.0 else 0.0

    # Implausible zero sub-second precision (many timestomping utilities only accept integer seconds)
    mtime_zero_sub = 1.0 if abs(mtime_sub) < 1e-7 else 0.0
    ctime_zero_sub = 1.0 if abs(ctime_sub) < 1e-7 else 0.0
    atime_zero_sub = 1.0 if abs(atime_sub) < 1e-7 else 0.0

    # Implausibly round timestamps (exact minute or exact hour)
    mtime_int = int(round(mtime))
    round_minute = 1.0 if (mtime_int % 60 == 0) and mtime_zero_sub == 1.0 else 0.0
    round_hour = 1.0 if (mtime_int % 3600 == 0) and mtime_zero_sub == 1.0 else 0.0

    # Folder context features
    if folder_context:
        f_mean = float(folder_context.get("folder_mtime_mean", mtime))
        f_std = float(folder_context.get("folder_mtime_std", 1.0))
        f_median = float(folder_context.get("folder_mtime_median", mtime))
    else:
        f_mean = float(meta.get("folder_mtime_mean", mtime))
        f_std = float(meta.get("folder_mtime_std", 1.0))
        f_median = float(meta.get("folder_mtime_median", mtime))

    if f_std < 1e-4:
        f_std = 1.0

    zscore = float((mtime - f_mean) / f_std)
    # Clip z-score to prevent numerical explosion
    zscore = float(np.clip(zscore, -20.0, 20.0))
    diff_median = float(abs(mtime - f_median))

    return {
        "delta_mtime_ctime": float(delta_m_c),
        "delta_atime_mtime": float(delta_a_m),
        "delta_atime_ctime": float(delta_a_c),
        "is_chronology_inverted": is_inverted,
        "mtime_zero_subseconds": mtime_zero_sub,
        "ctime_zero_subseconds": ctime_zero_sub,
        "atime_zero_subseconds": atime_zero_sub,
        "mtime_round_minute": round_minute,
        "mtime_round_hour": round_hour,
        "folder_mtime_deviation_zscore": zscore,
        "folder_mtime_diff_median": diff_median,
        "file_size_bytes": file_size,
    }


def extract_features_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts a DataFrame of artifact metadata into a structured feature matrix DataFrame.
    """
    records = []
    for _, row in df.iterrows():
        feat = extract_metadata_features_dict(row.to_dict())
        records.append(feat)
    return pd.DataFrame(records, columns=FEATURE_NAMES)
