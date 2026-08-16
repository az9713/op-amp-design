from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402

GRAPH = ROOT / "circuits" / "weeks" / "w12" / "graph.json"
MANIFEST = GRAPH.with_name("case-manifest.json")
VARIANTS = ("W12.BW", "W12.VDP", "W12.REG_TWIN")


def document() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def parts(variant: str):
    return {item.id: item for item in build_semantic_graph(document(), variant_id=variant, fidelity="ideal").components}


class Week12GraphTests(unittest.TestCase):
    def test_graph_validates_and_configurations_round_trip(self):
        self.assertEqual([], validate_document(document()))
        for variant in VARIANTS:
            semantic = build_semantic_graph(document(), variant_id=variant, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_butterworth_has_four_integrators_and_exact_coefficients(self):
        ps = parts("W12.BW")
        self.assertEqual("10u", ps["W12.BW.C_I0"].value)
        self.assertEqual("10u", ps["W12.BW.C_I1"].value)
        self.assertEqual("10u", ps["W12.BW.C_I2"].value)
        self.assertEqual("10u", ps["W12.BW.C_I3"].value)
        self.assertEqual("38.3k", ps["W12.BW.R_Q3"].value)
        self.assertEqual("38.3k", ps["W12.BW.R_Q1"].value)
        self.assertEqual("29.2k", ps["W12.BW.R_INV_X2"].value)
        self.assertEqual("W12.BW.INT3_SUM", dict(ps["DEV.U_INT3_OSC"].pins)["INM"])
        self.assertEqual("W12.BW.X", dict(ps["DEV.U_INT3_OSC"].pins)["OUT"])

    def test_van_der_pol_uses_two_true_four_quadrant_ad633s(self):
        ps = parts("W12.VDP")
        multipliers = [item for item in ps.values() if item.model_id == "MODEL.W12.AD633.I"]
        self.assertEqual(2, len(multipliers))
        m1 = dict(ps["W12.VDP.M_X2"].pins)
        m2 = dict(ps["W12.VDP.M_X2D1"].pins)
        self.assertEqual(m1["X1"], m1["Y1"])
        self.assertEqual("INT2.OUT", m1["X1"])
        self.assertEqual("W12.VDP.X2_DIV10", m1["W"])
        self.assertEqual("W12.VDP.X2_DIV10", m2["X1"])
        self.assertEqual("AMP1.OUT", m2["Y1"])
        self.assertEqual("W12.VDP.NONLIN", m2["W"])
        self.assertEqual("10k", ps["W12.VDP.R_NONLIN"].value)
        self.assertEqual("1Meg", ps["W12.VDP.R_SUM_D1"].value)

    def test_regulator_twin_uses_same_oscillator_event_and_measured_calibration(self):
        ps = parts("W12.REG_TWIN")
        self.assertEqual("OSC1.SQUARE", dict(ps["W12.TWIN.S_LOAD"].pins)["CTRL_P"])
        self.assertEqual("OSC1.SQUARE", dict(ps["W12.TWIN.R_SUM_IN"].pins)["P"])
        self.assertEqual("R_TWIN_LEAK", ps["W12.TWIN.R_LEAK"].value)
        self.assertEqual("R_TWIN_DRIVE", ps["W12.TWIN.R_DRIVE"].value)
        self.assertIn("REG1.Q_PASS", ps)
        self.assertNotIn("REG1.I_DIST", ps)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        calibration = manifest["configurations"]["W12.REG_TWIN"]["calibration"]
        self.assertIn("measured", calibration["K_DROOP"])
        self.assertIn("measured", calibration["TAU_MEAS"])

    def test_configs_are_distinct_and_multiplier_choice_is_explicit(self):
        self.assertNotIn("W12.VDP.M_X2", parts("W12.BW"))
        self.assertNotIn("W12.BW.C_I3", parts("W12.VDP"))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("AD633", manifest["configurations"]["W12.VDP"]["multiplier"])
        self.assertIn("Figure 12.9", " ".join(manifest["deferred"]))

    def test_week12_is_strict_physical_addition(self):
        week = next(item for item in document()["weekly_states"] if item["id"] == "W12")
        self.assertEqual("W11", week["inherits"])
        self.assertEqual([], week["delta"]["remove"])
        self.assertEqual([], week["delta"]["replace"])
        self.assertEqual({"W12.BW", "W12.VDP", "W12.REG_TWIN"}, set(week["configuration_ids"]))


if __name__ == "__main__":
    unittest.main()
