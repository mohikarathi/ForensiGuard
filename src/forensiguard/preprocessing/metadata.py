"""Filesystem metadata extraction and directory context analysis."""

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np


def compute_file_hashes(file_path: Path) -> Dict[str, str]:
    """Computes SHA-256 and MD5 cryptographic hashes for an artifact."""
    sha256 = hashlib.sha256()
    md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
                md5.update(chunk)
        return {
            "sha256": sha256.hexdigest(),
            "md5": md5.hexdigest(),
        }
    except Exception as e:
        return {
            "sha256": "error_reading_file",
            "md5": "error_reading_file",
        }


def extract_raw_metadata(file_path: Path) -> Dict[str, Any]:
    """
    Extracts raw filesystem attributes including high-resolution nanosecond timestamps
    and birthtime when supported by the underlying OS/filesystem.
    """
    file_path = Path(file_path)
    stat = file_path.stat()

    mtime_sec = stat.st_mtime
    atime_sec = stat.st_atime
    ctime_sec = stat.st_ctime

    # High precision sub-second components (POSIX stat_ns)
    mtime_ns = getattr(stat, "st_mtime_ns", int(mtime_sec * 1e9))
    atime_ns = getattr(stat, "st_atime_ns", int(atime_sec * 1e9))
    ctime_ns = getattr(stat, "st_ctime_ns", int(ctime_sec * 1e9))

    mtime_subsecond = (mtime_ns % int(1e9)) / 1e9
    ctime_subsecond = (ctime_ns % int(1e9)) / 1e9
    atime_subsecond = (atime_ns % int(1e9)) / 1e9

    # Birthtime / Creation time
    birthtime_sec = getattr(stat, "st_birthtime", None)
    if birthtime_sec is None:
        # On Linux EXT4, birthtime is often inaccessible via standard stat; fallback to min(ctime, mtime)
        birthtime_sec = min(ctime_sec, mtime_sec)

    return {
        "file_size_bytes": stat.st_size,
        "mtime": mtime_sec,
        "atime": atime_sec,
        "ctime": ctime_sec,
        "birthtime": birthtime_sec,
        "mtime_subsecond": mtime_subsecond,
        "ctime_subsecond": ctime_subsecond,
        "atime_subsecond": atime_subsecond,
        "mtime_ns": mtime_ns,
        "ctime_ns": ctime_ns,
        "atime_ns": atime_ns,
    }


def extract_folder_context(file_path: Path, max_neighbors: int = 50) -> Dict[str, float]:
    """
    Extracts statistical context from neighboring files in the same parent directory
    to detect contextual timeline anomalies.
    """
    file_path = Path(file_path)
    parent_dir = file_path.parent

    if not parent_dir.exists() or not parent_dir.is_dir():
        return {
            "folder_mtime_mean": 0.0,
            "folder_mtime_std": 1.0,
            "folder_mtime_median": 0.0,
            "folder_file_count": 1,
        }

    neighbor_mtimes: List[float] = []
    try:
        for entry in parent_dir.iterdir():
            if entry.is_file() and entry != file_path:
                try:
                    neighbor_mtimes.append(entry.stat().st_mtime)
                except Exception:
                    continue
            if len(neighbor_mtimes) >= max_neighbors:
                break
    except Exception:
        pass

    if not neighbor_mtimes:
        return {
            "folder_mtime_mean": file_path.stat().st_mtime if file_path.exists() else 0.0,
            "folder_mtime_std": 1.0,
            "folder_mtime_median": file_path.stat().st_mtime if file_path.exists() else 0.0,
            "folder_file_count": 1,
        }

    arr = np.array(neighbor_mtimes)
    std = float(np.std(arr))
    if std < 1e-4:
        std = 1.0

    return {
        "folder_mtime_mean": float(np.mean(arr)),
        "folder_mtime_std": std,
        "folder_mtime_median": float(np.median(arr)),
        "folder_file_count": len(neighbor_mtimes) + 1,
    }
