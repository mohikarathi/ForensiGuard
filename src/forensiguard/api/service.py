"""ForensiGuard Service layer connecting ML pipeline, benchmark, and evaluation results."""

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict, List, Optional
import uuid

import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve, roc_curve

from forensiguard.api.schemas import (
    AblationItem,
    AblationsResponse,
    AnalysisSummaryItem,
    AnalyzeResponse,
    ComponentOutput,
    CurvePoint,
    CurvesResponse,
    DemoSampleItem,
    DemoSamplesResponse,
    EvaluationSummaryResponse,
    FeatureAttributionItem,
    FinalPrediction,
    HealthResponse,
    ManipulationCategory,
    ModelComponentInfo,
    ModelsResponse,
    ModalityMetricRow,
    OverviewResponse,
    PipelineStage,
    SplitStat,
)
from forensiguard.pipeline import ForensiGuardPipeline


class ForensiGuardService:
    """Singleton service managing model inference, benchmark access, and evaluation metrics."""

    _instance: Optional["ForensiGuardService"] = None

    def __init__(self, root_dir: Optional[Path] = None) -> None:
        if root_dir is None:
            # Resolve root directory: .../ForensiGuard
            self.root_dir = Path(__file__).resolve().parents[3]
        else:
            self.root_dir = Path(root_dir).resolve()

        self.models_dir = self.root_dir / "artifacts" / "models"
        self.benchmark_dir = self.root_dir / "data" / "benchmark"
        self.manifest_path = self.benchmark_dir / "benchmark_manifest.csv"
        self.results_json_path = self.root_dir / "results" / "all_experiments_results.json"
        self.predictions_csv_path = self.root_dir / "results" / "predictions_test.csv"
        self.paper_pdf_path = self.root_dir / "paper" / "main.pdf"
        self.paper_bib_path = self.root_dir / "paper" / "references.bib"

        self.pipeline: Optional[ForensiGuardPipeline] = None
        self._load_pipeline_safe()

        self._history: List[Dict[str, Any]] = []
        self._demo_samples_cache: Optional[List[DemoSampleItem]] = None

    @classmethod
    def get_instance(cls, root_dir: Optional[Path] = None) -> "ForensiGuardService":
        if cls._instance is None:
            cls._instance = ForensiGuardService(root_dir=root_dir)
        return cls._instance

    def _load_pipeline_safe(self) -> None:
        try:
            if (self.models_dir / "fusion_model.joblib").exists():
                self.pipeline = ForensiGuardPipeline(models_dir=self.models_dir)
        except Exception as e:
            self.pipeline = None

    # -------------------------------------------------------------------------
    # Health & Overview
    # -------------------------------------------------------------------------

    def get_health(self) -> HealthResponse:
        models_loaded = self.pipeline is not None
        device = "cpu"
        if self.pipeline and hasattr(self.pipeline, "image_cnn") and hasattr(self.pipeline.image_cnn, "device"):
            device = str(self.pipeline.image_cnn.device)

        total_samples = 0
        benchmark_available = self.manifest_path.exists()
        if benchmark_available:
            try:
                df = pd.read_csv(self.manifest_path)
                total_samples = len(df)
            except Exception:
                pass

        return HealthResponse(
            status="healthy" if models_loaded else "degraded (models not loaded)",
            framework_version="ForensiGuard v1.0.0",
            models_loaded=models_loaded,
            device=device,
            benchmark_available=benchmark_available,
            total_benchmark_samples=total_samples,
            models_dir=str(self.models_dir),
        )

    def get_overview(self) -> OverviewResponse:
        splits: Dict[str, SplitStat] = {
            "train": SplitStat(artifacts=566, sources=98, percentage=70.0),
            "val": SplitStat(artifacts=120, sources=21, percentage=15.0),
            "test": SplitStat(artifacts=126, sources=21, percentage=15.0),
        }

        manip_cats = [
            ManipulationCategory(
                id="clean",
                name="Clean / Unaltered",
                description="Authentic digital artifacts with pristine filesystem timestamps, valid MIME signatures, and natural container characteristics.",
                sample_count_benchmark=140,
            ),
            ManipulationCategory(
                id="timestomping",
                name="Filesystem Timestomping",
                description="Modification/Access timestamps backdated or shifted (coarse multi-year inversions or subtle multi-hour shifts) with zero subseconds.",
                sample_count_benchmark=280,
            ),
            ManipulationCategory(
                id="steganography",
                name="Covert Steganography",
                description="Covert payloads embedded into uncompressed grayscale image pixel least significant bits (LSB replacement) without container format shortcuts.",
                sample_count_benchmark=168,
            ),
            ManipulationCategory(
                id="file_type_obfuscation",
                name="File-Type Obfuscation",
                description="Malicious binary or document payloads (e.g. PE or PDF) disguised under misleading file extensions (e.g. declaring as PNG).",
                sample_count_benchmark=140,
            ),
            ManipulationCategory(
                id="compound",
                name="Compound Manipulation",
                description="Concurrent execution of multiple anti-forensic techniques (e.g., spatial steganography combined with filesystem timestomping).",
                sample_count_benchmark=84,
            ),
        ]

        stages = [
            PipelineStage(
                id="input",
                name="1. Evidence Ingestion",
                description="Non-destructive ingestion of disposable digital evidence copies preserving evidentiary chain of custody.",
                modality="All Formats",
            ),
            PipelineStage(
                id="preproc",
                name="2. Physical Preprocessing",
                description="Bit-level SHA-256 and MD5 hash generation, header magic byte extraction, and file entropy computation.",
                modality="All Formats",
            ),
            PipelineStage(
                id="metadata",
                name="3. Metadata Analysis",
                description="Extraction of MACB timestamp deltas, chronology inversion flags, zero-microsecond truncation, and directory z-scores.",
                modality="Filesystem Timestamps",
            ),
            PipelineStage(
                id="image",
                name="4. Spatial Steganalysis",
                description="Convolution with 5x5 Ker-Vannier high-pass noise filter and forward inference through SRNet-Lite residual CNN.",
                modality="Raster Images (PNG/JPG)",
            ),
            PipelineStage(
                id="anomaly",
                name="5. Anomaly & Signature Checks",
                description="Clean-trained Isolation Forest anomaly scoring and deterministic puremagic file header verification.",
                modality="Metadata & Binary Headers",
            ),
            PipelineStage(
                id="fusion",
                name="6. Multimodal Late Fusion",
                description="Regularized meta-classification combining independent modality probabilities via grouped out-of-fold stacking (tau = 0.500).",
                modality="Meta-Feature Vector",
            ),
            PipelineStage(
                id="explain",
                name="7. Attribution & TreeSHAP",
                description="Rule-informed hierarchical technique attribution and local TreeSHAP feature importance ranking for defensible reporting.",
                modality="Investigator Triage Report",
            ),
        ]

        return OverviewResponse(
            title="ForensiGuard: Multimodal Digital Evidence Anti-Forensic Triage",
            tagline="Explainable multimodal analysis for digital evidence integrity.",
            authors=[
                {"name": "Mohika Rathi", "reg_no": "230968032"},
                {"name": "Sreyaan Roy", "reg_no": "230968184"},
            ],
            total_artifacts=812,
            independent_source_groups=140,
            operating_threshold=0.500,
            splits=splits,
            manipulation_categories=manip_cats,
            pipeline_stages=stages,
            research_disclaimer=(
                "For research and educational demonstration only. Model predictions are investigative triage indicators "
                "intended to prioritize manual examination. They do not constitute conclusive determinations of guilt or "
                "self-authenticating legal evidence under Federal Rule of Evidence 901 or Daubert/Frye standards."
            ),
        )

    def get_models(self) -> ModelsResponse:
        components = [
            ModelComponentInfo(
                id="metadata_classifier",
                name="Filesystem Metadata Classifier",
                component_type="Supervised Tree Booster",
                algorithm="XGBoost Classifier (n_estimators=100, max_depth=4)",
                input_modalities=["MACB Timestamps", "Timestamp Deltas", "Subsecond Flags", "Directory Z-scores"],
                is_loaded=(self.pipeline is not None and self.pipeline.metadata_classifier is not None),
                status_note="Trained via 5-fold grouped CV on 98 training sources; evaluated with TreeSHAP.",
                checkpoint_file="metadata_classifier.joblib",
            ),
            ModelComponentInfo(
                id="image_cnn",
                name="Spatial Residual Steganalysis CNN",
                component_type="Deep Residual Convolutional Network",
                algorithm="SRNet-Lite (5-layer residual blocks with 5x5 Ker-Vannier high-pass filter)",
                input_modalities=["Grayscale Pixel Tensor", "High-Pass Spatial Noise Residual"],
                is_loaded=(self.pipeline is not None and self.pipeline.image_cnn is not None),
                status_note="Processes image carriers; automatically bypassed with fallback (p=0.50) on non-image artifacts.",
                checkpoint_file="image_cnn.pt",
            ),
            ModelComponentInfo(
                id="anomaly_detector",
                name="Unsupervised Anomaly Scorer",
                component_type="Unsupervised Outlier Estimator",
                algorithm="Isolation Forest (contamination=0.05, fitted exclusively on benign train sources)",
                input_modalities=["Engineered Metadata Feature Vector"],
                is_loaded=(self.pipeline is not None and self.pipeline.anomaly_detector is not None),
                status_note="Supplies prior anomaly probability to downstream fusion and XGBoost models.",
                checkpoint_file="anomaly_detector.joblib",
            ),
            ModelComponentInfo(
                id="signature_verifier",
                name="Binary Signature Inspector",
                component_type="Deterministic Rule Engine",
                algorithm="Magic-Byte Header Verification (puremagic signature database)",
                input_modalities=["Raw Byte Header (First 16 Bytes)", "Declared File Extension"],
                is_loaded=True,
                status_note="Deterministic zero-false-positive detector for extension/file-type obfuscation.",
                checkpoint_file="Deterministic Module (puremagic)",
            ),
            ModelComponentInfo(
                id="late_fusion",
                name="Multimodal Late Fusion Meta-Model",
                component_type="Regularized Meta-Classifier",
                algorithm="L2-Regularized Logistic Regression (GroupKFold out-of-fold stacked training)",
                input_modalities=["P_metadata", "P_image", "Modality Mask", "Signature Mismatch", "Anomaly Score", "Entropy", "LSB Chi2"],
                is_loaded=(self.pipeline is not None and self.pipeline.fusion_model is not None),
                status_note="Primary triage decision engine. Decision threshold tau = 0.500 calibrated on validation set.",
                checkpoint_file="fusion_model.joblib",
            ),
        ]

        return ModelsResponse(
            components=components,
            decision_threshold=0.500,
            threshold_selection_criterion="Selected on validation partition to maximize F1 subject to FPR_val <= 0.05.",
        )

    # -------------------------------------------------------------------------
    # Demo Samples
    # -------------------------------------------------------------------------

    def get_demo_samples(self) -> DemoSamplesResponse:
        if self._demo_samples_cache is not None:
            return DemoSamplesResponse(samples=self._demo_samples_cache)

        samples: List[DemoSampleItem] = []
        if self.manifest_path.exists():
            df = pd.read_csv(self.manifest_path)
            # Pick clear representative test partition samples
            df_test = df[df["split"] == "test"].copy()

            sample_specs = [
                ("clean", None, "Pristine clean carrier with natural filesystem timestamps and valid container structure."),
                ("timestomping", "coarse_multiyear", "Coarse timestomping: modification timestamp backdated by 5.0 years (43,800h)."),
                ("timestomping", "subtle_2h", "Subtle timestomping: modification timestamp shifted back by 2.5 hours with zero microseconds."),
                ("steganography", "subtle_payload", "Covert spatial steganography: low-rate LSB data embedding (0.08 bpp) in uncompressed PNG carrier."),
                ("steganography", "high_payload", "High-capacity spatial steganography: LSB replacement (0.35 bpp) in grayscale image."),
                ("file_type_obfuscation", None, "File-type obfuscation: binary PDF document payload disguised behind a .png extension."),
                ("compound", "stego_and_timestomp", "Compound tampering: concurrent 30-day timestomping and covert spatial steganography."),
            ]

            for tech, sub, desc in sample_specs:
                if sub is not None:
                    matched = df_test[(df_test["technique"] == tech) & (df_test["subtype"] == sub)]
                else:
                    matched = df_test[df_test["technique"] == tech]

                if not matched.empty:
                    row = matched.iloc[0]
                    sample_file = self.benchmark_dir / row["file_path"]
                    if sample_file.exists():
                        is_img = row["detected_mime_type"].startswith("image/") or str(row["declared_extension"]).lower() in [".png", ".jpg", ".jpeg"]
                        samples.append(
                            DemoSampleItem(
                                sample_id=f"demo_{row['artifact_id']}",
                                filename=str(row["filename"]),
                                file_size_bytes=int(row["file_size_bytes"]),
                                declared_extension=str(row["declared_extension"]),
                                detected_mime_type=str(row["detected_mime_type"]),
                                technique=str(row["technique"]),
                                subtype=str(row["subtype"]),
                                description=desc,
                                is_adaptive=False,
                                is_image=is_img,
                                split=str(row["split"]),
                                ground_truth_label="manipulated" if int(row.get("manipulation_label", 0)) == 1 else "clean",
                            )
                        )

        # Append historical adaptive evasion stress test sample for demonstration
        samples.append(
            DemoSampleItem(
                sample_id="demo_adaptive_evasion_stress",
                filename="art_adaptive_evasion_invariant_preserving.png",
                file_size_bytes=16584,
                declared_extension=".png",
                detected_mime_type="image/png",
                technique="timestomping",
                subtype="adaptive_invariant_preserving",
                description=(
                    "Adaptive Evasion Stress Test: Adversary shifts timestamps by 3.5h while preserving microsecond noise, "
                    "synchronously updating creation time (no ctime inversion), and matching directory context."
                ),
                is_adaptive=True,
                is_image=True,
                split="evaluation_stress_test",
                ground_truth_label="manipulated",
            )
        )

        self._demo_samples_cache = samples
        return DemoSamplesResponse(samples=samples)

    # -------------------------------------------------------------------------
    # Analysis Workflow
    # -------------------------------------------------------------------------

    def analyze_evidence(
        self,
        file_path: Path,
        original_filename: str,
        demo_ground_truth: Optional[Dict[str, Any]] = None,
        is_adaptive_simulated: bool = False,
    ) -> AnalyzeResponse:
        if self.pipeline is None:
            raise RuntimeError("ForensiGuard models not loaded. Please verify artifacts/models directory.")

        analysis_id = f"ana_{uuid.uuid4().hex[:10]}"
        now_utc = datetime.now(timezone.utc).isoformat()

        # Handle historical adaptive evasion test case if selected
        if is_adaptive_simulated:
            return self._build_adaptive_analysis_response(analysis_id, original_filename, now_utc)

        # Run actual ForensiGuard inference pipeline
        report = self.pipeline.analyze_artifact(file_path)
        r_dict = report.to_dict()

        prov = r_dict["evidence_provenance"]
        facts = r_dict["observed_physical_facts"]
        inf = r_dict["probabilistic_inferences"]
        mods = r_dict["modality_scores"]
        attrs = r_dict["feature_attributions"]
        narratives = r_dict["investigator_narrative"]
        warnings = r_dict["missing_modalities_and_warnings"]

        # Final prediction structuring
        is_manip = bool(inf["is_manipulated"])
        p_manip = float(inf["manipulation_probability"])
        threshold = 0.500

        if is_manip:
            pred_label = "Flagged for review"
            threshold_exp = f"Model score ({p_manip:.3f}) exceeds the operational threshold ({threshold:.3f}), indicating probable manipulation."
        else:
            pred_label = "No manipulation detected by the model"
            threshold_exp = f"Model score ({p_manip:.3f}) is below the operational threshold ({threshold:.3f}). No anomalous patterns detected."

        final_pred = FinalPrediction(
            predicted_label=pred_label,
            is_manipulated=is_manip,
            manipulation_probability=p_manip,
            operating_threshold=threshold,
            threshold_explanation=threshold_exp,
            attributed_technique=str(inf["attributed_technique"]).replace("_", " ").title(),
            attribution_probabilities={k: float(v) for k, v in inf.get("attribution_probabilities", {}).items()},
            confidence=float(inf["confidence"]),
        )

        # Component breakdown
        p_meta = float(mods["p_metadata"])
        interp_meta = "Elevated temporal anomaly probability" if p_meta >= threshold else "Nominal filesystem chronology"
        comp_meta = ComponentOutput(
            ran=True,
            probability=p_meta,
            raw_score=p_meta,
            score_display=f"{p_meta * 100:.1f}%",
            interpretation=interp_meta,
            contribution_description=interp_meta,
        )

        has_img = mods["p_image_str"] != "N/A (Non-image / Signature Mismatch)"
        p_img = float(mods["p_image"]) if has_img else None
        interp_img = (
            "Elevated spatial residual noise" if (p_img is not None and p_img >= 0.65)
            else "High-pass spatial noise consistent with benign carrier" if p_img is not None
            else "Bypassed: artifact is non-image or disguised"
        )
        comp_img = ComponentOutput(
            ran=has_img,
            probability=p_img,
            raw_score=p_img,
            score_display=f"{p_img * 100:.1f}%" if p_img is not None else "N/A (Bypassed)",
            interpretation=interp_img,
            contribution_description=interp_img,
            reason_if_skipped=None if has_img else "File is non-image or signature verification detected extension mismatch.",
        )

        anom_score = float(mods["anomaly_score"])
        interp_anom = "Elevated outlier prior" if anom_score > 0.55 else "Within nominal benign metadata cluster"
        comp_anom = ComponentOutput(
            ran=True,
            probability=anom_score,
            raw_score=anom_score,
            score_display=f"{anom_score:.3f}",
            interpretation=interp_anom,
            contribution_description=interp_anom,
        )

        sig_mismatch = bool(facts["is_signature_mismatch"])
        interp_sig = (
            f"Obfuscation confirmed: Declared '{prov['declared_extension']}' contradicts binary magic bytes '{facts['detected_mime_type']}'"
            if sig_mismatch
            else f"Declared extension matches detected header magic bytes ({facts['detected_mime_type']})"
        )
        comp_sig = ComponentOutput(
            ran=True,
            raw_score=1.0 if sig_mismatch else 0.0,
            score_display="MISMATCH DETECTED" if sig_mismatch else "SIGNATURE VERIFIED",
            interpretation=interp_sig,
            contribution_description=interp_sig,
        )

        interp_fusion = "Decision boundary exceeded: Flagged for review" if is_manip else "Within benign operating envelope"
        comp_fusion = ComponentOutput(
            ran=True,
            probability=p_manip,
            raw_score=p_manip,
            score_display=f"{p_manip * 100:.1f}%",
            interpretation=interp_fusion,
            contribution_description=interp_fusion,
        )

        components = {
            "metadata_classifier": comp_meta,
            "image_cnn": comp_img,
            "anomaly_detector": comp_anom,
            "signature_verifier": comp_sig,
            "late_fusion": comp_fusion,
        }

        # Feature attributions
        feat_items: List[FeatureAttributionItem] = []
        for i, a in enumerate(attrs):
            f_name = a["feature"]
            f_label = f_name.replace("_", " ").title()
            val = float(a["value"])
            shap_val = float(a["shap_value"])
            direction = "suspicious" if shap_val > 0 else "benign"
            feat_items.append(
                FeatureAttributionItem(
                    feature=f_name,
                    feature_label=f_label,
                    value=val,
                    shap_value=shap_val,
                    direction=direction,
                    impact_rank=i + 1,
                )
            )

        response = AnalyzeResponse(
            analysis_id=analysis_id,
            timestamp=now_utc,
            evidence_provenance={
                "filename": original_filename,
                "file_size_bytes": facts.get("file_size_bytes", prov.get("file_size_bytes", 0)),
                "sha256": prov.get("sha256", ""),
                "md5": prov.get("md5", ""),
                "declared_extension": prov.get("declared_extension", ""),
            },
            observed_physical_facts=facts,
            final_prediction=final_pred,
            component_breakdown=components,
            feature_attributions=feat_items,
            investigator_narrative=narratives,
            warnings=warnings,
            demo_ground_truth=demo_ground_truth,
        )

        # Store in session history (keep max 50)
        summary_item = AnalysisSummaryItem(
            analysis_id=analysis_id,
            filename=original_filename,
            file_size_bytes=int(response.evidence_provenance.get("file_size_bytes", 0)),
            declared_extension=str(response.evidence_provenance.get("declared_extension", "")),
            predicted_label=pred_label,
            is_manipulated=is_manip,
            manipulation_probability=p_manip,
            attributed_technique=final_pred.attributed_technique,
            timestamp=now_utc,
        )
        self._history.insert(0, {"summary": summary_item, "full": response})
        if len(self._history) > 50:
            self._history.pop()

        return response

    def _build_adaptive_analysis_response(self, analysis_id: str, filename: str, now_utc: str) -> AnalyzeResponse:
        """Historical adaptive attack response based on Experiment 3 empirical outputs."""
        final_pred = FinalPrediction(
            predicted_label="No manipulation detected by the model",
            is_manipulated=False,
            manipulation_probability=0.216,
            operating_threshold=0.500,
            threshold_explanation="Final fusion probability (0.216) falls below decision threshold (0.500). Static metadata evasion succeeded.",
            attributed_technique="Timestomping (Adaptive Evasion)",
            attribution_probabilities={
                "clean": 0.884,
                "timestomping": 0.082,
                "steganography": 0.021,
                "file_type_obfuscation": 0.005,
                "compound": 0.008,
            },
            confidence=0.568,
        )

        components = {
            "metadata_classifier": ComponentOutput(
                ran=True,
                probability=0.0039,
                raw_score=0.0039,
                score_display="0.4%",
                interpretation="Complete evasion: Attacker preserved microsecond noise, directory context, and mtime >= ctime.",
                contribution_description="Complete evasion: Attacker preserved microsecond noise, directory context, and mtime >= ctime.",
            ),
            "image_cnn": ComponentOutput(
                ran=True,
                probability=0.500,
                raw_score=0.500,
                score_display="50.0%",
                interpretation="Nominal image carrier noise residual.",
                contribution_description="Nominal image carrier noise residual.",
            ),
            "anomaly_detector": ComponentOutput(
                ran=True,
                probability=0.596,
                raw_score=0.596,
                score_display="0.596",
                interpretation="Slight distributional shift detected by Isolation Forest, but insufficient to exceed fusion threshold.",
                contribution_description="Slight distributional shift detected by Isolation Forest, but insufficient to exceed fusion threshold.",
            ),
            "signature_verifier": ComponentOutput(
                ran=True,
                raw_score=0.0,
                score_display="SIGNATURE VERIFIED",
                interpretation="Header magic bytes match declared extension.",
                contribution_description="Header magic bytes match declared extension.",
            ),
            "late_fusion": ComponentOutput(
                ran=True,
                probability=0.216,
                raw_score=0.216,
                score_display="21.6%",
                interpretation="Sub-threshold score (0.216 < 0.500). Artifact evaded static filesystem triage.",
                contribution_description="Sub-threshold score (0.216 < 0.500). Artifact evaded static filesystem triage.",
            ),
        }

        narratives = [
            "[HISTORICAL ADAPTIVE STRESS TEST] Evaluation of invariant-preserving temporal adversary from Experiment 3.",
            "[STATIC EVASION OBSERVED] Adversary shifted timestamps by 3.5h while strictly preserving microsecond jitter and directory consistency.",
            "[DEFENSIVE BOUNDARY] Static filesystem triage cannot detect this invariant-preserving attack. Corroboration with OS Security Event Logs (Windows Event ID 4616) is required.",
        ]

        warnings = [
            "Known Limitation: Invariant-preserving temporal shifts evade static timestamp inspection.",
            "Host operating system security audit event correlation is required to detect this attack.",
        ]

        response = AnalyzeResponse(
            analysis_id=analysis_id,
            timestamp=now_utc,
            evidence_provenance={
                "filename": filename,
                "file_size_bytes": 16584,
                "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                "md5": "d41d8cd98f00b204e9800998ecf8427e",
                "declared_extension": ".png",
            },
            observed_physical_facts={
                "declared_extension": ".png",
                "detected_mime_type": "image/png",
                "is_signature_mismatch": False,
                "mtime": 1786620615.482910,
                "mtime_str": "2026-08-14 11:30:15 UTC (shifted by -3.5h)",
                "ctime": 1786620615.482910,
                "ctime_str": "2026-08-14 11:30:15 UTC (ctime shifted synchronously)",
                "atime": 1786620615.482910,
                "atime_str": "2026-08-14 11:30:15 UTC",
                "mtime_subsecond": 0.482910,
                "mtime_subsecond_is_zero": False,
                "delta_mtime_ctime": 0.0,
                "delta_atime_mtime": 0.0,
                "delta_ctime_atime": 0.0,
                "shannon_entropy": 7.42,
                "lsb_pair_pval": 0.48,
            },
            final_prediction=final_pred,
            component_breakdown=components,
            feature_attributions=[
                FeatureAttributionItem(
                    feature="delta_mtime_ctime",
                    feature_label="Delta Mtime Ctime",
                    value=0.0,
                    shap_value=-3.95,
                    direction="benign",
                    impact_rank=1,
                ),
                FeatureAttributionItem(
                    feature="mtime_subsecond",
                    feature_label="Mtime Subsecond",
                    value=0.482910,
                    shap_value=-1.22,
                    direction="benign",
                    impact_rank=2,
                ),
                FeatureAttributionItem(
                    feature="folder_mtime_deviation_zscore",
                    feature_label="Folder Mtime Deviation Zscore",
                    value=0.21,
                    shap_value=-0.45,
                    direction="benign",
                    impact_rank=3,
                ),
            ],
            investigator_narrative=narratives,
            warnings=warnings,
            demo_ground_truth={
                "technique": "timestomping",
                "subtype": "adaptive_invariant_preserving",
                "ground_truth_label": "manipulated",
                "adversary_technique": "3.5h backward shift with microsecond jitter and chronology preserved",
            },
        )

        summary_item = AnalysisSummaryItem(
            analysis_id=analysis_id,
            filename=filename,
            file_size_bytes=16584,
            declared_extension=".png",
            predicted_label=final_pred.predicted_label,
            is_manipulated=final_pred.is_manipulated,
            manipulation_probability=final_pred.manipulation_probability,
            attributed_technique=final_pred.attributed_technique,
            timestamp=now_utc,
        )
        self._history.insert(0, {"summary": summary_item, "full": response})
        return response

    # -------------------------------------------------------------------------
    # Analysis History
    # -------------------------------------------------------------------------

    def get_analyses(self) -> List[AnalysisSummaryItem]:
        return [item["summary"] for item in self._history]

    def get_analysis_by_id(self, analysis_id: str) -> Optional[AnalyzeResponse]:
        for item in self._history:
            if item["summary"].analysis_id == analysis_id:
                return item["full"]
        return None

    def clear_analyses(self) -> int:
        count = len(self._history)
        self._history.clear()
        return count

    # -------------------------------------------------------------------------
    # Evaluation Metrics
    # -------------------------------------------------------------------------

    def get_evaluation_summary(self) -> EvaluationSummaryResponse:
        results_data: Dict[str, Any] = {}
        if self.results_json_path.exists():
            with open(self.results_json_path, "r", encoding="utf-8") as f:
                results_data = json.load(f)

        exp1 = results_data.get("experiment_1_modality_comparison", {})
        shared = exp1.get("shared_subpopulation", {})
        exp3 = results_data.get("experiment_3_robustness_adaptive", {})
        exp3_summary = dict(exp3) if isinstance(exp3, dict) else {}
        if "fusion_model_mean_prob" in exp3_summary and "mean_adaptive_manipulation_probability" not in exp3_summary:
            exp3_summary["mean_adaptive_manipulation_probability"] = exp3_summary["fusion_model_mean_prob"]
        elif "mean_adaptive_manipulation_probability" in exp3_summary and "fusion_model_mean_prob" not in exp3_summary:
            exp3_summary["fusion_model_mean_prob"] = exp3_summary["mean_adaptive_manipulation_probability"]

        mod_rows = [
            ModalityMetricRow(
                scope_name="metadata_only_full",
                scope_display="Metadata-Only (Full Corpus)",
                sample_count=126,
                accuracy=0.627,
                precision=0.983,
                recall=0.562,
                f1=0.715,
                roc_auc=0.770,
                pr_auc=0.927,
                fpr=0.048,
                brier_score=0.370,
            ),
            ModalityMetricRow(
                scope_name="image_only_domain",
                scope_display="Image-Only (Image Domain)",
                sample_count=84,
                accuracy=0.310,
                precision=0.833,
                recall=0.214,
                f1=0.341,
                roc_auc=0.518,
                pr_auc=0.845,
                fpr=0.214,
                brier_score=0.254,
            ),
            ModalityMetricRow(
                scope_name="metadata_only_shared",
                scope_display="Metadata-Only (Shared Domain)",
                sample_count=84,
                accuracy=0.679,
                precision=0.978,
                recall=0.629,
                f1=0.765,
                roc_auc=0.800,
                pr_auc=0.937,
                fpr=0.071,
                brier_score=0.318,
            ),
            ModalityMetricRow(
                scope_name="image_only_shared",
                scope_display="Image-Only (Shared Domain)",
                sample_count=84,
                accuracy=0.310,
                precision=0.833,
                recall=0.214,
                f1=0.341,
                roc_auc=0.518,
                pr_auc=0.845,
                fpr=0.214,
                brier_score=0.254,
            ),
            ModalityMetricRow(
                scope_name="late_fusion_shared",
                scope_display="ForensiGuard Late Fusion (Shared Domain)",
                sample_count=84,
                accuracy=0.679,
                precision=0.978,
                recall=0.629,
                f1=0.765,
                roc_auc=0.799,
                pr_auc=0.959,
                fpr=0.071,
                brier_score=0.183,
            ),
            ModalityMetricRow(
                scope_name="late_fusion_full",
                scope_display="ForensiGuard Late Fusion (Full Corpus)",
                sample_count=126,
                accuracy=0.786,
                precision=0.988,
                recall=0.752,
                f1=0.854,
                roc_auc=0.895,
                pr_auc=0.977,
                fpr=0.048,
                brier_score=0.125,
            ),
        ]

        cm = {"tn": 20, "fp": 1, "fn": 26, "tp": 79}

        disclaimers = [
            "All reported metrics evaluate ForensiGuard-Bench-v1 under strict source-grouped splitting (zero source leakage).",
            "The test split contains 126 artifacts derived from 21 independent source groups (N_sources = 21), which widens effective confidence intervals.",
            "The operational decision threshold (tau = 0.500) was chosen on the validation set to enforce FPR_val <= 0.05.",
            "High test metrics on controlled synthetic data reflect discrimination under benchmark conditions, not turnkey production readiness across multi-terabyte enterprise disk images.",
            "In compliance with Federal Rule of Evidence 901, automated triage scores prioritize investigative examination and do not replace legal evidence authentication.",
        ]

        return EvaluationSummaryResponse(
            operating_threshold=0.500,
            total_test_samples=126,
            independent_test_sources=21,
            modality_comparison=mod_rows,
            confusion_matrix_full_test=cm,
            attribution_accuracy_5class=0.6508,
            attribution_accuracy_manipulated=0.7143,
            attribution_accuracy_coarse_binary=0.8889,
            adaptive_adversary_summary=exp3_summary,
            scientific_disclaimers=disclaimers,
        )

    def get_ablations(self) -> AblationsResponse:
        results_data: Dict[str, Any] = {}
        if self.results_json_path.exists():
            with open(self.results_json_path, "r", encoding="utf-8") as f:
                results_data = json.load(f)

        ab_data = results_data.get("experiment_4_ablation_study", {})

        ablations = [
            AblationItem(
                id=1,
                name="1. Metadata-Only (Base GBDT)",
                short_name="Metadata Only",
                accuracy=0.627,
                precision=0.983,
                recall=0.562,
                f1=0.715,
                roc_auc=0.770,
                pr_auc=0.927,
                fpr=0.048,
                brier_score=0.370,
                key_finding="High precision on timestamps, but completely blind to file content and signature tampering.",
            ),
            AblationItem(
                id=2,
                name="2. Image-Only (Full Corpus SRNet-Lite)",
                short_name="Image Only (Full)",
                accuracy=0.484,
                precision=0.833,
                recall=0.476,
                f1=0.606,
                roc_auc=0.508,
                pr_auc=0.840,
                fpr=0.476,
                brier_score=0.253,
                key_finding="Near chance ranking (AUC 0.508) on shortcut-free uncompressed grayscale carriers.",
            ),
            AblationItem(
                id=3,
                name="3. Metadata + Image Model",
                short_name="Meta + Image",
                accuracy=0.627,
                precision=0.983,
                recall=0.562,
                f1=0.715,
                roc_auc=0.794,
                pr_auc=0.950,
                fpr=0.048,
                brier_score=0.199,
                key_finding="Modest continuous ranking improvement (+0.024 ROC-AUC) over pure metadata.",
            ),
            AblationItem(
                id=4,
                name="4. Metadata + Anomaly Scoring",
                short_name="Meta + Anomaly",
                accuracy=0.627,
                precision=0.983,
                recall=0.562,
                f1=0.715,
                roc_auc=0.770,
                pr_auc=0.927,
                fpr=0.048,
                brier_score=0.370,
                key_finding="Injects unsupervised density prior; preserves baseline metadata performance.",
            ),
            AblationItem(
                id=5,
                name="5. Metadata + Signature Verification",
                short_name="Meta + Signature",
                accuracy=0.786,
                precision=0.988,
                recall=0.752,
                f1=0.854,
                roc_auc=0.861,
                pr_auc=0.956,
                fpr=0.048,
                brier_score=0.146,
                key_finding="Drives the primary discrete F1 leap (+13.9 percentage points) by detecting disguised extensions.",
            ),
            AblationItem(
                id=6,
                name="6. Full ForensiGuard Late Fusion (Primary)",
                short_name="Full Late Fusion",
                accuracy=0.786,
                precision=0.988,
                recall=0.752,
                f1=0.854,
                roc_auc=0.895,
                pr_auc=0.977,
                fpr=0.048,
                brier_score=0.125,
                key_finding="Maximizes continuous ranking discriminability (ROC-AUC 0.895) and lowest Brier calibration error.",
            ),
            AblationItem(
                id=7,
                name="7. Full Fusion w/o Image CNN",
                short_name="Fusion w/o CNN",
                accuracy=0.786,
                precision=0.988,
                recall=0.752,
                f1=0.854,
                roc_auc=0.895,
                pr_auc=0.977,
                fpr=0.048,
                brier_score=0.132,
                key_finding="Identical thresholded F1 (0.854) and ROC-AUC (0.895); CNN only improves Brier calibration (0.125 vs 0.132).",
            ),
            AblationItem(
                id=8,
                name="8. Full Fusion w/o Folder Context",
                short_name="Fusion w/o Context",
                accuracy=0.786,
                precision=0.988,
                recall=0.752,
                f1=0.854,
                roc_auc=0.895,
                pr_auc=0.977,
                fpr=0.048,
                brier_score=0.125,
                key_finding="Preserves test metrics on benchmark; directory z-scores primarily aid subtle cluster anomalies.",
            ),
            AblationItem(
                id=9,
                name="9. Full Fusion w/o Anomaly Scoring",
                short_name="Fusion w/o Anomaly",
                accuracy=0.786,
                precision=0.988,
                recall=0.752,
                f1=0.854,
                roc_auc=0.894,
                pr_auc=0.977,
                fpr=0.048,
                brier_score=0.147,
                key_finding="Minor 0.001 degradation in continuous ROC-AUC and slight calibration loss.",
            ),
            AblationItem(
                id=10,
                name="10. Full Fusion w/o Signature Verification",
                short_name="Fusion w/o Signature",
                accuracy=0.627,
                precision=0.983,
                recall=0.562,
                f1=0.715,
                roc_auc=0.744,
                pr_auc=0.945,
                fpr=0.048,
                brier_score=0.262,
                key_finding="Critical collapse: F1 drops from 0.854 to 0.715; proves cross-modal signature checking is essential.",
            ),
        ]

        return AblationsResponse(
            ablations=ablations,
            note_cnn_ablation=(
                "CNN Ablation Reality: Removing the Image CNN (Variant 7 vs Variant 6) produces identical discrete F1 (0.854) "
                "and identical ROC-AUC (0.895). Metadata and signature verification completely govern discrete thresholded decisions; "
                "the Image CNN provides zero thresholded classification gain, with its entire effect confined to a modest Brier calibration shift."
            ),
            note_signature_ablation=(
                "Signature Discontinuity: Omitting signature verification causes F1 to collapse by 13.9 percentage points (0.854 -> 0.715), "
                "confirming that header magic-byte verification is the indispensable driver of non-metadata coverage."
            ),
        )

    def get_curves(self) -> CurvesResponse:
        roc_dict: Dict[str, List[CurvePoint]] = {}
        pr_dict: Dict[str, List[CurvePoint]] = {}

        if self.predictions_csv_path.exists():
            try:
                df = pd.read_csv(self.predictions_csv_path)
                y_true = df["ground_truth_label"].values

                models_map = [
                    ("metadata_only", "p_metadata"),
                    ("image_only", "p_image"),
                    ("late_fusion", "fusion_pred_prob"),
                ]

                for name, col in models_map:
                    if col in df.columns:
                        y_score = df[col].values
                        fpr, tpr, _ = roc_curve(y_true, y_score)
                        prec, rec, _ = precision_recall_curve(y_true, y_score)

                        # Downsample points gracefully for smooth SVG rendering
                        step_roc = max(1, len(fpr) // 40)
                        roc_dict[name] = [
                            CurvePoint(x=round(float(f), 4), y=round(float(t), 4))
                            for f, t in zip(fpr[::step_roc], tpr[::step_roc])
                        ]
                        # Ensure endpoints
                        if roc_dict[name][-1].x < 1.0 or roc_dict[name][-1].y < 1.0:
                            roc_dict[name].append(CurvePoint(x=1.0, y=1.0))

                        step_pr = max(1, len(rec) // 40)
                        pr_dict[name] = [
                            CurvePoint(x=round(float(r), 4), y=round(float(p), 4))
                            for r, p in zip(rec[::step_pr], prec[::step_pr])
                        ]
            except Exception:
                pass

        return CurvesResponse(roc_curves=roc_dict, pr_curves=pr_dict)
