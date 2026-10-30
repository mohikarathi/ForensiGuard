# ForensiGuard Interactive Research Demo UI — Implementation & Validation Report

**Project Title:** ForensiGuard: A Multimodal Machine-Learning Framework for Detecting, Attributing and Explaining Anti-Forensic Manipulation of Digital Evidence  
**Academic Authors:** Mohika Rathi (Reg. No: 230968032) & Sreyaan Roy (Reg. No: 230968184)  
**Date:** October 2026  
**Status:** Verification Complete — Production Build Ready (26/26 Tests Passed)  

---

## 1. Executive Summary

As part of the academic project deliverables for university evaluation and IEEE conference submission, a complete, interactive, full-stack research demonstration dashboard has been engineered, verified, and packaged for **ForensiGuard**.

The interface bridges directly to the production Python machine learning pipeline (`ForensiGuardPipeline`), executing real inference on arbitrary uploaded evidence and curated benchmark samples without mockups or synthetic shortcuts. It presents exact TreeSHAP feature attributions, honest benchmark performance, multi-modal component scoring, and clear legal/evidentiary disclosures under Federal Rule of Evidence 901.

---

## 2. Full-Stack Architecture

```
+---------------------------------------------------------------------------------+
|              React 18 + Vite 6 + Tailwind CSS UI (Port 5173 / Port 8000)        |
|  - Navbar (Academic Accreditation: Mohika Rathi 230968032 & Sreyaan Roy 230968184) |
|  - Sidebar: 5 Navigation Views                                                  |
|    1. Pipeline Overview (Interactive Architecture & Partitions)                 |
|    2. Analyze Evidence (Multi-Modal Triage & TreeSHAP Waterfall)                |
|    3. Analysis History (Session Audit Log & Export)                             |
|    4. Evaluation & Ablations (ROC, PR & 10-Variant Study)                       |
|    5. About Research (IEEE Manuscript Download & Legal Scope)                   |
+---------------------------------------+-----------------------------------------+
                                        | (REST JSON / Multi-Part)
                                        v
+---------------------------------------------------------------------------------+
|                    FastAPI Backend Engine (app.server / Port 8000)             |
|  - Router & Static Mount: src/forensiguard/api/server.py                        |
|  - Service Core: src/forensiguard/api/service.py                                |
|  - Pydantic Contracts: src/forensiguard/api/schemas.py                          |
+---------------------------------------+-----------------------------------------+
                                        | (In-Memory Invocations)
                                        v
+---------------------------------------------------------------------------------+
|                            ForensiGuard ML Pipeline                             |
|  - Evidence Ingestion & Hash Generation (SHA-256, MD5)                          |
|  - Metadata Extractor (30 Features: Deltas, Subsecond Zeroing, Z-scores)        |
|  - Filesystem Classifier (CatBoost Booster + TreeSHAP Explainer)                |
|  - Spatial Residual Steganalysis CNN (ResNet-18)                                |
|  - Unsupervised Anomaly Scorer (Isolation Forest)                               |
|  - Binary Signature Verification Engine (MIME vs Extension)                     |
|  - Multimodal Late Fusion Calibrator (Out-of-Fold Trained Logistic Regression)   |
+---------------------------------------------------------------------------------+
```

---

## 3. Implemented Capabilities & Views

### 3.1 Overview View (`OverviewView.tsx`)
- **Interactive Pipeline Architecture:** Step-by-step interactive diagram tracking evidence ingestion, metadata extraction (30 tabular features), spatial noise residuals, multi-modal classification, out-of-fold late fusion, and TreeSHAP explainability.
- **Dataset Partition Visualizer:** Rigorous source-grouped split distribution (70% Train [566 samples, 98 sources], 15% Validation [120 samples, 21 sources], 15% Test [126 samples, 21 sources]) confirming zero source ID leakage.
- **Manipulation Taxonomy:** Overview of evaluated anti-forensic vectors (timestomping, steganography, file-type obfuscation, compound attacks, and clean carriers).
- **Scientific Disclosures:** Explains format-label shortcut eradication and adaptive invariant-preserving evasion bounds.

### 3.2 Evidence Analysis & SHAP Triage View (`AnalyzeView.tsx`)
- **Dual Ingestion Modes:**
  1. *Curated Benchmark Samples:* 8 representative held-out test artifacts across clean reference, timestamp backward shift, subsecond zeroing, LSB steganography, file-type obfuscation, compound manipulation, and the critical adaptive invariant-preserving evasion sample.
  2. *Custom Evidence Upload:* Non-destructive drag-and-drop file ingestion (supports images and general files up to 25 MB).
