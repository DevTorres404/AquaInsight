# Fase III: Comparación de modelos y optimización

Fuente numérica: `reports/phase3_results.json`. Esta página se genera con `python backend/render_results.py`, sin entrenar ni abrir los CSV.

## Protocolo experimental

Se compararon Dummy, KNN, SVM RBF, Random Forest y MLP sobre 6.396 registros de train. Se usó StratifiedKFold de 5 pliegues, shuffle y semilla 42. Cada Pipeline ajustó StandardScaler exclusivamente dentro del entrenamiento de cada pliegue. La fase IV contiene la evaluación final ya guardada; no debe repetirse.

`is_safe=0`: no segura. `is_safe=1`: segura según el dataset. Recall(1) mide reconocimiento de la clase segura, no detección de contaminación. ROC-AUC utiliza el score de clase 1. Accuracy es complementaria.

## Comparación en validación cruzada

Cada celda muestra media ± desviación estándar entre pliegues, sin equivaler a un intervalo de confianza. Las estimaciones de candidatos optimizados comparten los pliegues usados en la búsqueda: pueden ser optimistas y no son CV anidada.

| Modelo | Macro-F1 | ROC-AUC | Recall(1) | Precision(1) | Accuracy | Ajuste medio (s) | Inferencia media (ms/lote) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dummy | 0.4697 ± 0.0000 | 0.5000 ± 0.0000 | 0.0000 ± 0.0000 | 0.0000 ± 0.0000 | 0.8859 ± 0.0000 | 0.0007 | 0.099 |
| KNN | 0.6975 ± 0.0214 | 0.8656 ± 0.0096 | 0.3644 ± 0.0550 | 0.6016 ± 0.0496 | 0.8993 ± 0.0056 | 0.0032 | 353.868 |
| SVM RBF | 0.8207 ± 0.0159 | 0.9557 ± 0.0072 | 0.7808 ± 0.0237 | 0.6149 ± 0.0302 | 0.9190 ± 0.0079 | 0.1531 | 72.099 |
| RF base | 0.8863 ± 0.0135 | 0.9839 ± 0.0033 | 0.8795 ± 0.0215 | 0.7359 ± 0.0274 | 0.9501 ± 0.0063 | 0.1276 | 28.949 |
| MLP | 0.8509 ± 0.0251 | 0.9643 ± 0.0132 | 0.6507 ± 0.0616 | 0.8425 ± 0.0517 | 0.9459 ± 0.0084 | 0.4849 | 1.615 |
| RF-GA | 0.8967 ± 0.0132 | 0.9868 ± 0.0033 | 0.8603 ± 0.0311 | 0.7802 ± 0.0214 | 0.9564 ± 0.0054 | 0.2296 | 27.694 |
| RF-Grid | 0.8979 ± 0.0119 | 0.9870 ± 0.0028 | 0.8849 ± 0.0218 | 0.7657 ± 0.0226 | 0.9559 ± 0.0052 | 0.2378 | 27.688 |

La inferencia corresponde a `predict` sobre cada lote de validación (aproximadamente 1.279 registros), en milisegundos; no es latencia por registro ni incluye `predict_proba`. El JSON no conserva desviaciones de tiempos. Los tiempos de ajuste anteriores no deben confundirse con el tiempo total de búsqueda.

## Configuraciones y búsqueda

KNN: k=7, weights=distance. SVM: kernel=rbf, C=5, gamma=scale, class_weight=balanced. RF base: 100 árboles, max_depth=12, pesos balanced. MLP: (64,32), ReLU, Adam, max_iter=250 y early_stopping=True.

GA: 10 individuos, 5 generaciones, torneo binario, cruce uniforme, mutación 0,25 y 2 élites. Fitness: media de Macro-F1 de los 5 pliegues. Mejor configuración: 200 árboles, max_depth=20, min_samples_split=4, min_samples_leaf=1, criterion=entropy, class_weight=balanced.

GridSearch exploró 16 combinaciones: n_estimators=[100,200], max_depth=[8,14], min_samples_split=[2,6], criterion=[gini,entropy]. Mejor configuración: 200 árboles, max_depth=14, min_samples_split=2, min_samples_leaf=1 (por defecto), criterion=entropy y pesos balanced.

Búsqueda GA: 58.46 s. GridSearch: 7.79 s. Los espacios y presupuestos de búsqueda son distintos, por lo que los tiempos describen estas ejecuciones y no una superioridad general de un algoritmo.

## Selección fijada antes del test

GridSearch obtuvo la mayor media: 0,8979 ± 0,0119 frente a 0,8967 ± 0,0132 de RF-GA. La diferencia es 0,0012 y no demuestra equivalencia ni significación estadística. Se conservó RF-GA para materializar el eje metaheurístico, con rendimiento cercano y variabilidad similar. Fue una decisión académica documentada antes de la evaluación final, no la victoria numérica del GA. Dummy, KNN, SVM, MLP y RF base tuvieron menor Macro-F1 en estas validaciones.

La selección queda congelada. Los resultados del test en fase IV se utilizan para informar el desempeño, sin modificar hiperparámetros, umbral ni modelo.

