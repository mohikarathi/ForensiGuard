# ForensiGuard: Final Pre-Submission Validation & Quality Audit Report

**Project Title:** ForensiGuard: A Multimodal Machine-Learning Framework for Detecting, Attributing and Explaining Anti-Forensic Manipulation of Digital Evidence  
**Author:** Mohika Rathi (Registration No: `230968032`)  
**Institution:** Manipal Institute of Technology, Manipal Academy of Higher Education (MAHE), Manipal, India  
**Date of Validation:** October 24, 2026  
**Auditor / Environment:** Linux x86_64, Python 3.13.5 (Conda environment)

---

## 1. Executive Summary & Verification Matrix

This audit confirms that all mandatory submission requirements prescribed by the academic department have been fulfilled, empirically validated, and packaged without shortcuts, data leakage, or fabricated metrics.

| Requirement | Prescribed Deliverable | Verified Artifact Path | Validation Status |
| :--- | :--- | :--- | :---: |
| **Req 1: Project Report** | Prepared using institutional template (`Template.docx`), complete 16 chapters, abstract, TOC, figures, tables | `Project_Report.docx`<br>`results_and_figures/Project_Report.pdf` | **VERIFIED** (28 pages, all 16 chapters populated, TOC page numbers synchronized) |
| **Req 2: Dataset Source** | Dataset provenance, generation procedure, split specifications, and formal citation | `DATASET_SOURCE.md`<br>`data/benchmark/benchmark_manifest.csv` | **VERIFIED** (812 artifacts, 140 sources, format-matched carriers, zero source leakage) |
| **Req 3: Runnable Code** | Portable package, dependencies, pre-trained checkpoints, test suite, and evaluation script | `src/forensiguard/`<br>`artifacts/models/`<br>`tests/`<br>`requirements.txt` | **VERIFIED** (26/26 tests passing, exit code 0; relative paths enforced) |
| **Req 4: Saved Results & Figures** | Canonical quantitative JSON, test prediction matrix, format audit report, all publication figures | `results_and_figures/`<br>`results/all_experiments_results.json`<br>`results/predictions_test.csv` | **VERIFIED** (F1: 0.854, ROC-AUC: 0.895, FPR: 4.76%, all 6 figures verified) |
| **Req 5: Short README** | Novelty statement, provenance, reproduction command, demo guide, limitations, structure | `README.md` | **VERIFIED** (Honest scientific claims, explicit distinction from engineering) |
| **Package: Archive** | Complete submission directory and verified zip archive | `ForensiGuard_Mini_Project_Submission/`<br>`ForensiGuard_Mini_Project_Submission.zip` | **VERIFIED** (Archive tested with `zip -T`, cleanly unpacks) |

---

## 2. Experimental Execution & Reproduction Log

Every quantitative metric reported in the project report and research paper was reproduced by executing the codebase against the held-out test split ($N = 126$ artifacts, 21 unseen source groups).

### 2.1. Canonical Metric Reproduction
- **Execution Command:**
  ```bash
  /home/hp/anaconda3/bin/python scripts/evaluate.py
  ```
- **Exit Code:** `0` (Success)
- **Execution Time:** 7.4 seconds
- **Reproduced Output:**
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

### 2.2. Automated Test Suite Execution
- **Execution Command:**
  ```bash
  pytest tests/ -v
  ```
