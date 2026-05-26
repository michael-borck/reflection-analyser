"""HTTP smoke tests — the family contract surface."""
from fastapi.testclient import TestClient

from reflection_analyser.api import app
from reflection_analyser.manifest import MANIFEST


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"] == MANIFEST["version"]


def test_manifest():
    r = client.get("/manifest")
    assert r.status_code == 200
    m = r.json()
    assert m["name"] == "reflection-analyser"
    assert m["auto_routable"] is False
    assert m["extensions"] == []


def test_analyse_text_form_field():
    sample = "I realised today, looking back, however that I will plan better next time."
    r = client.post("/analyse", data={"text": sample})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["word_count"] > 0
    assert body["depth_band"] in {"descriptive", "dialogic", "critical", "transformative"}


def test_analyse_file_upload():
    text = "I realised something. Looking back, however, I noticed it. I will change."
    r = client.post("/analyse", files={"file": ("journal.md", text.encode(), "text/markdown")})
    assert r.status_code == 200, r.text


def test_analyse_no_input_returns_422():
    r = client.post("/analyse")
    assert r.status_code == 422


def test_analyse_both_inputs_returns_422():
    r = client.post(
        "/analyse",
        data={"text": "x"},
        files={"file": ("a.md", b"y", "text/markdown")},
    )
    assert r.status_code == 422
