"""Phase III: Model Comparison & Genetic Algorithm Optimization
Computational Intelligence Project - Water Quality Classification

Hard requirements:
- Baseline (DummyClassifier) + 4 models: KNN, SVM, Random Forest, MLP
- 5-fold Stratified Cross-Validation on training set only (No test set leakage)
- Metaheuristic optimization: Genetic Algorithm (GA) vs. GridSearchCV
- Evaluation metrics: Macro-F1, ROC-AUC, Recall (class 1), Precision (class 1), Accuracy, Time
- Fixed random seed = 42
"""

import json
import os
from pathlib import Path
import time
import warnings
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

warnings.filterwarnings("ignore")

RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

TRAIN_DATA_PATH = "data/processed/train.csv"
FIGURES_DIR = "reports/figures"
REPORTS_DIR = "reports"


def evaluate_cv(pipeline, X, y, cv):
    """Calcula métricas con validación cruzada estratificada sobre el train set."""
    macro_f1s, roc_aucs, recalls, precisions, accuracies = [], [], [], [], []
    fit_times, infer_times = [], []

    for train_idx, val_idx in cv.split(X, y):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        t0 = time.time()
        pipeline.fit(X_tr, y_tr)
        t_fit = time.time() - t0

        t0 = time.time()
        y_pred = pipeline.predict(X_val)
        t_infer = time.time() - t0

        # Probabilidades o score continuo para ROC-AUC
        if hasattr(pipeline, "predict_proba"):
            y_score = pipeline.predict_proba(X_val)[:, 1]
        elif hasattr(pipeline, "decision_function"):
            y_score = pipeline.decision_function(X_val)
        else:
            y_score = y_pred

        macro_f1s.append(f1_score(y_val, y_pred, average="macro", zero_division=0))
        roc_aucs.append(roc_auc_score(y_val, y_score))
        recalls.append(recall_score(y_val, y_pred, pos_label=1, zero_division=0))
        precisions.append(precision_score(y_val, y_pred, pos_label=1, zero_division=0))
        accuracies.append(accuracy_score(y_val, y_pred))
        fit_times.append(t_fit)
        infer_times.append(t_infer * 1000)

    return {
        "macro_f1_mean": float(np.mean(macro_f1s)),
        "macro_f1_std": float(np.std(macro_f1s)),
        "roc_auc_mean": float(np.mean(roc_aucs)),
        "roc_auc_std": float(np.std(roc_aucs)),
        "recall_mean": float(np.mean(recalls)),
        "recall_std": float(np.std(recalls)),
        "precision_mean": float(np.mean(precisions)),
        "precision_std": float(np.std(precisions)),
        "accuracy_mean": float(np.mean(accuracies)),
        "accuracy_std": float(np.std(accuracies)),
        "fit_time_mean": float(np.mean(fit_times)),
        "infer_time_mean": float(np.mean(infer_times)),
    }


