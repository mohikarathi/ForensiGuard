# ForensiGuard Design Decisions and Synopsis Deviations

## Key Design Decisions & Audit Remediation Log

### 1. Zero-Leakage Source-Grouped Partitioning
- **Decision**: Grouping split exclusively on `source_file_id`.
- **Rationale**: An original file (e.g. `doc_01.pdf` or `img_05.png`) produces multiple variations (clean, timestomped, stego, obfuscated). If clean `doc_01` is in `train` and timestomped `doc_01` is in `test`, a model might memorize file-content specifics (or exact file size) rather than generalizable manipulation signatures. Strict group splitting eliminates this source of data leakage ($\text{Train} \cap \text{Val} = \emptyset$, $\text{Train} \cap \text{Test} = \emptyset$).

### 2. Research Integrity Audit: Format-Shortcut Elimination
- **Audit Defect**: Early iterations saved clean images as JPEG and steganographically modified images as PNG. This introduced an artificial format shortcut where classifiers could achieve 100% detection based simply on container headers or file extensions.
- **Remediation**:
  - Standardized both clean and steganographic carriers to identical uncompressed 8-bit grayscale PNGs ($128 \times 128$).
  - Implemented opaque hash-based naming (`art_{src_id}_{uuid[:10]}.png`), preventing filename label cues.
  - Added unit test `tests/unit/test_no_format_shortcut.py` verifying that clean and stego carriers share identical bit-depth, MIME type, dimensions, and naming convention.
- **Scientific Impact**: On the shortcut-free benchmark, the isolated residual CNN achieved an F1 of 0.378 and ROC-AUC of 0.516, which is empirically faithful to the known difficulty of uncompressed LSB steganalysis without massive pretraining datasets (Fridrich & Kodovsky, 2012; Cogranne et al., ALASKA#2).

### 3. Leakage-Safe Grouped Out-of-Fold (OOF) Stacking
- **Audit Defect**: Previous iterations generated OOF predictions for tabular metadata, but used in-sample predictions for the PyTorch CNN.
- **Remediation**:
  - Implemented `GroupKFold(n_splits=5)` on `source_file_id` across the training split.
  - In each fold, inner training subsets fit the clean Isolation Forest, the metadata XGBoost, and the PyTorch SRNet-Lite CNN from scratch.
  - The held-out inner fold is evaluated to collect pure out-of-fold probability vectors.
  - Added automated test `tests/test_oof_leakage.py` proving zero source overlap between inner folds and verifying that fusion training consumes strictly out-of-fold features.

### 4. Evaluation Protocol on Intended and Shared Populations
- **Decision**: Evaluate single-modality detectors on their intended populations as well as on a shared multimodal subpopulation.
- **Rationale**:
  - Evaluating an image CNN on non-image files (e.g. PDFs) without masking would produce artificial false alarms (FPR = 100%) or requires default assumptions (e.g., $P=0.5$).
  - In the audited pipeline, missing modalities are explicitly masked with indicator flag $\mathbb{I}_{\text{has\_image}}$ and calibrated neutral imputations.
  - To provide fair scientific comparisons, Table I reports:
    1. Full corpus performance ($N=126$) for full-corpus detectors.
    2. Intended domain performance ($N=84$) for image detectors.
    3. Shared subpopulation performance ($N=84$) where all models are evaluated on the exact same image carrier artifacts.

### 5. Honest Adaptive Attack Stress Testing
- **Audit Defect**: Legacy documentation claimed 34.2% adaptive metadata detection and fusion resilience, whereas raw simulation reported 0.0%.
- **Remediation**:
  - Re-implemented the adaptive attack simulation with clear documentation of the stress-test parameters (3.5h backdating, $0.3\sigma$ sibling variance, subsecond microsecond preservation $0.482910\text{s}$, and $mtime \ge ctime$).
  - Recorded actual empirical results: Metadata XGBoost = 0.0% detection; Clean Isolation Forest anomaly score = 0.596; Late Fusion probability = 0.216 (below decision threshold $\tau = 0.290$, yielding 0.0% detection).
  - Explicitly documented this limitation in the research paper and reports: static filesystem metadata alone cannot detect an adversary who strictly respects filesystem invariants; operating system kernel audit logs (e.g., Windows Event ID 4616) are essential for defense-in-depth.

### 6. Clean-Only Anomaly Scorer in Tabular Pipeline
- **Decision**: Train an Isolation Forest exclusively on the clean partition of the training set.
- **Rationale**: In real-world forensic triage, examiners know what typical, benign filesystem timestamps look like within an enterprise or OS. Feeding an unsupervised anomaly score into XGBoost gives the tree booster a strong prior on distributional divergence without risking target leakage.

### 7. Standalone Benchmark Generator with External Ingestion Adapters
- **Decision**: Provide an automated synthetic benchmark engine (`ForensiGuard-Bench-v1`) with modular ingestion adapters for GovDocs1, BOSSbase, ALASKA#2, NIST CFReDS, and M57-Patents in `src/forensiguard/data/acquisition.py`.
- **Rationale**: Downloading multi-gigabyte forensic corpora is impractical for instantaneous automated reproduction and CI/CD testing. The benchmark produces full forensic fidelity (real binary headers, LSB image manipulation, real timestamp gaps, directory neighbor contexts), while allowing drop-in integration of raw external files whenever available.

### 8. Defensible Explainability and Evidentiary Boundaries
- **Decision**: Explicitly disclaim that ML inferences constitute absolute proof of guilt or tampering.
- **Rationale**: In accordance with Daubert / Frye legal standards and forensic best practice, automated tools provide investigative leads and statistical attribution. The generated investigator reports strictly delineate between verifiable digital facts (cryptographic hashes, raw timestamps, header signatures) and probabilistic model inferences.
