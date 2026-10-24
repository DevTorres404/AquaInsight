import { parseMeasurement } from './validation.js';
import aquaLogo from './assets/brand/Logo.png';
import React, { useState, useEffect, useRef } from 'react';
import {
  Droplets,
  AlertTriangle,
  ShieldCheck,
  CheckCircle2,
  FlaskConical,
  Activity,
  ArrowRight,
  RotateCcw,
  ChevronDown,
  Info,
  RefreshCw,
} from 'lucide-react';

// Vite proxies API paths locally; FastAPI serves the same paths in the built app.
const API_BASE = '';

const FEATURE_GROUPS = [
  {
    title: 'Metales y minerales',
    description: 'Componentes inorgánicos, radioactivos y metales disueltos en agua.',
    icon: FlaskConical,
    features: [
      { key: 'aluminium', label: 'Aluminio', unit: 'Escala original', help: 'Unidad y método originales sin verificar' },
      { key: 'arsenic', label: 'Arsénico', unit: 'Escala original', help: 'Referencia condicional OMS: 0.01 mg/L' },
      { key: 'barium', label: 'Bario', unit: 'Escala original', help: 'Referencia condicional OMS: 1.3 mg/L' },
      { key: 'cadmium', label: 'Cadmio', unit: 'Escala original', help: 'Referencia condicional OMS: 0.003 mg/L' },
      { key: 'chromium', label: 'Cromo Total', unit: 'Escala original', help: 'Referencia condicional OMS: 0.05 mg/L' },
      { key: 'copper', label: 'Cobre', unit: 'Escala original', help: 'Referencia condicional OMS: 2.0 mg/L' },
      { key: 'lead', label: 'Plomo', unit: 'Escala original', help: 'Referencia condicional OMS: 0.01 mg/L' },
      { key: 'mercury', label: 'Mercurio', unit: 'Escala original', help: 'Especie de mercurio sin verificar; sin comparación OMS' },
      { key: 'radium', label: 'Radio', unit: 'Unidad sin verificar', help: 'Radioactividad natural' },
      { key: 'selenium', label: 'Selenio', unit: 'Escala original', help: 'Referencia condicional OMS: 0.04 mg/L' },
      { key: 'silver', label: 'Plata', unit: 'Escala original', help: 'Desinfectante residual' },
      { key: 'uranium', label: 'Uranio', unit: 'Escala original', help: 'Referencia condicional OMS: 0.03 mg/L' },
    ],
  },
  {
    title: 'Compuestos químicos',
    description: 'Nutrientes agrícolas, subproductos de desinfección y percloratos.',
    icon: Activity,
    features: [
      { key: 'ammonia', label: 'Amoníaco', unit: 'Escala original', help: 'Indicador de escorrentía' },
      { key: 'chloramine', label: 'Cloramina', unit: 'Escala original', help: 'Agente potabilizador' },
      { key: 'flouride', label: 'Fluoruro', unit: 'Escala original', help: 'Referencia condicional OMS: 1.5 mg/L' },
      { key: 'nitrates', label: 'Nitratos (NO₃⁻)', unit: 'Escala original', help: 'Referencia condicional OMS: 50 mg/L' },
      { key: 'nitrites', label: 'Nitritos (NO₂⁻)', unit: 'Escala original', help: 'Referencia condicional OMS: 3.0 mg/L' },
      { key: 'perchlorate', label: 'Perclorato', unit: 'Escala original', help: 'Subproducto oxidante' },
    ],
  },
  {
    title: 'Indicadores biológicos',
    description: 'Nivel microbiológico relativo presente en la muestra analizada.',
    icon: Droplets,
    features: [
      { key: 'bacteria', label: 'Bacterias', unit: 'índice', help: 'Presencia bacteriana' },
      { key: 'viruses', label: 'Virus', unit: 'índice', help: 'Presencia viral' },
    ],
  },
];

const PRESET_PRESENTATION = {
  A: {
    name: 'Perfil inicial',
    badge: 'Ejemplo de referencia',
    description: 'Carga una muestra de referencia como punto de partida y modifica sus valores.',
  },
  B: {
    name: 'Metales y nitratos elevados',
    badge: 'Valores elevados',
    description: 'Explora las alertas asociadas a metales y nitratos por encima de las referencias.',
  },
  C: {
    name: 'Concentraciones extremas',
    badge: 'Fuera de rango',
    description: 'Revisa cómo se presentan las alertas y discrepancias ante valores extremos.',
  },
};

