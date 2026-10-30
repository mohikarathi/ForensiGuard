# ForensiGuard: Comprehensive Empirical Experiment Summary (Post-Audit)

**Date:** October 2026  
**Authors:** Mohika Rathi (230968032) & Sreyaan Roy (230968184)  
**Affiliation:** Department of Computer Science and Engineering, Manipal Institute of Technology (MAHE)  

---

## 1. Provenance & Artifacts Reference
- **Source Benchmark Manifest:** `data/benchmark/benchmark_manifest.csv`
- **Trained Model Checkpoints:**
  - Unsupervised Anomaly Scorer: `artifacts/models/anomaly_detector.joblib`
  - XGBoost Metadata Model: `artifacts/models/metadata_classifier.joblib`
  - PyTorch Noise-Residual CNN: `artifacts/models/image_cnn.pt`
  - Multimodal Late Fusion Engine: `artifacts/models/fusion_model.joblib`
  - Out-of-Fold Stacking Matrix: `artifacts/models/oof_fusion_train.csv`
- **Raw Experiment Output JSON:** `results/all_experiments_results.json`
- **Sample-Level Test Predictions Matrix:** `results/predictions_test.csv` (and `predictions_test.parquet`)
- **Grounded SHAP Forensic Case Studies:** `reports/shap_case_studies.json`
- **Benchmark Integrity Audit:** `reports/benchmark_audit_report.json`
- **Publication Figures:**
  - `paper/figures/fig1_roc_comparison.png`
  - `paper/figures/fig2_pr_comparison.png`
  - `paper/figures/fig3_confusion_matrix.png`
  - `paper/figures/fig4_ablation_study.png`
- **Publication LaTeX Tables:**
  - `paper/tables/table1_modality_comparison.tex`
  - `paper/tables/table2_ablation.tex`
- **Authoritative IEEE LaTeX Package:** `paper/main.tex`, `paper/IEEEtran.cls`, `paper/references.bib`
- **Supplementary Preview PDF:** `reports/ieee_report.pdf` (ReportLab preview)

---

## 2. Dataset Distribution & Leakage Verification
- **Total Generated Artifacts:** 812
- **Source Files Count:** 140
- **Partition Splitting Ratios (Source-Grouped):**
  - Training Partition: 566 artifacts (70% grouped sources, 98 unique source files)
  - Validation Partition: 120 artifacts (15% grouped sources, 21 unique source files)
  - Held-Out Testing Partition: 126 artifacts (15% grouped sources, 21 unique source files)
- **Class Breakdown:**
  - Timestomping: 280
  - Steganography: 168
  - Clean (Unaltered): 140
  - File-Type Obfuscation: 140
  - Compound (Timestomped + Stego): 84
- **Shortcut Elimination:** Standardized all clean and steganographic image carriers to identical uncompressed 8-bit grayscale PNGs ($128 \times 128$) with opaque hash-based filenames (`art_src_{id}_{hash}.png`), eliminating JPEG vs PNG container shortcuts.
- **Leakage Check Status:** PASSED (Strict zero source-level cross-partition overlap: $\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$, $\text{Val} \cap \text{Test} = \emptyset$).
- **Stacking Integrity:** Base models trained with 5-fold `GroupKFold` cross-validation on `source_file_id`; fusion meta-classifier trained exclusively on out-of-fold predictions.

---

## 3. Experiment 1: Modality Comparisons

| Architecture / Evaluation Scope | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | False Positive Rate | Sample Count (N) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Metadata-Only (Full Corpus)** | 0.627 | 0.983 | 0.562 | 0.715 | 0.770 | 0.927 | 0.048 | 126 |
| **Image-Only (Image Domain)** | 0.310 | 0.833 | 0.214 | 0.341 | 0.518 | 0.845 | 0.214 | 84 |
| **Metadata-Only (Shared Domain)** | 0.679 | 0.978 | 0.629 | 0.765 | 0.800 | 0.937 | 0.071 | 84 |
| **Image-Only (Shared Domain)** | 0.310 | 0.833 | 0.214 | 0.341 | 0.518 | 0.845 | 0.214 | 84 |
| **ForensiGuard Late Fusion (Shared)** | **0.679** | **0.978** | **0.629** | **0.765** | **0.799** | **0.959** | **0.071** | 84 |
| **ForensiGuard Late Fusion (Full Corpus)** | **0.786** | **0.988** | **0.752** | **0.854** | **0.895** | **0.977** | **0.048** | 126 |

