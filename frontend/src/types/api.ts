/**
 * TypeScript Interfaces for ForensiGuard REST API
 */

export interface HealthResponse {
  status: string;
  framework_version: string;
  models_loaded: boolean;
  device: string;
  benchmark_available: boolean;
  total_benchmark_samples: number;
  models_dir: string;
}

export interface SplitInfo {
  artifacts: number;
  sources: number;
  percentage: number;
}

export interface OverviewResponse {
  title: string;
  tagline: string;
  authors: { name: string; reg_no: string }[];
  total_artifacts: number;
  independent_source_groups: number;
  operating_threshold: number;
  splits: Record<string, SplitInfo>;
  manipulation_categories: string[];
  pipeline_stages: string[];
  research_disclaimer: string;
}

export interface ModelDetail {
  name: string;
  type: string;
  checkpoint_file: string;
  status: string;
  input_dimension?: string | number;
  description: string;
}

export interface ModelsResponse {
  pipeline_initialized: boolean;
  models: ModelDetail[];
}

export interface DemoSampleItem {
  sample_id: string;
  filename: string;
  file_size_bytes: number;
  declared_extension: string;
  detected_mime_type: string;
  technique: string;
  subtype: string;
  description: string;
  is_adaptive: boolean;
  is_image: boolean;
  split: string;
  ground_truth_label: 'clean' | 'manipulated';
}

export interface DemoSamplesResponse {
  samples: DemoSampleItem[];
}

export interface FinalPrediction {
  predicted_label: string;
  is_manipulated: boolean;
  manipulation_probability: number;
  operating_threshold: number;
  threshold_explanation: string;
  attributed_technique: string;
  attribution_probabilities: Record<string, number>;
  confidence: number;
}

export interface ComponentOutput {
  ran: boolean;
  probability?: number | null;
  raw_score?: number | null;
  score_display?: string;
  interpretation?: string;
  contribution_description?: string;
  note?: string;
  reason_if_skipped?: string | null;
}

export interface FeatureAttributionItem {
  feature: string;
  feature_label: string;
  value: number;
  shap_value: number;
  direction: 'manipulated' | 'benign' | 'suspicious';
  impact_rank: number;
}

export interface DemoGroundTruth {
  technique: string;
  subtype: string;
  ground_truth_label: string;
  adversary_technique?: string;
}

export interface AnalyzeResponse {
  analysis_id: string;
  timestamp: string;
  evidence_provenance: {
    filename: string;
    file_path?: string;
    file_size_bytes: number;
    sha256: string;
    md5: string;
    declared_extension?: string;
  };
  observed_physical_facts: {
    declared_extension?: string;
    detected_mime_type?: string;
    is_signature_mismatch?: boolean;
    mtime?: number;
    mtime_str?: string;
    atime?: number;
    atime_str?: string;
    ctime?: number;
    ctime_str?: string;
    birthtime?: number;
    mtime_subsecond?: number;
    mtime_subsecond_is_zero?: boolean;
    delta_mtime_ctime?: number;
    delta_atime_mtime?: number;
    delta_ctime_atime?: number;
    folder_mtime_diff_from_mean?: number;
    folder_mtime_zscore?: number;
    shannon_entropy?: number;
    lsb_pair_pval?: number;
    image_is_valid?: boolean;
    image_width?: number;
    image_height?: number;
    image_channels?: number;
  };
  final_prediction: FinalPrediction;
  component_breakdown: {
    metadata_classifier: ComponentOutput;
    image_cnn: ComponentOutput;
    anomaly_detector: ComponentOutput;
    signature_verifier: ComponentOutput;
    late_fusion: ComponentOutput;
  };
  feature_attributions: FeatureAttributionItem[];
  investigator_narrative: string[];
  warnings: string[];
  demo_ground_truth?: DemoGroundTruth | null;
  safe_image_preview_url?: string | null;
}

export interface AnalysisSummaryItem {
  analysis_id: string;
  filename: string;
  file_size_bytes: number;
  declared_extension: string;
  predicted_label: string;
  is_manipulated: boolean;
  manipulation_probability: number;
  attributed_technique: string;
  timestamp: string;
}

export interface ModalityMetricRow {
  scope_name: string;
  scope_display: string;
  sample_count: number;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  pr_auc: number;
  fpr: number;
  brier_score?: number | null;
}

export interface AblationItem {
  id: number;
  name: string;
  short_name: string;
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  pr_auc: number;
  fpr: number;
  brier_score: number;
  key_finding: string;
}

export interface AblationsResponse {
  ablations: AblationItem[];
  note_cnn_ablation: string;
  note_signature_ablation: string;
}

export interface EvaluationSummaryResponse {
  operating_threshold: number;
  total_test_samples: number;
  independent_test_sources: number;
  modality_comparison: ModalityMetricRow[];
  confusion_matrix_full_test: {
    tp: number;
    fp: number;
    tn: number;
    fn: number;
  };
  attribution_accuracy_5class: number;
  attribution_accuracy_manipulated: number;
  attribution_accuracy_coarse_binary: number;
  adaptive_adversary_summary?: {
    adaptive_sample_count?: number;
    metadata_model_detection_rate?: number;
    fusion_model_detection_rate?: number;
    fusion_model_mean_prob?: number;
    mean_adaptive_manipulation_probability?: number;
    metadata_model_mean_prob?: number;
    anomaly_detector_mean_score?: number;
    attack_description?: string;
    summary?: string;
  };
  scientific_disclaimers: string[];
}

export interface CurvePoint {
  x: number;
  y: number;
}

export interface CurvesResponse {
  roc_curves: Record<string, CurvePoint[]>;
  pr_curves: Record<string, CurvePoint[]>;
}