const FEATURE_LABELS = Object.fromEntries(
  FEATURE_GROUPS.flatMap((group) => group.features.map((feature) => [feature.key, feature.label]))
);

export default function App() {
  const requestVersion = useRef(0);
  const sampleEdited = useRef(false);
  const [presets, setPresets] = useState([]);
  const [formData, setFormData] = useState({});
  const [activeTab, setActiveTab] = useState(0);
  const [activePreset, setActivePreset] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [invalidField, setInvalidField] = useState(null);

  useEffect(() => {
    let cancelled = false;
    fetch(`${API_BASE}/api/v1/presets`)
      .then((response) => {
        if (!response.ok) throw new Error('No pudimos cargar los ejemplos. Puedes introducir una muestra manualmente.');
        return response.json();
      })
      .then((data) => {
        if (cancelled) return;
        const loadedPresets = Object.values(data).map((preset) => ({
          ...preset,
          ...PRESET_PRESENTATION[preset.code],
        }));
        setPresets(loadedPresets);
        const initialPreset = loadedPresets.find((preset) => preset.code === 'A');
        if (initialPreset && !sampleEdited.current) {
          setFormData(initialPreset.data);
          setActivePreset(initialPreset.code);
        }
      })
      .catch((error) => { if (!cancelled) setErrorMessage(error.message); });
    return () => { cancelled = true; };
  }, []);

  const handleInputChange = (featureKey, val) => {
    sampleEdited.current = true;
    requestVersion.current += 1;
    setLoading(false);
    setFormData((prev) => ({
      ...prev,
      [featureKey]: val,
    }));
    setActivePreset(null);
    setResult(null);
    setErrorMessage(null);
    setInvalidField(null);
  };

  const handleLoadPreset = (preset) => {
    sampleEdited.current = true;
    requestVersion.current += 1;
    setLoading(false);
    setFormData(preset.data);
    setResult(null);
    setActivePreset(preset.code);
    setErrorMessage(null);
    setInvalidField(null);
  };

  const handleAnalyze = async (e) => {
    if (e) e.preventDefault();
    const currentRequest = ++requestVersion.current;
    setLoading(true);
    setErrorMessage(null);

    setResult(null);
    setInvalidField(null);
    const payload = {};
    for (const [groupIndex, group] of FEATURE_GROUPS.entries()) {
      for (const feature of group.features) {
        try {
          payload[feature.key] = parseMeasurement(formData[feature.key], feature.label);
        } catch (error) {
          setActiveTab(groupIndex);
          setInvalidField(feature.key);
          setErrorMessage(error.message);
          setLoading(false);
          requestAnimationFrame(() => document.getElementById(feature.key)?.focus());
          return;
        }
      }
    }

    try {
      const response = await fetch(`${API_BASE}/api/v1/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        const detail = Array.isArray(errorData.detail)
          ? errorData.detail.map((item) => `${item.loc?.at(-1) ?? 'Entrada'}: ${item.msg}`).join('; ')
          : errorData.detail;
        throw new Error(detail || 'Error en la respuesta del servidor');
      }

      const data = await response.json();
      if (currentRequest !== requestVersion.current) return;
      setResult(data);
    } catch (err) {
      if (currentRequest !== requestVersion.current) return;
      setErrorMessage(
        err instanceof TypeError
          ? 'No se pudo conectar con el servicio de análisis. Comprueba la conexión y vuelve a intentarlo.'
          : `No se pudo analizar la muestra: ${err.message}`
      );
    } finally {
      if (currentRequest === requestVersion.current) setLoading(false);
    }
  };

  const handleReset = () => {
    sampleEdited.current = true;
    requestVersion.current += 1;
    setFormData({});
    setActivePreset(null);
    setActiveTab(0);
    setResult(null);
    setErrorMessage(null);
    setInvalidField(null);
    setLoading(false);
  };

  const resultSummary = result && (result.conflict
    ? {
        kicker: 'Revisión necesaria',
        title: 'Conflicto: predicción y alertas no coinciden',
        description: 'El modelo clasifica la muestra como agua segura, pero se detectaron alertas o mediciones fuera del rango de entrenamiento. Requiere verificación de laboratorio.',
      }
    : result.prediction === 1
    ? {
        kicker: 'Diagnóstico predictivo',
        title: 'Agua segura (Apta según datos)',
        description: 'El perfil coincide con muestras clasificadas como seguras en los datos de referencia. Este resultado no certifica potabilidad.',
      }
    : {
        kicker: 'Diagnóstico predictivo',
        title: 'Agua no segura (Contaminada)',
        description: 'El perfil coincide con muestras clasificadas como no seguras o contaminadas. Revisa las alertas y confirma con análisis de laboratorio.',
      });

  return (
    <div className="app-layout" id="top">
      <header className="navbar">
        <a className="nav-brand" href="#top" aria-label="AquaInsight, inicio">
          <svg className="brand-symbol" viewBox="260 55 760 955" aria-hidden="true">
            <image href={aquaLogo} width="1254" height="1254" />
          </svg>
          <div className="brand-lockup">
            <svg className="brand-wordmark" viewBox="60 1015 1145 205" aria-hidden="true">
              <image href={aquaLogo} width="1254" height="1254" />
            </svg>
            <span className="brand-subtitle">Análisis de calidad del agua</span>
          </div>
        </a>
        <a className="nav-analysis-link" href="#sample-analysis">Ir al análisis <ArrowRight size={16} aria-hidden="true" /></a>
      </header>

      <section className="hero-card" aria-labelledby="page-title">
        <div className="hero-copy">
        <div className="hero-pill"><span className="hero-indicator" aria-hidden="true" /> Análisis de calidad del agua</div>
        <h1 id="page-title" className="hero-title">Conoce la calidad de tu muestra</h1>
        <p className="hero-text">
          Ingresa tus mediciones y obtén una clasificación con alertas según los valores de referencia.
        </p>
        </div>
          <div className="hero-chips-row">
            <span className="hero-chip"><FlaskConical size={16} aria-hidden="true" /> 20 parámetros</span>
            <span className="hero-chip"><ShieldCheck size={16} aria-hidden="true" /> Referencias OMS</span>
          </div>
      </section>

      <section className="sample-examples" aria-labelledby="examples-title" aria-busy={!presets.length && !errorMessage}>
        <div className="examples-heading"><h2 id="examples-title">¿Quieres probar con datos de ejemplo?</h2><p>Selecciona un perfil o introduce tus propias mediciones.</p></div>
        <div className="presets-grid" role="group" aria-label="Ejemplos de muestras">
          {presets.map((preset) => (
            <button key={preset.code} type="button" className={`preset-card ${activePreset === preset.code ? 'active-preset' : ''}`} data-testid={`preset-${preset.code}`} aria-pressed={activePreset === preset.code} onClick={() => handleLoadPreset(preset)}>
              <span className="preset-icon" aria-hidden="true">{preset.code}</span>
              <span className="preset-copy">
                <span className="preset-name">{preset.name}</span>
                <span className="preset-desc">{preset.description}</span>
                <span className="preset-state">{activePreset === preset.code ? 'Ejemplo cargado' : 'Cargar ejemplo'}</span>
              </span>
              {activePreset === preset.code ? <CheckCircle2 className="preset-action" size={20} aria-hidden="true" /> : <ArrowRight className="preset-action" size={20} aria-hidden="true" />}
            </button>
          ))}
          {!presets.length && !errorMessage && <p className="examples-loading" role="status">Cargando ejemplos…</p>}
        </div>
      </section>

      <main className="workspace-grid">
        <section id="sample-analysis" className="form-card" aria-labelledby="analysis-title">
          <div className="form-heading">
            <div className="section-heading-group"><span className="section-number" aria-hidden="true">01</span><h2 id="analysis-title" className="section-title">Mediciones de la muestra</h2></div>
            <button className="btn-reset" type="button" onClick={handleReset}><RotateCcw size={15} aria-hidden="true" /> Limpiar campos</button>
          </div>
          <p className="section-subtitle form-subtitle">Completa los 20 parámetros. Puedes usar punto o coma decimal.</p>
          <div className="tabs-nav" role="group" aria-label="Grupo de parámetros">
            {FEATURE_GROUPS.map((group, index) => {
              const Icon = group.icon;
              return <button key={group.title} type="button" className={`tab-btn ${activeTab === index ? 'active' : ''}`} aria-pressed={activeTab === index} aria-controls="measurement-fields" onClick={() => setActiveTab(index)}><Icon size={16} aria-hidden="true" />{group.title} ({group.features.length})</button>;
            })}
          </div>
          <div className="tab-description">{FEATURE_GROUPS[activeTab].description}</div>
          <form onSubmit={handleAnalyze} noValidate>
            <div className="inputs-grid" id="measurement-fields">
              {FEATURE_GROUPS[activeTab].features.map((feature) => (
                <div key={feature.key} className="field-group">
                  <label className="field-label" htmlFor={feature.key}>{feature.label}</label>
                  <input id={feature.key} type="text" inputMode="decimal" autoComplete="off" spellCheck={false}
                    className={`field-input ${invalidField === feature.key ? 'has-error' : ''}`}
                    value={formData[feature.key] ?? ''} placeholder="0,00"
                    onChange={(event) => handleInputChange(feature.key, event.target.value)} title={feature.help}
                    aria-invalid={invalidField === feature.key} aria-describedby={invalidField === feature.key ? 'sample-error' : 'measurement-note'} />
                </div>
              ))}
            </div>
            <p className="measurement-note" id="measurement-note">Usa la escala de los datos de referencia. Confirma las unidades antes de interpretar las comparaciones.</p>
            {errorMessage && <div className="alert-item" id="sample-error" role="alert"><AlertTriangle size={18} aria-hidden="true" /><span>{errorMessage}</span></div>}
            <button type="submit" className="btn-analyze" disabled={loading} aria-busy={loading}>
              {loading ? <><RefreshCw className="spin" size={20} aria-hidden="true" /> Analizando muestra...</> : <>Analizar muestra <ArrowRight size={20} aria-hidden="true" /></>}
            </button>
          </form>
        </section>

        <section className="results-card" aria-labelledby="results-title" aria-live="polite" aria-busy={loading}>
          <div className="results-heading"><span className="section-number" aria-hidden="true">02</span><h2 className="results-title" id="results-title">Resultado del análisis</h2></div>
          {!result ? (
            <div className="empty-state">
              <div className="empty-icon"><Droplets size={42} aria-hidden="true" /></div>
              <h3 className="empty-title">Tu análisis aparecerá aquí</h3>
              <p className="empty-desc">Introduce las mediciones y selecciona <strong>Analizar muestra</strong> para consultar la clasificación y sus alertas.</p>
            </div>
          ) : (
            <div>
              <div className={`verdict-banner ${result.conflict ? 'conflict' : result.prediction === 1 ? 'safe' : 'unsafe'}`}>
                <div className="verdict-kicker">{resultSummary.kicker}</div>
                <h3 className="verdict-title">{resultSummary.title}</h3>
                <p className="verdict-copy">{resultSummary.description}</p>
              </div>
              <div className="metric-box">
                <div className="metric-header"><span className="metric-name">Probabilidad de contaminación</span><span className="metric-value">{result.risk_percentage.toFixed(1)}%</span></div>
                <div className="progress-track"><div className="progress-fill" style={{ width: `${Math.min(100, Math.max(0, result.risk_percentage))}%` }} /></div>
                <span className="metric-caption">Estimación predictiva del modelo. No representa un riesgo toxicológico calibrado.</span>
              </div>
              <div className="alerts-card">
                <h4 className="alerts-header"><ShieldCheck size={18} aria-hidden="true" /> Alertas según referencias OMS</h4>
                {result.who_alerts?.length > 0 ? result.who_alerts.map((alert, index) => (
                  <div key={index} className="alert-item"><AlertTriangle size={16} aria-hidden="true" /><span>{alert}</span></div>
                )) : <div className="alert-clean"><CheckCircle2 size={16} aria-hidden="true" /><span>Sin excesos en los parámetros comparados. Requiere confirmar unidades y especies químicas.</span></div>}
              </div>
              {result.out_of_range_features?.length > 0 && <div className="alert-item range-alert"><Info size={16} aria-hidden="true" /><span><strong>Fuera del rango de referencia:</strong>{' '}{result.out_of_range_features.map((item) => item.replace(/^\w+/, (name) => FEATURE_LABELS[name] || name)).join(', ')}</span></div>}
              <div className="disclaimer-box"><strong>Antes de tomar una decisión:</strong> este resultado es orientativo y no certifica potabilidad. Confirma la calidad del agua con un análisis de laboratorio.</div>
            </div>
          )}
        </section>
      </main>

      <details className="interpretation-note">
        <summary>Unidades y alcance del resultado <ChevronDown size={16} aria-hidden="true" /></summary>
        <p>Las unidades originales no están verificadas para todos los parámetros. Las comparaciones con referencias OMS suponen valores en mg/L y especies químicas coincidentes. Confirma la unidad y el método de cada medición.</p>
        <p>La clasificación identifica patrones en datos de referencia. Sus probabilidades no miden riesgo sanitario calibrado. La ausencia de alertas no demuestra potabilidad.</p>
      </details>
      <footer className="footer"><span><strong>AquaInsight</strong> · Análisis de calidad del agua</span><span>Clasificación orientativa. No certifica potabilidad.</span></footer>
    </div>
  );
}
