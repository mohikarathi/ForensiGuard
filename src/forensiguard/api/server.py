"""FastAPI application entrypoint for ForensiGuard REST backend."""

from contextlib import asynccontextmanager
import os
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict, List, Optional
import uuid

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse

from forensiguard.api.schemas import (
    AblationsResponse,
    AnalysisSummaryItem,
    AnalyzeResponse,
    CurvesResponse,
    DemoSamplesResponse,
    EvaluationSummaryResponse,
    HealthResponse,
    ModelsResponse,
    OverviewResponse,
)
from forensiguard.api.service import ForensiGuardService

MAX_UPLOAD_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB max upload limit


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize service and load models on startup
    service = ForensiGuardService.get_instance()
    app.state.service = service
    yield
    # Cleanup actions on shutdown if needed


app = FastAPI(
    title="ForensiGuard REST API",
    description="Research prototype API for multimodal digital evidence anti-forensic triage",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_service() -> ForensiGuardService:
    return ForensiGuardService.get_instance()


# -----------------------------------------------------------------------------
# Core Metadata & Overview Endpoints
# -----------------------------------------------------------------------------


@app.get("/api/health", response_model=HealthResponse, tags=["System"])
def health():
    """Returns application health, model checkpoint status, and device info."""
    return get_service().get_health()


@app.get("/api/overview", response_model=OverviewResponse, tags=["Overview"])
def overview():
    """Returns academic project metadata, benchmark split distributions, and pipeline stages."""
    return get_service().get_overview()


@app.get("/api/models", response_model=ModelsResponse, tags=["Models"])
def models():
    """Returns technical details and status for all five model components."""
    return get_service().get_models()


@app.get("/api/demo-samples", response_model=DemoSamplesResponse, tags=["Demo Samples"])
def demo_samples():
    """Returns a curated list of genuine benchmark samples across manipulation techniques."""
    return get_service().get_demo_samples()


# -----------------------------------------------------------------------------
# Evidence Analysis Endpoints
# -----------------------------------------------------------------------------


@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_evidence(
    file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
):
    """
    Executes complete defensive forensic analysis on uploaded evidence or a selected demo sample.
    Never alters target evidence.
    """
    service = get_service()
    if service.pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ForensiGuard models are not currently loaded. Verify artifacts/models directory.",
        )

    # Branch 1: Pre-indexed Demo Sample Selected
    if sample_id:
        demo_resp = service.get_demo_samples()
        matched = next((s for s in demo_resp.samples if s.sample_id == sample_id), None)
        if not matched:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Demo sample '{sample_id}' not found in benchmark manifest.",
            )

        if matched.is_adaptive:
            # Historical adaptive stress test
            return service.analyze_evidence(
                file_path=Path("/dev/null"),
                original_filename=matched.filename,
                demo_ground_truth={
                    "technique": matched.technique,
                    "subtype": matched.subtype,
                    "ground_truth_label": matched.ground_truth_label,
                    "provenance": "Experiment 3: Adaptive Evasion Stress Test",
                },
                is_adaptive_simulated=True,
            )

        # Locate genuine benchmark file on disk
        target_path: Optional[Path] = None
        if service.manifest_path.exists():
            import pandas as pd
            df = pd.read_csv(service.manifest_path)
            row_match = df[df["filename"] == matched.filename]
            if not row_match.empty:
                rel = row_match.iloc[0]["file_path"]
                candidate = service.benchmark_dir / rel
                if candidate.exists():
                    target_path = candidate

        if not target_path or not target_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Benchmark file '{matched.filename}' could not be located on disk.",
            )

        return service.analyze_evidence(
            file_path=target_path,
            original_filename=matched.filename,
            demo_ground_truth={
                "technique": matched.technique,
                "subtype": matched.subtype,
                "ground_truth_label": matched.ground_truth_label,
                "provenance": f"ForensiGuard-Bench-v1 ({matched.split} split)",
            },
        )

    # Branch 2: Custom File Uploaded
    if file is None or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either an evidence file must be uploaded or a demo sample_id must be provided.",
        )

    # Path traversal and filename sanitization
    raw_name = Path(file.filename).name
    if not raw_name or "\0" in raw_name or ".." in raw_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or dangerous filename supplied.",
        )

    # Create safe isolated temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="forensiguard_upload_"))
    temp_file_path = temp_dir / raw_name

    try:
        # Stream file to disk with strict size enforcement
        size = 0
        with open(temp_file_path, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"Uploaded file exceeds maximum permitted size of {MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)}MB.",
                    )
                buffer.write(chunk)

        if size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes).",
            )

        result = service.analyze_evidence(
            file_path=temp_file_path,
            original_filename=raw_name,
            demo_ground_truth=None,
        )
        return result

    finally:
        # Safely purge temporary upload container to avoid data leakage
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# -----------------------------------------------------------------------------
# Analysis History Endpoints
# -----------------------------------------------------------------------------


