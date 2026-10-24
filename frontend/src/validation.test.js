import assert from 'node:assert/strict';
import test from 'node:test';
import { parseMeasurement } from './validation.js';

test('accepts decimal point, decimal comma and scientific notation', () => {
  for (const [raw, expected] of [['0,01', 0.01], [' 0.01 ', 0.01], ['1e-3', 0.001], [0, 0]]) {
    assert.equal(parseMeasurement(raw, 'Arsénico'), expected);
  }
});

test('rejects partial numbers, missing values, non-finite values and negatives', () => {
  for (const raw of ['', ' ', null, undefined, true, '1abc', '1,2,3', 'NaN', 'Infinity', '1e309', '-0.08', '0x10']) {
    assert.throws(() => parseMeasurement(raw, 'Amoníaco'));
  }
});
