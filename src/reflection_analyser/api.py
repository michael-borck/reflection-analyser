"""FastAPI service — reflection-analyser."""
from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from lens_contract import add_contract_routes, add_cors, upload_tempfile

from .analyser import ReflectionAnalyser
from .exceptions import ReflectionAnalyserError
from .manifest import MANIFEST
from .schemas import ReflectionAnalysis

_lens = ReflectionAnalyser()

app = FastAPI(
    title="reflection-analyser",
    description="Reflective-writing analysis — metacognition, criticality, depth (Moon-style bands)",
    version=MANIFEST["version"],
    docs_url="/docs",
    redoc_url="/redoc",
)

add_contract_routes(app, MANIFEST)
add_cors(app, env_prefix="REFLECTION_ANALYSER")


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": "reflection-analyser",
        "version": MANIFEST["version"],
        "status": "running",
        "endpoints": {"health": "/health", "manifest": "/manifest", "analyse": "/analyse"},
    }


@app.post("/analyse", response_model=ReflectionAnalysis)
async def analyse(
    file: UploadFile | None = File(None, description="Reflection file (.txt/.md or .pdf/.docx with [documents])"),
    text: str | None = Form(None, description="Raw reflection text — use instead of file upload"),
) -> ReflectionAnalysis:
    if file is None and not text:
        raise HTTPException(status_code=422, detail="Supply either a 'file' upload or a 'text' form field")
    if file is not None and text:
        raise HTTPException(status_code=422, detail="Supply only one of 'file' or 'text', not both")

    if text:
        try:
            return _lens.analyse_text(text, source_kind="text")
        except ReflectionAnalyserError as e:
            raise HTTPException(status_code=400, detail=str(e))

    # file branch
    content = await file.read()  # type: ignore[union-attr]
    if not content:
        raise HTTPException(status_code=422, detail="Empty file")
    with upload_tempfile(content, file.filename) as tmp_path:  # type: ignore[union-attr]
        try:
            return _lens.analyse(tmp_path)
        except ReflectionAnalyserError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
