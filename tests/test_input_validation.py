"""Exercise real schema and pipeline inference without needing HTTP or test data."""

from unittest.mock import patch

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from backend.api import FEATURE_ORDER, PIPELINE, WaterSampleInput, get_presets, predict_water_quality


@pytest.mark.parametrize("feature", FEATURE_ORDER)
def test_schema_rejects_negative_measurements(feature):
    sample = dict(get_presets()["case_a_safe"]["data"])
    sample[feature] = -0.08
    with patch.object(PIPELINE, "predict") as predict:
        with pytest.raises(ValidationError):
            predict_water_quality(WaterSampleInput(**sample))
        predict.assert_not_called()


@pytest.mark.parametrize("value", ["", "abc", "1abc", "NaN", "Infinity", "-Infinity", "1e309", None, True])
def test_schema_rejects_invalid_values(value):
    sample = dict(get_presets()["case_a_safe"]["data"])
    sample["ammonia"] = value
    with pytest.raises(ValidationError):
        WaterSampleInput(**sample)


def test_schema_rejects_missing_or_unknown_features():
    sample = dict(get_presets()["case_a_safe"]["data"])
    sample.pop("arsenic")
    with pytest.raises(ValidationError):
        WaterSampleInput(**sample)
    sample.update(arsenic=0.01, unexpected=1)
    with pytest.raises(ValidationError):
        WaterSampleInput(**sample)


def test_decimal_comma_and_order_preserve_prediction():
    sample = dict(get_presets()["case_a_safe"]["data"])
    sample["arsenic"] = "0,01"
    result = predict_water_quality(WaterSampleInput(**dict(reversed(list(sample.items())))))
    assert result.prediction == 1
    assert result.conflict is False
    assert not result.who_alerts


@pytest.mark.parametrize("key,expected", [("case_a_safe",1),("case_b_contaminated",0),("case_c_adversarial",1)])
def test_real_inference_and_conflicts(key, expected):
    result = predict_water_quality(WaterSampleInput(**get_presets()[key]["data"]))
    assert result.prediction == expected
    assert result.probability_safe + result.probability_unsafe == pytest.approx(1)
    if key != "case_a_safe":
        assert result.who_alerts
        assert result.out_of_range_features
    assert result.conflict is (key == "case_c_adversarial")
    assert "no están calibradas" in result.interpretation_note


def test_excessively_large_finite_values_produce_user_error():
    sample = dict(get_presets()["case_a_safe"]["data"])
    sample["arsenic"] = 1e300
    with pytest.raises(HTTPException) as error:
        predict_water_quality(WaterSampleInput(**sample))
    assert error.value.status_code == 422
