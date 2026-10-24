"""Prototype checks that never open the reserved test set."""

import json
import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import backend.api as app  # noqa: E402


class Phase4PrototypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model, cls.report = app.load_artifacts()
        cls.features = cls.report["feature_order"]

    def test_serialized_pipeline_and_feature_order(self):
        self.assertEqual(len(self.features), 20)
        self.assertEqual(list(self.model.feature_names_in_), self.features)
        self.assertEqual(list(self.model.classes_), [0, 1])
        self.assertEqual(self.report["test_evaluations"], 1)

    def test_three_presets_produce_predictions(self):
        for name, values in (("safe", app.SAFE_CASE),
                             ("contaminated", app.CONTAMINATED_CASE),
                             ("adversarial", app.ADVERSARIAL_CASE)):
            with self.subTest(name=name):
                valid = app.validate_inputs({key: str(value) for key, value in values.items()}, self.features)
                row = pd.DataFrame([[valid[key] for key in self.features]], columns=self.features)
                self.assertIn(int(self.model.predict(row)[0]), (0, 1))
                self.assertAlmostEqual(float(self.model.predict_proba(row)[0].sum()), 1.0)
        safe_row = pd.DataFrame([[app.SAFE_CASE[key] for key in self.features]], columns=self.features)
        unsafe_row = pd.DataFrame([[app.CONTAMINATED_CASE[key] for key in self.features]], columns=self.features)
        adversarial_row = pd.DataFrame([[app.ADVERSARIAL_CASE[key] for key in self.features]], columns=self.features)
        self.assertEqual(int(self.model.predict(safe_row)[0]), 1)
        self.assertEqual(int(self.model.predict(unsafe_row)[0]), 0)
        # This known failure mode must be visible in the UI, never styled as a clean pass.
        self.assertEqual(int(self.model.predict(adversarial_row)[0]), 1)

    def test_invalid_and_excess_values(self):
        normal = {key: "0" for key in self.features}
        for invalid in ("", "text", "nan", "inf", "-1"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    app.validate_inputs({**normal, "arsenic": invalid}, self.features)
        self.assertEqual(app.validate_inputs({**normal, "arsenic": "0,01"}, self.features)["arsenic"], .01)
        self.assertTrue(any("Arsénico" in item for item in app.limit_alerts(app.CONTAMINATED_CASE)))
        self.assertTrue(any("índice combinado" in item for item in app.limit_alerts(app.ADVERSARIAL_CASE)))


if __name__ == "__main__":
    unittest.main()
