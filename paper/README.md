# ForensiGuard: IEEE Conference Paper Package

This directory contains the authoritative LaTeX source, figures, tables, and bibliography for the research paper:

> **ForensiGuard: A Multimodal Machine-Learning Framework for Detecting, Attributing and Explaining Anti-Forensic Manipulation of Digital Evidence**  
> **Authors:** Mohika Rathi (Registration No. 230968032) and Sreyaan Roy (Registration No. 230968184)  
> **Format:** Official IEEE Conference Proceedings (`\documentclass[conference]{IEEEtran}`)

---

## 1. Directory Structure

```
paper/
├── main.tex                    # Authoritative LaTeX manuscript
├── main.pdf                    # Compiled IEEE two-column camera-ready PDF
├── references.bib              # Complete BibTeX bibliography (14 verified entries)
├── IEEEtran.cls                # Official IEEE conference document class file
├── figures/                    # High-resolution publication figures (300 DPI)
│   ├── fig0_architecture.png   # End-to-end framework architecture
│   ├── fig1_roc_comparison.png # Modality ROC curves comparison
│   ├── fig2_pr_comparison.png  # Precision-Recall curves comparison
│   ├── fig3_confusion_matrix.png# Confusion matrix (N=126, tau=0.500)
│   └── fig4_ablation_study.png # 10-variant architectural ablation study
├── tables/                     # Modular LaTeX tables with booktabs formatting
│   ├── table1_modality_comparison.tex # Modality comparisons (N=126 / N=84)
│   └── table2_ablation.tex     # 10-permutation ablation metrics
├── rendered_pages/             # PNG page-by-page renders for visual inspection
│   ├── page-1.png ... page-8.png
└── README.md                   # Build instructions and validation documentation
```

---

## 2. Compilation Instructions

The manuscript is strictly typeset using the native `IEEEtran` document class. It can be compiled using either modern zero-configuration TeX engines or standard TeX Live toolchains.

### Option A: Modern Zero-Configuration Build (Recommended)
Tectonic automatically resolves packages, runs BibTeX passes, and generates the final camera-ready PDF:
```bash
# From repository root:
tectonic paper/main.tex

# Or inside the paper/ directory:
cd paper
tectonic main.tex
```
The resulting PDF will be generated at `paper/main.pdf`.

### Option B: Standard TeX Live / MiKTeX / latexmk Build
Using the classic multi-pass compilation sequence:
```bash
cd paper
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```
Alternatively, with `latexmk`:
```bash
cd paper
latexmk -pdf main.tex
```

### Option C: Overleaf Submission
1. Compress the contents of the `paper/` directory into a `.zip` archive:
   ```bash
   cd paper
   zip -r forensiguard_paper.zip main.tex references.bib IEEEtran.cls figures/ tables/
   ```
2. Log in to [Overleaf](https://www.overleaf.com/).
3. Click **New Project** $\to$ **Upload Project**, and upload `forensiguard_paper.zip`.
4. Ensure the compiler is set to **pdfLaTeX** or **XeLaTeX**. Click **Recompile**.

---

## 3. Formatting Invariants & IEEE Template Compliance

- **Document Class:** `\documentclass[conference]{IEEEtran}` with native margins, two-column layout, and standard column widths (3.5 inches per column, 0.25 inch gutter).
- **No Geometry Overrides:** The layout does not use `\geometry`, custom page dimensions, or artificially shrunk fonts.
- **Author Block:** Uses standard IEEEtran `\IEEEauthorblockN` and `\IEEEauthorblockA` commands with verified horizontal left-to-right ordering (Mohika Rathi on the left, Sreyaan Roy on the right). No email addresses, ORCID IDs, or funding text are fabricated.
- **Abstract & Keywords:** Single-paragraph abstract ($< 250$ words) without citations, followed by standard `IEEEkeywords`.
- **Figures:** Embedded using `\begin{figure}[htbp]` and full-width `\begin{figure*}[htbp]` with captions positioned below figures.
- **Tables:** Embedded using `\begin{table}[htbp]` with captions placed above tables, styled using `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), with `\resizebox{\columnwidth}{!}{...}` preventing column overflow.
- **Citations & Bibliography:** Formatted via `\bibliographystyle{IEEEtran}` and `\bibliography{references}`, generating numbered square-bracket citations (`[1]`, `[2]`).

---

## 4. Canonical Validated Results Summary

All numbers in `paper/main.tex` strictly match the canonical results in `results/all_experiments_results.json` and `results/predictions_test.csv` evaluated on the held-out test split of 126 artifacts derived from 21 disjoint sources (zero source leakage):

| Metric Parameter | Value | Reference Location in Paper |
| :--- | :---: | :--- |
| **Operating Threshold ($\tau^*$)** | `0.500` | Section IV-H, Eq. (13) |
| **Held-Out Test Sample Count ($N$)** | `126` | Section V-A, Table I, Table II |
| **Full Fusion Test Accuracy** | `78.57%` | Section VI-A, Table I |
| **Full Fusion F1-Score** | `0.854` | Section VI-A, Table I, Table II |
| **Full Fusion Precision / Recall** | `0.988` / `0.752` | Section VI-A |
| **Full Fusion ROC-AUC / PR-AUC** | `0.895` / `0.977` | Section VI-A, Table I, Table II |
| **Operational False Positive Rate** | `4.76%` | Section VI-A, Table I ($\text{FPR}_{\text{val}} \le 0.05$) |
| **Confusion Matrix ($TN, FP, FN, TP$)** | `20, 1, 26, 79` | Section VI-A, Fig. 4 |
| **Base Metadata-Only F1 / ROC-AUC** | `0.715` / `0.770` | Table I, Table II (Variant 1) |
| **Base Image-Only F1 / ROC-AUC** | `0.341` / `0.518` | Table I (Image Domain, N=84) |
| **Signature Ablation Drop** | `0.854 \to 0.715` | Section VI-D, Table II (Variant 10) |
| **Adaptive Evasion Detection Rate** | `0.0%` | Section VI-G |
