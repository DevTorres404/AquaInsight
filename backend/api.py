"""Academic inference service for water quality dataset classification.

Exposes endpoints for health check, presets, and real-time prediction
using the frozen scikit-learn pipeline from Phase IV.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "final_pipeline.joblib"
REPORT_PATH = ROOT / "reports" / "phase4_selection.json"

WHO_LIMITS_MG_L: Dict[str, tuple[float, str]] = {
    "arsenic": (0.01, "Arsénico"),
    "barium": (1.3, "Bario"),
    "cadmium": (0.003, "Cadmio"),
    "chromium": (0.05, "Cromo total"),
    "copper": (2.0, "Cobre"),
    "flouride": (1.5, "Fluoruro"),
    "lead": (0.01, "Plomo"),
    "nitrates": (50.0, "Nitrato como NO₃⁻"),
    "nitrites": (3.0, "Nitrito como NO₂⁻"),
    "selenium": (0.04, "Selenio"),
    "uranium": (0.03, "Uranio (toxicidad química)"),
}

# Load serialized pipeline and metadata once at startup
if not MODEL_PATH.is_file() or not REPORT_PATH.is_file():
    raise RuntimeError("Final model artifacts not found. Run backend/phase4_finalize.py first.")

PIPELINE = joblib.load(MODEL_PATH)
with open(REPORT_PATH, "r", encoding="utf-8") as f:
    SELECTION_REPORT = json.load(f)

FEATURE_ORDER: List[str] = SELECTION_REPORT["feature_order"]
TRAIN_MIN: Dict[str, float] = SELECTION_REPORT["train_feature_min"]
TRAIN_MAX: Dict[str, float] = SELECTION_REPORT["train_feature_max"]
INTERPRETATION_NOTE = (
    "Clasificación académica según etiquetas del dataset, sin certificación de potabilidad. "
    "Las probabilidades de clase no están calibradas como riesgo sanitario. "
    "Las alertas OMS son condicionales: requieren confirmar mg/L, especie química y método. "
    "Las unidades originales del dataset no están verificadas para todas las variables."
)

SAFE_CASE = {
    "aluminium": 0.08, "ammonia": 14.96, "arsenic": 0.01, "barium": 0.17,
    "cadmium": 0.002, "chloramine": 6.21, "chromium": 0.0, "copper": 0.81,
    "flouride": 0.24, "bacteria": 0.15, "viruses": 0.005, "lead": 0.005,
    "nitrates": 16.78, "nitrites": 1.58, "mercury": 0.002, "perchlorate": 18.68,
    "radium": 1.67, "selenium": 0.04, "silver": 0.0, "uranium": 0.03,
}
CONTAMINATED_CASE = {
    "aluminium": 3.90, "ammonia": 22.64, "arsenic": 0.41, "barium": 0.34,
    "cadmium": 0.03, "chloramine": 7.94, "chromium": 0.06, "copper": 0.28,
    "flouride": 0.28, "bacteria": 0.0, "viruses": 0.0, "lead": 0.137,
    "nitrates": 55.0, "nitrites": 1.55, "mercury": 0.009, "perchlorate": 13.18,
    "radium": 6.93, "selenium": 0.10, "silver": 0.26, "uranium": 0.02,
}
ADVERSARIAL_CASE = {
    **SAFE_CASE, "arsenic": 9.0, "nitrates": 150.0, "cadmium": 2.0, "lead": 5.0,
}


def load_artifacts():
    return PIPELINE, SELECTION_REPORT


def validate_inputs(raw: dict[str, Any], features: list[str]) -> dict[str, float]:
    """Validate dictionary of inputs, checking non-negative, numeric, and finite values."""
    import math
    values = {}
    for feature in features:
        if isinstance(raw.get(feature), bool):
            raise ValueError(f"{feature} debe ser numérico, no booleano.")
        text = str(raw.get(feature, "")).strip()
        if not text:
            raise ValueError(f"Falta el valor de {feature}.")
        try:
            value = float(text.replace(",", "."))
        except ValueError as err:
            raise ValueError(f"{feature} debe ser numérico.") from err
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{feature} debe ser finito y no negativo.")
        values[feature] = value
    return values


def limit_alerts(values: dict[str, float]) -> list[str]:
    alerts = []
    for feature, (limit, label) in WHO_LIMITS_MG_L.items():
        if values.get(feature, 0.0) > limit:
            alerts.append(f"{label}: {values[feature]:g} > {limit:g} mg/L")
    quotient = values.get("nitrates", 0.0) / 50.0 + values.get("nitrites", 0.0) / 3.0
    if quotient > 1.0:
        alerts.append(f"Nitrato + nitrito: índice combinado {quotient:.2f} > 1")
    return alerts


class WaterSampleInput(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)

    @field_validator("*", mode="before")
    @classmethod
    def validate_measurement(cls, value: Any, info: ValidationInfo) -> float:
        """Apply the same validation to direct API clients and the UI."""
        return validate_inputs({info.field_name: value}, [info.field_name])[info.field_name]

    aluminium: float = Field(..., ge=0.0, description="Aluminium value in original dataset scale (unit unverified)")
    ammonia: float = Field(..., ge=0.0, description="Ammonia value in original dataset scale")
    arsenic: float = Field(..., ge=0.0, description="Arsenic value in original dataset scale (unit unverified)")
    barium: float = Field(..., ge=0.0, description="Barium value in original dataset scale (unit unverified)")
    cadmium: float = Field(..., ge=0.0, description="Cadmium value in original dataset scale (unit unverified)")
    chloramine: float = Field(..., ge=0.0, description="Chloramine value in original dataset scale (unit unverified)")
    chromium: float = Field(..., ge=0.0, description="Chromium value in original dataset scale (unit unverified)")
    copper: float = Field(..., ge=0.0, description="Copper value in original dataset scale (unit unverified)")
    flouride: float = Field(..., ge=0.0, description="Flouride value in original dataset scale (unit unverified)")
    bacteria: float = Field(..., ge=0.0, description="Bacteria index")
    viruses: float = Field(..., ge=0.0, description="Viruses index")
    lead: float = Field(..., ge=0.0, description="Lead value in original dataset scale (unit unverified)")
    nitrates: float = Field(..., ge=0.0, description="Nitrates value in original dataset scale (unit unverified)")
    nitrites: float = Field(..., ge=0.0, description="Nitrites value in original dataset scale (unit unverified)")
    mercury: float = Field(..., ge=0.0, description="Mercury value in original dataset scale (unit unverified)")
    perchlorate: float = Field(..., ge=0.0, description="Perchlorate value in original dataset scale (unit unverified)")
    radium: float = Field(..., ge=0.0, description="Radium level")
    selenium: float = Field(..., ge=0.0, description="Selenium value in original dataset scale (unit unverified)")
    silver: float = Field(..., ge=0.0, description="Silver value in original dataset scale (unit unverified)")
    uranium: float = Field(..., ge=0.0, description="Uranium value in original dataset scale (unit unverified)")


class PredictionResponse(BaseModel):
    prediction: int = Field(..., description="0: Unsafe/Contaminated, 1: Safe according to dataset")
    label: str = Field(..., description="Human-readable decision label")
    probability_safe: float = Field(..., description="P(class=1)")
    probability_unsafe: float = Field(..., description="P(class=0)")
    risk_percentage: float = Field(..., description="Uncalibrated P(class=0) * 100, not health risk")
    who_alerts: List[str] = Field(default_factory=list, description="Conditional WHO comparisons assuming mg/L and matching species")
    out_of_range_features: List[str] = Field(default_factory=list, description="Features exceeding train min/max")
    conflict: bool = Field(..., description="True if predicted safe but WHO alerts or out-of-range exist")
    interpretation_note: str = INTERPRETATION_NOTE


app = FastAPI(
    title="AquaInsight API - Water Quality Classification",
    description=INTERPRETATION_NOTE,
    version="1.0.0",
)

# Enable CORS for local React/Vite development or production builds
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    """Return health status and model provenance metadata."""
    return {
        "status": "healthy",
        "model": SELECTION_REPORT["selection_locked_before_test"],
        "pipeline_steps": [name for name, _ in PIPELINE.steps],
        "test_macro_f1": SELECTION_REPORT["test_metrics"]["macro_f1"],
        "test_roc_auc": SELECTION_REPORT["test_metrics"]["roc_auc"],
    }


@app.get("/api/v1/presets", status_code=status.HTTP_200_OK)
def get_presets() -> Dict[str, Any]:
    """Return preconfigured demonstration cases required by the rubric."""
    return {
        "case_a_safe": {
            "name": "Caso A: Perfil seguro del dataset",
            "description": "Ejemplo de train etiquetado como seguro. No certifica potabilidad.",
            "code": "A", "type": "safe-preset", "badge": "Ejemplo del dataset",
            "data": SAFE_CASE,
        },
        "case_b_contaminated": {
            "name": "Caso B: Metales y nitrato alto",
            "description": "Activa alertas condicionales y extrapolaci\u00f3n de nitrato (55 > 19,83 en train).",
            "code": "B", "type": "contaminated-preset", "badge": "Alertas y extrapolaci\u00f3n",
            "data": CONTAMINATED_CASE,
        },
        "case_c_adversarial": {
            "name": "Caso C: Caso l\u00edmite / adverso",
            "description": "Falla conocida: predice clase segura con alertas y valores fuera de train. Se muestra el conflicto.",
            "code": "C", "type": "adversarial-preset", "badge": "Falla adversa conocida",
            "data": ADVERSARIAL_CASE,
        },
    }


@app.post("/api/v1/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
def predict_water_quality(sample: WaterSampleInput) -> PredictionResponse:
    """Predict drinking water safety for a given chemical and biological profile."""
    sample_dict = sample.model_dump()
    df_row = pd.DataFrame([[sample_dict[feature] for feature in FEATURE_ORDER]], columns=FEATURE_ORDER)

    # RF converts scaled features to float32. Reject unsupported scales explicitly.
    with np.errstate(over="ignore", invalid="ignore"):
        transformed = PIPELINE.named_steps["scaler"].transform(df_row)
    if not np.isfinite(transformed).all() or (np.abs(transformed) > np.finfo(np.float32).max).any():
        raise HTTPException(status_code=422, detail="La escala numérica excede la capacidad del pipeline. Revise las mediciones.")

    try:
        pred_int = int(PIPELINE.predict(df_row)[0])
        probas = PIPELINE.predict_proba(df_row)[0]
    except (ValueError, OverflowError) as exc:
        raise HTTPException(
            status_code=422,
            detail="La escala numérica excede la capacidad del pipeline. Revise las mediciones.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo procesar la muestra con el modelo guardado.",
        ) from exc

    classes_list = list(PIPELINE.classes_)
    idx_unsafe = classes_list.index(0)
    idx_safe = classes_list.index(1)

    prob_unsafe = float(probas[idx_unsafe])
    prob_safe = float(probas[idx_safe])

    # Comparisons assume mg/L and matching chemical species, without certification.
    who_alerts = limit_alerts(sample_dict)

    # Check out-of-range features
    out_of_range = []
    for feat in FEATURE_ORDER:
        val = sample_dict[feat]
        if val < TRAIN_MIN[feat] or val > TRAIN_MAX[feat]:
            out_of_range.append(f"{feat} ({val:g} fuera de [{TRAIN_MIN[feat]:g}, {TRAIN_MAX[feat]:g}])")

    conflict = (pred_int == 1) and bool(who_alerts or out_of_range)
    label = "Segura según el dataset" if pred_int == 1 else "Contaminada / no segura"

    return PredictionResponse(
        prediction=pred_int,
        label=label,
        probability_safe=prob_safe,
        probability_unsafe=prob_unsafe,
        risk_percentage=prob_unsafe * 100.0,
        who_alerts=who_alerts,
        out_of_range_features=out_of_range,
        conflict=conflict,
    )


# Serve built React frontend if available
FRONTEND_DIST = ROOT / "frontend" / "dist"
if FRONTEND_DIST.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
