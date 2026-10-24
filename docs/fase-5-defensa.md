# Fase V: comunicación y defensa

## Guion de 10 minutos

Distribución sugerida para que todos participen, sujeta a acuerdo del equipo:

| Tiempo | Contenido | Intervención sugerida |
|---|---|---|
| 0:00-2:30 | Problema, datos y tres ejes de IC | Melanie |
| 2:30-5:30 | Pipelines, CV, comparación y elección GA frente a Grid | Jean |
| 5:30-8:45 | Test guardado y demostración A, B, C, registro nuevo e inválido | Damián |
| 8:45-10:00 | Limitaciones, conclusiones y mejoras | Participación breve de todos |

Luego: cinco minutos para preguntas. No ejecutar entrenamiento ni evaluación de test durante la defensa. Mantener el servidor y navegador listos, con los artefactos finales cargados.

## Explicaciones que debe dominar el equipo

- `is_safe=1` es la clase segura del dataset. No equivale a certificación de potabilidad.
- Recall(1) mide reconocimiento de esa clase. Los 32 casos no seguros predichos seguros son falsos positivos si la clase positiva es 1.
- GridSearch tuvo la mayor media de Macro-F1 y menor tiempo de búsqueda registrado. La elección GA fue académica y previa al test. No se demostró equivalencia estadística.
- El caso C conserva clase 1, alertas y conflicto. El sistema muestra la falla en vez de cambiar la predicción.
- Un score alto de RF no es probabilidad sanitaria calibrada. Las comparaciones OMS requieren verificar unidades y especies.
- Se investigó lógica difusa. El prototipo maneja incertidumbre mediante scores, rangos y alertas, sin implementar Mamdani.

## Lista de entrega

| Requisito | Evidencia o acción |
|---|---|
| Informe 8-12 páginas | Fuente principal: `formato.tex`. Sin compilar por indicación del usuario; extensión final por comprobar cuando se autorice la compilación. |
| Máximo 10 diapositivas | Preparación pospuesta por indicación del usuario. |
| Tabla comparativa | `reports/model_comparison.csv`, fase III e informe |
| Modelo y código | `models/final_pipeline.joblib`, `backend/`, `frontend/` y notebooks |
| Instalación | README raíz, requirements y lockfile frontend |
| Tres capturas | `reports/evidence/case_a_safe.png`, `case_b_contaminated.png`, `case_c_adversarial.png` |
| Registro nuevo en vivo | Editar aluminio del caso A a 0,09 y analizar durante la defensa |
| Contribuciones | **El equipo debe completar y confirmar `docs/contribuciones.md`** |
| Declaración de IA | Revisar y confirmar en informe y anexo |

## Antes de presentar

Cuando se retome la entrega final, comprobar el informe y la presentación en el equipo de defensa. Por ahora el informe se edita únicamente en `formato.tex`, sin compilar, y no se preparan diapositivas. Verificar que el modelo y el frontend compilado están incluidos. Ensayar con un cronómetro. Confirmar aportes personales, nombres y declaración de IA; estas confirmaciones no se pueden inferir a partir del código.

## Verificación pendiente en el equipo de defensa

El host de revisión devuelve EACCES para conexiones locales. Las capturas incluidas muestran la interfaz con respuestas grabadas de inferencia directa real, en modo sin red. Antes de presentar, iniciar FastAPI, abrir el navegador y ejecutar `python -m pytest tests -q` en el equipo de defensa para completar la integración HTTP. `python tests/capture_prototype.py` regenera las capturas con el servidor real si se instaló Playwright y su navegador Chromium.
