"""CLI entry point for reflection-analyser."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    from lens_contract import run_contract_subcommands

    from .manifest import MANIFEST

    if run_contract_subcommands(
        MANIFEST,
        app_path="reflection_analyser.api:app",
        default_port=8015,
        env_prefix="REFLECTION_ANALYSER",
    ):
        return

    parser = argparse.ArgumentParser(
        prog="reflection-analyser",
        description="Reflective-writing analysis — metacognition, criticality, depth (Moon-style bands)",
        epilog="subcommands: `serve` (HTTP API on port 8015), `manifest` (capability manifest)",
    )
    parser.add_argument("file", help="File path; or '-' to read text from stdin")
    parser.add_argument("--json", action="store_true", dest="as_json", help="Output raw JSON")
    args = parser.parse_args()

    _run(args)


def _run(args) -> None:
    from .analyser import ReflectionAnalyser
    from .exceptions import ReflectionAnalyserError

    try:
        if args.file == "-":
            text = sys.stdin.read()
            result = ReflectionAnalyser().analyse_text(text, source_kind="stdin")
        else:
            result = ReflectionAnalyser().analyse(Path(args.file))
    except ReflectionAnalyserError as e:
        if args.as_json:
            print(json.dumps({"error": str(e)}), file=sys.stderr)
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.as_json:
        print(result.model_dump_json(indent=2))
        return

    _print_summary(result)


def _print_summary(result) -> None:
    print(f"Words:       {result.word_count:,}  Sentences: {result.sentence_count}")
    print(f"Depth band:  {result.depth_band}  (composite score: {result.composite_depth_score:.2f})")
    print()
    print("Markers (count · per-100-words):")
    for name, sig in (
        ("metacognition",   result.metacognition),
        ("criticality",     result.criticality),
        ("evidence",        result.evidence),
        ("affect",          result.affect),
        ("forward-looking", result.forward_looking),
    ):
        print(f"  {name:<16} {sig.count:>3}  ·  {sig.coverage_per_100_words:.2f}/100w")
    # Show one example sentence for the strongest marker.
    strongest = max(
        [("metacognition", result.metacognition), ("criticality", result.criticality),
         ("evidence", result.evidence), ("affect", result.affect),
         ("forward-looking", result.forward_looking)],
        key=lambda kv: kv[1].count,
    )
    if strongest[1].examples:
        print()
        print(f"Strongest signal: {strongest[0]}")
        for ex in strongest[1].examples[:2]:
            short = ex[:160] + ("…" if len(ex) > 160 else "")
            print(f"  · {short}")


if __name__ == "__main__":
    main()
