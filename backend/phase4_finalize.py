"""Fit the preselected model and consume the sealed test set exactly once.

Run from the repository root: python backend/phase4_finalize.py
The existing report is an intentional one-way guard against accidental re-evaluation.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
TRAIN_PATH = ROOT / "data/processed/train.csv"
TEST_PATH = ROOT / "data/processed/test.csv"
PHASE3_PATH = ROOT / "reports/phase3_results.json"
REPORT_PATH = ROOT / "reports/phase4_selection.json"
MODEL_PATH = ROOT / "models/final_pipeline.joblib"
FIGURE_PATH = ROOT / "reports/figures/08_test_confusion_matrix.png"
SEED = 42


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render_figure(matrix: np.ndarray) -> None:
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.imshow(matrix, cmap="Blues")
    threshold = matrix.max() / 2
    for row in range(2):
        for col in range(2):
            ax.text(col, row, str(matrix[row, col]), ha="center", va="center",
                    fontsize=17, color="white" if matrix[row, col] > threshold else "black")
    ax.set(xticks=[0, 1], yticks=[0, 1],
           xticklabels=["Contaminada (0)", "Segura (1)"],
           yticklabels=["Contaminada (0)", "Segura (1)"],
           xlabel="Predicción", ylabel="Valor real", title="Matriz de confusión · test reservado")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=250)
    plt.close(fig)


def main() -> None:
    # Guard BEFORE opening the test set. Never overwrite the one-shot result.
    if REPORT_PATH.exists():
        raise SystemExit(f"Test ya evaluado: {REPORT_PATH}. No se repetirá la evaluación.")

    phase3 = json.loads(PHASE3_PATH.read_text(encoding="utf-8"))
    ga = phase3["ga_optimization"]["best_params"]
    expected = {
        "n_estimators": "200", "max_depth": "20", "min_samples_split": "4",
        "min_samples_leaf": "1", "criterion": "entropy",
    }
    if ga != expected or phase3["random_state"] != SEED:
        raise ValueError("Fase III no coincide con la configuración preseleccionada; test intacto.")

    train = pd.read_csv(TRAIN_PATH)
    features = [name for name in train.columns if name != "is_safe"]
    if len(train) != 6396 or len(features) != 20 or train.isna().any().any():
        raise ValueError("Train inesperado; test intacto.")
    if set(train["is_safe"].unique()) != {0, 1}:
        raise ValueError("Etiquetas de train inesperadas; test intacto.")

    np.random.seed(SEED)
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=4,
            min_samples_leaf=1,
            criterion="entropy",
            class_weight="balanced",
            random_state=SEED,
            n_jobs=-1,
        )),
    ])
    pipeline.fit(train[features], train["is_safe"])
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    # No model/threshold/feature decisions are made after this point.
    test = pd.read_csv(TEST_PATH)
    if len(test) != 1600 or list(test.columns) != features + ["is_safe"]:
        raise ValueError("Test no cumple el contrato previsto; no se predijo sobre él.")
    if test.isna().any().any() or set(test["is_safe"].unique()) != {0, 1}:
        raise ValueError("Test inválido; no se predijo sobre él.")
    x_test, y_test = test[features], test["is_safe"]
    predictions = pipeline.predict(x_test)
    safe_probability = pipeline.predict_proba(x_test)[:, list(pipeline.classes_).index(1)]
    matrix = confusion_matrix(y_test, predictions, labels=[0, 1])

    payload = {
        "selection_locked_before_test": "Random Forest (GA-Optimized)",
        "selection_source": "reports/phase3_results.json",
        "class_labels": {"0": "Contaminada / no segura", "1": "Segura según el dataset"},
        "model_params": {
            "n_estimators": 200, "max_depth": 20, "min_samples_split": 4,
            "min_samples_leaf": 1, "criterion": "entropy",
            "class_weight": "balanced", "random_state": SEED,
        },
        "feature_order": features,
        "train_feature_min": {name: float(train[name].min()) for name in features},
        "train_feature_max": {name: float(train[name].max()) for name in features},
        "train_rows": len(train),
        "test_rows": len(test),
        "train_sha256": sha256(TRAIN_PATH),
        "test_sha256": sha256(TEST_PATH),
        "test_evaluations": 1,
        "test_metrics": {
            "confusion_matrix_labels_0_1": matrix.tolist(),
            "macro_f1": float(f1_score(y_test, predictions, average="macro", zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, safe_probability)),
            "recall_class_1_safe": float(recall_score(y_test, predictions, pos_label=1, zero_division=0)),
            "recall_class_0_unsafe": float(recall_score(y_test, predictions, pos_label=0, zero_division=0)),
            "precision_class_1_safe": float(precision_score(y_test, predictions, pos_label=1, zero_division=0)),
            "precision_class_0_unsafe": float(precision_score(y_test, predictions, pos_label=0, zero_division=0)),
            "accuracy": float(accuracy_score(y_test, predictions)),
        },
        "environment": {
            "python": platform.python_version(), "platform": platform.platform(),
            "processor": platform.processor(), "cpu_count": __import__("os").cpu_count(),
            "numpy": np.__version__, "pandas": pd.__version__,
            "scikit_learn": sklearn.__version__, "joblib": joblib.__version__,
            "matplotlib": matplotlib.__version__,
        },
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    render_figure(matrix)
    print(json.dumps(payload["test_metrics"], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["--render-figure"]:
        stored = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        render_figure(np.asarray(stored["test_metrics"]["confusion_matrix_labels_0_1"]))
    elif len(sys.argv) == 1:
        main()
    else:
        raise SystemExit("Uso: python backend/phase4_finalize.py [--render-figure]")
