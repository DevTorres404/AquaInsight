"""Unit tests for the FastAPI water quality service."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api import app, FEATURE_ORDER, PIPELINE, SELECTION_REPORT

client = TestClient(app)
pytestmark = pytest.mark.http


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Random Forest" in data["model"]
    assert data["test_macro_f1"] > 0.85


def test_presets_endpoint():
    response = client.get("/api/v1/presets")
    assert response.status_code == 200
    presets = response.json()
    assert "case_a_safe" in presets
    assert "case_b_contaminated" in presets
    assert "case_c_adversarial" in presets


def test_predict_safe_sample():
    presets = client.get("/api/v1/presets").json()
    safe_data = presets["case_a_safe"]["data"]
    response = client.post("/api/v1/predict", json=safe_data)
    assert response.status_code == 200
    res = response.json()
    assert res["prediction"] == 1
    assert "Segura" in res["label"]
    assert res["probability_safe"] > 0.5
    assert len(res["who_alerts"]) == 0


def test_predict_contaminated_sample():
    presets = client.get("/api/v1/presets").json()
    cont_data = presets["case_b_contaminated"]["data"]
    response = client.post("/api/v1/predict", json=cont_data)
    assert response.status_code == 200
    res = response.json()
    assert res["prediction"] == 0
    assert "Contaminada" in res["label"]
    assert res["probability_unsafe"] > 0.8
    assert len(res["who_alerts"]) > 0


def test_predict_adversarial_sample():
    presets = client.get("/api/v1/presets").json()
    adv_data = presets["case_c_adversarial"]["data"]
    response = client.post("/api/v1/predict", json=adv_data)
    assert response.status_code == 200
    res = response.json()
    assert res["prediction"] == 1  # Preserve the frozen model's known failure.
    assert res["conflict"] is True
    assert "no están calibradas" in res["interpretation_note"]
    assert len(res["who_alerts"]) > 0
    assert len(res["out_of_range_features"]) > 0


def test_invalid_negative_input():
    presets = client.get("/api/v1/presets").json()
    bad_data = presets["case_a_safe"]["data"].copy()
    bad_data["lead"] = -1.0  # Physically impossible negative
    response = client.post("/api/v1/predict", json=bad_data)
    assert response.status_code == 422  # Unprocessable Entity from Pydantic


@pytest.mark.parametrize("feature", FEATURE_ORDER)
def test_all_features_reject_negative_before_inference(feature):
    sample = client.get("/api/v1/presets").json()["case_a_safe"]["data"]
    sample[feature] = -0.08
    with patch.object(PIPELINE, "predict") as infer:
        response = client.post("/api/v1/predict", json=sample)
    assert response.status_code == 422
    infer.assert_not_called()


@pytest.mark.parametrize("value", ["", "abc", "1abc", "NaN", "Infinity", "-Infinity", "1e309", None, True])
def test_invalid_values_rejected_before_inference(value):
    sample = client.get("/api/v1/presets").json()["case_a_safe"]["data"]
    sample["ammonia"] = value
    with patch.object(PIPELINE, "predict") as infer:
        response = client.post("/api/v1/predict", json=sample)
    assert response.status_code == 422
    infer.assert_not_called()


def test_missing_and_unexpected_features_are_rejected():
    sample = client.get("/api/v1/presets").json()["case_a_safe"]["data"]
    sample.pop("arsenic")
    assert client.post("/api/v1/predict", json=sample).status_code == 422
    sample["arsenic"] = 0.01
    sample["unknown"] = 1
    assert client.post("/api/v1/predict", json=sample).status_code == 422


def test_decimal_comma_and_feature_order():
    sample = client.get("/api/v1/presets").json()["case_a_safe"]["data"]
    sample["arsenic"] = "0,01"
    response = client.post("/api/v1/predict", json=dict(reversed(list(sample.items()))))
    assert response.status_code == 200
    assert response.json()["prediction"] == 1
    assert SELECTION_REPORT["test_evaluations"] == 1


def test_large_finite_values_fail_gracefully():
    sample = client.get("/api/v1/presets").json()["case_a_safe"]["data"]
    sample["arsenic"] = 1e300
    assert client.post("/api/v1/predict", json=sample).status_code == 422
