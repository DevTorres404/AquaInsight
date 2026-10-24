# Fase II: Preparación y Exploración de Datos (EDA)

**Proyecto Integrador de Inteligencia Computacional**  
**Dominio:** Medio Ambiente &mdash; Seguridad del Agua  
**Integrantes:** Melanie Tomalá, Jean Cedeño, Damian Torres  
**Docente:** Ing. Daniel Quirumbay  

---

## 1. Procedencia y Dimensiones de los Datos

- **Fuente:** Repositorio público de Kaggle (*Water Quality Dataset* por `mssmartypants`).
- **Archivo original:** [`data/water_quality.csv`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/data/water_quality.csv).
- **Dimensiones originales:** 7.999 observaciones $\times$ 21 atributos.
- **Auditoría de Integridad:** Se identificaron exactamente **3 registros corruptos** que contenían cadenas de texto `#NUM!` en las variables `ammonia` y en la variable objetivo `is_safe` (filas con índices `7551`, `7568` y `7890`).
- **Dimensiones saneadas:** **7.996 registros limpios** (cero nulos remanentes), superando con holgura los 500 registros útiles requeridos por la consigna.

---

## 2. Variables y Distribución de Clases

El dataset cuenta con **20 características numéricas continuas** correspondientes a concentraciones de contaminantes químicos y patógenos biológicos, más la variable objetivo binaria:

- **Características ($X \in \mathbb{R}^{20}$):** `aluminium`, `ammonia`, `arsenic`, `barium`, `cadmium`, `chloramine`, `chromium`, `copper`, `flouride`, `bacteria`, `viruses`, `lead`, `nitrates`, `nitrites`, `mercury`, `perchlorate`, `radium`, `selenium`, `silver`, `uranium`.
- **Variable Objetivo ($y$):** `is_safe` $\in \{0, 1\}$.
  - **Clase 0 (Agua no segura / contaminada):** 7.084 muestras (**88.59%**).
  - **Clase 1 (Agua segura según el dataset):** 912 muestras (**11.41%**).

```
Distribución de clases:
[No segura (0)]  ████████████████████████████████████████  7,084 (88.59%)
[Segura (1)]     █████                                       912 (11.41%)
```

### Justificación Metodológica del Desbalance
El desbalance severo (~89/11) confirma empíricamente la regla de la cátedra: **la exactitud simple (*Accuracy*) está estrictamente prohibida como métrica única**. Un estimador trivial que prediga siempre clase 0 obtendría 88.59% de exactitud pero no identificaría ninguna muestra de la clase segura (Recall de la clase 1 = 0%). Por lo tanto, la optimización y selección se basará obligatoriamente en **Macro-F1, Precision, Recall y ROC-AUC**.

---

## 3. Visualizaciones Generadas

Las gráficas de alta resolución se encuentran generadas y disponibles en [`reports/figures/`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/figures/):

1. **[`01_class_distribution.png`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/figures/01_class_distribution.png):** Gráfico de barras que ilustra la marcada asimetría entre clases y documenta la necesidad de aprendizaje sensible al costo (*cost-sensitive learning*).
2. **[`02_correlation_heatmap.png`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/figures/02_correlation_heatmap.png):** Mapa de calor con correlaciones no paramétricas de Spearman entre los 20 contaminantes. Se observa baja multicolinealidad global entre predictores (todos con $r < 0.60$), sin que la baja correlación demuestre independencia, ortogonalidad ni utilidad predictiva de todas las variables.
3. **[`03_heavy_metals_boxplots.png`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/figures/03_heavy_metals_boxplots.png):** Diagramas de caja y bigotes para metales de alta toxicidad (aluminio, arsénico, cadmio, plomo, mercurio y cromo). Los valores atípicos se describen en la escala original del dataset; no se interpretan como excesos normativos sin verificar unidades y especies.
4. **[`04_contaminants_correlation_target.png`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/figures/04_contaminants_correlation_target.png):** Ranking de correlaciones individuales con la variable objetivo. Las correlaciones describen asociaciones con la etiqueta; no identifican causas de contaminación ni garantizan un orden de importancia del modelo.

---

## 4. Partición y Prevención Estricta de Fuga de Datos (*No Leakage*)

Para separar el ajuste de transformaciones de la evaluación:

1. **Partición Previa a Cualquier Transformación:** Se efectuó una división estratificada utilizando `train_test_split`:
   - **Conjunto de Entrenamiento (`train`):** **6.396 muestras** (80.0%), con un 11.41% de clase positiva.
   - **Conjunto de Prueba Reservado (`test`):** **1.600 muestras** (20.0%), con un 11.38% de clase positiva.
   - **Semilla Fija:** `RANDOM_STATE = 42` en todo el flujo.
2. **Aislamiento en Scikit-Learn `Pipeline`:** 
   - El escalador `StandardScaler` fue calibrado (`preprocessor.fit`) **estrictamente sobre `X_train`**.
   - Los datos de prueba jamás fueron consultados durante el cálculo de la media $\mu$ ni la desviación estándar $\sigma$.
   - El preprocesador ajustado fue persistido independientemente en [`data/processed/preprocessor.joblib`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/data/processed/preprocessor.joblib).

---

## 5. Inventario de Artefactos Producidos

| Artefacto | Ubicación | Descripción |
|---|---|---|
| Script de Ejecución | [`backend/eda_preprocessing.py`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/backend/eda_preprocessing.py) | Código modular reproducible de limpieza, EDA y partición. |
| Cuaderno Interactivo | [`notebooks/fase2_eda_preprocessing.ipynb`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/notebooks/fase2_eda_preprocessing.ipynb) | Notebook Jupyter documentado celda por celda para Google Colab o VS Code. |
| Conjunto Train | [`data/processed/train.csv`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/data/processed/train.csv) | 6.396 registros estratificados para entrenamiento y validación cruzada. |
| Conjunto Test | [`data/processed/test.csv`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/data/processed/test.csv) | 1.600 registros reservados para la evaluación final única en Fase IV. |
| Pipeline Serializado | [`data/processed/preprocessor.joblib`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/data/processed/preprocessor.joblib) | Objeto `StandardScaler` ajustado sin fuga de datos. |
| Resumen JSON | [`reports/phase2_summary.json`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/phase2_summary.json) | Metadatos cuantitativos de la fase para trazabilidad de experimentos. |
| Gráficas EDA | [`reports/figures/*.png`](file:///c:/Users/Damian/Documents/PROYECTO-I.C/reports/figures/) | 4 figuras de alta resolución (300 DPI) para el informe final. |

## Alcance de la exploración y corrección de interpretación

El EDA descriptivo se realizó sobre el dataset completo antes del split. No equivale a mantener el test literalmente sin abrir. El escalador se ajustó solo a train; las fases III y IV ajustaron nuevos pipelines, sin reutilizar el preprocesador independiente. La evaluación predictiva final ya está guardada y no debe repetirse. No se utilizaron las estadísticas globales del EDA para ajustar los transformadores.

La clase 1 indica segura según etiquetas, no potabilidad certificada. Recall(1)=0 en Dummy significa que no reconoce muestras seguras; no significa que omita contaminación. El error de falsa tranquilidad es clase real 0 predicha 1. Las unidades originales y procedencia analítica no están verificadas para todas las variables.
