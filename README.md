# AquaInsight: Clasificación de Calidad del Agua

> **Proyecto Integrador de Inteligencia Computacional — UPSE**  
> **Equipo:** Melanie Tomalá, Jean Cedeño, Damián Torres Cadena | **Docente:** Ing. Daniel Quirumbay  
> **Dominio:** Medio Ambiente | **Área:** Calidad del Agua y Salud Pública

---

## 🚀 Inicio Rápido (Quickstart Local)

En menos de 2 minutos puedes tener el prototipo completo (Backend FastAPI + Frontend React) funcionando localmente en un solo puerto:

### Prerrequisitos
- **Python 3.13+** (con `pip`)
- **Node.js 20+** (con `npm`)
- **Git**

---

### Opción 1: Windows (PowerShell)

Abre PowerShell en la raíz del proyecto y corre:

```powershell
# 1. Crear y activar entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias de Python
pip install -r requirements.txt

# 3. Compilar la aplicación React
npm --prefix frontend ci
npm --prefix frontend run build

# 4. Iniciar el servidor (FastAPI sirve el Backend y la app React)
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

> **Nota para PowerShell:** Si `Activate.ps1` da error de permisos de script, ejecuta primero:  
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

---

### Opción 2: Linux / macOS (Bash)

Abre una terminal en la raíz del proyecto y corre:

```bash
# 1. Crear y activar entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias de Python
pip install -r requirements.txt

# 3. Compilar la aplicación React
npm --prefix frontend ci
npm --prefix frontend run build

# 4. Iniciar el servidor
python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000
```

---

### 🌐 Dónde abrir la aplicación

Una vez iniciado el servidor, accede desde tu navegador:

| Servicio | URL | Descripción |
|---|---|---|
| **Prototipo Web (React)** | **[http://127.0.0.1:8000](http://127.0.0.1:8000)** | Interfaz interactiva de inferencia y análisis |
| **Documentación Swagger** | **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** | Pruebas interactivas de la API REST |
| **Health Check** | **[http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)** | Estado del servicio y pipeline en memoria |

---

## 🛠️ Modo Desarrollo (React con Vite HMR)

Si deseas modificar la interfaz y ver los cambios en tiempo real con recarga en caliente:

1. **Terminal 1 (Backend API):**
   ```bash
   python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload
   ```
2. **Terminal 2 (Frontend Vite):**
   ```bash
   npm --prefix frontend run dev
   ```
3. Abre **[http://localhost:3000](http://localhost:3000)** (las peticiones a `/api` y `/health` se redirigen automáticamente a FastAPI).

---

## 🧪 Cómo Ejecutar las Pruebas Automatizadas

Verifica la integridad de la API y de los componentes sin tocar el conjunto de prueba:

```powershell
# Suite completa de backend (Pytest: 76 pruebas)
python -m pytest tests -q

# Pruebas de validación del frontend y linter
npm --prefix frontend test
npm --prefix frontend run lint
```

---

## 🎯 Protocolo de Demostración en la Defensa

Para la presentación ante el tribunal docente:

1. **Caso A (Muestra Segura):** Clic en `Cargar Caso A` → `Analizar Muestra`. Resultado: `Segura según el dataset` (`is_safe = 1`).
2. **Caso B (Muestra Contaminada):** Clic en `Cargar Caso B` → `Analizar Muestra`. Resultado: `Contaminada` (`is_safe = 0`) con alertas OMS.
3. **Caso C (Caso Límite / Adverso):** Clic en `Cargar Caso C` → `Analizar Muestra`. Resultado: Bandera de **Conflicto** (predice 1 pero con contaminantes y valores fuera de rango de entrenamiento).
4. **Procesar un Registro Nuevo (Obligatorio por rúbrica):** Modifica cualquier valor en pantalla (ej. `Aluminio` a `0.09`) y presiona `Analizar Muestra` para demostrar inferencia en tiempo real.
5. **Validación de Entradas:** Ingresa letras (`abc`) o números negativos (`-1`) para comprobar que el sistema rechaza entradas inválidas.

---

## 📖 Resumen del Proyecto

- **Problema:** Clasificación binaria de calidad del agua (`is_safe = 1` vs `0`) a partir de 20 variables químicas y microbiológicas.
- **Modelos comparados:** Dummy, KNN, SVM, MLP y Random Forest (con CV estratificada de 5 pliegues sobre 6.396 filas de train).
- **Metaheurística:** Optimización de hiperparámetros con **Algoritmo Genético (GA)** vs GridSearch en Random Forest.
- **Modelo Final:** Random Forest + GA congelado en `models/final_pipeline.joblib`.
  - **Métricas en Test (1.600 filas):** Macro-F1: `0,9044` | ROC-AUC: `0,9829` | Precisión: `0,9618` | Recall: `0,9503`.
- **Aviso:** Clasificación académica descriptiva; no certifica potabilidad para consumo humano.

---

## 📁 Estructura del Repositorio

```text
PROYECTO-I.C/
├── backend/                       # API FastAPI y scripts de procesamiento
│   ├── api.py                     # API REST y servidor de frontend compilado
│   ├── eda_preprocessing.py       # Pipeline de preparación de datos
│   └── model_comparison_opt.py    # Comparación de modelos y optimización GA
├── frontend/                      # Prototipo SPA (React 19 + Vite 8)
│   ├── src/                       # Componentes interactivos y validadores
│   └── dist/                      # Bundle de producción optimizado
├── models/
│   └── final_pipeline.joblib      # Pipeline entrenado final congelado
├── data/                          # Dataset y diccionario de variables
├── notebooks/                     # Cuadernos Jupyter por fases (2, 3 y 4)
├── tests/                         # Tests unitarios y de integración
├── deliverables/
│   ├── Informe_AquaInsight.pdf        # Informe técnico final con anexo (PDF)
│   └── Diapositivas_AquaInsight.pdf   # Diapositivas para la defensa (PDF)
├── docs/                              # Documentación metodológica y consigna
└── requirements.txt                   # Dependencias de Python fijadas
```

---

## ⚖️ Declaración de Autoría

- **Autoría del equipo:** La investigación, revisión bibliográfica, análisis estadístico de datos, diseño experimental y redacción del informe técnico fueron realizados íntegramente por los integrantes del equipo.
- **Herramientas de apoyo:** Se usaron asistentes de IA de manera complementaria para asistencia técnica en sintaxis y depuración de código (`docs/contribuciones.md`).
