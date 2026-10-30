import json
from pathlib import Path

import httpx
import pytest

from backend.integrations import assistant
from backend.config import settings
from scripts.evaluate_assistant import evaluate, score
from test_workflow import client, auth

CATALOGUE = [{"id": "dap-50", "name": "DAP fertilizer", "unit": "50 kg bag"}]


@pytest.mark.parametrize("text", ["I want DAP in 50 kg bags.", "Nahitaji DAP ya kilo 50.", "3 bags of urea fertilizer, 50 kg each.", "-2 bags of 50 kg DAP.", "2 bags of 50 kg DAP and 3 packs of maize seed."])
def test_demo_parser_clarifies_missing_quantity_unknown_products_and_multiple_items(text):
    result = assistant.demo_parse(text, CATALOGUE)
    assert result.items == [] and result.clarification


def test_demo_parser_never_uses_pack_weight_as_count():
    result = assistant.demo_parse("DAP in 50 kg bags: I want 2 bags.", CATALOGUE)
    assert len(result.items) == 1 and result.items[0].quantity == 2


def model_response(monkeypatch, result):
    monkeypatch.setattr(settings, "ai_mode", "gemini")
    captured = []
    original_client = httpx.Client
    def handle(request):
        captured.append(json.loads(request.content))
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": json.dumps(result)}]}}]})
    monkeypatch.setattr(httpx, "Client", lambda **kwargs: original_client(transport=httpx.MockTransport(handle), **kwargs))
    return captured


@pytest.mark.parametrize("items", [
    [{"product_id": "outside-catalogue", "quantity": 2}],
    [{"product_id": "dap-50", "quantity": 2.0}],
    [{"product_id": "dap-50", "quantity": -1}],
    [{"product_id": "dap-50", "quantity": 2, "price_cents": 1}],
    [{"product_id": "dap-50", "quantity": 2}, {"product_id": "dap-50", "quantity": 3}],
])
def test_model_output_must_use_known_unique_items_and_strict_quantities(monkeypatch, items):
    model_response(monkeypatch, {"items": items, "clarification": None})
    with pytest.raises(ValueError):
        assistant.interpret("2 bags of DAP, 50 kg", CATALOGUE)


def test_model_interpretation_has_no_financial_side_effects_and_sends_no_farmer_data(client, monkeypatch):
    farmer = auth(client, "farmer-amina")
    captured = model_response(monkeypatch, {"items": [{"product_id": "dap-50", "quantity": 2}], "clarification": None})
    response = client.post("/api/assistant", headers=farmer, json={"text": "2 bags of DAP, 50 kg"})
    assert response.status_code == 200 and response.json()["mode"] == "gemini"
    payload = json.dumps(captured[0])
    assert "Amina" not in payload and "limit_cents" not in payload and "approval_reference" not in payload
    assert client.get("/api/state", headers=farmer).json()["orders"] == []
    assert client.get("/api/state", headers=farmer).json()["farmers"][0]["reserved_cents"] == 0


def test_evaluation_requires_correct_quantities_and_real_clarifications():
    case = {"items": [{"product_id": "dap-50", "quantity": 2}]}
    assert score(case, {"items": case["items"], "clarification": None})
    assert not score(case, {"items": [{"product_id": "dap-50", "quantity": 50}], "clarification": None})
    assert not score(case, {"items": [{"product_id": "dap-50", "quantity": 2.0}], "clarification": None})
    assert score({"clarification": True}, {"items": [], "clarification": "Which pack size?"})
    assert not score({"clarification": True}, {"items": case["items"], "clarification": "Which size?"})
    assert not score({"clarification": True}, {"items": [], "clarification": " "})


def test_gemini_evaluation_refuses_to_mislabel_demo_results(monkeypatch):
    monkeypatch.setattr(settings, "gemini_key", "")
    suite = json.loads((Path(__file__).resolve().parents[1] / "evaluations/assistant-cases.json").read_text())
    with pytest.raises(ValueError):
        evaluate(suite, "gemini", 1)
    monkeypatch.setattr(settings, "ai_mode", "demo")
    result = evaluate(suite, "demo", 2)
    assert result["mode"] == "demo" and result["model"] is None and result["total"] == 2