### Confusion Matrix on Held-Out Test Set (Full Corpus, $\tau = 0.500$):
- **True Negatives (TN):** 20
- **False Positives (FP):** 1 (FPR = 4.76%)
- **False Negatives (FN):** 26 (pure steganography without metadata cues)
- **True Positives (TP):** 79

### Multi-Class Technique Attribution:
- **Overall 5-Class Exact Match Accuracy:** 65.08%
- **Conditional Accuracy on Manipulated Evidence ($y=1$):** 71.43%
- **Coarse Binary Attribution Accuracy (Benign vs. Manipulated):** 88.89%

---

## 4. Experiment 2: Manipulation Difficulty Analysis

| Subtype / Strength | Sample Count (N) | Recall | F1-Score | ROC-AUC | Detection Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Coarse Timestomping (Multi-year)** | 42 | 1.000 | 0.977 | 0.984 | Large $\Delta_{m,c}$, inverted chronology, zero subsecond precision |
| **Subtle Timestomping (2.5h shift)** | 42 | 1.000 | 0.977 | 0.984 | Zero subseconds, folder neighbor $z$-score deviation |
| **File-Type Obfuscation (Disguised PDF)** | 42 | 1.000 | 0.977 | 0.955 | Binary magic byte signature mismatch against declared extension |
| **Compound (Stego + Timestomp)** | 35 | 1.000 | 0.966 | 1.000 | Dual metadata temporal anomaly + spatial residual features |
| **Steganography Alone (Uncompressed LSB)** | 42 | 0.071 | 0.129 | 0.516 | Demonstrates genuine baseline difficulty of subtle spatial steganalysis |

---

## 5. Experiment 3: Robustness and Adaptive Attack Analysis
- **Adversary Strategy:** An informed attacker modifies file modification time by 3.5 hours, preserves realistic microsecond jitter ($0.482910\text{s}$), maintains chronological order ($mtime \ge ctime$), and bounds shift within $0.3\sigma$ of directory siblings.
- **Empirical Findings:**
  - **Isolated Metadata XGBoost Detector:** **0.0% Detection Rate** (mean probability: $0.0039$).
  - **Clean-Trained Isolation Forest:** Successfully detected anomaly ($S_{\text{anom}} = 0.596$), raising fusion probability to $0.216$.
  - **Late Fusion Decision ($\tau = 0.500$):** Below decision threshold, yielding **0.0% Detection Rate**.
- **Scientific Conclusion:** Static filesystem metadata alone cannot reliably catch an adversary who preserves filesystem invariants. Independent OS audit log correlation (e.g., Windows Event ID 4616) is strictly required for full forensic defense.

---

## 6. Experiment 4: Comprehensive 10-Variant Architectural Ablation ($N=126$)

