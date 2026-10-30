"""Statistical byte features and LSB steganalysis diagnostics."""

import math
from pathlib import Path
from typing import Dict, Union
import numpy as np
from scipy import stats


def compute_byte_statistics(file_path: Union[str, Path]) -> Dict[str, float]:
    """
    Computes byte-level information-theoretic metrics on raw file content.
    """
    file_path = Path(file_path)
    if not file_path.exists() or file_path.stat().st_size == 0:
        return {
            "shannon_entropy": 0.0,
            "byte_chi_square": 0.0,
            "lsb_pair_pval": 1.0,
            "byte_transition_entropy": 0.0,
        }

    try:
        with open(file_path, "rb") as f:
            data = f.read(1048576)  # Read up to first 1 MB
    except Exception:
        return {
            "shannon_entropy": 0.0,
            "byte_chi_square": 0.0,
            "lsb_pair_pval": 1.0,
            "byte_transition_entropy": 0.0,
        }

    if not data:
        return {
            "shannon_entropy": 0.0,
            "byte_chi_square": 0.0,
            "lsb_pair_pval": 1.0,
            "byte_transition_entropy": 0.0,
        }

    arr = np.frombuffer(data, dtype=np.uint8)
    n = len(arr)

    # 1. Byte frequency and Shannon entropy
    counts = np.bincount(arr, minlength=256)
    probs = counts / n
    nonzero_probs = probs[probs > 0]
    entropy = -float(np.sum(nonzero_probs * np.log2(nonzero_probs)))

    # 2. Chi-square goodness-of-fit against uniform distribution
    expected = n / 256.0
    chi_square = float(np.sum((counts - expected) ** 2 / (expected + 1e-9)))

    # 3. LSB Sample Pair (PoVs) test for LSB replacement steganography
    # Under LSB embedding, pairs of values (2k, 2k+1) converge toward equal frequency
    pov_diffs = []
    for k in range(128):
        c_even = counts[2 * k]
        c_odd = counts[2 * k + 1]
        c_mean = (c_even + c_odd) / 2.0
        if c_mean > 0:
            pov_diffs.append(((c_even - c_mean) ** 2) / c_mean)

    if pov_diffs:
        chi_lsb = float(np.sum(pov_diffs))
        # Degrees of freedom = 127
        p_val = float(1.0 - stats.chi2.cdf(chi_lsb, df=127))
    else:
        p_val = 1.0

    # 4. Bigram / transition entropy
    if n > 1:
        first = arr[:-1].astype(np.uint32)
        second = arr[1:].astype(np.uint32)
        bigrams = (first << 8) | second
        b_counts = np.bincount(bigrams)
        b_probs = b_counts[b_counts > 0] / (n - 1)
        trans_entropy = -float(np.sum(b_probs * np.log2(b_probs)))
    else:
        trans_entropy = 0.0

    return {
        "shannon_entropy": entropy,
        "byte_chi_square": chi_square,
        "lsb_pair_pval": float(np.clip(p_val, 0.0, 1.0)),
        "byte_transition_entropy": trans_entropy,
    }
