# ForensiGuard-Bench-v1: Dataset Source and Provenance Specification

**Dataset Identifier:** `ForensiGuard-Bench-v1`  
**Dataset Type:** Controlled Synthetic Digital Forensic Benchmark  
**Generation Date:** October 2026 (Audited and Verified)  
**Authors & Curators:** Mohika Rathi (Reg. No: 230968032) & Sreyaan Roy (Reg. No: 230968184)  
**Branch:** Data Science  
**Subject:** Data Forensics  
**Repository Version:** v1.0.0  
**Manifest Path:** `data/benchmark/benchmark_manifest.csv`  

---

## 1. Provenance and Synthetic Nature

`ForensiGuard-Bench-v1` is a standardized synthetic digital forensics benchmark generated programmatically under controlled POSIX Linux filesystem environments specifically for this research project. 

> [!IMPORTANT]
> **Transparent Disclosure on Availability:** This dataset is a project-generated synthetic benchmark. It has **no public DOI, third-party repository URL, or external commercial host**. It is packaged directly within the project repository under `data/benchmark/`. Researchers must cite it as a project-generated benchmark using the formal citation provided below.

The dataset was engineered to address a pervasive deficiency in academic digital forensics: the lack of paired, ground-truth-labeled evidence containing synchronized filesystem timestamp tampering (timestomping), covert spatial steganography, and file-type obfuscation without identity or container-format shortcuts.

---

## 2. Origin and Generation Procedure

The generation process begins with **140 pristine, unmanipulated source carrier files** representing diverse file formats, resolutions, and text lengths:
- **Image Carriers:** Grayscale and colour images formatted as standard PNG and JPEG files.
- **Text & Document Carriers:** Plain-text files (`.txt`), configuration files (`.ini`, `.yaml`), source code (`.py`, `.sh`), and structured logs (`.log`).

From each pristine source file, a deterministic suite of anti-forensic mutations and benign controls was programmatically generated using POSIX system calls (`os.utime`, `stat`), PIL, and open-source steganography implementations:

1. **Clean Reference Generation:** Source files are copied to the benchmark folder, recording baseline POSIX timestamps (`mtime`, `atime`, `ctime`), nanosecond microsecond jitter, and authentic magic-byte headers.
2. **Timestomping Perturbations:**
   - *Coarse Backward Shifts:* `mtime` is shifted backward by 7 to 90 days.
   - *Forward Shifts:* `mtime` is moved forward into the future or post-incident timeframe.
   - *Subsecond Zeroing:* Nanosecond precision is truncated to exact zero (`000000000`), faithfully replicating artifacts produced by standard administrative utilities such as `touch -t`.
   - *Chronology Inversion:* `mtime` is modified while `ctime` remains unchanged, creating a chronological paradox where the recorded modification predates status change (`mtime < ctime`).
   - *Folder Variance Spoofing:* Modifying target timestamps while leaving sibling files in the same directory untouched, causing high z-score divergence.
3. **Spatial Steganography Insertion:**
   - Payloads are embedded into carrier image pixels using spatial domain Least Significant Bit (LSB) substitution.
   - Embedding rates span $0.05$, $0.10$, $0.20$, and $0.40$ bits per pixel (bpp).
   - *Format Shortcut Elimination:* Clean image carriers and steganographic image carriers are strictly generated with matched PNG format, grayscale color modes, and identical dimensions, eliminating trivial JPEG-vs-PNG container shortcuts.
4. **File-Type / Extension Obfuscation:**
   - Declared file extensions are intentionally altered (e.g. renaming an executable binary or image to `.txt`, `.log`, or `.dat`) while the underlying binary header magic bytes remain intact.
5. **Compound Manipulation:**
   - Simultaneous application of timestomping and spatial steganographic payload insertion on the same carrier.
6. **Adaptive Adversary Stress Test Corpus (Experiment 3):**
   - 21 specialized test artifacts where an adaptive adversary shifts `mtime` by 3.5 hours backward while synchronously updating `ctime` and `atime` (avoiding inversion), injecting uniform subsecond microsecond noise, and matching sibling folder timestamps.

---

## 3. Sample Counts and Partition Distribution

The benchmark comprises exactly **812 digital artifacts** derived from the **140 distinct source files**. To prevent identity leakage and optimistic bias, partitioning is enforced strictly by `source_file_id` using a 70% / 15% / 15% ratio:

