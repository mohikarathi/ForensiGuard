# ForensiGuard: IEEE LaTeX Build Validation & Quality Report

**Date of Validation:** October 21, 2026  
**Document Source:** `paper/main.tex`  
**Compiled Document:** `paper/main.pdf`  
**Document Class:** `\documentclass[conference]{IEEEtran}`  
**Compiler Used:** Tectonic 0.17.0 (XeTeX-based standalone TeX engine)  
**Authors:** Mohika Rathi (Registration No. 230968032), Sreyaan Roy (Registration No. 230968184)  

---

## 1. Build Execution & Toolchain Verification

The paper was compiled directly from the authoritative LaTeX source using the following command:
```bash
tectonic paper/main.tex
```

### Build Outcome
- **Exit Code:** `0` (Successful Clean Build)
- **PDF Size:** 974.5 KiB (`997,935 bytes`)
- **Page Count:** 8 pages
- **Page Dimensions:** US Letter ($8.5 \times 11$ inches, $612 \times 792$ points)
- **Layout:** Standard IEEE two-column format (3.5-inch column width, 0.25-inch inter-column gutter)
- **BibTeX Processing:** Fully resolved via `IEEEtran.bst` with 14 verified bibliography entries from `paper/references.bib`
- **Pass Convergence:** 3 TeX passes automatically executed to resolve all citations, equation numbers, figure numbers, and table references.

---

## 2. Warning & Diagnostic Audit

| Warning Type | Occurrences | Severity | Status / Resolution |
| :--- | :---: | :---: | :--- |
| **Undefined Citations (`\cite`)** | 0 | None | All 14 citations successfully resolved. |
| **Undefined References (`\ref`)** | 0 | None | All figure, table, and equation references resolved. |
| **Overfull `\hbox` (Text Overflow)** | 0 | None | **Zero overfull text boxes.** All equations and tables fit strictly within the 3.5-inch column width. |
| **Overfull `\vbox` (Vertical Overflow)**| 0 | None | Zero vertical overflow errors. |
| **Underfull `\hbox` / `\vbox`** | Minor | Low | Natural TeX inter-word spacing and column balancing. No visual distortion. |
| **Missing Fonts / Glyphs** | 0 | None | Standard Computer Modern and Latin Modern font outlines fully embedded. |
| **Package Warnings** | 1 | Low | `algorithmic.sty` line 11 non-ASCII author character warning (cosmetic comment in third-party package). |

---

## 3. Visual & Structural Inspection (Page by Page)

Every page was rendered to high-resolution PNG (`paper/rendered_pages/page-*.png`) and inspected:

1. **Page 1:**
   - Centered Paper Title in standard 24pt bold type.
   - Dual-author block featuring Mohika Rathi on the left and Sreyaan Roy on the right (horizontal left-to-right ordering) with student registration numbers only. No address or department strings. Line wrapping defects eliminated; no invented email addresses, ORCID IDs, or funding notes.
   - Abstract in a single self-contained paragraph ($< 250$ words) without citations or undefined abbreviations.
   - `IEEEkeywords` block with 5 selected keywords.
   - Two-column body beginning with **Section I: Introduction** and Roman-numbered headings.
   - Clear enumeration of the five core project contributions.
2. **Page 2:**
   - Continuation of contributions list.
   - **Section II: Related Work** organized into six thematic subsections (A through F) with numbered square-bracket citations (`[1]` to `[13]`).
   - Clean column balance without orphan headings.
3. **Page 3:**
   - **Section III: Problem Formulation and Threat Model** with numbered equations (Eq. 1 to Eq. 3) defining detection and attribution spaces.
   - Detailed adversary threat models ($T_1$ to $T_4$, $T_{\text{adapt}}$) and forensic demarcation.
   - **Section IV: Proposed Methodology** (Subsections A through C) with temporal difference equations (Eq. 4), chronology inversion (Eq. 5), subsecond flags (Eq. 6--7), and directory $z$-score (Eq. 8).
4. **Page 4:**
   - Full-width architectural pipeline diagram (**Fig. 1**) spanning both columns at the top of the page, illustrating evidence ingest, three modality extractors, grouped late fusion, and triage reporting.
   - Subsection D (Image-Based Detection) with Ker-Vannier $5 \times 5$ filter matrix (Eq. 9).
   - Subsection E (Anomaly Scoring and Signature Verification) with Isolation Forest probability (Eq. 10).
   - Subsection F (Multimodal Late Fusion) with 7-dimensional fusion vector (Eq. 11) and logistic model (Eq. 12).
   - Subsection G (Attribution and Explainability).
5. **Page 5:**
   - Subsections H and I (Threshold selection Eq. 13 and computational latency).
   - **Section V: Experimental Setup** covering dataset provenance (ForensiGuard-Bench-v1, 812 artifacts, 140 sources), source-grouped splitting (Eq. 14), and out-of-fold stacking.
   - **Section VI: Results and Discussion** introducing **TABLE I** (Performance Comparison Across Forensic Modalities).
   - TABLE I styled with `booktabs` and scaled with `\resizebox{\columnwidth}{!}{...}` to fit the column width.
