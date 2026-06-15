"""reflection-analyser — reflective-writing depth analysis for the lens family."""
from importlib.metadata import version as _v
from pathlib import Path

from .analyser import ReflectionAnalyser
from .exceptions import ReflectionAnalyserError
from .manifest import MANIFEST
from .schemas import (
    MarkerSignal,
    ReflectionAnalysis,
)

__version__ = _v("reflection-analyser")
del _v


def analyse(path: str | Path) -> ReflectionAnalysis:
    """Analyse a reflection file by path (mirrors ``ReflectionAnalyser.analyse``)."""
    return ReflectionAnalyser().analyse(Path(path))


__all__ = [
    "ReflectionAnalyser",
    "ReflectionAnalysis",
    "ReflectionAnalyserError",
    "MarkerSignal",
    "analyse",
    "MANIFEST",
    "__version__",
]
