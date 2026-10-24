"""Phase II: Exploratory Data Analysis & Preprocessing Pipeline
Computational Intelligence Project - Water Quality Classification
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from joblib import dump
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42
RAW_DATA_PATH = "data/water_quality.csv"
PROCESSED_DIR = "data/processed"
FIGURES_DIR = "reports/figures"
REPORTS_DIR = "reports"


def run_eda_and_preprocessing():
    if (Path(__file__).resolve().parents[1] / "reports/phase4_selection.json").exists():
        raise RuntimeError("Experimento cerrado: no sobrescribir la partición después de evaluar el test.")
    print("=" * 60)
    print("FASE II: EXPLORACIÓN Y PREPROCESAMIENTO DE DATOS")
    print("=" * 60)

    # 1. Carga de datos
    print(f"\n[1/6] Cargando datos desde {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH)
    print(f"Dimensiones iniciales: {df_raw.shape[0]} filas, {df_raw.shape[1]} columnas.")

    # 2. Detección y saneamiento de registros corruptos
    print("\n[2/6] Detección y saneamiento de registros corruptos (#NUM!)...")
    corrupt_ammonia = df_raw["ammonia"] == "#NUM!"
    corrupt_target = df_raw["is_safe"] == "#NUM!"
    corrupt_mask = corrupt_ammonia | corrupt_target
    corrupt_count = corrupt_mask.sum()
    corrupt_indices = df_raw[corrupt_mask].index.tolist()

    print(f"Registros corruptos encontrados: {corrupt_count} (Índices: {corrupt_indices})")

    # Filtrar registros corruptos
    df_clean = df_raw[~corrupt_mask].copy()

    # Convertir a tipos numéricos formales
    df_clean["ammonia"] = pd.to_numeric(df_clean["ammonia"], errors="raise")
    df_clean["is_safe"] = df_clean["is_safe"].astype(int)

    print(f"Dimensiones tras saneamiento: {df_clean.shape[0]} filas, {df_clean.shape[1]} columnas.")
    print(f"Valores nulos remanentes: {df_clean.isnull().sum().sum()}")

    # 3. Análisis de distribución de clases y estadísticas
    print("\n[3/6] Análisis de clases y estadísticas descriptivas...")
    class_counts = df_clean["is_safe"].value_counts().to_dict()
    class_ratios = df_clean["is_safe"].value_counts(normalize=True).to_dict()

    print(f"Clase 0 (No segura): {class_counts[0]} ({class_ratios[0]*100:.2f}%)")
    print(f"Clase 1 (Segura):    {class_counts[1]} ({class_ratios[1]*100:.2f}%)")

    features = [c for c in df_clean.columns if c != "is_safe"]

    # 4. Generación de Visualizaciones Rigurosas
    print(f"\n[4/6] Generando figuras en {FIGURES_DIR}...")
    sns.set_theme(style="whitegrid", palette="muted")

    # Figura 1: Distribución de clases (Desbalance)
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(
        ["No segura (0)", "Segura (1)"],
        [class_counts[0], class_counts[1]],
        color=["#D9534F", "#5CB85C"],
        width=0.5,
    )
    for bar in bars:
        yval = bar.get_height()
        pct = (yval / len(df_clean)) * 100
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            yval + 80,
            f"{yval:,} ({pct:.1f}%)",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    ax.set_title("Distribución de Clases - Seguridad del Agua", fontsize=13, fontweight="bold")
    ax.set_ylabel("Cantidad de Muestras", fontsize=11)
    ax.set_ylim(0, class_counts[0] * 1.15)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "01_class_distribution.png")
    fig.savefig(fig1_path, dpi=300)
    plt.close(fig)
    print(f"  -> Guardada: {fig1_path}")

    # Figura 2: Matriz de correlación
    fig, ax = plt.subplots(figsize=(14, 11))
    corr_matrix = df_clean.corr(method="spearman")
    sns.heatmap(
        corr_matrix,
        cmap="coolwarm",
        annot=True,
        fmt=".2f",
        annot_kws={"size": 7.5},
        ax=ax,
        linewidths=0.5,
        cbar_kws={"label": "Correlación de Spearman"},
    )
    ax.set_title("Matriz de Correlación de Spearman (20 Contaminantes + Target)", fontsize=13, fontweight="bold")
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "02_correlation_heatmap.png")
    fig.savefig(fig2_path, dpi=300)
    plt.close(fig)
    print(f"  -> Guardada: {fig2_path}")

    # Figura 3: Boxplots de metales pesados clave por clase
    metals = ["aluminium", "arsenic", "cadmium", "lead", "mercury", "chromium"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()
    for idx, metal in enumerate(metals):
        sns.boxplot(
            data=df_clean,
            x="is_safe",
            y=metal,
            ax=axes[idx],
            palette=["#D9534F", "#5CB85C"],
            showmeans=True,
            meanprops={"marker": "o", "markerfacecolor": "blue", "markeredgecolor": "blue"},
        )
        axes[idx].set_title(f"Concentración: {metal.capitalize()} (mg/L)", fontweight="bold")
        axes[idx].set_xlabel("Seguridad (0 = No segura, 1 = Segura)")
        axes[idx].set_ylabel("mg/L")
    plt.suptitle("Comparativa de Concentración de Metales Pesados por Clase", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "03_heavy_metals_boxplots.png")
    fig.savefig(fig3_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"  -> Guardada: {fig3_path}")

    # Figura 4: Top 10 correlaciones con 'is_safe'
    target_corr = corr_matrix["is_safe"].drop("is_safe").sort_values()
    fig, ax = plt.subplots(figsize=(9, 6))
    colors = ["#D9534F" if val < 0 else "#5CB85C" for val in target_corr.values]
    bars = ax.barh(target_corr.index, target_corr.values, color=colors, height=0.6)
    ax.axvline(0, color="gray", linestyle="--", linewidth=0.8)
    ax.set_title("Correlación de Spearman de cada Contaminante con 'is_safe'", fontsize=13, fontweight="bold")
    ax.set_xlabel("Coeficiente de Correlación")
    for bar in bars:
        w = bar.get_width()
        offset = 0.01 if w >= 0 else -0.04
        ax.text(w + offset, bar.get_y() + bar.get_height() / 2, f"{w:.2f}", va="center", fontsize=8.5)
    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "04_contaminants_correlation_target.png")
    fig.savefig(fig4_path, dpi=300)
    plt.close(fig)
    print(f"  -> Guardada: {fig4_path}")

    # 5. Partición Estratificada sin Fuga de Información
    print("\n[5/6] Partición estratificada Train (80%) / Test (20%)...")
    X = df_clean[features]
    y = df_clean["is_safe"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y
    )

    print(f"Dimensiones de X_train: {X_train.shape} (Clase 1: {y_train.mean()*100:.2f}%)")
    print(f"Dimensiones de X_test:  {X_test.shape} (Clase 1: {y_test.mean()*100:.2f}%)")

    # Construir pipeline de preprocesamiento (escalado estándar ajustado solo en train)
    preprocessor = Pipeline([
        ("scaler", StandardScaler())
    ])

    # Demostrar ausencia de data leakage: fit SOLO en X_train
    print("Ajustando preprocesador StandardScaler únicamente sobre X_train...")
    preprocessor.fit(X_train)

    # 6. Guardar datasets particionados y artefactos
    print(f"\n[6/6] Guardando artefactos en {PROCESSED_DIR}...")
    train_df = X_train.copy()
    train_df["is_safe"] = y_train

    test_df = X_test.copy()
    test_df["is_safe"] = y_test

    train_df.to_csv(os.path.join(PROCESSED_DIR, "train.csv"), index=False)
    test_df.to_csv(os.path.join(PROCESSED_DIR, "test.csv"), index=False)
    dump(preprocessor, os.path.join(PROCESSED_DIR, "preprocessor.joblib"))

    summary = {
        "raw_rows": int(len(df_raw)),
        "corrupted_rows_removed": int(corrupt_count),
        "clean_rows": int(len(df_clean)),
        "features_count": len(features),
        "features": features,
        "class_distribution": {
            "unsafe_0": int(class_counts[0]),
            "safe_1": int(class_counts[1]),
            "unsafe_ratio": float(class_ratios[0]),
            "safe_ratio": float(class_ratios[1]),
        },
        "train_samples": int(len(X_train)),
        "test_samples": int(len(X_test)),
        "random_state": RANDOM_STATE,
        "scaler_means": preprocessor.named_steps["scaler"].mean_.tolist(),
        "scaler_stds": np.sqrt(preprocessor.named_steps["scaler"].var_).tolist(),
    }

    summary_path = os.path.join(REPORTS_DIR, "phase2_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Resumen de Fase II exportado exitosamente a {summary_path}")
    print("\n¡FASE II COMPLETADA SATISFACTORIAMENTE!")


if __name__ == "__main__":
    run_eda_and_preprocessing()
