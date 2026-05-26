"""Capability manifest for the lens family (consumed by auto-analyser)."""
from __future__ import annotations

from lens_contract import make_manifest

# Explicit-only — same pattern as conversation-analyser. Prose extensions already
# auto-route to document-analyser; reflection is a different interpretation of
# the same words (depth/metacognition rather than readability).
MANIFEST = make_manifest(
    name="reflection-analyser",
    accepts=["reflection", "journal", "metacognition"],
    extensions=[],  # explicit-only — invoke deliberately
    auto_routable=False,
    produces="ReflectionAnalysis",
)