- **Exit Code:** `0` (Success)
- **Execution Time:** 9.23 seconds
- **Summary:** 26 passed, 0 failed, 0 warnings
- **Detailed Test Breakdown:**
  - `tests/test_api.py::test_health_endpoint` **PASSED**
  - `tests/test_api.py::test_overview_endpoint` **PASSED**
  - `tests/test_api.py::test_models_endpoint` **PASSED**
  - `tests/test_api.py::test_demo_samples_endpoint` **PASSED**
  - `tests/test_api.py::test_evaluation_summary_endpoint` **PASSED**
  - `tests/test_api.py::test_evaluation_ablations_endpoint` **PASSED**
  - `tests/test_api.py::test_evaluation_curves_endpoint` **PASSED**
  - `tests/test_api.py::test_analyze_demo_sample` **PASSED**
  - `tests/test_api.py::test_analyze_custom_file_upload` **PASSED**
  - `tests/test_api.py::test_paper_pdf_and_bib_endpoints` **PASSED**
  - `tests/test_api.py::test_analyses_history_and_clear` **PASSED**
  - `tests/test_no_source_leakage.py::test_no_source_file_overlap` **PASSED**
  - `tests/test_no_source_leakage.py::test_stratification_properties` **PASSED**
  - `tests/test_oof_leakage.py::test_oof_training_file_exists` **PASSED**
  - `tests/test_oof_leakage.py::test_oof_predictions_clean_leak_free` **PASSED**
  - `tests/test_oof_leakage.py::test_inner_stacking_group_disjoint` **PASSED**
  - `tests/unit/test_features.py::test_metadata_features_extractable` **PASSED**
  - `tests/unit/test_features.py::test_image_byte_statistics` **PASSED**
  - `tests/unit/test_features.py::test_magic_signature_verification` **PASSED**
  - `tests/unit/test_models.py::test_metadata_anomaly_detector` **PASSED**
  - `tests/unit/test_models.py::test_metadata_classifier` **PASSED**
  - `tests/unit/test_models.py::test_image_cnn_forward` **PASSED**
  - `tests/unit/test_models.py::test_late_fusion_meta_classifier` **PASSED**
  - `tests/unit/test_no_format_shortcut.py::test_no_format_leakage_in_benchmark` **PASSED**
  - `tests/unit/test_no_format_shortcut.py::test_comprehensive_benchmark_integrity` **PASSED**
  - `tests/unit/test_reporting.py::test_generate_investigator_report` **PASSED**

### 2.3. CLI Evidence Triage Inference
- **Execution Command:**
  ```bash
  python -m forensiguard.cli analyze data/benchmark/artifacts/folder_case_00/art_src_0000_47b0d1ab5f.png --out-dir reports/
  ```
- **Exit Code:** `0` (Success)
- **Triage Decision:** Tampered (Timestomping, Probability: 93.10%, Confidence: 89.49%)
- **Generated Reports:**
  - `reports/forensic_report_art_src_0000_47b0d1ab5f.md` (Markdown)
  - `reports/forensic_report_art_src_0000_47b0d1ab5f.html` (Interactive HTML)
  - `reports/forensic_report_art_src_0000_47b0d1ab5f.json` (Machine-readable JSON)
  - `reports/forensic_report_art_src_0000_47b0d1ab5f.pdf` (Court-ready PDF report)

### 2.4. Interactive Web Server Endpoints
- **Server Launch:** `uvicorn app.server:app --port 8000`
- **Endpoints Verified:**
  - `GET /api/v1/health` -> HTTP 200 OK (`{"status": "healthy"}`)
  - `GET /api/v1/evaluation/summary` -> HTTP 200 OK (`{"f1": 0.854, "roc_auc": 0.895}`)
  - `GET /api/v1/evaluation/ablations` -> HTTP 200 OK (all 10 variants returned)
  - `GET /api/v1/demo-samples` -> HTTP 200 OK (8 curated benchmark artifacts)
  - `POST /api/v1/analyze/sample` -> HTTP 200 OK (TreeSHAP attributions and triage decision)
  - `GET /` -> HTTP 200 OK (Compiled React single-page application served via static assets)

---

## 3. Cross-Artifact Metric Synchronization Audit

All numerical claims across the project report (`Project_Report.docx`), the IEEE conference paper (`paper/main.tex` / `paper/main.pdf`), the canonical results JSON (`results/all_experiments_results.json`), and the test predictions matrix (`results/predictions_test.csv`) were audited for absolute consistency.

