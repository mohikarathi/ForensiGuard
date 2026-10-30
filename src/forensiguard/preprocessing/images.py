"""Image preprocessing and spatial noise-residual computation for steganalysis."""

from pathlib import Path
from typing import Optional, Tuple, Union
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

# SRM (Spatial Rich Model) Filters for Steganalysis
LAPLACIAN_KERNEL = np.array([
    [0.0,  1.0, 0.0],
    [1.0, -4.0, 1.0],
    [0.0,  1.0, 0.0]
], dtype=np.float32)

KV_KERNEL = np.array([
    [-1.0,  2.0,  -2.0,  2.0, -1.0],
    [ 2.0, -6.0,   8.0, -6.0,  2.0],
    [-2.0,  8.0, -12.0,  8.0, -2.0],
    [ 2.0, -6.0,   8.0, -6.0,  2.0],
    [-1.0,  2.0,  -2.0,  2.0, -1.0]
], dtype=np.float32) / 12.0


def load_and_preprocess_image(
    image_path: Union[str, Path],
    target_size: Tuple[int, int] = (128, 128)
) -> Optional[np.ndarray]:
    """
    Loads an image safely, converts to grayscale, and resizes to target_size.
    Returns float32 numpy array normalized to [0, 1], or None if invalid.
    """
    try:
        with Image.open(image_path) as img:
            img = img.convert("L")  # Grayscale for spatial steganalysis
            img = img.resize(target_size, Image.Resampling.BILINEAR)
            arr = np.array(img, dtype=np.float32) / 255.0
            return arr
    except Exception:
        return None


def compute_noise_residual(
    image_gray: np.ndarray,
    filter_type: str = "kv"
) -> np.ndarray:
    """
    Computes spatial high-pass noise residuals from a grayscale image.
    Suppresses semantic image contents, isolating steganographic noise traces.
    """
    if filter_type.lower() == "laplacian":
        kernel = LAPLACIAN_KERNEL
    else:
        kernel = KV_KERNEL

    k_h, k_w = kernel.shape
    pad_h, pad_w = k_h // 2, k_w // 2

    img_tensor = torch.from_numpy(image_gray).unsqueeze(0).unsqueeze(0)  # [1, 1, H, W]
    kernel_tensor = torch.from_numpy(kernel).unsqueeze(0).unsqueeze(0)  # [1, 1, k_h, k_w]

    # Reflective padding to avoid artificial edge artifacts
    padded = F.pad(img_tensor, (pad_w, pad_w, pad_h, pad_h), mode="reflect")
    residual = F.conv2d(padded, kernel_tensor)

    res_arr = residual.squeeze(0).squeeze(0).numpy()
    # Truncate and normalize residuals as in SRM / SRNet
    T = 2.0
    res_arr = np.clip(res_arr * 10.0, -T, T) / T
    return res_arr.astype(np.float32)


def prepare_image_tensor(
    image_path: Union[str, Path],
    target_size: Tuple[int, int] = (128, 128),
    filter_type: str = "kv"
) -> Optional[torch.Tensor]:
    """
    Full pipeline: loads image, extracts noise residual, and returns torch.Tensor [1, 1, H, W].
    """
    arr = load_and_preprocess_image(image_path, target_size=target_size)
    if arr is None:
        return None
    res = compute_noise_residual(arr, filter_type=filter_type)
    return torch.from_numpy(res).unsqueeze(0).unsqueeze(0)  # [1, 1, H, W]