class GeneticAlgorithmRF:
    """Optimizador de Hiperparámetros por Algoritmo Genético para Random Forest."""

    def __init__(self, X, y, cv, pop_size=12, generations=5, mutation_rate=0.25, elitism=2):
        self.X = X
        self.y = y
        self.cv = cv
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elitism = elitism

        self.param_ranges = {
            "n_estimators": [60, 100, 150, 200, 250],
            "max_depth": [8, 12, 16, 20],
            "min_samples_split": [2, 4, 6, 8],
            "min_samples_leaf": [1, 2, 3],
            "criterion": ["gini", "entropy"],
        }
        self.history = []

    def _random_chromosome(self):
        return {k: np.random.choice(v) for k, v in self.param_ranges.items()}

    def _fitness(self, chromosome):
        model = Pipeline([
            ("scaler", StandardScaler()),
            ("rf", RandomForestClassifier(
                **chromosome,
                class_weight="balanced",
                random_state=RANDOM_STATE,
                n_jobs=-1
            ))
        ])
        scores = []
        for train_idx, val_idx in self.cv.split(self.X, self.y):
            X_tr, X_val = self.X.iloc[train_idx], self.X.iloc[val_idx]
            y_tr, y_val = self.y.iloc[train_idx], self.y.iloc[val_idx]
            model.fit(X_tr, y_tr)
            preds = model.predict(X_val)
            scores.append(f1_score(y_val, preds, average="macro", zero_division=0))
        return float(np.mean(scores))

    def _mutate(self, chromosome):
        mutated = chromosome.copy()
        for k, v in self.param_ranges.items():
            if np.random.rand() < self.mutation_rate:
                mutated[k] = np.random.choice(v)
        return mutated

    def _crossover(self, p1, p2):
        child = {}
        for k in self.param_ranges.keys():
            child[k] = p1[k] if np.random.rand() < 0.5 else p2[k]
        return child

    def run(self):
        print("  [GA] Inicializando población...", flush=True)
        population = [self._random_chromosome() for _ in range(self.pop_size)]
        best_fitness_global = -1
        best_chromosome_global = None

        for gen in range(self.generations):
            t_gen_start = time.time()
            fitness_scores = [self._fitness(ind) for ind in population]

            ranked_indices = np.argsort(fitness_scores)[::-1]
            population = [population[i] for i in ranked_indices]
            fitness_scores = [fitness_scores[i] for i in ranked_indices]

            gen_best_f = fitness_scores[0]
            gen_mean_f = np.mean(fitness_scores)

            if gen_best_f > best_fitness_global:
                best_fitness_global = gen_best_f
                best_chromosome_global = population[0].copy()

            self.history.append({
                "generation": gen + 1,
                "best_fitness": gen_best_f,
                "mean_fitness": float(gen_mean_f),
                "time_sec": time.time() - t_gen_start
            })

            print(f"  [GA] Gen {gen+1:02d}/{self.generations:02d} | "
                  f"Mejor Macro-F1: {gen_best_f:.4f} | Media: {gen_mean_f:.4f} | "
                  f"Tiempo: {self.history[-1]['time_sec']:.1f}s", flush=True)

            new_pop = population[:self.elitism]
            while len(new_pop) < self.pop_size:
                idx1, idx2 = np.random.choice(len(population), 2, replace=False)
                parent1 = population[min(idx1, idx2)]
                idx3, idx4 = np.random.choice(len(population), 2, replace=False)
                parent2 = population[min(idx3, idx4)]

                child = self._crossover(parent1, parent2)
                child = self._mutate(child)
                new_pop.append(child)

            population = new_pop

        return best_chromosome_global, best_fitness_global, self.history


