"""Automated test verifying no format or container shortcuts exist between clean and steganographic images.

Includes:
1. Generator unit test ensuring identical formats, color modes, dimensions, and signatures.
2. Full benchmark audit across all generated image carriers checking formats, dimensions, modes,
   signatures, opaque naming conventions, and mathematical zero-correlation with manipulation labels.
"""

from pathlib import Path
import tempfile
import numpy as np
import pandas as pd
from PIL import Image
import pytest

from forensiguard.data.generation import apply_steganography_lsb, create_synthetic_image
from forensiguard.preprocessing.file_type import inspect_file_signature


def test_clean_and_stego_carriers_have_identical_format_and_properties():
    """Unit test checking the single-image generator creates identical container properties."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        clean_img_path = tmp_path / "art_clean.png"
        stego_img_path = tmp_path / "art_stego.png"

        # Generate clean synthetic image
        create_synthetic_image(clean_img_path, width=128, height=128, seed=42)

        # Generate stego image from the clean image
        apply_steganography_lsb(clean_img_path, stego_img_path, payload_bpp=0.2, seed=42)

        # 1. Inspect file signatures
        clean_sig = inspect_file_signature(clean_img_path)
        stego_sig = inspect_file_signature(stego_img_path)

        assert clean_sig["detected_mime_type"] == stego_sig["detected_mime_type"] == "image/png", \
            "Clean and stego carriers must both be valid PNGs"
        assert clean_sig["declared_extension"] == stego_sig["declared_extension"] == ".png"
        assert clean_sig["is_signature_mismatch"] is False
        assert stego_sig["is_signature_mismatch"] is False

        # 2. Inspect PIL image metadata (mode, size, format)
        with Image.open(clean_img_path) as c_img, Image.open(stego_img_path) as s_img:
            assert c_img.format == s_img.format == "PNG", "Image formats must match exactly"
            assert c_img.mode == s_img.mode == "L", "Color modes must match exactly (grayscale)"
            assert c_img.size == s_img.size == (128, 128), "Dimensions must match exactly"

        # 3. File sizes must be comparable (not orders of magnitude apart like JPEG vs PNG)
        c_size = clean_img_path.stat().st_size
        s_size = stego_img_path.stat().st_size
        size_ratio = max(c_size, s_size) / min(c_size, s_size)
        assert size_ratio < 1.35, f"Carrier file sizes must be comparable, got ratio {size_ratio:.2f}"


def test_generated_benchmark_full_image_carriers_audit():
    """
    Exhaustive benchmark audit across all image carriers in ForensiGuard-Bench-v1.
    Verifies:
    1. Formats: 100% of image carriers are valid PNGs.
    2. Dimensions: 100% of image carriers are strictly 128x128 pixels.
    3. Modes: 100% of image carriers are 8-bit grayscale ('L').
    4. Signatures: Valid magic bytes without container contradictions (unless intentionally obfuscated).
    5. Opaque Naming: No label tokens ('clean', 'stego', 'tamper') in artifact filenames.
    6. Label Correlation: Container properties have exactly 0 variance, guaranteeing zero label shortcut.
    """
    base_dir = Path(__file__).resolve().parents[2]
    manifest_path = base_dir / "data" / "benchmark" / "benchmark_manifest.csv"
    if not manifest_path.exists():
        pytest.skip(f"Benchmark manifest not found at {manifest_path}")

    df = pd.read_csv(manifest_path)
    # Filter for image carrier rows (clean PNGs, steganography, compound, or obfuscated PNGs)
    img_rows = df[df["declared_extension"] == ".png"].copy().reset_index(drop=True)
    assert len(img_rows) > 0, "Benchmark must contain image carrier rows"

    formats = []
    widths = []
    heights = []
    modes = []
    file_sizes = []
    labels = []

    for _, row in img_rows.iterrows():
        file_path = base_dir / "data" / "benchmark" / row["file_path"]
        assert file_path.exists(), f"Image file {file_path} missing on disk"

        # Check opaque filename convention
        fname = file_path.name
        for label_word in ["clean", "stego", "tampered", "manipulated", "altered"]:
            assert label_word not in fname.lower(), f"Filename {fname} leaks label token: {label_word}"
        assert fname.startswith("art_src_"), f"Filename {fname} must follow standard opaque prefix"

        # File signature check
        sig = inspect_file_signature(file_path)
        if not row["is_signature_mismatch"]:
            assert sig["detected_mime_type"] == "image/png", f"{file_path} must be valid PNG"
            assert sig["is_signature_mismatch"] is False

            # Inspect PIL attributes
            with Image.open(file_path) as img:
                formats.append(img.format)
                widths.append(img.width)
                heights.append(img.height)
                modes.append(img.mode)
                file_sizes.append(file_path.stat().st_size)
                labels.append(row["manipulation_label"])

    # 1. Audit Format Consistency
    assert all(fmt == "PNG" for fmt in formats), "Every non-obfuscated image must be a PNG"
    assert all(w == 128 for w in widths), "Every non-obfuscated image must have width 128"
    assert all(h == 128 for h in heights), "Every non-obfuscated image must have height 128"
    assert all(m == "L" for m in modes), "Every non-obfuscated image must have mode 'L' (grayscale)"

    # 2. Audit Container-Label Correlation
    # Since width, height, format, and mode have zero variance, their correlation with label is 0.0
    assert np.var(widths) == 0.0, "Width variance must be 0 (no dimensional shortcut)"
    assert np.var(heights) == 0.0, "Height variance must be 0 (no dimensional shortcut)"

    # 3. Audit File Size Overlap
    clean_sizes = [sz for sz, lab in zip(file_sizes, labels) if lab == 0]
    stego_sizes = [sz for sz, lab in zip(file_sizes, labels) if lab == 1]
    assert len(clean_sizes) > 0 and len(stego_sizes) > 0

    med_clean = np.median(clean_sizes)
    med_stego = np.median(stego_sizes)
    ratio = max(med_clean, med_stego) / min(med_clean, med_stego)
    assert ratio < 1.15, f"Median carrier file size ratio must be close (<1.15), got {ratio:.3f}"
