from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402

GRAPH = ROOT / "circuits" / "weeks" / "w13" / "graph.json"
VARIANTS = (
    "W13.LAG_SUM1",
    "W13.LAG_INV1",
    "W13.ONEPOLE_AMP1",
    "W13.ONEPOLE_INT2",
    "W13.CLOAD_BASE",
    "W13.CLOAD_COMP",
    "W13.TWOPOLE_REG1",
)


def document() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def parts(variant: str):
    return {item.id: item for item in build_semantic_graph(document(), variant_id=variant, fidelity="ideal").components}


class Week13GraphTests(unittest.TestCase):
    def test_graph_validates_and_all_configs_round_trip(self):
        self.assertEqual([], validate_document(document()))
        for variant in VARIANTS:
            semantic = build_semantic_graph(document(), variant_id=variant, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_sum1_and_inv1_lag_graphs_are_separate_exact_series_rc_shunts(self):
        sum_parts = parts("W13.LAG_SUM1")
        inv_parts = parts("W13.LAG_INV1")
        self.assertIn("W13.LAG_SUM.R", sum_parts)
        self.assertIn("W13.LAG_SUM.C", sum_parts)
        self.assertNotIn("W13.LAG_INV.R", sum_parts)
        self.assertIn("W13.LAG_INV.R", inv_parts)
        self.assertIn("W13.LAG_INV.C", inv_parts)
        self.assertEqual({"P": "SUM1.SUM", "N": "W13.LAG_SUM.RC"}, dict(sum_parts["W13.LAG_SUM.R"].pins))
        self.assertEqual({"P": "W13.LAG_SUM.RC", "N": "SGND"}, dict(sum_parts["W13.LAG_SUM.C"].pins))

    def test_discrete_one_pole_uses_exactly_one_external_selected_capacitor(self):
        ps = parts("W13.ONEPOLE_AMP1")
        self.assertNotIn("AMP1.CC", ps)
        self.assertEqual("47p", ps["W13.AMP1.CC_SELECT"].value)
        self.assertEqual({"P": "AMP1.COMP_A", "N": "AMP1.COMP_B"}, dict(ps["W13.AMP1.CC_SELECT"].pins))

    def test_int2_one_pole_is_a_unity_inverter_not_an_integrator(self):
        ps = parts("W13.ONEPOLE_INT2")
        self.assertIn("DEV.U_INT2", ps)
        self.assertNotIn("INT2.CFB", ps)
        self.assertEqual("4.70k", ps["W13.INT2.RIN"].value)
        self.assertEqual("4.70k", ps["W13.INT2.RFB"].value)
        self.assertEqual("30p", ps["W13.INT2.CC_SELECT"].value)
        self.assertEqual({"P": "INT2.COMPA", "N": "INT2.COMPB"}, dict(ps["W13.INT2.CC_SELECT"].pins))

    def test_cload_baseline_and_compensated_feedback_graphs_are_distinct(self):
        base = parts("W13.CLOAD_BASE")
        comp = parts("W13.CLOAD_COMP")
        self.assertIn("REG1.CC", base)
        self.assertIn("REG1.V_LOOP_INJ", base)
        self.assertNotIn("W13.REG.C_F", base)
        self.assertNotIn("REG1.V_LOOP_INJ", comp)
        self.assertEqual({"P": "REG1.QEMIT", "N": "REG1.SENSE"}, dict(comp["W13.REG.C_F"].pins))
        self.assertEqual({"P": "REG1.VOUT", "N": "REG1.SENSE"}, dict(comp["W13.REG.R_FPATH"].pins))

    def test_regulator_two_pole_is_exact_c_r_c_two_port_and_not_figure_13_21_values(self):
        ps = parts("W13.TWOPOLE_REG1")
        self.assertNotIn("REG1.CC", ps)
        self.assertEqual({"P": "REG1.COMPA", "N": "W13.REG.TWOPOLE_MID"}, dict(ps["W13.REG.C_2P_1"].pins))
        self.assertEqual({"P": "W13.REG.TWOPOLE_MID", "N": "REG1.COMPB"}, dict(ps["W13.REG.C_2P_2"].pins))
        self.assertEqual({"P": "W13.REG.TWOPOLE_MID", "N": "SGND"}, dict(ps["W13.REG.R_2P"].pins))
        self.assertEqual("C1_2P", ps["W13.REG.C_2P_1"].value)
        self.assertEqual("R_2P", ps["W13.REG.R_2P"].value)
        self.assertEqual("C2_2P", ps["W13.REG.C_2P_2"].value)

    def test_week13_is_strict_physical_addition_with_seven_configs(self):
        week = next(item for item in document()["weekly_states"] if item["id"] == "W13")
        self.assertEqual("W12", week["inherits"])
        self.assertEqual([], week["delta"]["remove"])
        self.assertEqual([], week["delta"]["replace"])
        self.assertEqual(set(VARIANTS), set(week["configuration_ids"]))


if __name__ == "__main__":
    unittest.main()

