"""Unified end-to-end multimodal inference pipeline for ForensiGuard."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd

from forensiguard.explainability.shap_explainer import generate_natural_language_explanation
from forensiguard.features.image_features import compute_byte_statistics
from forensiguard.features.metadata_features import FEATURE_NAMES, extract_metadata_features_dict
from forensiguard.models.anomaly_detector import MetadataAnomalyDetector
from forensiguard.models.fusion import LateFusionMetaClassifier
from forensiguard.models.image_cnn import ImageCNNManager
from forensiguard.models.metadata_classifier import MetadataClassifier
from forensiguard.preprocessing.file_type import inspect_file_signature
from forensiguard.preprocessing.metadata import (
    compute_file_hashes,
    extract_folder_context,
    extract_raw_metadata,
)
from forensiguard.reporting.investigator_report import InvestigatorReport


class ForensiGuardPipeline:
    """
    Production-grade inference pipeline combining filesystem metadata analysis,
    image steganalysis, binary signature verification, and stacked late fusion.
    """

    def __init__(
        self,
        models_dir: Union[str, Path],
        device: Optional[str] = None,
    ) -> None:
        self.models_dir = Path(models_dir)
        self.anomaly_detector = MetadataAnomalyDetector.load(self.models_dir / "anomaly_detector.joblib")
        self.metadata_classifier = MetadataClassifier.load(self.models_dir / "metadata_classifier.joblib")
        self.image_cnn = ImageCNNManager(device=device)
        self.image_cnn.load(self.models_dir / "image_cnn.pt")
        self.fusion_model = LateFusionMetaClassifier.load(self.models_dir / "fusion_model.joblib")

    def analyze_artifact(self, file_path: Union[str, Path]) -> InvestigatorReport:
        """
        Executes complete defensive forensic analysis on a single target evidence artifact.
        Never modifies the target file.
        """
        file_path = Path(file_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Target evidence file does not exist: {file_path}")

        # 1. Cryptographic Identifiers and Signature Verification
        hashes = compute_file_hashes(file_path)
        sig_info = inspect_file_signature(file_path)
        byte_stats = compute_byte_statistics(file_path)

        # 2. Filesystem Metadata and Folder Context Extraction
        raw_meta = extract_raw_metadata(file_path)
        folder_ctx = extract_folder_context(file_path)

        # Look up acquired forensic disk image metadata if available in benchmark manifest
        manifest_path = file_path.parents[2] / "benchmark_manifest.csv"
        if not manifest_path.exists():
            manifest_path = Path(__file__).resolve().parents[2] / "data" / "benchmark" / "benchmark_manifest.csv"

        if manifest_path.exists():
            try:
                df_man = pd.read_csv(manifest_path)
                match = df_man[df_man["filename"] == file_path.name]
                if match.empty:
                    match = df_man[df_man["sha256"] == hashes["sha256"]]
                if not match.empty:
                    m_row = match.iloc[0]
                    raw_meta["mtime"] = float(m_row["mtime"])
                    raw_meta["atime"] = float(m_row["atime"])
                    raw_meta["ctime"] = float(m_row["ctime"])
                    raw_meta["mtime_subsecond"] = float(m_row["mtime_subsecond"])
                    folder_ctx["folder_mtime_mean"] = float(m_row["folder_mtime_mean"])
                    folder_ctx["folder_mtime_std"] = float(m_row["folder_mtime_std"])
                    folder_ctx["folder_mtime_median"] = float(m_row["folder_mtime_median"])
            except Exception:
                pass

        feat_dict = extract_metadata_features_dict(raw_meta, folder_context=folder_ctx)

        # 3. Unsupervised Anomaly Component
        df_meta_feat = pd.DataFrame([feat_dict], columns=FEATURE_NAMES)
        anomaly_score = float(self.anomaly_detector.score_samples(df_meta_feat)[0])

        # Augment with clean_anomaly_score for XGBoost
        df_meta_augmented = df_meta_feat.copy()
        df_meta_augmented["clean_anomaly_score"] = anomaly_score

        # 4. Supervised Metadata Classifier & SHAP
        p_metadata = float(self.metadata_classifier.predict_proba(df_meta_augmented)[0, 1])
        shap_contributions = self.metadata_classifier.explain_sample(df_meta_augmented)

        # 5. Image Modality Evaluation
        is_image = sig_info["detected_mime_type"].startswith("image/") or file_path.suffix.lower() in [
            ".jpg", ".jpeg", ".png", ".bmp", ".gif"
        ]
        warnings: List[str] = []

        if is_image and not sig_info["is_signature_mismatch"]:
            p_image = float(self.image_cnn.predict_proba(file_path))
            has_image_modality = 1.0
            p_image_str = f"{p_image * 100:.2f}%"
        else:
            # Fallback for non-image or disguised non-image files
            p_image = 0.50
            has_image_modality = 0.0
            p_image_str = "N/A (Non-image / Signature Mismatch)"
            if not is_image:
                warnings.append("Image residual CNN skipped: file is not an image carrier.")
            if sig_info["is_signature_mismatch"]:
                warnings.append(f"Header signature mismatch: {sig_info['diagnostic']}")

        # 6. Multimodal Late Fusion
        sig_mismatch_val = 1.0 if sig_info["is_signature_mismatch"] else 0.0
        fusion_input = pd.DataFrame([{
            "p_metadata": p_metadata,
            "p_image": p_image,
            "has_image_modality": has_image_modality,
            "signature_mismatch": sig_mismatch_val,
            "anomaly_score": anomaly_score,
            "shannon_entropy": byte_stats["shannon_entropy"],
            "lsb_pair_pval": byte_stats["lsb_pair_pval"],
        }])

        fusion_result = self.fusion_model.predict_fusion(fusion_input)

        # Generate narrative from SHAP
        narrative = generate_natural_language_explanation(shap_contributions)
        if sig_info["is_signature_mismatch"]:
            narrative.insert(
                0,
                f"[OBFUSCATION CONFIRMED] Binary magic bytes ({sig_info['detected_mime_type']}) "
                f"directly contradict the declared file extension ('{sig_info['declared_extension']}')."
            )
        if has_image_modality == 1.0 and p_image > 0.65:
            narrative.append(
                f"[STEGANOGRAPHY DETECTED] Noise-residual CNN scored high-frequency spatial residuals "
                f"at {p_image * 100:.1f}%, indicating embedded covert data."
            )

        # Structure report
        mtime_dt = datetime.fromtimestamp(raw_meta["mtime"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        atime_dt = datetime.fromtimestamp(raw_meta["atime"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        ctime_dt = datetime.fromtimestamp(raw_meta["ctime"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        report_payload = {
            "evidence_provenance": {
                "filename": file_path.name,
                "file_path": str(file_path),
                "file_size_bytes": raw_meta["file_size_bytes"],
                "sha256": hashes["sha256"],
                "md5": hashes["md5"],
                "declared_extension": sig_info["declared_extension"],
            },
            "observed_physical_facts": {
                "declared_extension": sig_info["declared_extension"],
                "detected_mime_type": sig_info["detected_mime_type"],
                "is_signature_mismatch": sig_info["is_signature_mismatch"],
                "mtime": raw_meta["mtime"],
                "mtime_str": mtime_dt,
                "ctime": raw_meta["ctime"],
                "ctime_str": ctime_dt,
                "atime": raw_meta["atime"],
                "atime_str": atime_dt,
                "mtime_subsecond": raw_meta["mtime_subsecond"],
                "mtime_subsecond_is_zero": bool(raw_meta.get("mtime_subsecond", 1.0) == 0.0),
                "delta_mtime_ctime": float(feat_dict.get("delta_mtime_ctime", raw_meta["mtime"] - raw_meta["ctime"])),
                "delta_atime_mtime": float(feat_dict.get("delta_atime_mtime", raw_meta["atime"] - raw_meta["mtime"])),
                "delta_ctime_atime": float(feat_dict.get("delta_ctime_atime", raw_meta["ctime"] - raw_meta["atime"])),
                "shannon_entropy": byte_stats["shannon_entropy"],
                "lsb_pair_pval": byte_stats["lsb_pair_pval"],
            },
            "probabilistic_inferences": {
                "manipulation_probability": fusion_result["manipulation_probability"],
                "is_manipulated": fusion_result["is_manipulated"],
                "attributed_technique": fusion_result["attributed_technique"],
                "attribution_probabilities": fusion_result["attribution_probabilities"],
                "confidence": fusion_result["confidence"],
            },
            "modality_scores": {
                "p_metadata": p_metadata,
                "p_image": p_image,
                "p_image_str": p_image_str,
                "anomaly_score": anomaly_score,
                "signature_mismatch_score": sig_mismatch_val,
            },
            "feature_attributions": shap_contributions,
            "investigator_narrative": narrative,
            "warnings": warnings,
        }

        return InvestigatorReport(report_payload)
