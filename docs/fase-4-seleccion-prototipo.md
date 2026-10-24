# Fase IV · Selección final y prototipo de calidad del agua

**Proyecto:** Inteligencia Computacional — Medio Ambiente / calidad del agua  
**Fecha:** 20 de octubre de 2026  
**Estado:** evaluación única del test completada; prototipo interactivo ejecutable.

## 1. Decisión fijada antes de abrir el test

Se seleccionó, por indicación del proyecto y antes de consultar `test.csv`, el **Random Forest optimizado mediante algoritmo genético (GA)**. Se tomó la configuración registrada en `reports/phase3_results.json`: 200 árboles, profundidad 20, mínimo 4 muestras para dividir, mínimo 1 por hoja, entropía, pesos de clase equilibrados y semilla 42. El preprocesamiento y estimador están juntos en `Pipeline(StandardScaler, RandomForestClassifier)`.

La decisión **no representa la mayor media numérica de Macro-F1 en Fase III**: GridSearch obtuvo 0,8979 ± 0,0119 frente a 0,8967 ± 0,0132 del GA; la diferencia de 0,0012 es pequeña respecto de la dispersión entre pliegues, sin que eso demuestre equivalencia estadística. Se conservó el candidato GA para materializar el eje metaheurístico de la rúbrica y por su desempeño cercano, ROC-AUC 0,9868 y baja dispersión. No se usó el test para escoger entre GA y GridSearch. GridSearch fue más rápido en la búsqueda registrada (7,8 s frente a 58,5 s), de modo que tampoco se afirma superioridad de complejidad del GA. KNN, SVM y MLP se descartan para el modelo final por su menor Macro-F1 en validación; el RF base (0,8863) queda por debajo del RF-GA. El Dummy (0,4697) muestra por qué accuracy por sí sola no basta en este conjunto desbalanceado.

**Semántica crítica:** `is_safe=0` significa *no segura/contaminada* y `is_safe=1` significa *segura según las etiquetas del dataset*. Por ello `recall` de clase 1 **no** es sensibilidad para detectar agua contaminada. La probabilidad de riesgo que muestra la interfaz es `predict_proba(...)[clase 0]` y no una probabilidad clínica calibrada.

## 2. Protocolo sin fuga y trazabilidad

1. Los 6.396 registros de `data/processed/train.csv` son el único conjunto de ajuste del escalador y del bosque. La comparación y optimización previas se hicieron sobre CV del train, según Fase III.
2. El script `backend/phase4_finalize.py` verifica primero que no existe `reports/phase4_selection.json`, comprueba los parámetros preseleccionados en Fase III, ajusta el pipeline al **100 % del train** y persiste `models/final_pipeline.joblib`.
3. Solo entonces abre los 1.600 registros de `data/processed/test.csv`. Se ejecutaron una vez `predict` y `predict_proba` del modelo ya fijado, sin búsqueda de hiperparámetros, modificación de umbral ni reentrenamiento posteriores. Las métricas se guardaron inmediatamente en `reports/phase4_selection.json`, junto con SHA-256 de ambos CSV, orden de las 20 variables, versiones y entorno. El guard de archivo impide repetir accidentalmente la evaluación. `--render-figure` reconstruye **solo** la figura a partir del JSON; no abre el test.
4. La gráfica se conserva en `reports/figures/08_test_confusion_matrix.png`. No se reutilizó el escalador persistido en Fase II: el `StandardScaler` dentro del pipeline final se ajustó de nuevo exclusivamente al train.

**Nota de auditoría del sello:** durante la inspección inicial de archivos se mostró el encabezado y la primera fila de `test.csv` para constatar su formato, antes de ejecutar la evaluación. No se calculó ninguna métrica, se entrenó con esa fila ni se modificó la selección preestablecida a partir de ella; sin embargo, el archivo no permaneció literalmente sin abrir hasta el ajuste final. La evaluación predictiva del conjunto completo sí se ejecutó una sola vez. Se deja constancia de esta desviación en vez de afirmar un sellado absoluto.

## 3. Resultados finales en test reservado

Filas = valores reales; columnas = predicciones. Orden de etiquetas `[0, 1]`:

