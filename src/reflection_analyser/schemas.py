"""Pydantic schemas for reflection-analyser output."""
from __future__ import annotations

from pydantic import BaseModel, Field


class MarkerSignal(BaseModel):
    """Counts + sample for one reflection-marker family."""

    count: int = 0
    coverage_per_100_words: float = Field(
        0.0,
        description="Hits per 100 words — a length-normalised proxy for marker density.",
    )
    examples: list[str] = Field(
        default_factory=list,
        description="First few sentences where the marker fired (capped, for transparency).",
    )


class ReflectionAnalysis(BaseModel):
    """Top-level result returned by ReflectionAnalyser.analyse* methods."""

    word_count: int = 0
    sentence_count: int = 0

    # Per-marker signals
    metacognition: MarkerSignal
    criticality: MarkerSignal
    evidence: MarkerSignal
    affect: MarkerSignal
    forward_looking: MarkerSignal

    # Composite scoring
    composite_depth_score: float = Field(
        0.0,
        description="0–1; weighted blend of per-marker coverages (see analyser._compute_depth).",
        ge=0.0,
        le=1.0,
    )
    depth_band: str = Field(
        "descriptive",
        description="descriptive | dialogic | critical | transformative",
    )

    # Provenance / source-of-input
    source_kind: str = Field(
        "text",
        description="'text' | 'file:txt' | 'file:md' | 'file:pdf' | 'file:docx' | …",
    )

    # Pooled, L2-normalised reflection vector from lens-embed (pinned
    # all-MiniLM-L6-v2). Comparable across members; None unless [embeddings] installed.
    embedding: list[float] | None = None
