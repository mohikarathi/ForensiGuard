"""File type verification and signature inspection for ForensiGuard."""

import mimetypes
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import puremagic

# Known header signatures for high-confidence fallback checking
MAGIC_SIGNATURES: Dict[bytes, Tuple[str, str]] = {
    b"\xff\xd8\xff": ("image/jpeg", ".jpg"),
    b"\x89PNG\r\n\x1a\n": ("image/png", ".png"),
    b"GIF87a": ("image/gif", ".gif"),
    b"GIF89a": ("image/gif", ".gif"),
    b"%PDF-": ("application/pdf", ".pdf"),
    b"PK\x03\x04": ("application/zip", ".zip"),
    b"\x7fELF": ("application/x-executable", ".elf"),
    b"MZ": ("application/x-dosexec", ".exe"),
    b"BM": ("image/bmp", ".bmp"),
    b"RIFF": ("audio/wav", ".wav"),
}

EXTENSION_TO_MIMES: Dict[str, List[str]] = {
    ".jpg": ["image/jpeg"],
    ".jpeg": ["image/jpeg"],
    ".png": ["image/png"],
    ".gif": ["image/gif"],
    ".pdf": ["application/pdf"],
    ".zip": ["application/zip"],
    ".exe": ["application/x-dosexec", "application/x-msdownload"],
    ".elf": ["application/x-executable"],
    ".txt": ["text/plain", "application/octet-stream"],
    ".bmp": ["image/bmp", "image/x-ms-bmp"],
}


def inspect_file_signature(file_path: Path) -> Dict[str, Any]:
    """
    Inspects file headers using magic bytes and validates against the declared file extension.
    Returns detected MIME type, declared extension, mismatch flag, and diagnostic message.
    """
    file_path = Path(file_path)
    declared_ext = file_path.suffix.lower()
    file_size = file_path.stat().st_size if file_path.exists() else 0

    if not file_path.exists() or file_size == 0:
        return {
            "declared_extension": declared_ext,
            "detected_mime_type": "application/octet-stream",
            "is_signature_mismatch": False,
            "diagnostic": "File empty or non-existent",
        }

    detected_mime = "application/octet-stream"
    detected_ext_from_magic = None

    # First check magic bytes via puremagic
    try:
        matches = puremagic.magic_file(str(file_path))
        if matches:
            best_match = matches[0]
            detected_mime = best_match.mime_type or "application/octet-stream"
            detected_ext_from_magic = best_match.extension
    except Exception:
        pass

    # Fallback to direct byte inspection for critical forensic signatures
    try:
        with open(file_path, "rb") as f:
            header = f.read(16)
        for magic, (mime, ext) in MAGIC_SIGNATURES.items():
            if header.startswith(magic):
                detected_mime = mime
                detected_ext_from_magic = ext
                break
    except Exception:
        pass

    # Signature mismatch evaluation
    is_mismatch = False
    diagnostic = "Signature consistent with file extension"

    expected_mimes = EXTENSION_TO_MIMES.get(declared_ext, [])
    if expected_mimes:
        if detected_mime not in expected_mimes and detected_mime != "application/octet-stream":
            is_mismatch = True
            diagnostic = (
                f"Obfuscation detected: File extension is '{declared_ext}', "
                f"but binary signature indicates '{detected_mime}' ({detected_ext_from_magic})."
            )
    else:
        # Check standard python mimetypes
        guessed, _ = mimetypes.guess_type(str(file_path))
        if guessed and detected_mime != "application/octet-stream" and guessed != detected_mime:
            is_mismatch = True
            diagnostic = (
                f"Potential mismatch: Extension suggests '{guessed}', "
                f"magic signature detected '{detected_mime}'."
            )

    return {
        "declared_extension": declared_ext,
        "detected_mime_type": detected_mime,
        "detected_extension": detected_ext_from_magic,
        "is_signature_mismatch": is_mismatch,
        "diagnostic": diagnostic,
    }
