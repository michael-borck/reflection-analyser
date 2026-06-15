"""Canonical public-surface contract for the lens family."""
import reflection_analyser as ra


def test_canonical_names_importable():
    from reflection_analyser import (  # noqa: F401
        MANIFEST,
        ReflectionAnalyser,
        ReflectionAnalysis,
        ReflectionAnalyserError,
        analyse,
        __version__,
    )


def test_analyse_is_callable():
    assert callable(ra.analyse)


def test_manifest_name():
    assert ra.MANIFEST["name"] == "reflection-analyser"


def test_version_is_str():
    assert isinstance(ra.__version__, str)


def test_names_in_all():
    for name in (
        "ReflectionAnalyser",
        "ReflectionAnalysis",
        "analyse",
        "MANIFEST",
        "__version__",
    ):
        assert name in ra.__all__
