"""Unit tests for metadata and image feature extraction."""

from pathlib import Path
import tempfile
import numpy as np
import pytest

from forensiguard.features.image_features import compute_byte_statistics
from forensiguard.features.metadata_features import extract_metadata_features_dict
from forensiguard.preprocessing.file_type import inspect_file_signature


def test_metadata_feature_extraction():
    # Synthetic metadata dictionary simulating a timestomped file (mtime < ctime, 0 subseconds)
    meta = {
        "mtime": 1700000000.0,
        "ctime": 1700010000.0,
        "atime": 1700010100.0,
        "mtime_subsecond": 0.0,
        "ctime_subsecond": 0.45,
        "atime_subsecond": 0.88,
        "file_size_bytes": 1024,
    }
    folder_ctx = {
        "folder_mtime_mean": 1700010000.0,
        "folder_mtime_std": 1000.0,
        "folder_mtime_median": 1700010000.0,
    }

    feats = extract_metadata_features_dict(meta, folder_context=folder_ctx)

    assert feats["is_chronology_inverted"] == 1.0, "Should detect inverted chronology when mtime < ctime"
    assert feats["mtime_zero_subseconds"] == 1.0, "Should detect zero subseconds on mtime"
    assert feats["delta_mtime_ctime"] == -10000.0
    assert abs(feats["folder_mtime_deviation_zscore"] - (-10.0)) < 1e-4


def test_byte_statistics_computation():
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        # Uniform random bytes -> high entropy (~8 bits/byte)
        rnd = np.random.randint(0, 256, size=10000, dtype=np.uint8)
        tmp.write(rnd.tobytes())
        tmp_path = Path(tmp.name)

    try:
        stats = compute_byte_statistics(tmp_path)
        assert 7.8 <= stats["shannon_entropy"] <= 8.0, "Uniform random data should exhibit ~8.0 entropy"
        assert "byte_chi_square" in stats
        assert "lsb_pair_pval" in stats
    finally:
        tmp_path.unlink()


def test_file_signature_inspection():
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        # Write PDF header disguised under .jpg extension
        tmp.write(b"%PDF-1.4\n%header")
        tmp_path = Path(tmp.name)

    try:
        sig = inspect_file_signature(tmp_path)
        assert sig["is_signature_mismatch"] is True, "Should detect disguised PDF with .jpg extension"
        assert sig["detected_mime_type"] == "application/pdf"
        assert sig["declared_extension"] == ".jpg"
    finally:
        tmp_path.unlink()
