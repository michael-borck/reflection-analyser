"""CLI smoke tests."""
import json
import subprocess
import sys
from pathlib import Path


def _run(*args, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "reflection_analyser.cli", *map(str, args)],
        capture_output=True,
        text=True,
        input=stdin,
    )


def test_file(tmp_path: Path):
    p = tmp_path / "journal.md"
    p.write_text("I realised today, looking back, however that I will plan better next time.")
    r = _run(p)
    assert r.returncode == 0, r.stderr
    assert "Depth band:" in r.stdout
    assert "Markers" in r.stdout


def test_json(tmp_path: Path):
    p = tmp_path / "journal.md"
    p.write_text("I realised something significant.")
    r = _run(p, "--json")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert "depth_band" in data


def test_stdin():
    r = _run("-", stdin="I realised, looking back, that I will change.")
    assert r.returncode == 0, r.stderr
    assert "Depth band:" in r.stdout


def test_manifest_subcommand():
    r = _run("manifest")
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert data["name"] == "reflection-analyser"