6. **Page 6:**
   - **Fig. 2** (ROC Curves) and **Fig. 3** (Precision-Recall Curves).
   - **Fig. 4** (Confusion Matrix at $\tau = 0.500$).
   - **TABLE II** (Ablation Analysis Across Ten Architectural Permutations).
   - **Fig. 5** (Ablation Study horizontal bar chart).
   - Comprehensive analysis of the 10 ablation permutations, highlighting the primary role of magic-byte verification on discrete F1 (+13.9%) and late fusion on continuous ROC-AUC.
7. **Page 7:**
   - Subsection E (Attribution Performance) with exact multi-class metrics (65.08% 5-class, 71.43% manipulated, 88.89% coarse binary).
   - Subsection F (Explainability Analysis) covering the five grounded TreeSHAP case studies.
   - Subsection G (Adaptive-Attack Evaluation) documenting the empirical 0.0% detection rate under invariant-preserving evasion.
   - Subsection H (Error Analysis) reviewing the 1 False Positive and 26 False Negatives.
   - **Section VII: Threats to Validity and Limitations** enumerating five specific limitations.
8. **Page 8:**
   - **Section VIII: Conclusion and Future Work** summarizing proven findings and outline of OS Event ID 4616/1102 transformers.
   - Unnumbered **Acknowledgment** section thanking the Department of Data Science and Computer Applications at Manipal Institute of Technology (MAHE).
   - Numbered **References** section formatted strictly in IEEE style, listing all 14 references ([1]--[14]).

---

## 4. Cross-Deliverable Numerical Parity

Every value reported in `paper/main.tex` was verified against `results/all_experiments_results.json`:

| Metric / Parameter | Value in Paper | Value in JSON | Verified Parity |
| :--- | :---: | :---: | :---: |
| **Operating Decision Threshold ($\tau^*$)** | `0.500` | `0.5` | 100% Match |
| **Test Set Size ($N$)** | `126` | `126` | 100% Match |
| **Full Fusion Accuracy** | `78.57%` | `0.785714` | 100% Match |
| **Full Fusion F1 Score** | `0.854` | `0.854054` | 100% Match |
| **Full Fusion Precision** | `0.988` | `0.987500` | 100% Match |
| **Full Fusion Recall** | `0.752` | `0.752381` | 100% Match |
| **Full Fusion ROC-AUC** | `0.895` | `0.895238` | 100% Match |
| **Full Fusion PR-AUC** | `0.977` | `0.976822` | 100% Match |
| **Full Fusion FPR** | `4.76%` | `0.047619` | 100% Match |
| **Confusion Matrix ($TN, FP, FN, TP$)** | `20, 1, 26, 79` | `20, 1, 26, 79` | 100% Match |
| **Base Metadata-Only F1 / ROC-AUC** | `0.715` / `0.770` | `0.715152` / `0.769841` | 100% Match |
| **Base Image-Only Precision / Recall ($N=84$)** | `0.833` / `0.214` | `0.833333` / `0.214286` | 100% Match |
| **Base Image-Only F1 / ROC-AUC ($N=84$)** | `0.341` / `0.518` | `0.340909` / `0.518367` | 100% Match |
| **Variant 5 (Meta + Signature) F1** | `0.854` | `0.854054` | 100% Match |
| **Variant 7 (Full Fusion w/o CNN) F1 / ROC-AUC** | `0.854` / `0.895` | `0.854054` / `0.895238` | 100% Match |
| **Variant 6 vs. 7 Brier Score Calibration** | `0.125` vs. `0.132` | `0.124645` vs. `0.132270` | 100% Match |
| **Variant 10 (Fusion w/o Signature) F1** | `0.715` | `0.715152` | 100% Match |
| **Adaptive Attack Detection Rate** | `0.0%` | `0.0` | 100% Match |
| **Attribution 5-Class Exact Match ($82/126$)** | `65.08%` | `0.650794` | 100% Match |
| **Conditional Attribution on Manipulated ($75/105$)** | `71.43%` | `0.714286` | 100% Match |
| **Coarse Binary Attribution Accuracy ($112/126$)** | `88.89%` | `0.888889` | 100% Match |

---

## 5. Overleaf Submission Package Verification

The `paper/` directory was verified to be completely self-contained. It contains:
- `main.tex`: Master manuscript with native `\documentclass[conference]{IEEEtran}`.
- `references.bib`: Complete BibTeX bibliography with 14 verified entries.
- `IEEEtran.cls`: Official IEEE conference class file.
- `figures/`: All 5 figures embedded in the text (`fig0_architecture.png`, `fig1_roc_comparison.png`, `fig2_pr_comparison.png`, `fig3_confusion_matrix.png`, `fig4_ablation_study.png`).
- `tables/`: Modular `table1_modality_comparison.tex` and `table2_ablation.tex`.

The package can be compiled directly on any standard TeX Live / MiKTeX / Overleaf environment without external dependencies.
