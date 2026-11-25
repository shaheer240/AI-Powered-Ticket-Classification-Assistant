import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import app

client = TestClient(app)


def post(ticket, **extra):
    return client.post("/analyze", json={"ticket": ticket, **extra})


def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_categories_endpoint():
    assert len(client.get("/categories").json()) == 10


def test_analyze_valid_ticket():
    res = post("I was charged twice for the same order.", prompt_version="v2")
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "payment_issue"
    assert body["prompt_version"] == "v2"


def test_blank_ticket_returns_400():
    assert post("   ").status_code == 400


def test_missing_ticket_returns_422():
    assert client.post("/analyze", json={}).status_code == 422


def test_bad_prompt_version_returns_422():
    assert post("Where is my order?", prompt_version="v9").status_code == 422


def test_invalid_model_output_returns_502():
    assert post("Where is my order?", simulate="bad_output").status_code == 502


def test_backend_down_returns_503():
    assert post("Where is my order?", simulate="backend_down").status_code == 503
