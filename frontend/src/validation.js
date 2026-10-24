// Accept decimal comma or point, while rejecting partial parses and non-finite values.
export function parseMeasurement(raw, label) {
  const text = String(raw ?? '').trim().replace(',', '.');
  const decimal = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i;
  const value = Number(text);
  if (typeof raw === 'boolean' || !decimal.test(text) || !Number.isFinite(value)) {
    throw new Error(`El indicador '${label}' debe ser un número finito válido.`);
  }
  if (value < 0) {
    throw new Error(`'${label}' no puede ser una medición negativa.`);
  }
  return value;
}
