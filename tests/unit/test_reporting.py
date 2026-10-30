"""Unit tests for InvestigatorReport formatting and export."""

from pathlib import Path
import tempfile
import pytest

from forensiguard.reporting.investigator_report import InvestigatorReport


def test_investigator_report_exports():
    sample_data = {
        "evidence_provenance": {
            "filename": "evidence_sample.jpg",
            "file_size_bytes": 10240,
            "sha256": "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
            "md5": "1234567890abcdef1234567890abcdef",
            "declared_extension": ".jpg",
        },
        "observed_physical_facts": {
            "detected_mime_type": "image/jpeg",
            "is_signature_mismatch": False,
            "mtime": 1700000000.0,
            "mtime_str": "2023-11-14 22:13:20 UTC",
            "mtime_subsecond": 0.0,
            "atime_str": "2023-11-14 22:15:00 UTC",
            "ctime_str": "2023-11-14 22:14:00 UTC",
            "shannon_entropy": 7.42,
            "lsb_pair_pval": 0.0001,
        },
        "probabilistic_inferences": {
            "manipulation_probability": 0.94,
            "is_manipulated": True,
            "attributed_technique": "steganography",
            "attribution_probabilities": {"clean": 0.06, "steganography": 0.88, "timestomping": 0.06},
            "confidence": 0.92,
        },
        "modality_scores": {
            "p_metadata": 0.45,
            "p_image": 0.96,
            "p_image_str": "96.00%",
            "anomaly_score": 0.35,
            "signature_mismatch_score": 0.0,
        },
        "feature_attributions": [
            {"feature": "lsb_pair_pval", "value": 0.0001, "shap_value": 0.45, "direction": "suspicious"}
        ],
        "investigator_narrative": [
            "LSB sample pair chi-square test indicates payload alteration."
        ],
        "warnings": [],
    }

    report = InvestigatorReport(sample_data)

    # 1. JSON
    json_str = report.to_json()
    assert "evidence_sample.jpg" in json_str
    assert "steganography" in json_str

    # 2. Markdown
    md_str = report.to_markdown()
    assert "# FORENSIC TRIAGE REPORT" in md_str
    assert "TAMPERED / MANIPULATED" in md_str

    # 3. HTML
    html_str = report.to_html()
    assert "<!DOCTYPE html>" in html_str
    assert "ForensiGuard Forensic Report" in html_str

    # 4. PDF via ReportLab
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = Path(tmp.name)

    try:
        report.to_pdf(pdf_path)
        assert pdf_path.exists()
        assert pdf_path.stat().st_size > 1000, "PDF must have generated valid binary structure"
    finally:
        if pdf_path.exists():
            pdf_path.unlink()
