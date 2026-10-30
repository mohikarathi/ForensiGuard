# FORENSIC TRIAGE REPORT — FORENSIGUARD
**Analysis Timestamp (UTC):** 2026-10-21T12:15:42.573794+00:00
**Framework Version:** ForensiGuard v1.0.0

## 1. EVIDENCE PROVENANCE (OBJECTIVE FACTS)
- **Filename:** `src_0000_stego_high_payload.png`
- **File Size:** 11,950 bytes
- **SHA-256:** `91dc99123c5b92e9465cfc0ab94489760e739845521b6c85cac5c9b8d42be648`
- **MD5:** `826f24829dd1b3115f7e999f98b7ed70`
- **Declared Extension:** `.png`
- **Detected MIME Type:** `image/png`
- **Signature Mismatch:** `NO - CONSISTENT`

## 2. OBSERVED PHYSICAL METADATA
- **Modification Time (mtime):** 2024-10-27 03:43:38 UTC (subseconds: 0.094508s)
- **Access Time (atime):** 2024-10-27 03:46:40 UTC
- **Metadata Change Time (ctime):** 2024-10-27 03:43:39 UTC
- **Shannon Entropy:** 7.9824 bits/byte
- **LSB PoVs Chi-Square P-Value:** 0.999940

## 3. PROBABILISTIC MODEL INFERENCES
- **Overall Assessment:** **TAMPERED / MANIPULATED**
- **Manipulation Probability:** 87.59%
- **Confidence Score:** 82.33%
- **Attributed Anti-Forensic Technique:** `STEGANOGRAPHY`

### Modality-Specific Breakdown
- **Filesystem Metadata Model (XGBoost):** 0.37%
- **Image Residual CNN (SRNet-Lite):** 51.01%
- **Unsupervised Anomaly Score:** 0.3301 (baseline divergence)
- **Binary Signature Anomaly:** 0.0

## 4. EXPLANATORY EVIDENCE & SHAP ATTRIBUTION
- Time interval between modification and metadata change (mtime - ctime) (observed: -1.17, SHAP: -4.843) supported benign classification.
- Time interval between access and modification (atime - mtime) (observed: 182.17, SHAP: -0.499) supported benign classification.
- Isolation Forest deviation from clean filesystem baseline (observed: 0.33, SHAP: -0.025) supported benign classification.
- Time interval between access and metadata change (atime - ctime) (observed: 181.00, SHAP: -0.025) supported benign classification.

## 6. FORENSIC CAVEAT & LEGAL DISCLAIMER
> ForensiGuard provides probabilistic forensic triage indicators based on machine-learning models. These inferences do NOT constitute proof of guilt or conclusive evidentiary admissibility under Daubert/Frye. Independent manual examination of filesystem journal logs, file slack, and carving is mandatory.