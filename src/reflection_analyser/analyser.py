"""Core reflection analyser — text → markers → composite depth → Moon-style band."""
from __future__ import annotations

import re
from pathlib import Path

from .exceptions import ReflectionAnalyserError
from .lexicon import lexicons
from reflection_analyser.embedding import embed_document
from .schemas import MarkerSignal, ReflectionAnalysis

# Weighting per marker family in the composite depth score. Tuned so that
# metacognition + criticality + evidence dominate, with affect and forward-
# looking acting as supporting indicators. Sums to 1.0.
_WEIGHTS = {
    "metacognition": 0.30,
    "criticality":   0.25,
    "evidence":      0.20,
    "affect":        0.10,
    "forward":       0.15,
}

# A marker reaches its weight-cap when its coverage hits this many hits per
# 100 words. Avoids a wordy passage with 30 'however's saturating the score.
_COVERAGE_CAP_PER_100W = 2.0

# Moon-style band thresholds. Tuneable per rubric.
_BAND_THRESHOLDS = [
    (0.75, "transformative"),
    (0.50, "critical"),
    (0.25, "dialogic"),
    (0.00, "descriptive"),
]

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_WORD_SPLIT = re.compile(r"\b\w+\b")

_TEXT_SUFFIXES = {".txt", ".md", ".markdown", ".text", ".rst", ".qmd", ""}


class ReflectionAnalyser:
    """Score the reflective depth of a piece of writing."""

    def analyse_text(self, text: str, *, source_kind: str = "text") -> ReflectionAnalysis:
        if not text or not text.strip():
            raise ReflectionAnalyserError("Empty input — nothing to analyse")

        words = _WORD_SPLIT.findall(text)
        word_count = len(words)
        sentences = [s for s in _SENTENCE_SPLIT.split(text) if s.strip()]

        lex = lexicons()
        signals: dict[str, MarkerSignal] = {}
        for name, compiled in lex.items():
            count, samples = compiled.find_hits(text, sentences)
            coverage = (count / word_count * 100) if word_count else 0.0
            signals[name] = MarkerSignal(
                count=count,
                coverage_per_100_words=round(coverage, 4),
                examples=samples,
            )

        composite = _compute_depth(signals)
        band = _band_for(composite)

        embedding = embed_document(text)

        return ReflectionAnalysis(
            word_count=word_count,
            sentence_count=len(sentences),
            metacognition=signals["metacognition"],
            criticality=signals["criticality"],
            evidence=signals["evidence"],
            affect=signals["affect"],
            forward_looking=signals["forward"],
            composite_depth_score=round(composite, 4),
            depth_band=band,
            source_kind=source_kind,
            embedding=embedding,
        )

    def analyse(self, path: str | Path) -> ReflectionAnalysis:
        """Read a file (text directly, binary via document-analyser if [documents] extra is installed)."""
        p = Path(path)
        if not p.exists():
            raise ReflectionAnalyserError(f"File not found: {p}")

        suffix = p.suffix.lower()
        if suffix in _TEXT_SUFFIXES:
            text = p.read_text(encoding="utf-8", errors="replace")
            return self.analyse_text(text, source_kind=f"file:{suffix.lstrip('.') or 'text'}")

        # Binary path → compose with document-analyser if available.
        try:
            from document_analyser.extraction import extract_text
        except ImportError as e:
            raise ReflectionAnalyserError(
                f"Reading {suffix} requires the [documents] extra "
                f"(pip install 'reflection-analyser[documents]'): {e}"
            ) from e

        try:
            text = extract_text(p)
        except Exception as e:
            raise ReflectionAnalyserError(f"document-analyser could not extract text from {p}: {e}") from e

        return self.analyse_text(text, source_kind=f"file:{suffix.lstrip('.')}")


def _compute_depth(signals: dict[str, MarkerSignal]) -> float:
    """Weighted composite of capped per-marker coverages, normalised to 0–1."""
    score = 0.0
    for name, weight in _WEIGHTS.items():
        sig = signals.get(name)
        if sig is None:
            continue
        # Normalise coverage to [0, 1] by capping at _COVERAGE_CAP_PER_100W.
        normalised = min(sig.coverage_per_100_words / _COVERAGE_CAP_PER_100W, 1.0)
        score += weight * normalised
    return max(0.0, min(score, 1.0))


def _band_for(composite: float) -> str:
    for threshold, name in _BAND_THRESHOLDS:
        if composite >= threshold:
            return name
    return "descriptive"