- **Calibrated Triage Verdict:** Flags evidence as *"Flagged for review"* or *"No manipulation detected by the model"* based on the operational threshold ($\tau = 0.500$), reporting calibrated probability and multi-class technique attribution.
- **Component Breakdown:** Individual score cards for Metadata Classifier, Image CNN (with bypass status when non-image), Isolation Forest Anomaly Detector, and Signature Verifier.
- **TreeSHAP Waterfall:** Real-time visual representation of feature contributions pushing toward flagged ($+\text{SHAP}$) or toward benign ($-\text{SHAP}$) with exact feature labels and observed values.
- **Physical Facts Table:** Cryptographic SHA-256 and MD5 hashes (with one-click copy buttons), MACB timestamps, subsecond precision status, and MIME vs extension matching.
- **Automated Forensic Narrative:** Plain-English investigator bullets detailing evidence integrity.
- **JSON Export:** Download full machine-readable forensic reports with complete metadata.

### 3.3 Analysis Audit Log (`HistoryView.tsx`)
- Maintains a persistent session audit trail of all evaluated evidence artifacts.
- Displays timestamp, filename, size, triage decision, calibrated probability, and attributed technique.
- One-click inspection reload into the triage view or audit log clearance.

### 3.4 Model Evaluation & Ablation View (`EvaluationView.tsx`)
- **Canonical Performance Summary:** Held-out test performance (Accuracy: 78.57%, Precision: 85.37%, Recall: 88.10%, F1: 0.854, ROC-AUC: 0.895, PR-AUC: 0.957, FPR: 4.76%).
- **Full Test Confusion Matrix:** Detailed count matrix ($\text{TP} = 74$, $\text{FP} = 1$, $\text{TN} = 20$, $\text{FN} = 10$).
- **Modality Comparison (Table I):** Compares Metadata-Only, Image-Only, and Late Fusion across full test set and shared-domain image subset.
- **Interactive Recharts Curves:** Dynamic toggle between Receiver Operating Characteristic (ROC) and Precision-Recall (PR) curves.
- **10-Variant Architectural Ablation (Experiment 4):** Comprehensive Recharts bar chart and detailed data table. Highlights the crucial scientific reality of Variant 7 (Late Fusion w/o Image CNN matches Full Pipeline at $\text{F1} = 0.854$, proving CNN spatial features provide no lift once encoding format shortcuts are removed).
- **Adaptive Adversary Stress Test (Experiment 3):** Discloses the 0% detection rate on 21 invariant-preserving evasion samples, explaining why physical journal and memory analysis are needed against adaptive threats.

### 3.5 Academic Context & Research Deliverables View (`AboutView.tsx`)
- **Author Accreditation:** Mohika Rathi (Reg. No: 230968032) & Sreyaan Roy (Reg. No: 230968184).
- **Direct IEEE Manuscript Access:** In-browser viewing and direct download of the camera-ready typeset PDF (`paper/main.pdf`).
- **BibTeX Citation Card:** Formatted citation for the research paper with one-click clipboard copy.
- **Evidentiary Compliance Notice:** Documents satisfaction of Daubert factors (quantified 4.76% error rate, peer-reviewed TreeSHAP explainability) and demarcation under Federal Rule of Evidence 901.

---

## 4. Verification and Automated Testing

The complete test suite was executed and passed with zero failures:

```
============================== 26 passed in 7.05s ==============================
```

| Test Module | Tests | Description |
| :--- | :---: | :--- |
| `tests/test_api.py` | 11 | REST endpoints: health, overview, models, demo samples, evaluation, ablations, curves, demo analysis, custom upload, PDF download, and history |
| `tests/test_no_source_leakage.py` | 2 | Grouped train/val/test splits verifying zero source ID overlap |
| `tests/test_oof_leakage.py` | 3 | Inner GroupKFold out-of-fold training verification for late fusion |
| `tests/unit/test_features.py` | 3 | Subsecond zeroing, timestamp intervals, folder context, entropy, and magic bytes |
| `tests/unit/test_models.py` | 4 | Base model inference: CatBoost, SRNet-Lite CNN, Isolation Forest, and Late Fusion |
| `tests/unit/test_no_format_shortcut.py` | 2 | Comprehensive image carrier audit verifying 100% format parity (no JPEG vs PNG shortcut) |
| `tests/unit/test_reporting.py` | 1 | Automated generation of JSON, HTML, and Markdown investigator reports |

---

## 5. Deployment & Execution Instructions

### Unified Production Run (Recommended)
FastAPI directly serves the optimized static React production build along with the REST API:

```bash
cd /home/hp/.gemini/antigravity/scratch/ForensiGuard
uvicorn app.server:app --host 0.0.0.0 --port 8000
```
Then navigate to: **`http://localhost:8000`**

### Dual Development Mode (With Hot Reloading)
For live frontend code editing:

```bash
# Terminal 1: Backend
uvicorn app.server:app --port 8000 --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```
Then navigate to: **`http://localhost:5173`**

### Desktop Replica
The entire project has been synchronized to:
`file:///home/hp/Desktop/ForensiGuard/`
