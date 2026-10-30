# FORENSIC TRIAGE REPORT — FORENSIGUARD
**Analysis Timestamp (UTC):** 2026-10-21T12:15:45.490705+00:00
**Framework Version:** ForensiGuard v1.0.0

## 1. EVIDENCE PROVENANCE (OBJECTIVE FACTS)
- **Filename:** `src_0000_obfuscated.jpg`
- **File Size:** 313 bytes
- **SHA-256:** `bdf588cee79cbc7a7e779d0c5d36b105f020761ebac56f9f599c16850ce36678`
- **MD5:** `78f2d44af0224dc78282690b60a71073`
- **Declared Extension:** `.jpg`
- **Detected MIME Type:** `application/pdf`
- **Signature Mismatch:** `YES - OBFUSCATED`

## 2. OBSERVED PHYSICAL METADATA
- **Modification Time (mtime):** 2024-10-27 03:43:38 UTC (subseconds: 0.094508s)
- **Access Time (atime):** 2024-10-27 03:46:40 UTC
- **Metadata Change Time (ctime):** 2024-10-27 03:43:39 UTC
- **Shannon Entropy:** 4.7979 bits/byte
- **LSB PoVs Chi-Square P-Value:** 0.993956

## 3. PROBABILISTIC MODEL INFERENCES
- **Overall Assessment:** **TAMPERED / MANIPULATED**
- **Manipulation Probability:** 90.93%
- **Confidence Score:** 87.81%
- **Attributed Anti-Forensic Technique:** `FILE_TYPE_OBFUSCATION`

### Modality-Specific Breakdown
- **Filesystem Metadata Model (XGBoost):** 0.37%
- **Image Residual CNN (SRNet-Lite):** N/A (Non-image / Signature Mismatch)
- **Unsupervised Anomaly Score:** 0.3497 (baseline divergence)
- **Binary Signature Anomaly:** 1.0

## 4. EXPLANATORY EVIDENCE & SHAP ATTRIBUTION
- [OBFUSCATION CONFIRMED] Binary magic bytes (application/pdf) directly contradict the declared file extension ('.jpg').
- Time interval between modification and metadata change (mtime - ctime) (observed: -1.17, SHAP: -4.843) supported benign classification.
- Time interval between access and modification (atime - mtime) (observed: 182.17, SHAP: -0.499) supported benign classification.
- Isolation Forest deviation from clean filesystem baseline (observed: 0.35, SHAP: -0.025) supported benign classification.
- Time interval between access and metadata change (atime - ctime) (observed: 181.00, SHAP: -0.025) supported benign classification.

## 5. MODALITY WARNINGS & LIMITATIONS
- [WARNING] Header signature mismatch: Obfuscation detected: File extension is '.jpg', but binary signature indicates 'application/pdf' (.pdf).

## 6. FORENSIC CAVEAT & LEGAL DISCLAIMER
> ForensiGuard provides probabilistic forensic triage indicators based on machine-learning models. These inferences do NOT constitute proof of guilt or conclusive evidentiary admissibility under Daubert/Frye. Independent manual examination of filesystem journal logs, file slack, and carving is mandatory.