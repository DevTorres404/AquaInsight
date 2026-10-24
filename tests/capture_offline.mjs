// Review the real built UI using recorded outputs of the real inference function.
// Requests are fulfilled in memory: this does not verify HTTP transport to FastAPI.
import fs from 'node:fs/promises';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';

const root = path.resolve(import.meta.dirname, '..');
const evidence = path.resolve(process.env.AQUA_UI_OUTPUT_DIR || path.join(root, 'reports/evidence'));
await fs.mkdir(evidence, { recursive: true });
const dist = path.join(root, 'frontend/dist');
const packagePath = execFileSync('python', ['-c', 'import pathlib,playwright; print(pathlib.Path(playwright.__file__).parent / "driver/package/index.mjs")'], { encoding: 'utf8' }).trim();
const { chromium } = await import(pathToFileURL(packagePath).href);
const recorded = JSON.parse(await fs.readFile(path.join(root, 'reports/evidence/inference_reference.json'), 'utf8'));
const cases = recorded.cases;
const presets = Object.fromEntries(Object.entries(cases).filter(([key]) => key !== 'new_record').map(([key, item]) => {
  const { response, ...preset } = item;
  return [key, preset];
}));
const browser = await chromium.launch({ headless: true });
try {
  const page = await browser.newPage({ viewport: { width: 1500, height: 1100 }, deviceScaleFactor: 1 });
  const errors = [];
  const predictionRequests = [];
  let responseDelay = 0;
  let releasePresets;
  let presetsGate = null;
  page.on('pageerror', error => errors.push(error.message));
  await page.route('**/*', async route => {
    const url = new URL(route.request().url());
    if (url.host !== 'aqua.local') return route.abort();
    if (url.pathname === '/health') return route.fulfill({ json: { status: 'healthy' } });
    if (url.pathname === '/api/v1/presets') {
      if (presetsGate) await presetsGate;
      return route.fulfill({ json: presets });
    }
    if (url.pathname === '/api/v1/predict') {
      const input = route.request().postDataJSON();
      predictionRequests.push(input);
      const match = Object.values(cases).find(item => Object.keys(item.data).every(key => item.data[key] === input[key]));
      if (!match) throw new Error('UI sent unexpected measurements.');
      if (responseDelay) await new Promise(resolve => setTimeout(resolve, responseDelay));
      return route.fulfill({ json: match.response });
    }
    const requested = url.pathname === '/' ? 'index.html' : url.pathname.slice(1);
    const filename = path.resolve(dist, requested);
    if (!filename.startsWith(dist + path.sep)) return route.abort();
    const mime = { '.html': 'text/html', '.js': 'application/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png' };
    return route.fulfill({ body: await fs.readFile(filename), contentType: mime[path.extname(filename)] || 'application/octet-stream' });
  });
  await page.goto('http://aqua.local/', { waitUntil: 'networkidle' });
  await page.evaluate(async () => {
    const brand = document.querySelector('.brand-symbol image');
    if (!brand) throw new Error('Brand image is missing.');
    const image = new Image();
    image.src = brand.getAttribute('href');
    await image.decode();
    if (!image.naturalWidth) throw new Error('Brand image did not load.');
  });
  await page.evaluate(() => {
    const caption = document.createElement('div');
    caption.textContent = 'REVISIÓN VISUAL SIN RED · Respuestas reales de inferencia directa · Integración HTTP pendiente';
    caption.style.cssText = 'padding:12px;text-align:center;background:#e9f0f5;color:#183b56;font:14px Arial';
    document.body.prepend(caption);
  });
  await page.getByTestId('preset-A').waitFor({ state: 'attached' });
  for (const code of ['A', 'B', 'C']) {
    if (!await page.getByTestId(`preset-${code}`).isVisible()) throw new Error('Examples must be immediately visible.');
  }
  if (await page.getByTestId('preset-A').getAttribute('aria-pressed') !== 'true') throw new Error('Initial example is not selected.');
  if (Number(await page.locator('#aluminium').inputValue()) !== Object.values(cases).find(item => item.code === 'A').data.aluminium) throw new Error('Initial example was not loaded.');
  if (await page.getByText('Servicio disponible', { exact: true }).count()) throw new Error('Service badge must be removed.');
  await page.screenshot({ path: path.join(evidence, 'product_desktop.png'), fullPage: true });
  await page.getByRole('button', { name: 'Limpiar campos', exact: true }).click();
  await page.getByRole('button', { name: 'Analizar muestra', exact: true }).click();
  await page.locator('#aluminium[aria-invalid="true"]').waitFor();
  if (predictionRequests.length) throw new Error('An empty sample reached inference.');
  const forbiddenCopy = /proyecto|universidad|universitari|acad[eé]mic|c[aá]tedra|UPSE|docente|integrantes|defensa|FastAPI|uvicorn|Random Forest|Macro-F1|test set|algoritmo gen[eé]tico/i;
  if (forbiddenCopy.test(await page.locator('body').innerText()) || forbiddenCopy.test(await page.title())) {
    throw new Error('Academic or implementation copy leaked into the product UI.');
  }
  await page.getByTestId('preset-A').click();
  await page.getByRole('button', { name: 'Compuestos químicos', exact: false }).click();
  await page.locator('#ammonia').fill('');
  await page.getByRole('button', { name: 'Metales y minerales', exact: false }).click();
  await page.getByRole('button', { name: 'Analizar muestra', exact: true }).click();
  await page.locator('#ammonia[aria-invalid="true"]').waitFor();
  if (await page.locator('#ammonia').evaluate(node => node !== document.activeElement)) throw new Error('Invalid hidden field was not focused.');
  await page.getByRole('button', { name: 'Metales y minerales', exact: false }).click();
  for (const [code, stem] of [['A','case_a_safe'],['B','case_b_contaminated'],['C','case_c_adversarial']]) {
    await page.getByTestId(`preset-${code}`).click();
    if (await page.locator('.verdict-banner').count()) throw new Error('Stale result after loading preset.');
    await page.getByRole('button', { name: 'Analizar muestra', exact: false }).click();
    await page.locator('.verdict-banner').waitFor();
    if (forbiddenCopy.test(await page.locator('body').innerText())) throw new Error('Academic or implementation copy leaked through results.');
    if (code === 'C') {
      await page.locator('.verdict-banner.conflict').waitFor();
      await page.locator('.verdict-banner').screenshot({ path: path.join(evidence, 'case_c_banner.png') });
    }
    await page.screenshot({ path: path.join(evidence, `${stem}.png`), fullPage: true });
  }
  await page.getByTestId('preset-A').click();
  await page.locator('#aluminium').fill('0,09');
  await page.getByRole('button', { name: 'Analizar muestra', exact: false }).click();
  await page.locator('.verdict-banner').waitFor();
  const validRequestCount = predictionRequests.length;
  for (const value of ['1abc', '', 'NaN', 'Infinity', '-1']) {
    await page.locator('#arsenic').fill(value);
    if (await page.locator('.verdict-banner').count()) throw new Error('Stale result after edit.');
    await page.getByRole('button', { name: 'Analizar muestra', exact: false }).click();
    await page.locator('.alert-item').filter({ hasText: 'Arsénico' }).waitFor();
  }
  await page.getByTestId('preset-A').click();
  await page.getByRole('button', { name: 'Compuestos químicos', exact: false }).click();
  await page.locator('#ammonia').fill('-0.08');
  await page.getByRole('button', { name: 'Analizar muestra', exact: false }).click();
  await page.locator('.alert-item').filter({ hasText: 'Amoníaco' }).waitFor();
  if (predictionRequests.length !== validRequestCount) throw new Error('Invalid input sent to inference.');
  await page.getByTestId('preset-A').click();
  await page.getByRole('button', { name: 'Metales y minerales', exact: false }).click();
  responseDelay = 500;
  await page.getByRole('button', { name: 'Analizar muestra', exact: false }).click();
  await page.locator('#arsenic').fill('abc');
  await page.waitForTimeout(700);
  if (await page.locator('.verdict-banner').count()) throw new Error('An old response overwrote an edited sample.');
  responseDelay = 0;
  await page.getByRole('button', { name: 'Limpiar campos', exact: true }).click();
  if (await page.locator('#aluminium').inputValue() !== '' || await page.locator('.verdict-banner').count()) throw new Error('Reset did not clear the sample.');
  for (const group of ['Metales y minerales','Compuestos químicos','Indicadores biológicos']) {
    await page.getByRole('button', { name: group, exact: false }).click();
    const values = await page.locator('.field-input').evaluateAll(inputs => inputs.map(input => input.value));
    if (values.some(value => value !== '')) throw new Error('Reset left hidden measurements populated.');
  }
  await page.getByRole('button', { name: 'Metales y minerales', exact: false }).click();
  await page.getByTestId('preset-C').click();
  await page.getByRole('button', { name: 'Analizar muestra', exact: true }).click();
  await page.locator('.verdict-banner.conflict').waitFor();
  await page.locator('.interpretation-note summary').click();
  if (forbiddenCopy.test(await page.locator('body').innerText())) throw new Error('Academic copy in interpretation details.');
  await page.locator('.interpretation-note summary').click();
  await page.screenshot({ path: path.join(evidence, 'product_result_desktop.png'), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.screenshot({ path: path.join(evidence, 'product_mobile.png'), fullPage: true });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth);
  if (overflow) throw new Error('The mobile interface overflows horizontally.');
  await page.setViewportSize({ width: 320, height: 740 });
  if (await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth)) {
    throw new Error('The interface overflows on narrow mobile screens.');
  }
  await page.screenshot({ path: path.join(evidence, 'product_mobile_narrow.png'), fullPage: true });
  presetsGate = new Promise(resolve => { releasePresets = resolve; });
  await page.reload({ waitUntil: 'domcontentloaded' });
  await page.locator('#aluminium').fill('0.42');
  releasePresets();
  await page.getByTestId('preset-A').waitFor();
  if (await page.locator('#aluminium').inputValue() !== '0.42' || await page.getByTestId('preset-A').getAttribute('aria-pressed') !== 'false') {
    throw new Error('Late examples overwrote manually entered measurements.');
  }
  if (errors.length) throw new Error(errors.join('\n'));
  await fs.writeFile(path.join(evidence, 'browser_checks.json'), JSON.stringify({
    mode: 'Offline UI review using recorded real direct inference responses',
    integrated_http_verified: false, host_limitation: 'EACCES on loopback',
    cases: ['A','B','C','new_record'], invalid_inputs_blocked: true,
    stale_results_cleared: true, stale_inflight_response_ignored: true,
    browser_errors: errors, prediction_requests: predictionRequests.length,
    product_copy_verified: true, initial_example_loaded: true, examples_visible: true, service_badge_removed: true, hidden_invalid_field_focused: true,
    sample_reset_verified: true, late_presets_preserve_edits: true, mobile_horizontal_overflow: false, test_dataset_loaded: false,
  }, null, 2) + '\n');
  console.log('Offline UI checks passed: three cases, new record, invalid inputs, cleared results. HTTP not verified.');
} finally {
  await browser.close();
}
