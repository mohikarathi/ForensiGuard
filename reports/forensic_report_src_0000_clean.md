# FORENSIC TRIAGE REPORT — FORENSIGUARD
**Analysis Timestamp (UTC):** 2026-10-21T12:15:36.357528+00:00
**Framework Version:** ForensiGuard v1.0.0

## 1. EVIDENCE PROVENANCE (OBJECTIVE FACTS)
- **Filename:** `src_0000_clean.jpg`
- **File Size:** 5,829 bytes
- **SHA-256:** `82033024a5fc6b75e75b78a234bd9e674c73d11f1fab08e0206a344b4b827aa0`
- **MD5:** `5bf4b46c97c18fdf3e131901087d004a`
- **Declared Extension:** `.jpg`
- **Detected MIME Type:** `image/jpeg`
- **Signature Mismatch:** `NO - CONSISTENT`

## 2. OBSERVED PHYSICAL METADATA
- **Modification Time (mtime):** 2024-10-27 03:43:38 UTC (subseconds: 0.094508s)
- **Access Time (atime):** 2024-10-27 03:46:40 UTC
- **Metadata Change Time (ctime):** 2024-10-27 03:43:39 UTC
- **Shannon Entropy:** 7.8784 bits/byte
- **LSB PoVs Chi-Square P-Value:** 0.006491

## 3. PROBABILISTIC MODEL INFERENCES
- **Overall Assessment:** **CLEAN / BENIGN**
- **Manipulation Probability:** 3.39%
- **Confidence Score:** 93.81%
- **Attributed Anti-Forensic Technique:** `CLEAN`

### Modality-Specific Breakdown
- **Filesystem Metadata Model (XGBoost):** 0.37%
- **Image Residual CNN (SRNet-Lite):** 51.00%
- **Unsupervised Anomaly Score:** 0.3149 (baseline divergence)
- **Binary Signature Anomaly:** 0.0

## 4. EXPLANATORY EVIDENCE & SHAP ATTRIBUTION
- Time interval between modification and metadata change (mtime - ctime) (observed: -1.17, SHAP: -4.843) supported benign classification.
- Time interval between access and modification (atime - mtime) (observed: 182.17, SHAP: -0.499) supported benign classification.
- Isolation Forest deviation from clean filesystem baseline (observed: 0.31, SHAP: -0.025) supported benign classification.
- Time interval between access and metadata change (atime - ctime) (observed: 181.00, SHAP: -0.025) supported benign classification.

## 6. FORENSIC CAVEAT & LEGAL DISCLAIMER
> ForensiGuard provides probabilistic forensic triage indicators based on machine-learning models. These inferences do NOT constitute proof of guilt or conclusive evidentiary admissibility under Daubert/Frye. Independent manual examination of filesystem journal logs, file slack, and carving is mandatory.