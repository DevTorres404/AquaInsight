# AquaInsight: Clasificación Académica de Calidad del Agua

> **Proyecto Integrador de Inteligencia Computacional — UPSE**  
> **Área / Dominio:** Medio Ambiente | **Docente:** Ing. Daniel Quirumbay  
> **Integrantes:** Melanie Tomalá, Jean Cedeño, Damián Torres Cadena  
> **Consigna oficial de referencia:** [Proyecto_Inteligencia_Computacional_1.md](file:///c:/Users/Damian/Documents/PROYECTO-I.C/Proyecto_Inteligencia_Computacional_1.md)

---

## 1. Descripción del Proyecto

**AquaInsight** es una solución integral de inteligencia computacional para la evaluación de parámetros químicos y microbiológicos en muestras de agua. El sistema implementa un flujo experimental riguroso para predecir si una muestra se clasifica como segura (`is_safe = 1`) o no segura (`is_safe = 0`) según el dataset analizado.

### Arquitectura de la Solución
El prototipo funcional se compone de dos capas desacopladas pero integrables en un único servidor:
- **Backend (API REST & Inferencia):** Implementado en **FastAPI** (`backend/api.py`), carga el pipeline final congelado (`models/final_pipeline.joblib`) compuesto por un `RobustScaler` y un clasificador **Random Forest** optimizado mediante **Algoritmos Genéticos (GA)**.
- **Frontend (Prototipo Interactivo):** Desarrollado en **React 19** y **Vite 8** (`frontend/`), ofrece una interfaz de usuario moderna y reactiva que valida datos, muestra métricas de confianza, detecta valores fuera de rango de entrenamiento y resalta alertas basadas en umbrales de la OMS.

> [!WARNING]
> **Aviso de Alcance Académico:** La clasificación refleja estrictamente las relaciones aprendidas sobre el dataset de estudio. No constituye una certificación sanitaria ni garantiza la potabilidad real del agua para consumo humano.

---

## 2. Requisitos Previos

- **Python:** 3.13.x (compatible con las versiones exactas de `requirements.txt`).
- **Node.js:** 20.x o superior (Node.js 22 LTS recomendado) y `npm`.
- **Git** para clonar el repositorio.

---

## 3. Guía de Instalación y Reproducibilidad

Siga estos pasos para configurar el entorno y ejecutar la solución completa:

### Paso 1: Configurar el entorno de Python (Backend)

**En Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**En Linux / macOS (Bash):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Paso 2: Compilar la Interfaz de Usuario (Frontend)

Desde la raíz del proyecto, instale las dependencias y construya la aplicación estática de React:

```bash
npm --prefix frontend ci
npm --prefix frontend run build
```
*Este comando genera el paquete optimizado en `frontend/dist`.*

---

## 4. Ejecución del Prototipo

El sistema soporta dos modalidades de despliegue:

### Modalidad A: Producción Integrada (Recomendada para la Defensa)
FastAPI sirve automáticamente la aplicación React compilada (`frontend/dist`) y la API REST en el mismo puerto:

```powershell
# Windows
.\.venv\Scripts\python.exe -m uvicorn backend.api:app --host 127.0.0.1 --port 8000

# Linux/macOS
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

- **Prototipo Interactivo (React):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Documentación OpenAPI (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Endpoint de Estado:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Modalidad B: Entorno de Desarrollo (HMR Desacoplado)
Si se desea editar el frontend con recarga en vivo:
1. Inicie el backend en la terminal 1:
   ```bash
   uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
   ```
2. Inicie el servidor de desarrollo de Vite en la terminal 2:
   ```bash
   npm --prefix frontend run dev
   ```
3. Acceda a [http://localhost:3000](http://localhost:3000) (las llamadas a `/api` y `/health` son redirigidas automáticamente a FastAPI).

> [!IMPORTANT]
> **Integridad del Modelo:** **No ejecute** `backend/phase4_finalize.py` durante la evaluación. El modelo final y sus artefactos ya fueron evaluados una sola vez sobre el conjunto de prueba y se encuentran congelados en `models/final_pipeline.joblib` para garantizar ausencia absoluta de fuga de datos (*data leakage*).

---

## 5. Protocolo de Demostración en la Defensa

Para cumplir con los criterios de evaluación y demostrar los **3 casos de uso obligatorios** (incluyendo el caso límite/adverso y el procesamiento de un nuevo registro):

1. **Caso A (Muestra Segura):**
   - Presione el botón **"Cargar Caso A"** en el panel lateral.
   - Haga clic en **"Analizar Muestra"**.
   - *Resultado esperado:* Predicción `Segura según el dataset` (`is_safe = 1`), probabilidad de seguridad elevada (>85%) y sin alertas de concentración.
2. **Caso B (Muestra Contaminada):**
   - Presione **"Cargar Caso B"**.
   - Haga clic en **"Analizar Muestra"**.
   - *Resultado esperado:* Predicción `Contaminada / no segura` (`is_safe = 0`), alta probabilidad de riesgo y alertas por superación de límites de referencia OMS.
3. **Caso C (Caso Límite / Adverso — Condición de Conflicto):**
   - Presione **"Cargar Caso C"**.
   - Haga clic en **"Analizar Muestra"**.
   - *Resultado esperado:* Alerta destacada de **Conflicto**. El modelo predice clase 1, pero el sistema detecta valores fuera del rango de entrenamiento y contaminantes que superan umbrales normativos. Esto evidencia el comportamiento del modelo ante distribuciones no vistas.
4. **Procesamiento de un Registro Nuevo (Requisito Indispensable):**
   - Sobre cualquiera de los casos (por ejemplo, Caso A), modifique manualmente el valor de **Aluminio** a `0.09` o ingrese valores de prueba propios.
   - Haga clic en **"Analizar Muestra"** y observe cómo el pipeline ejecuta la inferencia en tiempo real.
5. **Manejo de Errores y Robustez:**
   - Ingrese un valor inválido (ej. número negativo `-1`, texto `abc` o deje un campo vacío).
   - Verifique que tanto la interfaz React como el validador Pydantic de la API rechazan la entrada y bloquean predicciones inconsistentes.

---

## 6. Verificación Automatizada y Tests

Para validar la integridad de la API, preprocesamiento y componentes del frontend sin tocar el conjunto de prueba:

```powershell
# Ejecutar suite de pruebas de backend (Pytest)
.\.venv\Scripts\python.exe -m pytest tests -q

# Ejecutar pruebas del frontend y análisis estático (Linter)
npm --prefix frontend test
npm --prefix frontend run lint
```

---

## 7. Resultados Experimentales y Trazabilidad

- **Partición:** 6.396 registros de entrenamiento (80%) y 1.600 de prueba (20%) estratificados con semilla aleatoria fija (`seed = 42`).
- **Modelos Evaluados (CV 5-fold sobre train):**
  - Dummy Classifier (Línea base): Macro-F1 = 0,4662 ± 0,0001
  - KNN: Macro-F1 = 0,8417 ± 0,0114
  - SVM (RBF): Macro-F1 = 0,8547 ± 0,0097
  - MLP (Red Neuronal): Macro-F1 = 0,8794 ± 0,0073
  - Random Forest (GridSearch): Macro-F1 = 0,8979 ± 0,0119
  - **Random Forest (Optimizado con Algoritmo Genético - GA):** Macro-F1 = 0,8967 ± 0,0132
- **Evaluación Final en Test (RF-GA):**
  - **Macro-F1:** `0,9044`
  - **ROC-AUC:** `0,9829`
  - **Precisión:** `0,9618` | **Recall:** `0,9503`

Los reportes completos de cada fase se encuentran en `reports/phase3_results.json` y `reports/phase4_selection.json`.

---

## 8. Estructura del Repositorio

```text
PROYECTO-I.C/
├── backend/                       # Servicios de API e inferencia
│   ├── api.py                     # API FastAPI y montaje estático de React
│   ├── eda_preprocessing.py       # Pipeline de preprocesamiento y limpieza
│   ├── model_comparison_opt.py    # Entrenamiento de modelos y optimización GA
│   ├── phase4_finalize.py         # Selección y evaluación única en test
│   └── render_results.py          # Generador de tablas y figuras
├── frontend/                      # Prototipo web interactivo (React + Vite)
│   ├── src/                       # Componentes React, hooks y lógica de validación
│   ├── dist/                      # Bundle de producción compilado
│   └── package.json               # Dependencias de npm y scripts
├── models/
│   └── final_pipeline.joblib      # Pipeline entrenado final congelado
├── data/
│   ├── water_quality.csv          # Dataset original
│   └── README.md                  # Procedencia, diccionario de variables y licencias
├── notebooks/                     # Cuadernos Jupyter por fases (reproducibles)
│   ├── fase2_eda_preprocessing.ipynb
│   ├── fase3_model_comparison.ipynb
│   └── fase4_model_selection.ipynb
├── tests/                         # Suite de pruebas unitarias y de integración
│   ├── test_api.py
│   ├── test_input_validation.py
│   └── test_phase4.py
├── deliverables/
│   └── Informe_AquaInsight.pdf    # Informe técnico final en PDF
├── reports/
│   ├── evidence/                  # Capturas de prueba de los casos de uso
│   ├── phase3_results.json        # Métricas de validación cruzada
│   └── phase4_selection.json     # Métricas finales en test
├── docs/                          # Documentación detallada por fase
│   ├── contribuciones.md          # Declaración de aportes individuales e IA
│   └── fase-5-defensa.md          # Guion y preparación de la defensa
├── formato.tex                    # Código fuente del informe en LaTeX
└── requirements.txt               # Dependencias de Python fijadas
```

---

## 9. Declaración Ética y Autoría del Equipo

En cumplimiento con el artículo 10 de la consigna:
- **Autoría del equipo:** La formulación del problema, la investigación y revisión bibliográfica, el análisis de datos, la interpretación de resultados y la confección del informe técnico fueron realizados íntegramente por los integrantes del equipo de trabajo.
- **Herramientas de apoyo técnico:** Se utilizaron asistentes de IA generativa (OpenAI Codex y Google Antigravity) como apoyo puntual para la sintaxis y depuración de scripts de código.
- El detalle de aportes individuales se encuentra documentado en [docs/contribuciones.md](file:///c:/Users/Damian/Documents/PROYECTO-I.C/docs/contribuciones.md).
