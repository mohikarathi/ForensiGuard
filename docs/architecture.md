# ForensiGuard Architecture Specification

ForensiGuard is a multimodal machine-learning framework designed to detect, attribute, and explain anti-forensic manipulations in digital evidence.

## System Overview

```
                      +-----------------------------+
                      |   Target Digital Artifact   |
                      +--------------+--------------+
                                     |
           +-------------------------+-------------------------+
           |                                                   |
           v                                                   v
+-----------------------+                           +-----------------------+
|  Filesystem Metadata  |                           |     Image / Binary    |
|   Extractor & Logic   |                           |    Extractor & Logic  |
+----------+------------+                           +-----------+-----------+
           |                                                    |
           v                                                    v
+-----------------------+                           +-----------------------+
| Feature Engineering:  |                           | Statistical Signals:  |
| - Timestamp Deltas    |                           | - Byte Entropy        |
| - Sub-second Precision|                           | - LSB Chi-Square      |
| - Inversion Flags     |                           | - Signature Match     |
| - Folder Context Z    |                           +-----------+-----------+
+----------+------------+                                       |
           |                                                    v
           v                                        +-----------------------+
+-----------------------+                           | Spatial Residual CNN  |
| Clean-Trained Anomaly |                           | (High-pass filtering  |
| Detector (IsoForest)  |                           |  + Deep ResNet-Lite)  |
+----------+------------+                           +-----------+-----------+
           |                                                    |
           v                                                    |
+-----------------------+                                       |
|  XGBoost Classifier   |                                       |
|  (P_metadata, SHAP)   |                                       |
+----------+------------+                                       |
           |                                                    |
           +-------------------------+--------------------------+
                                     |
                                     v
                        +-------------------------+
                        |   Late-Fusion Engine    |
                        |   (Stacked Meta-Model)  |
                        +------------+------------+
                                     |
           +-------------------------+-------------------------+
           |                         |                         |
           v                         v                         v
+--------------------+    +--------------------+    +--------------------+
|   Manipulation     |    |     Technique      |    |   SHAP Evidence    |
| Probability & Conf |    |    Attribution     |    | Investigator Report|
+--------------------+    +--------------------+    +--------------------+
```

## Modality 1: Filesystem Metadata Pipeline
1. **Extraction**: Collects MACB timestamps (Modified, Accessed, Changed/Metadata, Birth/Created), file sizes, and directory neighbor timestamps.
2. **Feature Engineering**:
   - $\Delta(mtime, ctime)$, $\Delta(atime, mtime)$, $\Delta(atime, ctime)$.
   - Chronology inversion indicator: $\mathbb{I}(mtime < ctime)$.
   - Zero-subsecond truncation indicator: $\mathbb{I}(\text{microsecond} == 0)$.
   - Round minute / round hour flags.
   - Folder context z-score: Normalized deviation of artifact $mtime$ from directory siblings.
3. **Unsupervised Anomaly Component**: Isolation Forest trained strictly on clean training metadata. Outputs anomaly score $S_{\text{anomaly}} \in [0, 1]$.
4. **Supervised XGBoost Classifier**: Ingests engineered features + $S_{\text{anomaly}}$ to produce $P_{\text{meta}}$.
5. **Local Explainability**: TreeSHAP produces exact Shapley values ranking feature contributions.

## Modality 2: Image and Binary Artifact Pipeline
1. **Signature Verification**: Validates file magic bytes against file extension.
2. **Byte Statistics**: Computes Shannon entropy $H(X)$, byte distribution uniformity, and LSB pair chi-square test.
3. **Noise Residual Representation**: Applies high-pass spatial filtering (Laplacian / SRM KV kernel) to suppress image semantics and isolate steganographic noise residuals:
   $$R(x, y) = I(x, y) * K_{\text{SRM}}$$
4. **Residual CNN (SRNet-Lite)**: 5-layer convolutional network with residual connections and global pooling, outputting $P_{\text{stego}}$.

## Modality 3: Late-Fusion Meta-Classifier
- **Input Vector**: $[P_{\text{meta}}, P_{\text{stego}}, S_{\text{sig\_mismatch}}, S_{\text{anomaly}}, H_{\text{entropy}}, P_{\text{lsb\_pval}}]$.
- **Training Strategy**: Out-of-fold (OOF) cross-validation on the training set to prevent meta-level data leakage.
- **Outputs**:
  - Binary Manipulation Probability $P(\text{manipulated}) \in [0, 1]$.
  - Multi-class Technique Attribution: `Clean`, `Timestomping`, `Steganography`, `File_Type_Obfuscation`, `Compound_Manipulation`.
  - Calibrated Decision Confidence.
- **Missing Modality Handling**: Graceful fallback when non-image files are analyzed (masking CNN features, adjusting meta-weights).

## Investigator Reporting
Automated generation of court-defensible forensic reports detailing:
- Cryptographic provenance (SHA-256, MD5).
- Objective observed facts vs. probabilistic model inferences.
- SHAP feature attributions.
- Forensic caveats and verification protocols.
