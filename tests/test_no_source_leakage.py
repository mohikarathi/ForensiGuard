"""Automated tests verifying zero source-level data leakage across dataset partitions."""

from pathlib import Path
import sys
import pandas as pd
import pytest

root_dir = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root_dir / "src"))

from forensiguard.data.splitting import perform_source_grouped_split, verify_no_source_leakage


def test_source_grouped_split_zero_leakage():
    # Construct mock dataset with 30 sources, each producing 5 variants
    records = []
    for s_idx in range(30):
        src_id = f"src_{s_idx:03d}"
        for v_idx in range(5):
            records.append({
                "source_file_id": src_id,
                "variant_id": f"{src_id}_var_{v_idx}",
                "value": s_idx * 10 + v_idx,
            })
    df = pd.DataFrame(records)

    split_df = perform_source_grouped_split(
        df,
        source_col="source_file_id",
        split_ratios={"train": 0.70, "val": 0.15, "test": 0.15},
        seed=42,
    )

    # 1. Verification function must pass without assertion error
    assert verify_no_source_leakage(split_df, source_col="source_file_id", split_col="split")

    # 2. Check disjointness of set of source IDs
    train_sources = set(split_df[split_df["split"] == "train"]["source_file_id"])
    val_sources = set(split_df[split_df["split"] == "val"]["source_file_id"])
    test_sources = set(split_df[split_df["split"] == "test"]["source_file_id"])

    assert len(train_sources.intersection(val_sources)) == 0, "Train and Val share source IDs!"
    assert len(train_sources.intersection(test_sources)) == 0, "Train and Test share source IDs!"
    assert len(val_sources.intersection(test_sources)) == 0, "Val and Test share source IDs!"

    # 3. All variants of a single source must have identical split
    for src_id, grp in split_df.groupby("source_file_id"):
        assert len(grp["split"].unique()) == 1, f"Source {src_id} has multiple splits assigned!"


def test_data_leakage_detector_raises_on_leaked_source():
    # Deliberately construct a leaked partition to test the leakage guard
    leaked_data = pd.DataFrame([
        {"source_file_id": "src_001", "split": "train"},
        {"source_file_id": "src_001", "split": "test"},
        {"source_file_id": "src_002", "split": "train"},
    ])

    with pytest.raises(AssertionError, match="DATA LEAKAGE DETECTED"):
        verify_no_source_leakage(leaked_data)