| Real / Predicha | No segura (0) | Segura (1) |
|---|---:|---:|
| **No segura (0)** | 1.386 | **32** |
| **Segura (1)** | 30 | 152 |

| Indicador | CV train (5 pliegues, RF-GA) | Test final (única evaluación) |
|---|---:|---:|
| Macro-F1 | 0,8967 ± 0,0132 | **0,9044** |
| ROC-AUC (score clase 1) | 0,9868 ± 0,0033 | **0,9829** |
| Recall clase 1 (segura) | 0,8603 ± 0,0311 | **0,8352** |
| Precision clase 1 (segura) | 0,7802 ± 0,0214 | **0,8261** |
| Recall clase 0 (no segura) | No reportado en Fase III | **0,9774** |
| Precision clase 0 (no segura) | No reportado en Fase III | **0,9788** |
| Accuracy (solo complementaria) | 0,9564 ± 0,0054 | **0,9613** |

Los **32 casos realmente no seguros predichos como seguros** son el error de mayor preocupación práctica: falsa tranquilidad. Los otros 30 errores corresponden a agua etiquetada segura que se clasificó como no segura. El ROC-AUC se calculó con probabilidad de clase 1, conforme al etiquetado; no se interpretó como garantía de calibración. El desbalance (1.418 no seguras frente a 182 seguras en test) exige presentar Macro-F1, ambas sensibilidades y matriz de confusión, no solo accuracy. Estos resultados son de una partición, no una validación externa ni certificación sanitaria.

## 4. Prototipo ejecutable

**Entorno reproducido:** Windows 11 (10.0.26200), procesador Intel64 Family 6 Model 198 Stepping 2, 24 CPU lógicas, Python 3.13.13, NumPy 2.5.1, pandas 3.0.5, scikit-learn 1.9.0, joblib 1.5.3, matplotlib 3.11.2. Las versiones están en `requirements.txt` y en el JSON de resultados; el prototipo actual usa FastAPI y React/Vite, con dependencias registradas en requirements.txt y frontend/package-lock.json.

Desde la raíz del proyecto:

```powershell
python -m pip install -r requirements.txt
npm --prefix frontend ci
npm --prefix frontend run build
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

La aplicación unificada sirve la interfaz interactiva React y la API REST en `http://localhost:8000` (con documentación Swagger en `/docs`). No ejecute `backend/phase4_finalize.py` durante la instalación ni la defensa; el modelo y la evaluación ya están guardados. Un artefacto `joblib` se debe cargar únicamente desde una fuente local confiable, pues su deserialización puede ejecutar código.

La aplicación acepta **20 valores** distribuidos en pestañas de metales y minerales, compuestos químicos e indicadores biológicos; al inferir, los reordena exactamente según el pipeline. A la derecha presenta predicción, probabilidad de clase 0 y alertas. Admite punto o coma decimal. Los campos vacíos, textos, infinitos, `NaN` y negativos se rechazan con mensajes claros; se avisa de valores fuera de los rangos del train. Un valor extremo válido puede producir predicción, pero se etiqueta como extrapolación poco fiable. Nota de calidad del dataset: el mínimo de amoníaco en train es −0,08; la UI rechaza mediciones negativas por no ser físicamente interpretables, sin alterar el entrenamiento ya fijado.

### Casos preconfigurados para la defensa

1. **A · Perfil seguro del dataset:** ejemplo de la clase 1 observado en train, sin excesos entre las sustancias con valores guía comparables bajo la hipótesis de mg/L. Ilustra el flujo, **no certifica agua potable** ni equivale a una muestra nueva de laboratorio.
2. **B · Metales y nitrato alto:** perfil con arsénico, cadmio, plomo y nitrato elevados; 55 de nitrato excede el máximo de train (19,83), por lo que se muestra la advertencia de extrapolación. El caso ilustra simultáneamente alerta y predicción de clase 0, no es un perfil «típico» del dataset en nitrato.
3. **C · Extremo adverso:** arsénico, cadmio, plomo y nitrato muy por encima de train; activa alertas y advertencias de rango. En el pipeline actual, este perfil **recibe clase 1 («segura») pese a las alertas**: es una falla adversa deliberada, no evidencia de potabilidad. La interfaz conserva la predicción exacta, pero marca el conflicto de forma prominente y evita presentarlo como un resultado limpio. Para demostrar datos inválidos, cambie un campo a `abc`, vacío o `-1` y observe el rechazo sin inferencia.

