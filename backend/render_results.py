"""Render tables and figures from frozen reports without loading data or models."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "Dummy (Baseline)": "Dummy", "KNN": "KNN", "SVM (RBF Balanced)": "SVM RBF",
    "Random Forest (Base)": "RF base", "MLP (Red Neuronal)": "MLP",
    "Random Forest (GA-Optimized)": "RF-GA", "Random Forest (GridSearch)": "RF-Grid",
}


def load_results():
    return json.loads((ROOT / "reports/phase3_results.json").read_text(encoding="utf-8"))


def render():
    report = load_results()
    models = report["models"]
    metric_keys = ["macro_f1", "roc_auc", "recall", "precision", "accuracy"]
    lines = [
        "# Fase III: Comparación de modelos y optimización\n",
        "Fuente numérica: `reports/phase3_results.json`. Esta página se genera con "
        "`python backend/render_results.py`, sin entrenar ni abrir los CSV.\n",
        "## Protocolo experimental\n",
        "Se compararon Dummy, KNN, SVM RBF, Random Forest y MLP sobre 6.396 registros de train. "
        "Se usó StratifiedKFold de 5 pliegues, shuffle y semilla 42. Cada Pipeline ajustó "
        "StandardScaler exclusivamente dentro del entrenamiento de cada pliegue. "
        "La fase IV contiene la evaluación final ya guardada; no debe repetirse.\n",
        "`is_safe=0`: no segura. `is_safe=1`: segura según el dataset. Recall(1) mide "
        "reconocimiento de la clase segura, no detección de contaminación. "
        "ROC-AUC utiliza el score de clase 1. Accuracy es complementaria.\n",
        "## Comparación en validación cruzada\n",
        "Cada celda muestra media ± desviación estándar entre pliegues, sin equivaler "
        "a un intervalo de confianza. Las estimaciones de candidatos optimizados comparten "
        "los pliegues usados en la búsqueda: pueden ser optimistas y no son CV anidada.\n",
        "| Modelo | Macro-F1 | ROC-AUC | Recall(1) | Precision(1) | Accuracy | Ajuste medio (s) | Inferencia media (ms/lote) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    rows = []
    for name, metrics in models.items():
        cells = [f"{metrics[k + '_mean']:.4f} ± {metrics[k + '_std']:.4f}" for k in metric_keys]
        lines.append("| " + " | ".join([NAMES[name], *cells,
                     f"{metrics['fit_time_mean']:.4f}", f"{metrics['infer_time_mean']:.3f}"]) + " |")
        rows.append({"model": name, **metrics})
    lines.extend([
        "\nLa inferencia corresponde a `predict` sobre cada lote de validación (aproximadamente "
        "1.279 registros), en milisegundos; no es latencia por registro ni incluye `predict_proba`. "
        "El JSON no conserva desviaciones de tiempos. Los tiempos de ajuste anteriores no "
        "deben confundirse con el tiempo total de búsqueda.\n",
        "## Configuraciones y búsqueda\n",
        "KNN: k=7, weights=distance. SVM: kernel=rbf, C=5, gamma=scale, "
        "class_weight=balanced. RF base: 100 árboles, max_depth=12, pesos balanced. "
        "MLP: (64,32), ReLU, Adam, max_iter=250 y early_stopping=True.\n",
        "GA: 10 individuos, 5 generaciones, torneo binario, cruce uniforme, "
        "mutación 0,25 y 2 élites. Fitness: media de Macro-F1 de los 5 pliegues. "
        "Mejor configuración: 200 árboles, max_depth=20, min_samples_split=4, "
        "min_samples_leaf=1, criterion=entropy, class_weight=balanced.\n",
        "GridSearch exploró 16 combinaciones: n_estimators=[100,200], max_depth=[8,14], "
        "min_samples_split=[2,6], criterion=[gini,entropy]. Mejor configuración: "
        "200 árboles, max_depth=14, min_samples_split=2, min_samples_leaf=1 (por defecto), "
        "criterion=entropy y pesos balanced.\n",
        f"Búsqueda GA: {report['ga_optimization']['execution_time_sec']:.2f} s. "
        f"GridSearch: {report['grid_search']['execution_time_sec']:.2f} s. "
        "Los espacios y presupuestos de búsqueda son distintos, por lo que los tiempos "
        "describen estas ejecuciones y no una superioridad general de un algoritmo.\n",
        "## Selección fijada antes del test\n",
        "GridSearch obtuvo la mayor media: 0,8979 ± 0,0119 frente a 0,8967 ± 0,0132 "
        "de RF-GA. La diferencia es 0,0012 y no demuestra equivalencia ni significación "
        "estadística. Se conservó RF-GA para materializar el eje metaheurístico, con "
        "rendimiento cercano y variabilidad similar. Fue una decisión académica "
        "documentada antes de la evaluación final, no la victoria numérica del GA. "
        "Dummy, KNN, SVM, MLP y RF base tuvieron menor Macro-F1 en estas validaciones.\n",
        "La selección queda congelada. Los resultados del test en fase IV se utilizan "
        "para informar el desempeño, sin modificar hiperparámetros, umbral ni modelo.\n",
    ])
    (ROOT / "docs/fase-3-comparacion-modelos.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    with (ROOT / "reports/model_comparison.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    labels = [NAMES[name] for name in models]
    ax.bar(labels, [m["macro_f1_mean"] for m in models.values()],
           yerr=[m["macro_f1_std"] for m in models.values()], capsize=4, color="#286486")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Macro-F1 (media ± desviación estándar)")
    ax.set_title("Validación cruzada de 5 pliegues, solo train")
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(ROOT / "reports/figures/05_model_comparison_metrics.png", dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for key, label in [("ga_optimization", "GA"), ("grid_search", "GridSearch")]:
        item = report[key]
        ax.scatter(item["execution_time_sec"], item["best_macro_f1"], s=110)
        ax.annotate(f"{label}: F1={item['best_macro_f1']:.4f}, {item['execution_time_sec']:.1f} s",
                    (item["execution_time_sec"], item["best_macro_f1"]),
                    xytext=(0, 14 if key == "grid_search" else -24),
                    textcoords="offset points", ha="center")
    ax.set_xlim(-10, 78)
    ax.set_ylim(.8955, .8990)
    ax.set_xlabel("Tiempo total de búsqueda (s), presupuestos distintos")
    ax.set_ylabel("Mejor Macro-F1 CV")
    ax.set_title("Comparación descriptiva de búsquedas")
    fig.tight_layout()
    fig.savefig(ROOT / "reports/figures/07_ga_vs_grid_tradeoff.png", dpi=180)
    plt.close(fig)
    print("Tablas y figuras actualizadas desde JSON. No se cargaron datos ni modelos.")


if __name__ == "__main__":
    render()
