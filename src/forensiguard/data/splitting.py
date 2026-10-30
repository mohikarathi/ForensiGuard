"""Leakage-safe grouped dataset splitting logic for ForensiGuard."""

from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Dict, List, Set, Tuple


def perform_source_grouped_split(
    df: pd.DataFrame,
    source_col: str = "source_file_id",
    split_ratios: Dict[str, float] = None,
    seed: int = 42
) -> pd.DataFrame:
    """
    Assign splits grouped strictly by source_col to guarantee 0% data leakage.
    All variations (clean, timestomped, stego, etc.) generated from source X
    will belong to the exact same split.
    """
    if split_ratios is None:
        split_ratios = {"train": 0.70, "val": 0.15, "test": 0.15}

    total_ratio = sum(split_ratios.values())
    assert abs(total_ratio - 1.0) < 1e-4, f"Split ratios must sum to 1.0, got {total_ratio}"

    df = df.copy()
    unique_sources = df[source_col].unique()
    rng = np.random.RandomState(seed)
    shuffled_sources = rng.permutation(unique_sources)

    n_sources = len(shuffled_sources)
    n_train = int(np.floor(split_ratios["train"] * n_sources))
    n_val = int(np.floor(split_ratios["val"] * n_sources))

    train_sources = set(shuffled_sources[:n_train])
    val_sources = set(shuffled_sources[n_train:n_train + n_val])
    test_sources = set(shuffled_sources[n_train + n_val:])

    def assign_split(src: str) -> str:
        if src in train_sources:
            return "train"
        elif src in val_sources:
            return "val"
        else:
            return "test"

    df["split"] = df[source_col].map(assign_split)

    # Verify zero leakage constraint immediately
    verify_no_source_leakage(df, source_col=source_col, split_col="split")

    return df


def verify_no_source_leakage(
    df: pd.DataFrame,
    source_col: str = "source_file_id",
    split_col: str = "split"
) -> bool:
    """
    Verifies that no source_file_id appears across multiple splits.
    Raises AssertionError if leakage is detected.
    """
    source_to_splits: Dict[str, Set[str]] = defaultdict(set)
    for _, row in df[[source_col, split_col]].iterrows():
        source_to_splits[row[source_col]].add(row[split_col])

    leaked_sources = {src: splits for src, splits in source_to_splits.items() if len(splits) > 1}
    if leaked_sources:
        sample_leak = list(leaked_sources.items())[:5]
        raise AssertionError(
            f"DATA LEAKAGE DETECTED! {len(leaked_sources)} source IDs found in multiple splits: {sample_leak}"
        )
    return True