Para procesar **un registro nuevo durante la defensa**, edite al menos un valor de cualquiera de los perfiles y pulse **Analizar Muestra con IA**. La interfaz retorna etiqueta, `P(clase 0)` y alertas; las pruebas automatizadas de los tres botones, inferencia y entrada inválida están en `tests/`. Ejecución:

```powershell
python -m pip install -r requirements.txt
python -m pytest tests -q
npm --prefix frontend test
```

## 5. Límites OMS e interpretación responsable

La interfaz muestra comparaciones **condicionales**, no un dictamen sanitario. Las [Guías de la OMS para agua de consumo, cuarta edición con tres adendas (2026)](https://www.who.int/publications/i/item/9789240121225), [capítulo de aspectos químicos, tablas 8.9, 8.11, 8.14 y 8.16](https://cdn.who.int/media/docs/default-source/wash-documents/water-safety-and-quality/dwq-guidelines-4/gdwq_4ed_with_third-addenda_chemical-aspects.pdf?sfvrsn=dc5e51fc_5), proporcionan los valores guía usados: arsénico 0,01; bario 1,3; cadmio 0,003; cromo total 0,05; cobre 2; fluoruro 1,5; plomo 0,01; nitrato como NO₃⁻ 50; nitrito como NO₂⁻ 3; selenio 0,04; uranio (químico) 0,03 mg/L. También se avisa si `nitratos/50 + nitritos/3 > 1`, índice conjunto recomendado por la OMS.

**Restricción esencial:** la procedencia Kaggle no aporta aquí verificación analítica suficiente de **unidad, forma química ni método** para todas las columnas. `flouride` se conserva con la grafía errónea original para compatibilidad del modelo. No se comparan automáticamente con guías OMS variables sin equivalencia defendible (`bacteria`, `viruses`, `radium`, `chloramine`, etc.); para mercurio, la guía indicada es específica de mercurio inorgánico y la columna no demuestra especiación. Las alertas se leen como «si la cifra corresponde a mg/L y la especie coincide». Un valor bajo los límites implementados **no** demuestra potabilidad ni ausencia de patógenos; una predicción de clase 1 tampoco. Las alertas no cambian artificialmente el resultado del modelo, y las probabilidades no han sido calibradas contra riesgos reales.

## 6. Alcance y originalidad

El prototipo es académico y exploratorio. No se recomienda para decidir consumo humano sin muestreo y validación por laboratorio acreditado, verificación de unidades, calidad de etiquetas, validación externa y análisis de sesgos. El desarrollo de scripts, pruebas y esta documentación recibió asistencia de IA generativa (OpenAI Codex); el equipo debe revisar, comprender y declarar este apoyo en el informe y la defensa.

## Correcciones de coherencia del prototipo (21/10/2026)

La interfaz obtiene los tres perfiles desde `/api/v1/presets` y retira los resultados al editar o cambiar de caso. La API usa la misma validación para las veinte variables, incluido amoníaco: rechaza negativos, booleanos, campos ausentes o desconocidos, texto y números no finitos antes de inferir. Las escalas finitas que exceden la capacidad numérica del pipeline producen un error 422 legible.

Se retiraron las afirmaciones de cumplimiento normativo y las unidades radiológicas supuestas. Los scores se muestran como probabilidades de clase no calibradas. La ausencia de excesos solo describe las comparaciones implementadas y no demuestra potabilidad. No se implementa un sistema difuso Mamdani. Las pruebas de API requieren pytest; unittest por sí solo no descubre sus funciones.

### Alcance de pruebas en el host de revisión

El sistema operativo deniega loopback con EACCES. Las pruebas directas de esquema e inferencia real sí se ejecutaron. Las comprobaciones HTTP quedan explícitamente omitidas hasta ejecutarlas en un equipo que permita conexión local. La revisión visual usa el build React y respuestas grabadas de inferencia directa real. El manifiesto `reports/evidence/browser_checks.json` distingue esta revisión sin red de una integración HTTP. Las capturas no se presentan como evidencia de transporte de extremo a extremo.