def run_phase3():
    if (Path(__file__).resolve().parents[1] / "reports/phase4_selection.json").exists():
        raise RuntimeError("Experimento cerrado: conservar resultados y selección previos al test.")
    print("=" * 65, flush=True)
    print("FASE III: COMPARACIÓN DE MODELOS Y OPTIMIZACIÓN METAHEURÍSTICA", flush=True)
    print("=" * 65, flush=True)

    print(f"\n[1/5] Cargando train dataset desde {TRAIN_DATA_PATH}...", flush=True)
    df_train = pd.read_csv(TRAIN_DATA_PATH)
    features = [c for c in df_train.columns if c != "is_safe"]
    X = df_train[features]
    y = df_train["is_safe"]

    print(f"Muestras: {len(X)} | Características: {len(features)} | Positivas: {y.mean()*100:.2f}%", flush=True)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

    print("\n[2/5] Evaluando modelos base con 5-Fold Stratified CV...", flush=True)

    models = {
        "Dummy (Baseline)": Pipeline([
            ("model", DummyClassifier(strategy="most_frequent"))
        ]),
        "KNN": Pipeline([
            ("scaler", StandardScaler()),
            ("model", KNeighborsClassifier(n_neighbors=7, weights="distance"))
        ]),
        "SVM (RBF Balanced)": Pipeline([
            ("scaler", StandardScaler()),
            ("model", SVC(kernel="rbf", C=5.0, gamma="scale", class_weight="balanced", random_state=RANDOM_STATE))
        ]),
        "Random Forest (Base)": Pipeline([
            ("scaler", StandardScaler()),
            ("model", RandomForestClassifier(n_estimators=100, max_depth=12, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1))
        ]),
        "MLP (Red Neuronal)": Pipeline([
            ("scaler", StandardScaler()),
            ("model", MLPClassifier(hidden_layer_sizes=(64, 32), activation="relu", solver="adam", max_iter=250, random_state=RANDOM_STATE, early_stopping=True))
        ]),
    }

    results = {}
    for name, pipe in models.items():
        print(f"  -> Evaluando: {name}...", end="", flush=True)
        t_eval0 = time.time()
        metrics = evaluate_cv(pipe, X, y, cv)
        results[name] = metrics
        print(f" Listo ({time.time()-t_eval0:.1f}s) | Macro-F1: {metrics['macro_f1_mean']:.4f} ± {metrics['macro_f1_std']:.4f} | "
              f"ROC-AUC: {metrics['roc_auc_mean']:.4f} | Recall: {metrics['recall_mean']:.4f} | Acc: {metrics['accuracy_mean']*100:.1f}%", flush=True)

    print("\n[3/5] Ejecutando Optimización Metaheurística con Algoritmo Genético (GA)...", flush=True)
    ga_start = time.time()
    ga_optimizer = GeneticAlgorithmRF(X, y, cv, pop_size=10, generations=5, mutation_rate=0.25, elitism=2)
    best_params_ga, best_score_ga, ga_history = ga_optimizer.run()
    ga_total_time = time.time() - ga_start
    print(f"  [GA] Mejor Macro-F1: {best_score_ga:.4f} en {ga_total_time:.1f}s", flush=True)
    print(f"  [GA] Mejores hiperparámetros: {best_params_ga}", flush=True)

    best_rf_ga = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(**best_params_ga, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1))
    ])
    results["Random Forest (GA-Optimized)"] = evaluate_cv(best_rf_ga, X, y, cv)

    print("\n[4/5] Ejecutando Búsqueda Convencional con GridSearchCV...", flush=True)
    grid_params = {
        "model__n_estimators": [100, 200],
        "model__max_depth": [8, 14],
        "model__min_samples_split": [2, 6],
        "model__criterion": ["gini", "entropy"],
    }
    rf_base_pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1))
    ])
    grid_start = time.time()
    grid_search = GridSearchCV(
        rf_base_pipe,
        grid_params,
        scoring="f1_macro",
        cv=cv,
        n_jobs=-1,
        verbose=0
    )
    grid_search.fit(X, y)
    grid_total_time = time.time() - grid_start
    print(f"  [GridSearch] Mejor Macro-F1: {grid_search.best_score_:.4f} en {grid_total_time:.1f}s", flush=True)

    results["Random Forest (GridSearch)"] = evaluate_cv(grid_search.best_estimator_, X, y, cv)

    print(f"\n[5/5] Generando figuras de comparación en {FIGURES_DIR}...", flush=True)
    sns.set_theme(style="whitegrid", palette="muted")

    # Figura 5: Comparativa de Métricas Principales
    model_names = list(results.keys())
    macro_f1s = [results[m]["macro_f1_mean"] for m in model_names]
    roc_aucs = [results[m]["roc_auc_mean"] for m in model_names]
    recalls = [results[m]["recall_mean"] for m in model_names]
    accuracies = [results[m]["accuracy_mean"] for m in model_names]

    x = np.arange(len(model_names))
    width = 0.2

    fig, ax = plt.subplots(figsize=(14, 7))
    r1 = ax.bar(x - 1.5*width, macro_f1s, width, label="Macro-F1 (Reina)", color="#2B6CB0")
    r2 = ax.bar(x - 0.5*width, roc_aucs, width, label="ROC-AUC", color="#48BB78")
    r3 = ax.bar(x + 0.5*width, recalls, width, label="Recall Clase 1 (Sanitario)", color="#ED8936")
    r4 = ax.bar(x + 1.5*width, accuracies, width, label="Accuracy (Engañoso)", color="#A0AEC0", alpha=0.7)

    ax.set_ylabel("Puntuación (0.0 - 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Comparativa General de Modelos de IA (5-Fold CV sobre Train)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, rotation=18, ha="right", fontsize=9.5, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.legend(loc="upper left", frameon=True)

    for bar in r1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h + 0.02, f"{h:.2f}", ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    fig5_path = os.path.join(FIGURES_DIR, "05_model_comparison_metrics.png")
    fig.savefig(fig5_path, dpi=300)
    plt.close(fig)
    print(f"  -> Guardada: {fig5_path}", flush=True)

    # Figura 6: Convergencia del GA
    fig, ax = plt.subplots(figsize=(8, 5))
    gens = [h["generation"] for h in ga_history]
    best_f = [h["best_fitness"] for h in ga_history]
    mean_f = [h["mean_fitness"] for h in ga_history]

    ax.plot(gens, best_f, marker="o", color="#2B6CB0", linewidth=2.5, label="Mejor Individuo (Macro-F1)")
    ax.plot(gens, mean_f, marker="s", color="#ED8936", linestyle="--", linewidth=1.8, label="Media de la Población")
    ax.set_title("Convergencia del Algoritmo Genético a lo largo de las Generaciones", fontsize=12, fontweight="bold")
    ax.set_xlabel("Generación", fontsize=10, fontweight="bold")
    ax.set_ylabel("Macro-F1 (5-Fold CV)", fontsize=10, fontweight="bold")
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig6_path = os.path.join(FIGURES_DIR, "06_ga_convergence.png")
    fig.savefig(fig6_path, dpi=300)
    plt.close(fig)
    print(f"  -> Guardada: {fig6_path}", flush=True)

    # Figura 7: Tradeoff GA vs. GridSearch
    fig, ax = plt.subplots(figsize=(7, 5))
    comparisons = ["Random Forest (Base)", "Random Forest (GridSearch)", "Random Forest (GA-Optimized)"]
    f1_vals = [results[c]["macro_f1_mean"] for c in comparisons]
    times = [results[comparisons[0]]["fit_time_mean"] * 5, grid_total_time, ga_total_time]

    ax.scatter(times, f1_vals, s=[250, 300, 350], c=["#A0AEC0", "#ED8936", "#2B6CB0"], edgecolors="black", zorder=3)
    for i, txt in enumerate(["Base", "GridSearch", "Algoritmo Genético"]):
        ax.annotate(f"{txt}\n(F1={f1_vals[i]:.4f}, T={times[i]:.1f}s)", (times[i], f1_vals[i] + 0.003), ha="center", fontsize=9, fontweight="bold")

    ax.set_title("Trade-off de Optimización: Desempeño vs. Tiempo de Cómputo", fontsize=12, fontweight="bold")
    ax.set_xlabel("Tiempo Total de Búsqueda (segundos)", fontsize=10, fontweight="bold")
    ax.set_ylabel("Macro-F1 (5-Fold CV)", fontsize=10, fontweight="bold")
    ax.set_ylim(min(f1_vals) - 0.015, max(f1_vals) + 0.02)
    plt.tight_layout()
    fig7_path = os.path.join(FIGURES_DIR, "07_ga_vs_grid_tradeoff.png")
    fig.savefig(fig7_path, dpi=300)
    plt.close(fig)
    print(f"  -> Guardada: {fig7_path}", flush=True)

    export_payload = {
        "random_state": RANDOM_STATE,
        "cv_folds": 5,
        "models": results,
        "ga_optimization": {
            "best_params": {k: str(v) for k, v in best_params_ga.items()},
            "best_macro_f1": float(best_score_ga),
            "execution_time_sec": float(ga_total_time),
            "history": ga_history
        },
        "grid_search": {
            "best_params": {k: str(v) for k, v in grid_search.best_params_.items()},
            "best_macro_f1": float(grid_search.best_score_),
            "execution_time_sec": float(grid_total_time)
        }
    }

    results_path = os.path.join(REPORTS_DIR, "phase3_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)

    print(f"\nResultados exportados a {results_path}", flush=True)
    print("\n" + "=" * 88, flush=True)
    print("TABLA COMPARATIVA FINAL DE RESULTADOS (FASE III)", flush=True)
    print("=" * 88, flush=True)
    print(f"{'Modelo':<28} | {'Macro-F1 (±std)':<18} | {'ROC-AUC':<8} | {'Recall(1)':<9} | {'Accuracy':<8} | {'Fit(s)':<6}", flush=True)
    print("-" * 88, flush=True)
    for m, d in results.items():
        print(f"{m:<28} | {d['macro_f1_mean']:.4f} ± {d['macro_f1_std']:.4f} | {d['roc_auc_mean']:.4f}   | {d['recall_mean']:.4f}    | {d['accuracy_mean']*100:.1f}%    | {d['fit_time_mean']:.2f}", flush=True)

    print("\n¡FASE III COMPLETADA EXITOSAMENTE!", flush=True)


if __name__ == "__main__":
    run_phase3()