@app.get("/api/analyses", response_model=List[AnalysisSummaryItem], tags=["History"])
def get_analysis_history():
    """Returns the list of recent analyses performed during this application session."""
    return get_service().get_analyses()


@app.get("/api/analyses/{analysis_id}", response_model=AnalyzeResponse, tags=["History"])
def get_analysis_by_id(analysis_id: str):
    """Retrieves the full structured triage report for a previous analysis."""
    result = get_service().get_analysis_by_id(analysis_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID '{analysis_id}' not found in session history.",
        )
    return result


@app.delete("/api/analyses", tags=["History"])
def clear_analysis_history():
    """Clears all session analysis history."""
    count = get_service().clear_analyses()
    return {"message": "Analysis history cleared successfully", "cleared_count": count}


# -----------------------------------------------------------------------------
# Model Evaluation & Research Endpoints
# -----------------------------------------------------------------------------


@app.get("/api/evaluation/summary", response_model=EvaluationSummaryResponse, tags=["Evaluation"])
def evaluation_summary():
    """Returns canonical test set metrics, modality comparison, and confusion matrix."""
    return get_service().get_evaluation_summary()


@app.get("/api/evaluation/ablations", response_model=AblationsResponse, tags=["Evaluation"])
def evaluation_ablations():
    """Returns complete 10-variant architectural ablation study results."""
    return get_service().get_ablations()


@app.get("/api/evaluation/curves", response_model=CurvesResponse, tags=["Evaluation"])
def evaluation_curves():
    """Returns ROC and Precision-Recall curve coordinates for Recharts visualization."""
    return get_service().get_curves()


# -----------------------------------------------------------------------------
# Safe Document & Sample Serving Endpoints
# -----------------------------------------------------------------------------


@app.get("/api/sample-preview/{sample_id}", tags=["Media"])
def get_sample_preview(sample_id: str):
    """Safely serves image preview for genuine demo benchmark artifacts."""
    service = get_service()
    demo_resp = service.get_demo_samples()
    matched = next((s for s in demo_resp.samples if s.sample_id == sample_id), None)
    if not matched or not matched.is_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image preview not available.")

    if service.manifest_path.exists():
        import pandas as pd
        df = pd.read_csv(service.manifest_path)
        row = df[df["filename"] == matched.filename]
        if not row.empty:
            target = service.benchmark_dir / row.iloc[0]["file_path"]
            if target.exists():
                return FileResponse(target, media_type=matched.detected_mime_type)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact file not found.")


@app.get("/api/paper/pdf", tags=["Research"])
def get_paper_pdf():
    """Safely serves the compiled camera-ready IEEE conference manuscript PDF."""
    service = get_service()
    if not service.paper_pdf_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Compiled paper PDF (paper/main.pdf) not found on disk.",
        )
    return FileResponse(
        service.paper_pdf_path,
        media_type="application/pdf",
        filename="ForensiGuard_IEEE_Paper.pdf",
    )


@app.get("/api/paper/bib", tags=["Research"])
def get_paper_bib():
    """Safely serves the BibTeX bibliography source file."""
    service = get_service()
    if not service.paper_bib_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="BibTeX bibliography (paper/references.bib) not found.",
        )
    with open(service.paper_bib_path, "r", encoding="utf-8") as f:
        content = f.read()
    return PlainTextResponse(content, media_type="text/plain")


# -----------------------------------------------------------------------------
# Static Frontend Serving (if production build exists)
# -----------------------------------------------------------------------------
frontend_dist = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    from fastapi.staticfiles import StaticFiles

    if (frontend_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def serve_spa(full_path: str):
        if full_path.startswith("api"):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API endpoint not found")
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(frontend_dist / "index.html")

