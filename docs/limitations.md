# ForensiGuard Limitations and Legal/Ethical Considerations

## Limitations

1. **Filesystem Differences**:
   - Different filesystems (EXT4, NTFS, APFS, FAT32) handle timestamp granularities differently (e.g. FAT32 has 2-second timestamp resolution on modification time and 10ms on creation time, whereas NTFS has 100ns precision).
   - Zero subseconds in FAT32 is standard behavior, not necessarily malicious timestomping. In NTFS or EXT4, zero subseconds on user files is highly suspicious.
   - The detector currently benchmarks against high-resolution POSIX/NTFS contexts.

2. **Synthetic Manipulation vs. Zero-Day Tooling**:
   - The benchmark trains on known mathematical operations (LSB, spatial noise, timestamp shifting). Advanced zero-day steganographic tools using content-adaptive syndrome-trellis codes (STC) at microscopic payload rates (<0.01 bpp) remain challenging.

3. **Missing Modalities**:
   - Non-image files (plain text, code, archives) lack visual residual channels. The fusion engine must fall back to metadata and binary signature analysis, reducing multimodal redundancy.

4. **Admissibility and Evidentiary Boundaries**:
   - Machine-learning outputs must never be used alone to establish guilt or conclusive evidentiary proof in legal proceedings.
   - ForensiGuard is designed for forensic triage: guiding human investigators toward anomalies requiring in-depth manual analysis.
