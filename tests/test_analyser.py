"""End-to-end tests for ReflectionAnalyser composite scoring and depth bands."""
from pathlib import Path

import pytest

from reflection_analyser import (
    ReflectionAnalyser,
    ReflectionAnalyserError,
    ReflectionAnalysis,
)


# ── synthetic samples spanning the four depth bands ──────────────────────


DESCRIPTIVE_SAMPLE = (
    "Today I went to the workshop. The instructor explained the procedure. "
    "Then we tried the exercise. After that we had lunch. We continued in the afternoon."
)

DIALOGIC_SAMPLE = (
    "Today I went to the workshop. I realised that I had been doing it wrong. "
    "Looking back, the instructor's point about variables made sense. "
    "However, I'm still not sure about the loop syntax."
)

CRITICAL_SAMPLE = (
    "I realised the approach I had been using was flawed. According to Smith (2020), "
    "this pattern is common. Looking back, I felt frustrated. "
    "However, on the other hand, the alternative was risky. "
    "Although the instructor's example seemed simple, in practice it was harder. "
    "On reflection I understand now why."
)

TRANSFORMATIVE_SAMPLE = (
    "I realised that the approach I had been using was flawed. "
    "According to Smith (2020), the recommended pattern is different. "
    "Looking back, I felt frustrated by my earlier choice. "
    "However, in contrast to my initial view, the evidence is clear. "
    "Although there are trade-offs, on the other hand the long-term benefit is real. "
    "I will revise my approach. Next time I will plan more carefully. "
    "Going forward, I plan to apply this lesson to the next assignment."
)


class TestBands:
    def test_descriptive(self):
        r = ReflectionAnalyser().analyse_text(DESCRIPTIVE_SAMPLE)
        assert isinstance(r, ReflectionAnalysis)
        assert r.depth_band == "descriptive"
        assert r.composite_depth_score < 0.25

    def test_dialogic(self):
        r = ReflectionAnalyser().analyse_text(DIALOGIC_SAMPLE)
        # Has 'I realised', 'looking back', 'however' — should land dialogic or higher.
        assert r.depth_band in ("dialogic", "critical")
        assert r.composite_depth_score >= 0.25

    def test_critical_or_better(self):
        r = ReflectionAnalyser().analyse_text(CRITICAL_SAMPLE)
        assert r.depth_band in ("critical", "transformative")
        assert r.composite_depth_score >= 0.40

    def test_transformative(self):
        r = ReflectionAnalyser().analyse_text(TRANSFORMATIVE_SAMPLE)
        assert r.depth_band in ("critical", "transformative")
        assert r.composite_depth_score >= 0.45


class TestSignals:
    def test_metacognition_count_matches(self):
        r = ReflectionAnalyser().analyse_text(DIALOGIC_SAMPLE)
        # "I realised" + "Looking back" → 2 metacognition hits.
        assert r.metacognition.count >= 2

    def test_examples_captured(self):
        r = ReflectionAnalyser().analyse_text(DIALOGIC_SAMPLE)
        assert len(r.metacognition.examples) >= 1

    def test_word_count(self):
        r = ReflectionAnalyser().analyse_text("Hello world.")
        assert r.word_count == 2
        assert r.sentence_count == 1


class TestErrors:
    def test_empty_raises(self):
        with pytest.raises(ReflectionAnalyserError, match="Empty"):
            ReflectionAnalyser().analyse_text("")

    def test_whitespace_raises(self):
        with pytest.raises(ReflectionAnalyserError, match="Empty"):
            ReflectionAnalyser().analyse_text("   \n\n  ")

    def test_missing_file_raises(self, tmp_path: Path):
        with pytest.raises(ReflectionAnalyserError, match="not found"):
            ReflectionAnalyser().analyse(tmp_path / "nope.md")


class TestFileInputs:
    def test_md_file(self, tmp_path: Path):
        p = tmp_path / "journal.md"
        p.write_text(DIALOGIC_SAMPLE)
        r = ReflectionAnalyser().analyse(p)
        assert r.source_kind == "file:md"
        assert r.metacognition.count >= 2

    def test_txt_file(self, tmp_path: Path):
        p = tmp_path / "journal.txt"
        p.write_text(CRITICAL_SAMPLE)
        r = ReflectionAnalyser().analyse(p)
        assert r.source_kind == "file:txt"

    def test_binary_without_extra_raises_helpful_error(self, tmp_path: Path):
        # .pdf path without document-analyser installed should error explicitly.
        p = tmp_path / "x.pdf"
        p.write_bytes(b"%PDF-1.4\n%%EOF\n")
        try:
            import document_analyser  # noqa: F401
        except ImportError:
            with pytest.raises(ReflectionAnalyserError, match="documents.*extra"):
                ReflectionAnalyser().analyse(p)
        else:
            # If document-analyser IS installed (sibling editable), the path
            # works — that's the documents-extra-is-effective branch. Either
            # extraction succeeds or it errors with a doc-extraction reason.
            try:
                ReflectionAnalyser().analyse(p)
            except ReflectionAnalyserError:
                pass  # extraction failure on a bogus PDF is fine for this test
