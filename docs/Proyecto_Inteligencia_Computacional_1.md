# INTELIGENCIA COMPUTACIONAL | PROYECTO INTEGRADOR FINAL

## Proyecto Parcial integrador

**Investigación, comparación de modelos de inteligencia artificial e implementación de una solución funcional**

**Modalidad:** equipos de 2 a 3 estudiantes | **Puntaje:** 25 puntos
**Área / Dominio asignado:** Medio Ambiente

## 1. Propósito

Diseñar una solución a un problema real mediante un proceso de investigación aplicada, análisis de datos, entrenamiento y comparación de varios modelos de inteligencia artificial. A partir de resultados verificables, el equipo seleccionará un modelo, lo optimizará y lo integrará en un prototipo que permita realizar predicciones o apoyar decisiones con datos nuevos.

## 2. Relación con Inteligencia Computacional

El proyecto deberá conectar explícitamente teoría y práctica con al menos tres ejes: (a) aprendizaje automático y redes neuronales; (b) búsqueda y optimización de parámetros mediante algoritmos evolutivos u otra metaheurística; y (c) razonamiento aproximado o manejo de incertidumbre mediante lógica difusa o análisis de confianza, según la naturaleza del problema. No es necesario que los tres ejes formen parte del modelo final, pero sí deben investigarse, justificarse y evidenciarse en el informe.

## 3. Selección del problema

> **Dominio asignado:** **Medio Ambiente** (ej. calidad del aire, calidad del agua, deforestación, emisiones, o predicción meteorológica/climática).

Cada equipo elegirá un problema de clasificación o regresión con utilidad demostrable en educación, salud pública (sin decisiones clínicas automáticas), ambiente, agricultura, movilidad, energía, industria o seguridad informática. Debe formular una pregunta medible, identificar usuarios beneficiarios y definir una variable objetivo.

Ejemplos orientativos: predecir consumo eléctrico, identificar fallas en equipos, clasificar calidad del agua, estimar rendimiento académico o detectar anomalías de red. Los ejemplos no son temas obligatorios, etc.

Datos: utilizar un conjunto de datos público con licencia o condiciones de uso claras (p. ej., UCI Machine Learning Repository, Kaggle u organismos públicos). Incluir enlace, fuente, fecha de consulta, diccionario de variables y descripción de limitaciones. Se recomiendan al menos 500 registros útiles; si hay menos, justificar la decisión.

## 4. Fases y actividades obligatorias

### Fase I. Investigación y formulación

- Plantear problema, objetivo general, dos o tres objetivos específicos, pregunta de investigación e impacto esperado.
- Revisar al menos seis fuentes académicas pertinentes (preferentemente recientes); comparar enfoques, ventajas, limitaciones y métricas utilizadas.
- Explicar los fundamentos de redes neuronales, una técnica de optimización bioinspirada/evolutiva y lógica difusa o manejo de incertidumbre; justificar su relación con el problema.
- Formular una hipótesis comprobable o criterio de éxito, sin asumir que un modelo será superior antes de evaluarlo.

### Fase II. Preparación y exploración de datos

- Documentar procedencia, tamaño, variables, valores faltantes, duplicados, distribución de clases y posibles sesgos.
- Realizar visualizaciones pertinentes y justificar limpieza, codificación, escalado y selección de variables.
- Separar entrenamiento y prueba antes de ajustar transformaciones; usar Pipeline para evitar fuga de información.

### Fase III. Comparación de modelos de IA

- Entrenar como mínimo cuatro modelos: k-vecinos más cercanos (KNN), máquina de vectores de soporte (SVM), bosque aleatorio (Random Forest) y red neuronal multicapa (MLP). Justificar sustituciones si la naturaleza de los datos lo exige.
- Comparar con una línea base sencilla (DummyClassifier/DummyRegressor) y aplicar validación cruzada sobre entrenamiento.
- Reportar hiperparámetros, tiempo de entrenamiento/inferencia y métricas apropiadas; presentar una tabla única de resultados.
- Incorporar al menos una experiencia de optimización de hiperparámetros con algoritmo genético, PSO u otra metaheurística, y compararla con una búsqueda convencional o configuración inicial.

