# Dataset: Water Quality (Seguridad y Contaminación del Agua)

## Ficha Técnica y Procedencia

- **Nombre del dataset:** *Water Quality (Water Safety & Contaminants)*
- **Fuente original:** [Kaggle: Water Quality Dataset (mssmartypants)](https://www.kaggle.com/datasets/mssmartypants/water-quality)
- **Licencia:** Database: Open Database, Contents: Database Contents (Uso abierto de investigación).
- **Fecha de consulta / descarga:** 2026-10-20
- **Ubicación local:** `data/water_quality.csv`
- **Dimensiones:** 7.999 registros $\times$ 21 columnas (20 características físico-químicas/biológicas + 1 variable objetivo).

## Diccionario de Variables

| Variable | Tipo | Unidad | Descripción y Relevancia Ambiental |
|---|---|---|---|
| `aluminium` | Numérico continuo | Sin verificar | Aluminio (valor en la escala original del dataset). |
| `ammonia` | Numérico continuo | Sin verificar | Amoníaco (valor en la escala original del dataset). |
| `arsenic` | Numérico continuo | Sin verificar | Arsénico (valor en la escala original del dataset). |
| `barium` | Numérico continuo | Sin verificar | Bario (valor en la escala original del dataset). |
| `cadmium` | Numérico continuo | Sin verificar | Cadmio (valor en la escala original del dataset). |
| `chloramine` | Numérico continuo | Sin verificar | Cloramina (valor en la escala original del dataset). |
| `chromium` | Numérico continuo | Sin verificar | Cromo (valor en la escala original del dataset). |
| `copper` | Numérico continuo | Sin verificar | Cobre (valor en la escala original del dataset). |
| `flouride` | Numérico continuo | Sin verificar | Fluoruro (valor en la escala original del dataset). |
| `bacteria` | Numérico continuo | Sin verificar | Bacterias (valor en la escala original del dataset). |
| `viruses` | Numérico continuo | Sin verificar | Virus (valor en la escala original del dataset). |
| `lead` | Numérico continuo | Sin verificar | Plomo (valor en la escala original del dataset). |
| `nitrates` | Numérico continuo | Sin verificar | Nitratos (valor en la escala original del dataset). |
| `nitrites` | Numérico continuo | Sin verificar | Nitritos (valor en la escala original del dataset). |
| `mercury` | Numérico continuo | Sin verificar | Mercurio (valor en la escala original del dataset). |
| `perchlorate` | Numérico continuo | Sin verificar | Perclorato (valor en la escala original del dataset). |
| `radium` | Numérico continuo | Sin verificar | Radio (valor en la escala original del dataset). |
| `selenium` | Numérico continuo | Sin verificar | Selenio (valor en la escala original del dataset). |
| `silver` | Numérico continuo | Sin verificar | Plata (valor en la escala original del dataset). |
| `uranium` | Numérico continuo | Sin verificar | Uranio (valor en la escala original del dataset). |
| `is_safe` | Categórico binario | {0, 1} | Objetivo: 1 = segura según el dataset; 0 = no segura según el dataset. No certifica potabilidad. |

## Distribución de Clases, Calidad y Limpieza

- **Total de registros:** 7.999 filas.
- **Registros corruptos:** 3 filas presentan cadenas `#NUM!` tanto en `ammonia` como en `is_safe`. Se eliminan de forma justificada en el preprocesamiento, dejando **7.996 registros útiles válidos** (>15 veces los 500 requeridos por la consigna).
- **Distribución de clases (sobre 7.996 registros):**
  - **Clase 0 (No segura / Contaminada):** 7.084 muestras (**88.60%**)
  - **Clase 1 (Segura / Potable):** 912 muestras (**11.40%**)
- **Desbalance severo y justificación experimental:**
  - Este marcado desbalance (~89/11) hace que la exactitud (*Accuracy*) sea completamente engañosa: un modelo trivial (`DummyClassifier(strategy='most_frequent')`) obtendría 88.6% de acierto prediciendo siempre "no segura", pero tendría Recall = 0.0 sobre el agua segura.
  - Esto valida formalmente el requisito de la cátedra de evaluar con **Macro-F1, Precision, Recall y ROC-AUC**, además de implementar técnicas de balance de clases (`class_weight='balanced'`) en los modelos.

## Unidades, sesgos y límites de uso

No se verificaron unidades, especies químicas, métodos analíticos, país ni laboratorio de origen para todas las columnas. Las unidades mg/L, CFU/mL, PFU/mL, pCi/L o Bq/L mencionadas en versiones previas eran supuestos y no deben tratarse como hechos. El prototipo usa la escala numérica original, sin conversión de unidades. Las comparaciones OMS son condicionales a confirmar unidad y especie.

Se conserva el nombre original `flouride` para compatibilidad. En train, `ammonia` tiene mínimo -0,08, anomalía que no se elimina retroactivamente del experimento. La interfaz y API rechazan valores negativos nuevos. La distribución 89/11 puede sesgar los modelos. La ausencia de identificadores temporales y de entidades impide comprobar independencia por fuente o generalización cronológica.

No se documenta validación externa ni calibración sanitaria. El caso adverso recibe clase 1 pese a valores extremos y debe mostrarse como conflicto. Una etiqueta segura no equivale a autorización de consumo.
