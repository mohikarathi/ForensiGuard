# ForensiGuard: A Multimodal Machine-Learning Framework for Detecting, Attributing and Explaining Anti-Forensic Manipulation of Digital Evidence

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://forensi1guard.streamlit.app)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Tests Status](https://img.shields.io/badge/tests-26%20passed-brightgreen.svg)]()
[![Forensic Benchmark](https://img.shields.io/badge/benchmark-812%20artifacts-blueviolet.svg)](DATASET_SOURCE.md)
[![Academic Evaluation](https://img.shields.io/badge/Late%20Fusion%20F1-0.854-success.svg)]()
[![ROC-AUC](https://img.shields.io/badge/ROC--AUC-0.895-success.svg)]()

> **Live Interactive Cloud Demo:** [https://forensi1guard.streamlit.app](https://forensi1guard.streamlit.app)  
> **GitHub Repository:** [https://github.com/mohikarathi/ForensiGuard](https://github.com/mohikarathi/ForensiGuard)

---

### Academic Information & Authors
- **Student Authors:**
  - Mohika Rathi (Registration No: 230968032)
  - Sreyaan Roy (Registration No: 230968184)
- **Institution:** Manipal Academy of Higher Education
- **Branch:** Data Science
- **Subject:** Data Forensics
- **Project:** ForensiGuard
- **Live Demo Dashboard:** [https://forensi1guard.streamlit.app](https://forensi1guard.streamlit.app)
- **GitHub Repository:** [https://github.com/mohikarathi/ForensiGuard](https://github.com/mohikarathi/ForensiGuard)

---

## 1. Problem Overview & Approach

Digital forensics relies on the fundamental presumption that acquired electronic artifacts reflect historical system activity without deliberate post-incident alteration. Anti-forensic techniques—such as **filesystem timestomping**, **covert steganography**, and **extension/file-type obfuscation**—undermine this evidentiary foundation.

Existing forensic tools suffer from three fundamental limitations:
1. **Unimodal Brittleness:** Single-signal detectors inspect artifacts in isolation. A forged timestamp may leave statistical traces in high-frequency pixel residuals or binary magic bytes, and vice versa.
2. **Benchmark Data Leakage & Shortcut Learning:** Conventional studies frequently permit data leakage across source files or introduce container shortcuts (e.g., saving clean images as JPEG and stego images as PNG), inflating reported performance.
3. **Black-Box Inadmissibility:** Machine-learning inferences must withstand rigorous scrutiny under legal standards (*Daubert* and *Frye* standards, Federal Rule of Evidence 901).

**ForensiGuard** addresses these challenges through a unified multimodal architecture:
- **Filesystem Metadata Detection:** MACB timestamp intervals, zero-subsecond truncation checks, folder context $z$-scores, and an unsupervised clean-trained Isolation Forest anomaly scorer feeding a gradient-boosted decision tree (**XGBoost**).
- **Spatial Steganalysis:** Spatial Rich Model (SRM) high-pass noise-residual filtering coupled with a deep residual convolutional network (**SRNet-Lite**), evaluated on format-standardized carriers without container shortcuts.
- **Binary Signature Verification:** Header magic byte extraction vs. declared extension inspection and Shannon entropy analysis.
- **Calibrated Multimodal Late Fusion:** A stacked meta-classifier trained via **GroupKFold out-of-fold (OOF)** stacking on source file groups, preventing data leakage.
- **Investigator-Facing Explainability:** Exact **TreeSHAP** feature attributions translated into automated forensic triage reports (Markdown, HTML, JSON, and PDF).

---

## 2. Novelty and Scientific Contributions

It is vital to distinguish between standard engineering integration and the genuine scientific contributions of this work:

### Genuine Scientific & Methodological Novelty
1. **Source-Grouped Leakage-Free Out-of-Fold Stacking:** Rather than training late fusion on standard $k$-fold splits that leak related files from the same disk image, ForensiGuard implements strict source-grouped cross-validation (`GroupKFold` on `source_file_id`). Inner base models predict exclusively on unseen evidence sources, producing honest calibration.
2. **Empirical Shortcut Remediation & Negative Finding:** By standardizing all image carriers to uncompressed grayscale PNGs, ForensiGuard eliminates container format shortcuts (e.g., JPEG vs. PNG label leakage). The subsequent empirical finding—that the image CNN achieves only $\text{ROC-AUC} = 0.518$ and that removing the CNN preserves overall fusion performance ($\text{F1} = 0.854$, $\text{ROC-AUC} = 0.895$)—is a rigorous scientific negative result demonstrating that subtle spatial steganography cannot be trivially solved by off-the-shelf CNNs on clean format-matched carriers.
3. **Dual Unsupervised-Supervised Temporal Modeling:** Coupling an unsupervised Isolation Forest trained solely on benign baseline filesystem distributions with supervised tree boosting allows the model to flag out-of-distribution timestamp patterns without requiring pre-labeled training examples of novel evasion techniques.
4. **Legally Grounded Forensic Explainability:** Unlike black-box models, ForensiGuard maps local Shapley attributions directly to forensic rules and statutory requirements (*Daubert*, Federal Rule of Evidence 901), producing natural-language audit narratives for court defense.

### Engineering & System Integration
- An end-to-end Python package (`forensiguard`) with CLI commands (`generate-benchmark`, `train-and-evaluate`, `analyze`).
- Multi-format forensic reporting engine generating Markdown, HTML, JSON, and PDF reports.
- Full-stack interactive demonstration web application featuring FastAPI and React with interactive TreeSHAP waterfall charts and Recharts evaluation curves.

---

## 3. Dataset Source, Provenance & Citation

The experimental benchmark used throughout this project is **`ForensiGuard-Bench-v1`**, a standardized, leak-free digital forensics corpus engineered specifically to evaluate multi-modal anti-forensic triage without container-format shortcuts or identity leakage.

### Dataset Access & Manifest Links
- **Dataset Manifest:** [`data/benchmark/benchmark_manifest.csv`](data/benchmark/benchmark_manifest.csv) *(Complete ground-truth catalog of all 812 artifacts)*
- **Artifacts Directory:** [`data/benchmark/artifacts/`](data/benchmark/artifacts/) *(Curated forensic test cases organized by folder and source)*
- **Authoritative Provenance Document:** [`DATASET_SOURCE.md`](DATASET_SOURCE.md) *(Detailed generation algorithms, parameters, and schema specification)*

### Dataset Origin & Construction
The benchmark was synthesized from **140 authentic, unmanipulated source carrier files** across multiple data modalities:
- **Image Carriers:** Format-standardized grayscale PNG images ($128 \times 128$) to eliminate container-label shortcuts (e.g. clean JPEG vs stego PNG).
- **Text & Document Carriers:** Plain-text documents (`.txt`), structured logs (`.log`), shell scripts (`.sh`), Python source code (`.py`), and system configuration files (`.ini`, `.yaml`).

From each pristine carrier, deterministic anti-forensic mutations were generated using POSIX Linux system interfaces (`os.utime`, `stat`), PIL, and open-source steganographic encoders across 5 manipulation classes:
1. `clean`: Pristine baseline carriers with intact filesystem timestamps and valid container magic bytes.
2. `timestomping`: Backward and forward modification shifts (coarse multi-year and subtle sub-day shifts) with zeroed microsecond precision.
3. `steganography`: Spatial LSB embedding across payload rates $\alpha \in [0.08, 0.35]$ bits per pixel without container leakage.
4. `extension_mismatch`: File-type obfuscation where declared extensions contradict binary magic-byte signatures.
5. `compound`: Synchronized dual-vector tampering (e.g., spatial stego payload combined with timestamp rollback).

### Partition Breakdown & Zero Source Leakage
All artifacts are strictly partitioned by `source_file_id` (70% Train, 15% Validation, 15% Test) to guarantee that no evidence artifact derived from a test carrier ever appears during model training:

| Partition | Source Groups | Artifact Count | Clean Artifacts | Manipulated Artifacts | Primary Role |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Train** | 98 sources (70%) | 568 artifacts | 98 (17.3%) | 470 (82.7%) | Base model & OOF stacked fusion training |
| **Validation** | 21 sources (15%) | 118 artifacts | 21 (17.8%) | 97 (82.2%) | Threshold calibration ($\tau = 0.500$) |
| **Held-Out Test** | 21 sources (15%) | 126 artifacts | 21 (16.7%) | 105 (83.3%) | Final blind performance evaluation |
| **Total** | **140 sources** | **812 artifacts** | **140 (17.2%)** | **672 (82.8%)** | Full benchmark corpus |

### Dataset Schema
The ground-truth manifest ([`data/benchmark/benchmark_manifest.csv`](data/benchmark/benchmark_manifest.csv)) defines the following schema:
- `artifact_id`: Unique deterministic identifier (e.g., `art_src_0001_aa1163a6cf`).
- `source_file_id`: Identifier of the source file family to ensure grouped isolation.
- `filename` / `file_path`: Relative disk location of the physical artifact.
- `label`: Binary classification target (`0 = clean`, `1 = manipulated`).
- `manipulation_technique`: Categorical attribution (`clean`, `timestomping`, `steganography`, `extension_mismatch`, `compound`).
- `subtype`: Granular attack parameters (e.g., `coarse_multiyear`, `subtle_2h`, `high_payload_0.35`).
- `split`: Pre-assigned partition assignment (`train`, `val`, `test`).
- `file_size_bytes` & `declared_extension`: Physical container metadata.

### Formal Dataset Citation
To cite `ForensiGuard-Bench-v1` in research publications and academic reports:

```bibtex
@misc{rathi2026forensiguard_bench,
  author       = {Mohika Rathi and Sreyaan Roy},
  title        = {{ForensiGuard-Bench-v1: Standardized Multimodal Digital Evidence Anti-Forensic Benchmark}},
  year         = {2026},
  month        = {October},
  howpublished = {Project Repository and Academic Benchmark Suite, Branch: Data Science, Subject: Data Forensics},
  note         = {Controlled synthetic benchmark of 812 forensic artifacts across 140 source groups with zero source leakage and format-shortcut remediation}
}
```

*M. Rathi and S. Roy, "ForensiGuard-Bench-v1: Standardized Multimodal Digital Evidence Anti-Forensic Benchmark," Data Forensics Benchmark Suite, Branch: Data Science, Dec. 2026.*

---

## 4. Quickstart & Installation

### Prerequisites
- Linux, macOS, or Windows WSL
- Python 3.10+ (tested and verified on Python 3.13)

### Environment Setup
```bash
# Clone or navigate to the repository directory
cd ForensiGuard

# Install dependencies
pip install -r requirements.txt

# Install the forensiguard package in editable mode
pip install --no-deps -e .
```

---

## 5. How to Reproduce the Main Results

A single command reproduces the canonical evaluation results across all 126 held-out test artifacts in under 10 seconds:

```bash
python scripts/evaluate.py
```

*(Note: To retrain all models from scratch before evaluation, pass the `--retrain` flag: `python scripts/evaluate.py --retrain`.)*

### Expected Canonical Output Metrics
```
======================================================================
CANONICAL EXPERIMENTAL EVALUATION RESULTS (N = 126 test artifacts)
======================================================================
Architecture                        | Acc     | F1      | ROC-AUC | FPR    
----------------------------------------------------------------------
Metadata-Only (Full Corpus)         | 62.70% | 0.715 |   0.770 |  4.76%
Image-Only (Intended Domain)        | 30.95% | 0.341 |   0.518 | 21.43%
ForensiGuard Late Fusion (Full)     | 78.57% | 0.854 |   0.895 |  4.76%
----------------------------------------------------------------------
Decision Threshold:          tau* = 0.500
Technique Attribution Acc:   65.08% (82/126 exact 5-class match)
Conditional Attribution:     71.43% (75/105 tampered artifacts)
Adaptive Evasion Detection:  0.00% (Mean score: 0.216)
Ablation Check (No CNN):     F1 = 0.854 | ROC-AUC = 0.895
Results Saved To:            results/all_experiments_results.json
======================================================================
```

All metrics, prediction CSVs, and figures are saved to:
- Quantitative metrics: [`results/all_experiments_results.json`](results/all_experiments_results.json)
- Per-sample test predictions: [`results/predictions_test.csv`](results/predictions_test.csv)
- Curated deliverable bundle: [`results_and_figures/`](results_and_figures/)

---

## 6. How to Run & Deploy the Interactive Demos

ForensiGuard offers two interactive forensic triage interfaces:

### Option A: Streamlit Dashboard (Live Cloud Deployment & Local)

- **Live Cloud Demo:** **[https://forensi1guard.streamlit.app](https://forensi1guard.streamlit.app)** *(Instant browser access, zero local installation required)*

Run locally:
```bash
streamlit run streamlit_app.py
```
Open **`http://localhost:8501`** in your browser.

#### Deploy to Streamlit Community Cloud:
1. Fork or push to GitHub (`https://github.com/mohikarathi/ForensiGuard`).
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Connect the repository, set main file path to `streamlit_app.py`, and click **Deploy**.

---

### Option B: FastAPI + React Evidence Inspector

Run locally:
```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser.

#### Features:
- **Active Evidence Triage:** Drag-and-drop suspect files up to 25 MB with instantaneous hash computation, MIME extraction, and metadata scoring.
- **Benchmark Sample Selector:** Test against curated benchmark artifacts covering clean files, timestomping, steganography, extension mismatches, and adaptive evasion.
- **TreeSHAP Explainability:** Game-theoretic feature attributions detailing the exact signals driving the prediction.
- **Interactive Benchmarks:** Live ROC/PR curves, confusion matrix, and 10-variant ablation comparisons.

---

## 7. Honest Scientific Limitations

In accordance with rigorous academic integrity, this project explicitly documents its empirical boundaries:

1. **Weak Image-Only Baseline ($\text{ROC-AUC} = 0.518$):** When image containers are format-standardized to uncompressed PNGs, standard spatial residual CNNs cannot reliably detect low-density LSB steganography without extensive domain-specific pre-training.
2. **CNN Ablation Equality:** Ablation Variant 7 (Late Fusion without CNN) achieves identical performance ($\text{F1} = 0.854$, $\text{ROC-AUC} = 0.895$) to Variant 6 (Full Pipeline). The fusion model correctly down-weights the noisy CNN output.
3. **Vulnerability to Invariant-Preserving Adaptive Timestomping ($0\%$ Detection):** In Experiment 3, an adaptive evasion attack that shifts modification timestamps by 3.5 hours while preserving chronological ordering ($mtime \ge ctime$) and subsecond microsecond noise completely evades static metadata models (mean score $0.216$). Static metadata inspection is insufficient against disciplined adversaries without correlating external OS audit logs (e.g., Windows Event ID 4616).
4. **Synthetic Benchmark Scope:** `ForensiGuard-Bench-v1` is an isolated forensic benchmark. Performance on raw, dirty, uncurated enterprise disk images (with multi-year filesystem churn) remains subject to future investigation.

---

## 8. Verification & Test Suite

The test suite validates data leakage guards, format shortcut checks, model contracts, feature extractors, reporting engines, and REST endpoints:

```bash
pytest tests/ -v
```

All 26 tests pass with exit code 0:
- `tests/test_api.py` (11 tests): Endpoints, schema validation, report downloads, upload triage.
- `tests/test_no_source_leakage.py` (2 tests): Verifies zero source file overlap across dataset partitions.
- `tests/test_oof_leakage.py` (3 tests): Verifies inner cross-validation folds strictly enforce group independence.
- `tests/unit/test_features.py` (3 tests): Feature extraction correctness for timestamps, entropy, and signatures.
- `tests/unit/test_models.py` (4 tests): Verifies model training, inference, and serialization contracts.
- `tests/unit/test_no_format_shortcut.py` (2 tests): Comprehensive audit of image carriers for format-label leakage.
- `tests/unit/test_reporting.py` (1 test): Report formatting across Markdown, HTML, and JSON.

---

## 9. Project Directory Structure

```
ForensiGuard/
├── DATASET_SOURCE.md           # Dataset Provenance, Schema & Citation
├── README.md                   # This comprehensive project documentation
├── requirements.txt            # Python dependencies
├── pyproject.toml              # Build system configuration
│
├── results_and_figures/        # Saved experimental artifacts & plots
│   ├── all_experiments_results.json    # Canonical quantitative metrics
│   ├── predictions_test.csv            # Per-artifact model prediction outputs
│   ├── benchmark_audit_report.json     # Format shortcut audit report
│   ├── fig0_architecture.png          # System architecture diagram
│   ├── fig1_roc_comparison.png         # Modality ROC curves
│   ├── fig2_pr_comparison.png          # Modality PR curves
│   ├── fig3_confusion_matrix.png       # 5-class confusion matrix
│   ├── fig4_ablation_study.png         # 10-variant ablation bar chart
│   └── fig_modality_comparison_bar.png # Modality comparison bar chart
│
├── src/forensiguard/           # Core Python package
│   ├── data/                           # Ingestion, schema, benchmark generator
│   ├── features/                       # Metadata, image, and binary feature extractors
│   ├── models/                         # IsolationForest, XGBoost, SRNet-Lite CNN, Late Fusion
│   ├── explainability/                 # TreeSHAP explainer & narrative triage engine
│   ├── reporting/                      # Multi-format report generator (MD, HTML, JSON, PDF)
│   ├── evaluation/                     # Leakage-free experiment runner & metrics
│   └── cli.py                          # Unified command-line interface
│
├── app/                        # FastAPI REST API Backend
│   └── server.py                       # REST API endpoints & static asset serving
│
├── frontend/                   # Interactive React Demonstration Web Application
│   ├── dist/                           # Production compiled static bundle (served by FastAPI)
│   ├── src/                            # React / TypeScript source code
│   └── package.json                    # Frontend package dependencies
│
├── configs/                    # Default configuration YAML
│   └── default.yaml
│
├── scripts/                    # Runnable execution & reproduction scripts
│   ├── evaluate.py                     # Single-command evaluation & metric reproduction
│   ├── generate_architecture_diagram.py # Architecture figure generator
│   └── generate_benchmark.py           # Benchmark generation entrypoint
│
├── tests/                      # Automated pytest validation suite (26 passing tests)
│   ├── test_api.py
│   ├── test_no_source_leakage.py
│   ├── test_oof_leakage.py
│   └── unit/
│
├── data/benchmark/             # Forensic benchmark (812 artifacts, 140 sources)
│   ├── benchmark_manifest.csv          # Ground-truth partition manifest
│   └── artifacts/                      # Evidence artifacts by folder case
│
└── artifacts/models/           # Pre-trained, serialized model checkpoints
    ├── anomaly_detector.joblib
    ├── metadata_classifier.joblib
    ├── image_cnn.pt
    ├── fusion_model.joblib
    └── oof_fusion_train.csv
```
