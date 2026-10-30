"""Benchmark dataset generator for controlled, reproducible anti-forensic evidence.

Audited and hardened to eliminate format-label shortcuts, ensure consistent carrier encoding,
and provide opaque artifact naming with zero label leakage in file paths.
"""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import random
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid
import numpy as np
import pandas as pd
from PIL import Image

import shutil
from forensiguard.data.schema import ArtifactRecord, ManipulationType
from forensiguard.data.splitting import perform_source_grouped_split
from forensiguard.preprocessing.file_type import inspect_file_signature
from forensiguard.preprocessing.metadata import compute_file_hashes


def create_synthetic_image(output_path: Path, width: int = 128, height: int = 128, seed: int = 42) -> None:
    """
    Creates a realistic synthetic texture image (continuous gradients + texture noise).
    Standardized as lossless grayscale PNG to match steganographic carriers exactly,
    preventing any compression or container format shortcut.
    """
    rng = np.random.RandomState(seed)
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    base = np.sin(xx * np.pi * 2) * np.cos(yy * np.pi * 2) * 60 + 128
    texture = rng.normal(0, 8, (height, width))
    img_data = np.clip(base + texture, 0, 255).astype(np.uint8)

    img = Image.fromarray(img_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Save as PNG to match stego carriers in encoding, dimensions, and bit-depth
    img.save(output_path, format="PNG")


def create_synthetic_document(output_path: Path, doc_type: str = "pdf") -> None:
    """Creates a small valid synthetic document (PDF or text)."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if doc_type == "pdf":
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
            b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\n0000000102 00000 n\n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n185\n%%EOF\n"
        )
        with open(output_path, "wb") as f:
            f.write(pdf_content)
    else:
        text = f"Forensic evidentiary sample generated for ForensiGuard testing.\nID: {uuid.uuid4()}\n"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)


def apply_steganography_lsb(image_path: Path, output_path: Path, payload_bpp: float = 0.2, seed: int = 42) -> Dict[str, Any]:
    """
    Embeds pseudo-random bitstream into LSBs of image pixels.
    Output format is strictly identical to the input clean image (grayscale PNG).
    """
    with Image.open(image_path) as img:
        arr = np.array(img, dtype=np.uint8)

    rng = np.random.RandomState(seed)
    total_pixels = arr.size
    n_bits = int(total_pixels * payload_bpp)
    indices = rng.choice(total_pixels, size=n_bits, replace=False)
    payload_bits = rng.randint(0, 2, size=n_bits, dtype=np.uint8)

    flat = arr.ravel()
    flat[indices] = (flat[indices] & 0xFE) | payload_bits
    stego_arr = flat.reshape(arr.shape)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    stego_img = Image.fromarray(stego_arr)
    stego_img.save(output_path, format="PNG")

    return {
        "payload_bpp": payload_bpp,
        "bits_embedded": n_bits,
        "method": "LSB_replacement",
    }


def set_custom_file_timestamps(file_path: Path, mtime: float, atime: float) -> None:
    """Sets modification and access timestamps on disk via POSIX utime."""
    try:
        os.utime(file_path, (atime, mtime))
    except Exception:
        pass


class BenchmarkGenerator:
    """
    Orchestrates generation of a versioned, leakage-safe forensic benchmark.
    Uses opaque artifact filenames to prevent label leakage via paths.
    """

    def __init__(self, output_dir: Union[str, Path], seed: int = 42) -> None:
        self.output_dir = Path(output_dir)
        self.seed = seed
        self.rng = random.Random(seed)
        self.np_rng = np.random.RandomState(seed)

    def generate_benchmark(self, num_sources: int = 140, clean_existing: bool = True) -> pd.DataFrame:
        """
        Generates full benchmark corpus across folder clusters.
        If clean_existing is True, any existing artifacts directory is purged first
        to maintain exact 1:1 parity with the manifest and prevent orphaned files.
        """
        artifacts_dir = self.output_dir / "artifacts"
        if clean_existing and artifacts_dir.exists():
            shutil.rmtree(artifacts_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)
        records: List[Dict[str, Any]] = []

        base_time = 1730000000.0  # Reference forensic timeline base

        n_folders = max(3, num_sources // 20)
        folder_contexts = [f"folder_case_{i:02d}" for i in range(n_folders)]

        folder_means = {
            f: base_time + (i * 86400 * 7) + self.rng.uniform(-3600, 3600)
            for i, f in enumerate(folder_contexts)
        }

        for src_idx in range(num_sources):
            src_id = f"src_{src_idx:04d}"
            folder_id = self.rng.choice(folder_contexts)
            f_mean = folder_means[folder_id]

            # Realistic clean timestamps for source
            source_mtime = f_mean + self.rng.gauss(0, 1800)
            subsec = self.rng.uniform(0.001, 0.999)
            source_mtime = float(int(source_mtime)) + subsec
            source_ctime = source_mtime + self.rng.uniform(0.01, 5.0)
            source_atime = source_ctime + self.rng.uniform(1.0, 300.0)
            source_birth = source_mtime - self.rng.uniform(60, 3600)

            # 60% images, 40% documents
            is_image_source = (src_idx % 10) < 6
            src_ext = ".png" if is_image_source else ".pdf"

            source_dir = self.output_dir / "artifacts" / folder_id
            source_dir.mkdir(parents=True, exist_ok=True)

            # Generate random unique token for opaque file naming
            def make_opaque_name(ext: str) -> str:
                tok = uuid.uuid4().hex[:10]
                return f"art_{src_id}_{tok}{ext}"

            # 1. Clean artifact
            clean_filename = make_opaque_name(src_ext)
            clean_path = source_dir / clean_filename
            if is_image_source:
                create_synthetic_image(clean_path, seed=self.seed + src_idx)
            else:
                create_synthetic_document(clean_path, doc_type="pdf")

            set_custom_file_timestamps(clean_path, source_mtime, source_atime)
            clean_hashes = compute_file_hashes(clean_path)
            clean_sig = inspect_file_signature(clean_path)

            records.append({
                "artifact_id": str(uuid.uuid4()),
                "source_file_id": src_id,
                "filename": clean_filename,
                "file_path": str(clean_path.relative_to(self.output_dir)),
                "sha256": clean_hashes["sha256"],
                "md5": clean_hashes["md5"],
                "file_size_bytes": clean_path.stat().st_size,
                "declared_extension": src_ext,
                "detected_mime_type": clean_sig["detected_mime_type"],
                "is_signature_mismatch": clean_sig["is_signature_mismatch"],
                "manipulation_label": 0,
                "technique": ManipulationType.CLEAN.value,
                "subtype": "unaltered",
                "tool_name": "clean_baseline",
                "parameters_json": json.dumps({"source_file": clean_filename}),
                "mtime": source_mtime,
                "atime": source_atime,
                "ctime": source_ctime,
                "birthtime": source_birth,
                "mtime_subsecond": subsec,
                "folder_context_id": folder_id,
                "folder_mtime_mean": f_mean,
                "folder_mtime_std": 1800.0,
                "folder_mtime_median": f_mean,
            })

            # 2. Timestomping: Coarse Jump
            coarse_filename = make_opaque_name(src_ext)
            coarse_path = source_dir / coarse_filename
            if is_image_source:
                create_synthetic_image(coarse_path, seed=self.seed + src_idx)
            else:
                create_synthetic_document(coarse_path, doc_type="pdf")

            coarse_mtime = float(int(source_mtime - (5 * 365 * 86400)))
            set_custom_file_timestamps(coarse_path, coarse_mtime, coarse_mtime)
            c_hashes = compute_file_hashes(coarse_path)
            c_sig = inspect_file_signature(coarse_path)

            records.append({
                "artifact_id": str(uuid.uuid4()),
                "source_file_id": src_id,
                "filename": coarse_filename,
                "file_path": str(coarse_path.relative_to(self.output_dir)),
                "sha256": c_hashes["sha256"],
                "md5": c_hashes["md5"],
                "file_size_bytes": coarse_path.stat().st_size,
                "declared_extension": src_ext,
                "detected_mime_type": c_sig["detected_mime_type"],
                "is_signature_mismatch": c_sig["is_signature_mismatch"],
                "manipulation_label": 1,
                "technique": ManipulationType.TIMESTOMPING.value,
                "subtype": "coarse_multiyear",
                "tool_name": "setmtime_cli",
                "parameters_json": json.dumps({"shift_years": -5, "zero_subsecond": True}),
                "mtime": coarse_mtime,
                "atime": coarse_mtime,
                "ctime": source_ctime,
                "birthtime": source_birth,
                "mtime_subsecond": 0.0,
                "folder_context_id": folder_id,
                "folder_mtime_mean": f_mean,
                "folder_mtime_std": 1800.0,
                "folder_mtime_median": f_mean,
            })

            # 3. Timestomping: Subtle Shift
            subtle_filename = make_opaque_name(src_ext)
            subtle_path = source_dir / subtle_filename
            if is_image_source:
                create_synthetic_image(subtle_path, seed=self.seed + src_idx)
            else:
                create_synthetic_document(subtle_path, doc_type="pdf")

            subtle_mtime = float(int(source_mtime - 9000))
            set_custom_file_timestamps(subtle_path, subtle_mtime, subtle_mtime)
            s_hashes = compute_file_hashes(subtle_path)
            s_sig = inspect_file_signature(subtle_path)

            records.append({
                "artifact_id": str(uuid.uuid4()),
                "source_file_id": src_id,
                "filename": subtle_filename,
                "file_path": str(subtle_path.relative_to(self.output_dir)),
                "sha256": s_hashes["sha256"],
                "md5": s_hashes["md5"],
                "file_size_bytes": subtle_path.stat().st_size,
                "declared_extension": src_ext,
                "detected_mime_type": s_sig["detected_mime_type"],
                "is_signature_mismatch": s_sig["is_signature_mismatch"],
                "manipulation_label": 1,
                "technique": ManipulationType.TIMESTOMPING.value,
                "subtype": "subtle_2h",
                "tool_name": "touch_r",
                "parameters_json": json.dumps({"shift_seconds": -9000, "zero_subsecond": True}),
                "mtime": subtle_mtime,
                "atime": subtle_mtime,
                "ctime": source_ctime,
                "birthtime": source_birth,
                "mtime_subsecond": 0.0,
                "folder_context_id": folder_id,
                "folder_mtime_mean": f_mean,
                "folder_mtime_std": 1800.0,
                "folder_mtime_median": f_mean,
            })

            # 4. Steganography (for images only)
            if is_image_source:
                for payload_rate, sub_name in [(0.35, "high_payload"), (0.08, "subtle_payload")]:
                    stego_filename = make_opaque_name(".png")
                    stego_path = source_dir / stego_filename
                    params = apply_steganography_lsb(clean_path, stego_path, payload_bpp=payload_rate, seed=self.seed + src_idx)
                    set_custom_file_timestamps(stego_path, source_mtime, source_atime)
                    st_hashes = compute_file_hashes(stego_path)
                    st_sig = inspect_file_signature(stego_path)

                    records.append({
                        "artifact_id": str(uuid.uuid4()),
                        "source_file_id": src_id,
                        "filename": stego_filename,
                        "file_path": str(stego_path.relative_to(self.output_dir)),
                        "sha256": st_hashes["sha256"],
                        "md5": st_hashes["md5"],
                        "file_size_bytes": stego_path.stat().st_size,
                        "declared_extension": ".png",
                        "detected_mime_type": st_sig["detected_mime_type"],
                        "is_signature_mismatch": st_sig["is_signature_mismatch"],
                        "manipulation_label": 1,
                        "technique": ManipulationType.STEGANOGRAPHY.value,
                        "subtype": sub_name,
                        "tool_name": "openpuff_lsb",
                        "parameters_json": json.dumps(params),
                        "mtime": source_mtime,
                        "atime": source_atime,
                        "ctime": source_ctime,
                        "birthtime": source_birth,
                        "mtime_subsecond": subsec,
                        "folder_context_id": folder_id,
                        "folder_mtime_mean": f_mean,
                        "folder_mtime_std": 1800.0,
                        "folder_mtime_median": f_mean,
                    })

            # 5. File Type / Extension Obfuscation
            # Disguise PDF content under .png extension
            obf_filename = make_opaque_name(".png")
            obf_path = source_dir / obf_filename
            create_synthetic_document(obf_path, doc_type="pdf")
            set_custom_file_timestamps(obf_path, source_mtime, source_atime)
            obf_hashes = compute_file_hashes(obf_path)
            obf_sig = inspect_file_signature(obf_path)

            records.append({
                "artifact_id": str(uuid.uuid4()),
                "source_file_id": src_id,
                "filename": obf_filename,
                "file_path": str(obf_path.relative_to(self.output_dir)),
                "sha256": obf_hashes["sha256"],
                "md5": obf_hashes["md5"],
                "file_size_bytes": obf_path.stat().st_size,
                "declared_extension": ".png",
                "detected_mime_type": obf_sig["detected_mime_type"],
                "is_signature_mismatch": obf_sig["is_signature_mismatch"],
                "manipulation_label": 1,
                "technique": ManipulationType.FILE_TYPE_OBFUSCATION.value,
                "subtype": "disguised_pdf_header",
                "tool_name": "extension_disguise",
                "parameters_json": json.dumps({"payload_type": "pdf", "carrier_extension": ".png"}),
                "mtime": source_mtime,
                "atime": source_atime,
                "ctime": source_ctime,
                "birthtime": source_birth,
                "mtime_subsecond": subsec,
                "folder_context_id": folder_id,
                "folder_mtime_mean": f_mean,
                "folder_mtime_std": 1800.0,
                "folder_mtime_median": f_mean,
            })

            # 6. Compound Manipulation (Timestomped + Stego)
            if is_image_source:
                comp_filename = make_opaque_name(".png")
                comp_path = source_dir / comp_filename
                c_params = apply_steganography_lsb(clean_path, comp_path, payload_bpp=0.25, seed=self.seed + src_idx)
                comp_mtime = float(int(source_mtime - 86400 * 30))
                set_custom_file_timestamps(comp_path, comp_mtime, comp_mtime)
                comp_hashes = compute_file_hashes(comp_path)
                comp_sig = inspect_file_signature(comp_path)

                records.append({
                    "artifact_id": str(uuid.uuid4()),
                    "source_file_id": src_id,
                    "filename": comp_filename,
                    "file_path": str(comp_path.relative_to(self.output_dir)),
                    "sha256": comp_hashes["sha256"],
                    "md5": comp_hashes["md5"],
                    "file_size_bytes": comp_path.stat().st_size,
                    "declared_extension": ".png",
                    "detected_mime_type": comp_sig["detected_mime_type"],
                    "is_signature_mismatch": comp_sig["is_signature_mismatch"],
                    "manipulation_label": 1,
                    "technique": ManipulationType.COMPOUND.value,
                    "subtype": "stego_and_timestomp",
                    "tool_name": "compound_pipeline",
                    "parameters_json": json.dumps({"shift_days": -30, "stego": c_params}),
                    "mtime": comp_mtime,
                    "atime": comp_mtime,
                    "ctime": source_ctime,
                    "birthtime": source_birth,
                    "mtime_subsecond": 0.0,
                    "folder_context_id": folder_id,
                    "folder_mtime_mean": f_mean,
                    "folder_mtime_std": 1800.0,
                    "folder_mtime_median": f_mean,
                })

        df = pd.DataFrame(records)
        df = perform_source_grouped_split(df, source_col="source_file_id", seed=self.seed)

        manifest_path = self.output_dir / "benchmark_manifest.csv"
        df.to_csv(manifest_path, index=False)
        return df
