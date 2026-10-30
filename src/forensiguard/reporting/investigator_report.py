"""Investigator-facing forensic report generator (Markdown, HTML, JSON, and PDF)."""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib import colors


class InvestigatorReport:
    """
    Standardized, court-defensible forensic report structure adhering to
    strict separation of objective physical facts and probabilistic inferences.
    """

    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data
        self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_metadata": {
                "framework": "ForensiGuard v1.0.0",
                "generated_at_utc": self.created_at,
                "analyst_mode": "Automated Triage",
            },
            "evidence_provenance": self.data.get("evidence_provenance", {}),
            "observed_physical_facts": self.data.get("observed_physical_facts", {}),
            "probabilistic_inferences": self.data.get("probabilistic_inferences", {}),
            "modality_scores": self.data.get("modality_scores", {}),
            "feature_attributions": self.data.get("feature_attributions", []),
            "investigator_narrative": self.data.get("investigator_narrative", []),
            "missing_modalities_and_warnings": self.data.get("warnings", []),
            "forensic_limitations_and_disclaimer": (
                "ForensiGuard provides probabilistic forensic triage indicators based on machine-learning models. "
                "These inferences do NOT constitute proof of guilt or conclusive evidentiary admissibility under Daubert/Frye. "
                "Independent manual examination of filesystem journal logs, file slack, and carving is mandatory."
            ),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        d = self.to_dict()
        prov = d["evidence_provenance"]
        facts = d["observed_physical_facts"]
        inf = d["probabilistic_inferences"]
        mods = d["modality_scores"]
        attrs = d["feature_attributions"]
        narratives = d["investigator_narrative"]
        warnings = d["missing_modalities_and_warnings"]

        md = []
        md.append("# FORENSIC TRIAGE REPORT — FORENSIGUARD")
        md.append(f"**Analysis Timestamp (UTC):** {d['report_metadata']['generated_at_utc']}")
        md.append(f"**Framework Version:** {d['report_metadata']['framework']}\n")

        md.append("## 1. EVIDENCE PROVENANCE (OBJECTIVE FACTS)")
        md.append(f"- **Filename:** `{prov.get('filename', 'N/A')}`")
        md.append(f"- **File Size:** {prov.get('file_size_bytes', 0):,} bytes")
        md.append(f"- **SHA-256:** `{prov.get('sha256', 'N/A')}`")
        md.append(f"- **MD5:** `{prov.get('md5', 'N/A')}`")
        md.append(f"- **Declared Extension:** `{prov.get('declared_extension', 'N/A')}`")
        md.append(f"- **Detected MIME Type:** `{facts.get('detected_mime_type', 'N/A')}`")
        md.append(f"- **Signature Mismatch:** `{'YES - OBFUSCATED' if facts.get('is_signature_mismatch') else 'NO - CONSISTENT'}`\n")

        md.append("## 2. OBSERVED PHYSICAL METADATA")
        md.append(f"- **Modification Time (mtime):** {facts.get('mtime_str', 'N/A')} (subseconds: {facts.get('mtime_subsecond', 0.0):.6f}s)")
        md.append(f"- **Access Time (atime):** {facts.get('atime_str', 'N/A')}")
        md.append(f"- **Metadata Change Time (ctime):** {facts.get('ctime_str', 'N/A')}")
        md.append(f"- **Shannon Entropy:** {facts.get('shannon_entropy', 0.0):.4f} bits/byte")
        md.append(f"- **LSB PoVs Chi-Square P-Value:** {facts.get('lsb_pair_pval', 1.0):.6f}\n")

        md.append("## 3. PROBABILISTIC MODEL INFERENCES")
        status = "**TAMPERED / MANIPULATED**" if inf.get("is_manipulated") else "**CLEAN / BENIGN**"
        md.append(f"- **Overall Assessment:** {status}")
        md.append(f"- **Manipulation Probability:** {inf.get('manipulation_probability', 0.0) * 100:.2f}%")
        md.append(f"- **Confidence Score:** {inf.get('confidence', 0.0) * 100:.2f}%")
        md.append(f"- **Attributed Anti-Forensic Technique:** `{inf.get('attributed_technique', 'N/A').upper()}`\n")

        md.append("### Modality-Specific Breakdown")
        md.append(f"- **Filesystem Metadata Model (XGBoost):** {mods.get('p_metadata', 0.0) * 100:.2f}%")
        md.append(f"- **Image Residual CNN (SRNet-Lite):** {mods.get('p_image_str', 'N/A')}")
        md.append(f"- **Unsupervised Anomaly Score:** {mods.get('anomaly_score', 0.0):.4f} (baseline divergence)")
        md.append(f"- **Binary Signature Anomaly:** {mods.get('signature_mismatch_score', 0.0):.1f}\n")

        md.append("## 4. EXPLANATORY EVIDENCE & SHAP ATTRIBUTION")
        for item in narratives:
            md.append(f"- {item}")
        md.append("")

        if warnings:
            md.append("## 5. MODALITY WARNINGS & LIMITATIONS")
            for w in warnings:
                md.append(f"- [WARNING] {w}")
            md.append("")

        md.append("## 6. FORENSIC CAVEAT & LEGAL DISCLAIMER")
        md.append(f"> {d['forensic_limitations_and_disclaimer']}")

        return "\n".join(md)

    def to_html(self) -> str:
        md = self.to_markdown()
        # Convert simple markdown to clean HTML
        html_lines = []
        html_lines.append("<!DOCTYPE html><html><head><meta charset='utf-8'>")
        html_lines.append("<title>ForensiGuard Forensic Report</title>")
        html_lines.append("<style>")
        html_lines.append("body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 900px; margin: 40px auto; padding: 20px; color: #24292e; background-color: #f6f8fa; }")
        html_lines.append(".card { background: white; border-radius: 8px; border: 1px solid #e1e4e8; padding: 24px; margin-bottom: 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }")
        html_lines.append("h1 { color: #0366d6; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }")
        html_lines.append("h2 { color: #24292e; border-bottom: 1px solid #eaecef; padding-bottom: 6px; margin-top: 24px; }")
        html_lines.append("code { background: #f1f3f5; padding: 2px 6px; border-radius: 4px; font-family: Consolas, monospace; font-size: 0.9em; }")
        html_lines.append(".badge-tampered { background: #d73a49; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; }")
        html_lines.append(".badge-clean { background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-weight: bold; }")
        html_lines.append(".disclaimer { background: #fffbdd; border-left: 4px solid #d99b00; padding: 12px; font-size: 0.9em; border-radius: 4px; }")
        html_lines.append("</style></head><body><div class='card'>")

        for line in md.split("\n"):
            if line.startswith("# "):
                html_lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                html_lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("- "):
                html_lines.append(f"<p style='margin: 4px 0 4px 20px;'>• {line[2:]}</p>")
            elif line.startswith("> "):
                html_lines.append(f"<div class='disclaimer'><b>LEGAL NOTICE:</b> {line[2:]}</div>")
            elif line.strip():
                html_lines.append(f"<p>{line}</p>")

        html_lines.append("</div></body></html>")
        return "\n".join(html_lines)

    def to_pdf(self, output_path: Union[str, Path]) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = SimpleDocTemplate(str(output_path), pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1a365d"),
            spaceAfter=12
        )
        h2_style = ParagraphStyle(
            "ReportH2",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#2b6cb0"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle("ReportBody", parent=styles["BodyText"], fontSize=9, leading=12)
        code_style = ParagraphStyle("ReportCode", parent=styles["Code"], fontSize=8, leading=10, textColor=colors.HexColor("#2d3748"))

        story = []
        d = self.to_dict()
        prov = d["evidence_provenance"]
        facts = d["observed_physical_facts"]
        inf = d["probabilistic_inferences"]
        mods = d["modality_scores"]

        story.append(Paragraph("FORENSIC TRIAGE REPORT — FORENSIGUARD", title_style))
        story.append(Paragraph(f"<b>Timestamp (UTC):</b> {d['report_metadata']['generated_at_utc']} | <b>Tool:</b> {d['report_metadata']['framework']}", body_style))
        story.append(Spacer(1, 10))

        # Provenance Table
        story.append(Paragraph("1. Evidence Provenance & Cryptographic Identifiers", h2_style))
        prov_data = [
            ["Attribute", "Value"],
            ["Filename", prov.get("filename", "N/A")],
            ["File Size", f"{prov.get('file_size_bytes', 0):,} bytes"],
            ["SHA-256", prov.get("sha256", "N/A")[:32] + "..."],
            ["MD5", prov.get("md5", "N/A")],
            ["Declared Ext / MIME", f"{prov.get('declared_extension', 'N/A')} / {facts.get('detected_mime_type', 'N/A')}"],
            ["Signature Check", "MISMATCH (ANOMALY)" if facts.get("is_signature_mismatch") else "Consistent"],
        ]
        t_prov = Table(prov_data, colWidths=[150, 390])
        t_prov.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#edf2f7")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1a202c")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_prov)
        story.append(Spacer(1, 10))

        # Inference Summary Table
        story.append(Paragraph("2. Probabilistic Model Inferences & Technique Attribution", h2_style))
        verdict = "TAMPERED / MANIPULATED" if inf.get("is_manipulated") else "CLEAN / BENIGN"
        inf_data = [
            ["Verdict", verdict],
            ["Manipulation Probability", f"{inf.get('manipulation_probability', 0.0) * 100:.2f}%"],
            ["Attributed Technique", inf.get("attributed_technique", "N/A").upper()],
            ["Confidence Score", f"{inf.get('confidence', 0.0) * 100:.2f}%"],
            ["Metadata XGBoost Score", f"{mods.get('p_metadata', 0.0) * 100:.2f}%"],
            ["Image Residual CNN Score", mods.get("p_image_str", "N/A")],
            ["Clean-Baseline Anomaly", f"{mods.get('anomaly_score', 0.0):.4f}"],
        ]
        t_inf = Table(inf_data, colWidths=[180, 360])
        t_inf.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e0")),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#feebc8") if inf.get("is_manipulated") else colors.HexColor("#c6f6d5")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t_inf)
        story.append(Spacer(1, 10))

        # Key Explanations
        story.append(Paragraph("3. Forensic Narrative & Explanations", h2_style))
        for exp in d["investigator_narrative"]:
            story.append(Paragraph(f"• {exp}", body_style))
            story.append(Spacer(1, 3))

        story.append(Spacer(1, 10))
        story.append(Paragraph("4. Legal Disclaimer & Evidentiary Scope", h2_style))
        disclaimer_p = Paragraph(f"<i>{d['forensic_limitations_and_disclaimer']}</i>", body_style)
        story.append(disclaimer_p)

        doc.build(story)
        return output_path
