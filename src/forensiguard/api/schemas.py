"""Pydantic schemas for the ForensiGuard REST API."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    framework_version: str = "ForensiGuard v1.0.0"
    models_loaded: bool
    device: str
    benchmark_available: bool
    total_benchmark_samples: int
    models_dir: str


class SplitStat(BaseModel):
    artifacts: int
    sources: int
    percentage: float


class ManipulationCategory(BaseModel):
    id: str
    name: str
    description: str
    sample_count_benchmark: int


class PipelineStage(BaseModel):
    id: str
    name: str
    description: str
    modality: str
    status: str = "operational"


class OverviewResponse(BaseModel):
    title: str
    tagline: str
    authors: List[Dict[str, str]]
    total_artifacts: int
    independent_source_groups: int
    operating_threshold: float
    splits: Dict[str, SplitStat]
    manipulation_categories: List[ManipulationCategory]
    pipeline_stages: List[PipelineStage]
    research_disclaimer: str


class ModelComponentInfo(BaseModel):
    id: str
    name: str
    component_type: str
    algorithm: str
    input_modalities: List[str]
    is_loaded: bool
    status_note: str
    checkpoint_file: str


class ModelsResponse(BaseModel):
    components: List[ModelComponentInfo]
    decision_threshold: float
    threshold_selection_criterion: str


class DemoSampleItem(BaseModel):
    sample_id: str
    filename: str
    file_size_bytes: int
    declared_extension: str
    detected_mime_type: str
    technique: str
    subtype: str
    description: str
    is_adaptive: bool
    is_image: bool
    split: str
    ground_truth_label: str


class DemoSamplesResponse(BaseModel):
    samples: List[DemoSampleItem]


class FeatureAttributionItem(BaseModel):
    feature: str
    feature_label: str
    value: float
    shap_value: float
    direction: str  # "suspicious" or "benign"
    impact_rank: int


class ComponentOutput(BaseModel):
    ran: bool
    probability: Optional[float] = None
    raw_score: Optional[float] = None
    score_display: str
    interpretation: str
    contribution_description: Optional[str] = None
    reason_if_skipped: Optional[str] = None


class FinalPrediction(BaseModel):
    predicted_label: str  # "Flagged for review" or "No manipulation detected by the model"
    is_manipulated: bool
    manipulation_probability: float
    operating_threshold: float
    threshold_explanation: str
    attributed_technique: str
    attribution_probabilities: Dict[str, float]
    confidence: float


class AnalyzeResponse(BaseModel):
    analysis_id: str
    timestamp: str
    evidence_provenance: Dict[str, Any]
    observed_physical_facts: Dict[str, Any]
    final_prediction: FinalPrediction
    component_breakdown: Dict[str, ComponentOutput]
    feature_attributions: List[FeatureAttributionItem]
    investigator_narrative: List[str]
    warnings: List[str]
    demo_ground_truth: Optional[Dict[str, Any]] = None
    safe_image_preview_url: Optional[str] = None


class AnalysisSummaryItem(BaseModel):
    analysis_id: str
    filename: str
    file_size_bytes: int
    declared_extension: str
    predicted_label: str
    is_manipulated: bool
    manipulation_probability: float
    attributed_technique: str
    timestamp: str


class ModalityMetricRow(BaseModel):
    scope_name: str
    scope_display: str
    sample_count: int
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_auc: float
    fpr: float
    brier_score: Optional[float] = None


class AblationItem(BaseModel):
    id: int
    name: str
    short_name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_auc: float
    fpr: float
    brier_score: float
    key_finding: str


class AblationsResponse(BaseModel):
    ablations: List[AblationItem]
    note_cnn_ablation: str
    note_signature_ablation: str


class EvaluationSummaryResponse(BaseModel):
    operating_threshold: float
    total_test_samples: int
    independent_test_sources: int
    modality_comparison: List[ModalityMetricRow]
    confusion_matrix_full_test: Dict[str, int]
    attribution_accuracy_5class: float
    attribution_accuracy_manipulated: float
    attribution_accuracy_coarse_binary: float
    adaptive_adversary_summary: Dict[str, Any]
    scientific_disclaimers: List[str]


class CurvePoint(BaseModel):
    x: float  # FPR for ROC, Recall for PR
    y: float  # TPR for ROC, Precision for PR


class CurvesResponse(BaseModel):
    roc_curves: Dict[str, List[CurvePoint]]
    pr_curves: Dict[str, List[CurvePoint]]
