"""Comprehensive test suite for ForensiGuard REST API service and endpoints."""

import io
import pytest
from fastapi.testclient import TestClient

from forensiguard.api.server import app


@pytest.fixture(scope="module")
def client():
    """Provides a reusable FastAPI TestClient."""
    return TestClient(app)


def test_health_endpoint(client):
    """Verifies that the /api/health endpoint returns model and system status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["models_loaded"] is True
    assert "cuda" in data["device"] or "cpu" in data["device"]
    assert data["benchmark_available"] is True
    assert data["total_benchmark_samples"] > 0


def test_overview_endpoint(client):
    """Verifies that /api/overview returns academic project metadata and authors."""
    response = client.get("/api/overview")
    assert response.status_code == 200
    data = response.json()
    assert "ForensiGuard" in data["title"]
    assert len(data["authors"]) == 2
    authors = {a["name"]: a["reg_no"] for a in data["authors"]}
    assert authors["Mohika Rathi"] == "230968032"
    assert authors["Sreyaan Roy"] == "230968184"
    assert data["operating_threshold"] == 0.5
    assert "train" in data["splits"]
    assert "val" in data["splits"]
    assert "test" in data["splits"]


def test_models_endpoint(client):
    """Verifies that /api/models returns technical status for all 5 pipeline components."""
    response = client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "components" in data
    assert len(data["components"]) >= 5
    component_ids = [m["id"] for m in data["components"]]
    assert "metadata_classifier" in component_ids
    assert "image_cnn" in component_ids
    assert "anomaly_detector" in component_ids
    assert "signature_verifier" in component_ids
    assert "late_fusion" in component_ids


def test_demo_samples_endpoint(client):
    """Verifies that /api/demo-samples returns curated benchmark samples."""
    response = client.get("/api/demo-samples")
    assert response.status_code == 200
    data = response.json()
    samples = data["samples"]
    assert len(samples) >= 7
    techniques = {s["technique"] for s in samples}
    assert "clean" in techniques
    assert "timestomping" in techniques
    assert "steganography" in techniques
    assert "file_type_obfuscation" in techniques


def test_evaluation_summary_endpoint(client):
    """Verifies that /api/evaluation/summary returns canonical test set metrics."""
    response = client.get("/api/evaluation/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["operating_threshold"] == 0.5
    assert data["total_test_samples"] == 126
    assert data["independent_test_sources"] == 21
    assert len(data["modality_comparison"]) >= 6
    cm = data["confusion_matrix_full_test"]
    assert cm["tp"] + cm["fp"] + cm["tn"] + cm["fn"] == 126
    # Check FPR is ~4.76% (1 FP out of 21 clean)
    assert cm["fp"] == 1
    assert cm["tn"] == 20


def test_evaluation_ablations_endpoint(client):
    """Verifies that /api/evaluation/ablations returns all 10 experimental variants."""
    response = client.get("/api/evaluation/ablations")
    assert response.status_code == 200
    data = response.json()
    assert len(data["ablations"]) == 10
    assert "Variant 7" in data["note_cnn_ablation"] or "Image CNN" in data["note_cnn_ablation"]


def test_evaluation_curves_endpoint(client):
    """Verifies that /api/evaluation/curves returns ROC and PR curve coordinate arrays."""
    response = client.get("/api/evaluation/curves")
    assert response.status_code == 200
    data = response.json()
    assert "late_fusion" in data["roc_curves"]
    assert "late_fusion" in data["pr_curves"]
    assert len(data["roc_curves"]["late_fusion"]) > 0
    assert len(data["pr_curves"]["late_fusion"]) > 0


def test_analyze_demo_sample(client):
    """Verifies end-to-end forensic analysis on a curated benchmark demo sample."""
    demos_resp = client.get("/api/demo-samples").json()
    demo_id = demos_resp["samples"][0]["sample_id"]

    response = client.post("/api/analyze", data={"sample_id": demo_id})
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert "final_prediction" in data
    assert 0.0 <= data["final_prediction"]["manipulation_probability"] <= 1.0
    assert len(data["feature_attributions"]) > 0
    assert len(data["investigator_narrative"]) > 0
    assert "evidence_provenance" in data
    assert len(data["evidence_provenance"]["sha256"]) == 64


def test_analyze_custom_file_upload(client):
    """Verifies file upload ingestion, processing, and prediction output."""
    test_bytes = b"Sample suspect forensic evidence test buffer \x00\x01\x02"
    file_payload = {"file": ("suspect_artifact.bin", io.BytesIO(test_bytes), "application/octet-stream")}
    response = client.post("/api/analyze", files=file_payload)
    assert response.status_code == 200
    data = response.json()
    assert "analysis_id" in data
    assert data["final_prediction"]["operating_threshold"] == 0.5
    assert data["evidence_provenance"]["filename"] == "suspect_artifact.bin"
    assert data["evidence_provenance"]["file_size_bytes"] == len(test_bytes)


def test_paper_pdf_and_bib_endpoints(client):
    """Verifies that the compiled IEEE manuscript and BibTeX are served correctly."""
    pdf_resp = client.get("/api/paper/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 50000  # Camera-ready PDF is ~1MB

    bib_resp = client.get("/api/paper/bib")
    assert bib_resp.status_code == 200
    assert "@" in bib_resp.text
    assert "conlan" in bib_resp.text.lower() or "garfinkel" in bib_resp.text.lower()


def test_analyses_history_and_clear(client):
    """Verifies that analyses are recorded in session history and can be cleared."""
    history_resp = client.get("/api/analyses")
    assert history_resp.status_code == 200
    initial_count = len(history_resp.json())
    assert initial_count >= 1

    clear_resp = client.delete("/api/analyses")
    assert clear_resp.status_code == 200
    assert clear_resp.json()["cleared_count"] >= initial_count

    history_after = client.get("/api/analyses")
    assert len(history_after.json()) == 0
