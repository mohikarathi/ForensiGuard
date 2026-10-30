"""Data schema and definitions for ForensiGuard forensic artifacts."""

from dataclasses import asdict, dataclass, field
from enum import Enum
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ManipulationType(str, Enum):
    CLEAN = "clean"
    TIMESTOMPING = "timestomping"
    STEGANOGRAPHY = "steganography"
    FILE_TYPE_OBFUSCATION = "file_type_obfuscation"
    COMPOUND = "compound"


TECHNIQUE_TO_ID: Dict[str, int] = {
    ManipulationType.CLEAN.value: 0,
    ManipulationType.TIMESTOMPING.value: 1,
    ManipulationType.STEGANOGRAPHY.value: 2,
    ManipulationType.FILE_TYPE_OBFUSCATION.value: 3,
    ManipulationType.COMPOUND.value: 4,
}

ID_TO_TECHNIQUE: Dict[int, str] = {v: k for k, v in TECHNIQUE_TO_ID.items()}


@dataclass
class ArtifactRecord:
    """Documented record of a digital artifact in the benchmark."""
    artifact_id: str
    source_file_id: str
    filename: str
    file_path: str
    sha256: str
    md5: str
    file_size_bytes: int
    declared_extension: str
    detected_mime_type: str
    is_signature_mismatch: bool
    manipulation_label: int  # 0 = clean, 1 = manipulated
    technique: str          # clean, timestomping, steganography, file_type_obfuscation, compound
    subtype: str            # coarse, subtle, lsb_0.2bpp, disguised_pdf, etc.
    tool_name: str
    parameters_json: str
    mtime: float
    atime: float
    ctime: float
    birthtime: float
    mtime_subsecond: float
    folder_context_id: str
    split: str = "train"    # train, val, test
    generator_version: str = "1.0.0"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactRecord":
        return cls(**data)