### Fase IV. Selección, mejora y prototipo funcional

- Seleccionar UN modelo final según métricas, estabilidad, complejidad y requisitos del problema; argumentar por qué se descartan los demás.
- Reentrenar el modelo seleccionado con los datos de entrenamiento y validar una sola vez en el conjunto de prueba reservado.
- Guardar el pipeline entrenado y construir una interfaz funcional (Streamlit, Gradio, Flask o consola interactiva) que acepte datos nuevos y devuelva una predicción interpretable.
- Demostrar al menos tres casos de uso, incluido uno límite o adverso; documentar manejo de entradas inválidas y límites de uso.

### Fase V. Comunicación científica y defensa

- Presentar informe técnico, código ejecutable, instrucciones de instalación, dataset o enlace estable y evidencias de funcionamiento.
- Exponer en 10 minutos y responder preguntas durante 5 minutos; todos los integrantes deben participar.
- Analizar errores, sesgos, implicaciones éticas, limitaciones, mejoras futuras y relación con Inteligencia Computacional.

## 5. Evaluación experimental mínima

Para clasificación: matriz de confusión, precisión, recall, F1 (macro si hay desbalance), y ROC-AUC cuando sea aplicable. Para regresión: MAE, RMSE y R². No utilizar exactitud como única medida en datos desbalanceados. Mostrar media y dispersión de validación cruzada, y resultados de prueba separados.

Fijar semilla aleatoria; describir hardware/software y versiones. Si hay series temporales, emplear partición temporal; si hay individuos repetidos, evitar que el mismo individuo aparezca en entrenamiento y prueba. Cualquier ajuste debe hacerse sin consultar el conjunto de prueba.

## 6. Entregables

- Informe PDF o Word (8–12 páginas, sin anexos): portada, resumen, problema, antecedentes, metodología, resultados, discusión, conclusiones y referencias APA/IEEE.
- Repositorio o carpeta comprimida: notebooks/scripts .py, requirements.txt, README, pipeline entrenado y evidencia del dataset o enlace.
- Prototipo ejecutable con instrucciones y capturas de al menos tres pruebas.
- Presentación de máximo 10 diapositivas y tabla comparativa de modelos.
- Anexo de contribuciones de cada integrante y declaración de uso de herramientas de IA generativa.

## 7. Rúbrica de calificación

| Criterio | Evidencia esperada | Puntos |
|---|---|---:|
| Investigación y fundamento teórico | Fuentes, problema y conexión con paradigmas de IC | 2 |
| Datos y preparación | EDA, calidad de datos, partición y ausencia de fugas | 5 |
| Modelos y optimización | 4 modelos, línea base, validación y metaheurística | 8 |
| Modelo final y funcionamiento | Selección justificada, prueba y prototipo operativo | 5 |
| Informe y defensa | Reproducibilidad, análisis crítico y presentación | 5 |
| **TOTAL** | | **25** |

1. ¿Qué errores podría cometer el sistema y qué consecuencias tendrían?

## 10. Reglas de entrega y originalidad

No se aceptarán únicamente capturas o notebooks sin ejecución reproducible. Se deberá citar toda fuente externa, identificar los datos utilizados y declarar el uso de IA generativa en redacción o programación. El equipo debe comprender y poder explicar cada componente. No se exige alcanzar una métrica fija: se valoran la validez experimental, la justificación de decisiones y el funcionamiento demostrado.

Condición indispensable de aprobación del proyecto: entregar un prototipo que cargue el modelo final entrenado y procese al menos un registro nuevo durante la defensa.

---

*Proyecto integrador • Inteligencia Computacional*