| Partition Split | Source Groups | Total Artifacts | Clean Reference | Timestomped | Steganography | Obfuscated | Compound |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Train Partition (70%)** | 98 Sources | 566 | 98 | 196 | 116 | 98 | 58 |
| **Validation Partition (15%)** | 21 Sources | 120 | 21 | 42 | 26 | 21 | 10 |
| **Held-Out Test Split (15%)** | 21 Sources | 126 | 21 | 42 | 26 | 21 | 16 |
| **Total Benchmark Corpus** | **140 Sources** | **812** | **140** | **280** | **168** | **140** | **84** |

### Zero Source-Leakage Guarantee
- There is **strictly zero overlap** of source file IDs between Train, Validation, and Test sets:
  $$\text{Train Sources} \cap \text{Val Sources} = \emptyset, \quad \text{Train Sources} \cap \text{Test Sources} = \emptyset, \quad \text{Val Sources} \cap \text{Test Sources} = \emptyset$$
- Test artifacts originate exclusively from sources never observed during feature standardization, tree training, or CNN gradient descent.

---

## 4. Benchmark Manifest Schema

The canonical manifest is stored at [`data/benchmark/benchmark_manifest.csv`](file:///home/hp/.gemini/antigravity/scratch/ForensiGuard/data/benchmark/benchmark_manifest.csv). It contains 812 records with 25 metadata attributes:

- `artifact_id`: Unique UUID identifier for the forensic artifact.
- `source_file_id`: Identifier of the original source carrier group (enforces grouping).
- `filename`: Local filename on disk.
- `file_path`: Relative path within the benchmark directory.
- `sha256`: Cryptographic SHA-256 hash (64 hex characters).
- `md5`: Cryptographic MD5 hash (32 hex characters).
- `file_size_bytes`: Physical byte length.
- `declared_extension`: User-visible file extension (e.g. `.png`, `.txt`).
- `detected_mime_type`: True MIME type determined via puremagic binary header inspection.
- `is_signature_mismatch`: Boolean indicator of extension-to-magic-byte conflict.
- `manipulation_label`: Binary label ($0 = \text{clean}$, $1 = \text{manipulated}$).
- `technique`: Coarse manipulation class (`clean`, `timestomping`, `steganography`, `file_type_obfuscation`, `compound`).
- `subtype`: Granular attack variant (e.g., `coarse_backdate`, `subsecond_zeroed`, `lsb_high_payload`, `mismatch_extension`).
- `tool_name`: Simulating generation tool (`synthetic_timestomp`, `synthetic_stego`, etc.).
- `parameters_json`: Machine-readable dictionary of manipulation parameters (e.g., delta seconds, payload bpp).
- `mtime`, `atime`, `ctime`, `birthtime`: Raw epoch timestamps.
- `mtime_subsecond`: Subsecond microsecond floating fraction.
- `folder_context_id`: Directory grouping identifier.
- `folder_mtime_mean`, `folder_mtime_std`, `folder_mtime_median`: Sibling directory timestamp statistics.
- `split`: Partition assignment (`train`, `val`, `test`).

---

## 5. External Datasets & Source Material

No external commercial corpora or proprietary disk images were used:
- Baseline source carriers were synthesized or adapted from standard open-source royalty-free media and documentation.
- All manipulation tools and scripts are fully bundled under `src/forensiguard/data/generation.py`.

---

## 6. Usage Restrictions & Evidentiary Disclaimer

- **Usage Restrictions:** The dataset is intended strictly for academic, research, and non-destructive defensive forensic evaluation.
- **Evidentiary Disclaimer:** The synthetic samples simulate POSIX filesystem artifacts. They do not represent real criminal case evidence and must not be submitted as real forensic casework.

---

## 7. Dataset Citation

To cite `ForensiGuard-Bench-v1` in academic publications or project reports:

```bibtex
@misc{rathi2026forensiguard_bench,
  author       = {Mohika Rathi and Sreyaan Roy},
  title        = {{ForensiGuard-Bench-v1: Standardized Multimodal Digital Evidence Anti-Forensic Benchmark}},
  year         = {2026},
  month        = {October},
  howpublished = {Project Repository and Academic Benchmark Suite, Manipal Institute of Technology},
  note         = {Controlled synthetic benchmark of 812 forensic artifacts across 140 source groups with zero source leakage and format-shortcut remediation}
}
```
