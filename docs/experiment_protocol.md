# ForensiGuard Experimental Protocol

This document details the scientific evaluation protocol implemented to benchmark ForensiGuard.

## 1. Security-Oriented Evaluation Metrics
Forensic triage demands strong guarantees against false positives, as wrongly alleging evidence tampering incurs heavy legal and operational costs. We evaluate:
- **Accuracy, Precision, Recall, Macro F1, Weighted F1**
- **ROC-AUC & PR-AUC**
- **False Positive Rate at Fixed Operating Points**: FPR at 95% Recall, and Recall at FPR $\le 1\%$ and $\le 5\%$.
- **Brier Score**: Quadratic penalty measuring probability calibration.
- **Confusion Matrices**: Detailed error distribution across Clean and Manipulated classes.
- **Technique Attribution Accuracy**: Top-1 multi-class classification accuracy.

## 2. Core Experimental Suite

### Experiment 1: Single Modality vs. Late Fusion
- **Objective**: Quantify whether combining filesystem metadata and image/binary content outperforms isolated single-modality detectors.
- **Configurations**:
  1. Metadata-Only (XGBoost + Anomaly Score)
  2. Image-Only (Residual CNN + Statistical Byte Tests)
  3. Late Fusion (Stacked Calibrated Meta-Classifier)
- **Constraint**: Evaluated on the exact same held-out test split containing multimodal artifacts.

### Experiment 2: Manipulation Difficulty Analysis
- **Objective**: Evaluate detector degradation across manipulation intensity.
- **Timestomping**:
  - Coarse: Multi-year jumps, epoch resets (1970).
  - Subtle: 1 to 4 hour shifts, microsecond zeroing.
- **Steganography**:
  - High payload: 0.40 bits per pixel (bpp).
  - Low payload: 0.05 to 0.10 bits per pixel (bpp).

### Experiment 3: Robustness and Adaptive Attacks
- **Objective**: Assess model stability when an attacker is aware of detection heuristics.
- **Adaptive Scenarios**:
  - Timestamp jitter preservation: Attacker preserves realistic microsecond noise and keeps chronological ordering ($mtime > ctime$).
  - Directory neighbor matching: Attacker samples timestamps within the interquartile range of neighboring files in the folder.
  - Low-entropy payload embedding: Steganographic payloads designed to minimize global entropy changes.

### Experiment 4: Component Ablation Study
- **Objective**: Measure marginal contribution of each architectural subsystem:
  - Base metadata XGBoost without Anomaly Score.
  - Metadata model without folder context features.
  - CNN trained on raw RGB pixels vs. Noise Residuals.
  - Late fusion without signature mismatch rule.

### Experiment 5: Generalization and Cross-Domain Validation
- **Objective**: Test performance across unseen file formats and realistic filesystem context distributions.