| Metric Description | Canonical Results JSON | Project Report (DOCX & PDF) | IEEE Paper (`main.tex`) | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Late Fusion Accuracy (Full Corpus)** | 78.57% (99/126) | 78.57% (Chapter 10, Table 5) | 78.57% (Section V, Table I) | **SYNCHRONIZED** |
| **Late Fusion F1-Score** | 0.854 | 0.854 (Chapter 10, Table 5) | 0.854 (Section V, Table I) | **SYNCHRONIZED** |
| **Late Fusion ROC-AUC** | 0.895 | 0.895 (Chapter 10, Table 5) | 0.895 (Section V, Table I) | **SYNCHRONIZED** |
| **Late Fusion PR-AUC** | 0.977 | 0.977 (Chapter 10, Table 5) | 0.977 (Section V, Table I) | **SYNCHRONIZED** |
| **False Positive Rate (FPR)** | 4.76% (1/21 clean false alarm) | 4.76% (Chapter 10, Table 5) | 4.76% (Section V, Table I) | **SYNCHRONIZED** |
| **Decision Threshold ($\tau^*$)** | 0.500 | 0.500 (Chapter 9, Table 4) | 0.500 (Section IV-C) | **SYNCHRONIZED** |
| **Metadata-Only F1-Score** | 0.715 | 0.715 (Chapter 10, Table 5) | 0.715 (Section V, Table I) | **SYNCHRONIZED** |
| **Image-Only (Domain) F1-Score** | 0.341 | 0.341 (Chapter 10, Table 5) | 0.341 (Section V, Table I) | **SYNCHRONIZED** |
| **Image-Only (Domain) ROC-AUC** | 0.518 | 0.518 (Chapter 10, Table 5) | 0.518 (Section V, Table I) | **SYNCHRONIZED** |
| **Technique Attribution Accuracy** | 65.08% (82/126) | 65.08% (Chapter 10, Section 10.2) | 65.08% (Section V-B) | **SYNCHRONIZED** |
| **Conditional Attribution Accuracy** | 71.43% (75/105) | 71.43% (Chapter 10, Section 10.2) | 71.43% (Section V-B) | **SYNCHRONIZED** |
| **Adaptive Evasion Detection Rate** | 0.00% (Mean prob: 0.216) | 0.00% (Chapter 10, Table 7) | 0.00% (Section V-C, Table III) | **SYNCHRONIZED** |
| **Ablation Variant 7 (No CNN) F1** | 0.854 | 0.854 (Chapter 10, Table 6) | 0.854 (Section V-D, Table II) | **SYNCHRONIZED** |

---

## 4. Academic Integrity & Anti-Shortcut Verification

1. **Absence of Container Shortcuts:** In initial iterations of the project, clean carriers were saved as JPEGs while steganographically altered carriers were saved as PNGs, creating an artificial shortcut that allowed naive CNNs to claim $>95\%$ accuracy. In `ForensiGuard-Bench-v1`, **100% of all image carriers are standardized to uncompressed grayscale PNG format**. The format audit confirmed:
   - Zero correlation between carrier format and manipulation label ($p = 1.0$).
   - Uniform dimensions ($512 \times 512$ pixels) and single-channel grayscale across both clean and tampered samples.
2. **Absence of Source Leakage:** The 812 benchmark artifacts stem from 140 unique parent evidence files. Grouped splitting (`GroupKFold` on `source_file_id`) guarantees that:
   - Train split (98 sources), Validation split (21 sources), and Test split (21 sources) share **zero** overlapping sources.
   - Inner stacking folds for meta-classifier training strictly partition sources across folds, ensuring out-of-fold predictions represent genuine generalization.
3. **Transparent Scientific Reporting:** The report does not conceal negative findings. The empirical result showing that spatial residual CNNs achieve near-chance performance ($\text{ROC-AUC} = 0.518$) on format-matched carriers and that static metadata models fail ($0\%$ detection) against invariant-preserving adaptive timestomping are highlighted as core scientific insights regarding the necessity of multimodal correlation and external OS journal auditing.

---

## 5. Deliverable Packaging Verification

The complete submission package is assembled in `ForensiGuard_Mini_Project_Submission/` and compressed to `ForensiGuard_Mini_Project_Submission.zip`:

- **Archive Test Command:**
  ```bash
  zip -T ForensiGuard_Mini_Project_Submission.zip
  ```
- **Archive Verification Status:** `test of ForensiGuard_Mini_Project_Submission.zip OK`
- **Archive Size:** ~16 MB (including complete dataset, model checkpoints, compiled reports, frontend dist, and source code).

---

## 6. Student Action Items for Final Submission

Prior to uploading to the university evaluation portal:

1. **Institutional Similarity Check (Turnitin / iThenticate):**
   - Upload `Project_Report.docx` (or the accompanying `results_and_figures/Project_Report.pdf`) to your institutional Turnitin / iThenticate student submission portal.
   - Download the official digital similarity receipt showing the percentage similarity score (expected $< 10\%$).
   - Note the submission ID and date in Chapter 16 of the report.
2. **Portal Upload Checklist:**
   - [x] Primary Report: `Project_Report.docx`
   - [x] Supplementary PDF Report: `results_and_figures/Project_Report.pdf`
   - [x] Dataset Provenance Guide: `DATASET_SOURCE.md`
   - [x] Complete Runnable Zip: `ForensiGuard_Mini_Project_Submission.zip`
   - [x] Supplementary IEEE Conference Paper: `paper/main.pdf`

---
*Report generated and validated automatically on October 24, 2026.*
