# ForensiGuard Benchmark Dataset Schema

## Overview
To prevent data leakage, all generated artifacts are tracked with strict provenance linking back to a unique `source_file_id`. All variations derived from the same source artifact reside in exactly one split (`train`, `val`, or `test`).

## Schema Fields

| Column Name | Type | Description | Example |
| :--- | :--- | :--- | :--- |
| `artifact_id` | String (UUID) | Unique identifier of this forensic artifact | `"a8f1e94b-1234-..."` |
| `source_file_id` | String | Identifier of original clean source artifact | `"src_img_0042"` |
| `filename` | String | Filename on disk | `"src_img_0042_timestomped_coarse.jpg"` |
| `file_path` | String | Relative path to artifact | `"data/benchmark/test/src_img_0042_..."` |
| `sha256` | String (Hex 64) | SHA-256 cryptographic hash | `"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"` |
| `md5` | String (Hex 32) | MD5 cryptographic hash | `"d41d8cd98f00b204e9800998ecf8427e"` |
| `file_size_bytes` | Integer | Exact file size in bytes | `24518` |
| `declared_extension` | String | Extension according to filename | `".jpg"` |
| `detected_mime_type` | String | MIME type detected via magic bytes | `"image/jpeg"` |
| `is_signature_mismatch` | Boolean | True if MIME does not match extension | `false` |
| `manipulation_label` | Integer | 0 for Clean, 1 for Manipulated | `1` |
| `technique` | String | Attribution category | `"timestomping"`, `"steganography"`, `"file_type_obfuscation"`, `"compound"`, `"clean"` |
| `subtype` | String | Specific parameter / strength | `"subtle_2h"`, `"coarse_5y"`, `"lsb_0.2bpp"`, `"disguised_pdf"` |
| `tool_name` | String | Tool or script used for manipulation | `"ForensiGuard-Manipulator-v1"` |
| `parameters_json` | String (JSON) | Detailed perturbation parameters | `'{"shift_seconds": 7200, "zero_micro": true}'` |
| `mtime` | Float | POSIX modification timestamp | `1729500000.0` |
| `atime` | Float | POSIX access timestamp | `1729500100.0` |
| `ctime` | Float | POSIX metadata change timestamp | `1729499800.0` |
| `birthtime` | Float | POSIX creation / birth timestamp | `1729490000.0` |
| `mtime_subsecond` | Float | Fractional subsecond of mtime | `0.0` |
| `split` | String | Dataset split assignment | `"train"`, `"val"`, or `"test"` |
| `generator_version` | String | Benchmark generator release version | `"1.0.0"` |

## Splitting Invariant
$$\forall s \in \text{Sources}, \quad |\{ \text{split}(a) : a \in \text{Artifacts}, \text{source}(a) = s \}| = 1$$
No `source_file_id` may ever exist in more than one split partition.
