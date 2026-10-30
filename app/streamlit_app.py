"""ForensiGuard Interactive Forensic Triage Dashboard (Streamlit)."""

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import sys
from typing import Optional
import numpy as np
import pandas as pd
import streamlit as st

# Configure page layout and title
st.set_page_config(
    page_title="ForensiGuard | Anti-Forensics Triage",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Root directory resolution and module path insertion
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR / "src") not in sys.path:
    sys.path.insert(0, str(ROOT_DIR / "src"))

MODELS_DIR = ROOT_DIR / "artifacts" / "models"
BENCHMARK_DIR = ROOT_DIR / "data" / "benchmark"

# Custom CSS for styling
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1e3a8a; margin-bottom: 0px; }
    .subtitle { font-size: 1.05rem; color: #4b5563; margin-bottom: 20px; }
    .badge-clean { background-color: #10b981; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 1.1rem; }
    .badge-tampered { background-color: #ef4444; color: white; padding: 6px 14px; border-radius: 20px; font-weight: 700; font-size: 1.1rem; }
    .metric-card { background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 12px; }
    .disclaimer-box { background-color: #fffbeb; border-left: 5px solid #f59e0b; padding: 12px 16px; border-radius: 6px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_pipeline():
    from forensiguard.pipeline import ForensiGuardPipeline
    return ForensiGuardPipeline(models_dir=MODELS_DIR)


def main():
    st.markdown('<div class="main-title">🛡️ ForensiGuard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">A Multimodal Machine-Learning Framework for Detecting, Attributing & Explaining Anti-Forensic Evidence Manipulation</div>',
        unsafe_allow_html=True,
    )

    # Sidebar: Navigation and Configuration
    st.sidebar.header("📁 Evidence Input")
    input_mode = st.sidebar.radio(
        "Select Artifact Source:",
        ["Sample Evidence Gallery", "Upload Custom Evidence File"],
    )

    selected_file_path: Optional[Path] = None

    if input_mode == "Sample Evidence Gallery":
        manifest_path = BENCHMARK_DIR / "benchmark_manifest.csv"
        if manifest_path.exists():
            df_manifest = pd.read_csv(manifest_path)
            sample_types = ["clean", "timestomping", "steganography", "file_type_obfuscation", "compound"]
            selected_type = st.sidebar.selectbox("Filter Technique:", sample_types)

            filtered = df_manifest[df_manifest["technique"] == selected_type]
            if not filtered.empty:
                sample_filenames = filtered["filename"].tolist()[:10]
                chosen_filename = st.sidebar.selectbox("Select Artifact:", sample_filenames)
                rel_path = filtered[filtered["filename"] == chosen_filename]["file_path"].values[0]
                selected_file_path = BENCHMARK_DIR / rel_path
        else:
            st.sidebar.warning("Benchmark dataset not found on disk. Run `forensiguard generate-benchmark` first.")
    else:
        uploaded_file = st.sidebar.file_uploader(
            "Upload digital evidence (disposable copy):",
            type=["jpg", "jpeg", "png", "bmp", "pdf", "txt", "bin"],
        )
        if uploaded_file is not None:
            # Save uploaded bytes safely to a temporary sandbox
            temp_dir = Path(tempfile.gettempdir()) / "forensiguard_uploads"
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_file_path = temp_dir / uploaded_file.name
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            selected_file_path = temp_file_path

    if selected_file_path is None or not selected_file_path.exists():
        st.info("👈 Please select an artifact from the gallery or upload an evidence file in the sidebar to begin triage.")
        return

    # Check if models exist
    if not (MODELS_DIR / "fusion_model.joblib").exists():
        st.error("Trained models not found in `artifacts/models`. Please run `forensiguard train-and-evaluate` first.")
        return

    pipeline = load_pipeline()

    with st.spinner("Analyzing artifact across metadata, image, and signature modalities..."):
        report = pipeline.analyze_artifact(selected_file_path)

    d = report.to_dict()
    prov = d["evidence_provenance"]
    facts = d["observed_physical_facts"]
    inf = d["probabilistic_inferences"]
    mods = d["modality_scores"]
    attrs = d["feature_attributions"]
    narrative = d["investigator_narrative"]

    # Top Metrics Layout
    col_verdict, col_prob, col_tech, col_conf = st.columns([1.2, 1, 1.2, 1])
    is_tampered = inf["is_manipulated"]

    with col_verdict:
        st.markdown("**Forensic Verdict**")
        if is_tampered:
            st.markdown('<span class="badge-tampered">⚠️ MANIPULATION DETECTED</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-clean">✅ CLEAN / UNALTERED</span>', unsafe_allow_html=True)

    with col_prob:
        p_val = inf["manipulation_probability"]
        st.metric("Tamper Probability", f"{p_val * 100:.1f}%")

    with col_tech:
        st.metric("Attributed Technique", inf["attributed_technique"].upper())

    with col_conf:
        st.metric("Decision Confidence", f"{inf['confidence'] * 100:.1f}%")

    st.markdown("---")

    # Tabs for In-Depth Analysis
    tab_overview, tab_modalities, tab_shap, tab_report = st.tabs([
        "🔍 Evidence Inspection",
        "⚖️ Multimodal Breakdown",
        "💡 SHAP Explanations",
        "📄 Investigator Report & Export",
    ])

    with tab_overview:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🏷️ Cryptographic & Provenance Facts")
            st.write(f"**Filename:** `{prov['filename']}`")
            st.write(f"**File Size:** {prov['file_size_bytes']:,} bytes")
            st.write(f"**SHA-256:** `{prov['sha256']}`")
            st.write(f"**MD5:** `{prov['md5']}`")
            st.write(f"**Declared Extension:** `{prov['declared_extension']}`")

        with col2:
            st.markdown("### 🔬 Binary & Signature Observations")
            st.write(f"**Detected MIME Type:** `{facts['detected_mime_type']}`")
            if facts["is_signature_mismatch"]:
                st.error("🚨 Signature Mismatch: Magic bytes contradict file extension!")
            else:
                st.success("✔️ Binary header is consistent with extension.")

            st.write(f"**Modification Time:** `{facts['mtime_str']}`")
            st.write(f"**Subsecond Precision:** `{facts['mtime_subsecond']:.6f}s`")
            st.write(f"**Shannon Entropy:** `{facts['shannon_entropy']:.4f} bits/byte`")
            st.write(f"**LSB Chi-Square P-Value:** `{facts['lsb_pair_pval']:.6f}`")

    with tab_modalities:
        st.markdown("### 🧩 Modality-Level Signal Comparison")
        st.write("ForensiGuard integrates independent signals through a calibrated late-fusion meta-classifier:")

        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Metadata Model (XGBoost)", f"{mods['p_metadata'] * 100:.1f}%")
        with m_col2:
            st.metric("Image Residual CNN", mods["p_image_str"])
        with m_col3:
            st.metric("Clean Anomaly Scorer", f"{mods['anomaly_score']:.3f}")
        with m_col4:
            st.metric("Header Obfuscation Flag", f"{mods['signature_mismatch_score']:.1f}")

        # Technique Attribution Probabilities Chart
        st.markdown("#### Technique Attribution Probabilities")
        probs_df = pd.DataFrame(
            list(inf["attribution_probabilities"].items()),
            columns=["Technique", "Probability"]
        ).sort_values("Probability", ascending=False)
        st.bar_chart(probs_df.set_index("Technique"))

    with tab_shap:
        st.markdown("### 💡 Explainable AI: Feature Contributions (SHAP)")
        st.write("SHAP game-theoretic attributions rank how each physical observation influenced the decision:")

        if attrs:
            shap_df = pd.DataFrame(attrs)
            st.dataframe(
                shap_df[["feature", "value", "shap_value", "direction"]],
                use_container_width=True,
            )

        st.markdown("#### 📝 Automated Forensic Interpretations")
        for item in narrative:
            st.info(item)

    with tab_report:
        st.markdown("### 📋 Generated Forensic Triage Report")
        st.text_area("Markdown Preview", report.to_markdown(), height=260)

        # Download Buttons
        d_col1, d_col2, d_col3, d_col4 = st.columns(4)
        with d_col1:
            st.download_button(
                "⬇️ Download Markdown",
                data=report.to_markdown(),
                file_name=f"report_{prov['filename']}.md",
                mime="text/markdown",
            )
        with d_col2:
            st.download_button(
                "⬇️ Download HTML",
                data=report.to_html(),
                file_name=f"report_{prov['filename']}.html",
                mime="text/html",
            )
        with d_col3:
            st.download_button(
                "⬇️ Download JSON",
                data=report.to_json(),
                file_name=f"report_{prov['filename']}.json",
                mime="application/json",
            )
        with d_col4:
            # Generate temporary PDF for download
            pdf_temp = Path(tempfile.gettempdir()) / f"report_{prov['filename']}.pdf"
            report.to_pdf(pdf_temp)
            with open(pdf_temp, "rb") as pdf_file:
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=pdf_file.read(),
                    file_name=f"report_{prov['filename']}.pdf",
                    mime="application/pdf",
                )

    st.markdown("---")
    st.markdown(
        '<div class="disclaimer-box"><b>⚖️ Legal & Forensic Notice:</b> '
        + d["forensic_limitations_and_disclaimer"]
        + "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
