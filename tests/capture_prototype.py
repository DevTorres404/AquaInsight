"""Exercise the built local app, save defense evidence, and never open test data."""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "reports/evidence"


def main():
    # Fail promptly when the host denies loopback instead of hanging in asyncio.
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        with socket.create_connection(listener.getsockname(), timeout=2):
            pass
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
    results = []
    with (EVIDENCE / "server.log").open("w", encoding="utf-8") as log:
        server = subprocess.Popen([sys.executable, "-m", "uvicorn", "backend.api:app", "--host", "127.0.0.1",
                                   "--port", str(port)], cwd=ROOT, stdout=log, stderr=log, creationflags=flags)
        try:
            for _ in range(80):
                try:
                    with urlopen(base + "/health", timeout=1) as response:
                        if response.status == 200:
                            break
                except OSError:
                    if server.poll() is not None:
                        raise RuntimeError((EVIDENCE / "server.log").read_text(encoding="utf-8"))
                    time.sleep(.5)
            else:
                raise RuntimeError("Local server did not start.")
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1500, "height": 1100}, device_scale_factor=1)
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(base, wait_until="networkidle")
                page.locator('.sample-examples summary').click()
                for code, stem, expected in [('A','case_a_safe',1),('B','case_b_contaminated',0),('C','case_c_adversarial',1)]:
                    page.get_by_test_id(f'preset-{code}').click()
                    expect(page.locator('.empty-state')).to_be_visible()
                    with page.expect_response('**/api/v1/predict') as response:
                        page.get_by_role('button',name='Analizar muestra',exact=False).click()
                    payload = response.value.json()
                    assert response.value.status == 200
                    assert payload['prediction'] == expected
                    expect(page.locator('.verdict-banner')).to_be_visible()
                    if code == 'C':
                        assert payload['conflict'] is True
                        expect(page.locator('.verdict-banner.conflict')).to_be_visible()
                        page.locator('.verdict-banner').screenshot(path=str(EVIDENCE/'case_c_banner.png'))
                    page.screenshot(path=str(EVIDENCE/f'{stem}.png'),full_page=True)
                    results.append({'case':code,'response':payload})
                page.get_by_test_id('preset-A').click()
                page.locator('#aluminium').fill('0,09')
                with page.expect_response('**/api/v1/predict') as response:
                    page.get_by_role('button',name='Analizar muestra',exact=False).click()
                assert response.value.status == 200
                expect(page.locator('.verdict-banner')).to_be_visible()
                results.append({'case':'new_record','changed':{'aluminium':0.09},'response':response.value.json()})
                requests=[]
                page.on('request',lambda request: requests.append(request.url) if request.url.endswith('/api/v1/predict') else None)
                for invalid in ['1abc','','NaN','Infinity','-1']:
                    page.locator('#arsenic').fill(invalid)
                    expect(page.locator('.empty-state')).to_be_visible()
                    page.get_by_role('button',name='Analizar muestra',exact=False).click()
                    expect(page.locator('.alert-item').filter(has_text='Arsénico')).to_be_visible()
                    expect(page.locator('.verdict-banner')).to_have_count(0)
                assert not requests, 'Invalid inputs reached prediction API.'
                page.get_by_role('button',name='Compuestos químicos',exact=False).click()
                page.locator('#ammonia').fill('-0.08')
                page.locator('#arsenic').count()  # Arsenic stays invalid in state while this tab is active.
                # Restore all measurements, then verify ammonia specifically.
                page.get_by_test_id('preset-A').click()
                page.locator('#ammonia').fill('-0.08')
                page.get_by_role('button',name='Analizar muestra',exact=False).click()
                expect(page.locator('.alert-item').filter(has_text='Amoníaco')).to_be_visible()
                assert not requests
                assert not errors, errors
                (EVIDENCE/'browser_checks.json').write_text(json.dumps({
                    'cases':results,'invalid_inputs_blocked':True,'stale_results_cleared':True,
                    'browser_errors':errors,'test_dataset_loaded':False,
                },ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
                browser.close()
            print('Browser checks passed: A, B, C, new record, invalid inputs, cleared results.')
        finally:
            server.terminate()
            server.wait(timeout=10)


if __name__ == '__main__':
    main()
