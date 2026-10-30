# FORENSIC TRIAGE REPORT — FORENSIGUARD
**Analysis Timestamp (UTC):** 2026-10-24T14:28:20.833947+00:00
**Framework Version:** ForensiGuard v1.0.0

## 1. EVIDENCE PROVENANCE (OBJECTIVE FACTS)
- **Filename:** `art_src_0000_47b0d1ab5f.png`
- **File Size:** 11,603 bytes
- **SHA-256:** `34ac93f45df7124efd025638162c273d82d43a2fef47caa390574fa18d6642f6`
- **MD5:** `5c90f917872e661c7d0870adf954c879`
- **Declared Extension:** `.png`
- **Detected MIME Type:** `image/png`
- **Signature Mismatch:** `NO - CONSISTENT`

## 2. OBSERVED PHYSICAL METADATA
- **Modification Time (mtime):** 2024-10-27 03:43:38 UTC (subseconds: 0.094508s)
- **Access Time (atime):** 2024-10-27 03:46:40 UTC
- **Metadata Change Time (ctime):** 2024-10-27 03:43:39 UTC
- **Shannon Entropy:** 7.9843 bits/byte
- **LSB PoVs Chi-Square P-Value:** 1.000000

## 3. PROBABILISTIC MODEL INFERENCES
- **Overall Assessment:** **CLEAN / BENIGN**
- **Manipulation Probability:** 26.68%
- **Confidence Score:** 52.49%
- **Attributed Anti-Forensic Technique:** `STEGANOGRAPHY`

### Modality-Specific Breakdown
- **Filesystem Metadata Model (XGBoost):** 0.37%
- **Image Residual CNN (SRNet-Lite):** 49.09%
- **Unsupervised Anomaly Score:** 0.3287 (baseline divergence)
- **Binary Signature Anomaly:** 0.0

## 4. EXPLANATORY EVIDENCE & SHAP ATTRIBUTION
- Time interval between modification and metadata change (mtime - ctime) (observed: -1.17, SHAP: -4.843) supported benign classification.
- Time interval between access and modification (atime - mtime) (observed: 182.17, SHAP: -0.499) supported benign classification.
- Z-score deviation from sibling files in parent directory (observed: -0.21, SHAP: -0.026) supported benign classification.
- Time interval between access and metadata change (atime - ctime) (observed: 181.00, SHAP: -0.025) supported benign classification.

## 6. FORENSIC CAVEAT & LEGAL DISCLAIMER
> ForensiGuard provides probabilistic forensic triage indicators based on machine-learning models. These inferences do NOT constitute proof of guilt or conclusive evidentiary admissibility under Daubert/Frye. Independent manual examination of filesystem journal logs, file slack, and carving is mandatory.