| Variant | Accuracy | F1-Score | ROC-AUC | PR-AUC | False Positive Rate | Key Scientific Finding |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **1. Metadata-Only (Base Metadata)** | 0.627 | 0.715 | 0.770 | 0.927 | 0.048 | High precision on timestamps, blind to content tampering |
| **2. Image-Only (Full Corpus)** | 0.484 | 0.606 | 0.508 | 0.840 | 0.476 | Uncompressed grayscale spatial LSB near random guessing |
| **3. Metadata + Image Model** | 0.627 | 0.715 | 0.794 | 0.950 | 0.048 | Improves ranking AUC over pure metadata (+0.024 AUC) |
| **4. Metadata + Anomaly Score** | 0.627 | 0.715 | 0.770 | 0.927 | 0.048 | Injects unsupervised distribution prior |
| **5. Metadata + Signature Verification** | 0.786 | 0.854 | 0.861 | 0.956 | 0.048 | Drives primary discrete F1 jump (+13.9%) via header checking |
| **6. Full ForensiGuard Late Fusion** | **0.786** | **0.854** | **0.895** | **0.977** | **0.048** | Optimal overall ranking discriminability across all modalities |
| **7. Full Fusion w/o Image CNN** | 0.786 | 0.854 | 0.895 | 0.977 | 0.048 | Identical threshold F1; slightly higher Brier error (0.132 vs 0.125) |
| **8. Full Fusion w/o Folder Context** | 0.786 | 0.854 | 0.895 | 0.977 | 0.048 | Preserves threshold metrics; removes directory baseline |
| **9. Full Fusion w/o Anomaly Scoring** | 0.786 | 0.854 | 0.894 | 0.977 | 0.048 | Minor degradation in continuous ROC-AUC (0.894 vs 0.895) |
| **10. Full Fusion w/o Signature Check** | 0.627 | 0.715 | 0.744 | 0.945 | 0.048 | Critical drop: F1 collapses to 0.715, AUC drops to 0.744 |

---

## 7. Experiment 5: Domain & Subpopulation Breakdown
- **Document Domain (PDF artifacts, $N=21$):** Accuracy: 1.000, F1: 1.000, ROC-AUC: 1.000, FPR: 0.000.
- **Image Domain ($N=105$):** Accuracy: 0.743, F1: 0.828, ROC-AUC: 0.830, FPR: 0.071.
- **Modality Fallback Verification:** Non-image files gracefully mask missing image channels without producing spurious errors or high false alarm rates.

---

## 8. Grounded SHAP Forensic Case Studies (from `reports/shap_case_studies.json`)
1. **True Positive Coarse Timestomping (`art_src_0001_9817babc97.png`):**
   - Observations: $\Delta_{m,c} = -157,680,003$\,s (43,800.0 hours older than $ctime$), $\Delta_{a,m} = 0.00$\,s, Folder $z$-score $-20.0\sigma$.
   - Attributions: $\Delta_{m,c}$ SHAP = +5.026, $\Delta_{a,m}$ SHAP = +0.527, Folder $z$-score SHAP = +0.025.
   - Result: Metadata Probability = 0.995, Fusion Probability = 0.983 (TP).
2. **True Positive Subtle Timestomping (`art_src_0001_c0ac53e960.png`):**
   - Observations: $\Delta_{m,c} = -9,003$\,s (2.5h shift), Folder $z$-score $-5.14\sigma$.
   - Attributions: $\Delta_{m,c}$ SHAP = +5.026, $\Delta_{a,m}$ SHAP = +0.527, Folder $z$-score SHAP = +0.025.
   - Result: Metadata Probability = 0.995, Fusion Probability = 0.983 (TP).
3. **False Positive Clean Sample (`art_src_0092_d9f9fec154.png`):**
   - Observations: Synthetic generation write jitter caused $\Delta_{m,c} = -5.00$\,s.
   - Attributions: $\Delta_{m,c}$ pushed SHAP to +3.743 (suspicious direction), overcoming benign features.
   - Result: Metadata Probability = 0.952, Fusion Probability = 0.975 (FP, the sole false alarm in test set).
4. **False Negative Steganography Sample (`art_src_0001_84ea643005.png`):**
   - Observations: Timestamps completely unmanipulated ($\Delta_{m,c} = -2.73$\,s, natural chronology).
   - Attributions: $\Delta_{m,c}$ SHAP = -4.843 (strongly benign direction).
   - Result: Metadata Probability = 0.0037, Fusion Probability = 0.274 ($< \tau = 0.500$, FN).
5. **True Positive Compound Manipulation (`art_src_0001_913ec116a3.png`):**
   - Observations: $\Delta_{m,c} = -2,592,003$\,s (30 days backdated) + spatial LSB steganography.
   - Attributions: $\Delta_{m,c}$ SHAP = +5.026, $\Delta_{a,m}$ SHAP = +0.527.
   - Result: Metadata Probability = 0.995, Fusion Probability = 0.983 (TP).
