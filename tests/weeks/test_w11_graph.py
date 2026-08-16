from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402

GRAPH = ROOT / "circuits" / "weeks" / "w11" / "graph.json"
MANIFEST = GRAPH.with_name("case-manifest.json")
VARIANTS = (
    "W11.INT_OPERATE", "W11.INT_RESET", "W11.INT_HOLD",
    "W11.DUT_EO", "W11.DUT_IMINUS", "W11.DUT_IPLUS", "W11.RECT",
)


def document() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


def parts(variant: str):
    return {item.id: item for item in build_semantic_graph(document(), variant_id=variant, fidelity="ideal").components}


class Week11GraphTests(unittest.TestCase):
    def test_graph_validates_and_all_variants_round_trip(self):
        self.assertEqual([], validate_document(document()))
        for variant in VARIANTS:
            semantic = build_semantic_graph(document(), variant_id=variant, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_mode_truth_table_and_safe_hold_default(self):
        expected = {
            "W11.INT_OPERATE": ("persistent-installed", "persistent-inactive", True, False),
            "W11.INT_RESET": ("persistent-inactive", "persistent-installed", False, True),
            "W11.INT_HOLD": ("persistent-inactive", "persistent-inactive", False, False),
        }
        for variant, (op_state, rst_state, op_source, rst_source) in expected.items():
            ps = parts(variant)
            for tag in ("I1", "I2"):
                self.assertEqual(op_state, ps[f"W11.{tag}.S_OP"].state_class)
                self.assertEqual(rst_state, ps[f"W11.{tag}.S_RST"].state_class)
                self.assertEqual(op_source, f"W11.{tag}.V_OP" in ps)
                self.assertEqual(rst_source, f"W11.{tag}.V_RST" in ps)
                self.assertEqual("100k", ps[f"W11.{tag}.R_LOGIC_OP_PD"].value)
                self.assertEqual("100k", ps[f"W11.{tag}.R_LOGIC_RST_PD"].value)

    def test_both_channels_are_independent_practical_copies(self):
        ps = parts("W11.INT_OPERATE")
        for tag in ("I1", "I2"):
            self.assertEqual("9.975k", ps[f"W11.{tag}.R_OP"].value)
            self.assertEqual("10k", ps[f"W11.{tag}.R2_TOP"].value)
            self.assertEqual("10k", ps[f"W11.{tag}.R2_BOTTOM"].value)
            self.assertEqual("2N4391", ps[f"W11.{tag}.S_OP"].parameters["historical_type"])
            self.assertEqual("2N4091", ps[f"W11.{tag}.S_RST"].parameters["historical_type"])
            self.assertEqual("2N2907", ps[f"W11.{tag}.Q_OP_DRV"].parameters["historical_type"])

    def test_error_fixtures_are_mutually_exclusive_and_source_values_match(self):
        active = {
            "W11.DUT_EO": {"W11.ERR.R_EO_G", "W11.ERR.R_EO_FB", "W11.ERR.NONINV_GND", "W11.ERR.R_LOAD"},
            "W11.DUT_IMINUS": {"W11.ERR.R_IM", "W11.ERR.NONINV_GND", "W11.ERR.R_LOAD"},
            "W11.DUT_IPLUS": {"W11.ERR.R_IP", "W11.ERR.VFOLLOW", "W11.ERR.R_LOAD"},
        }
        for variant, expected in active.items():
            actual = {cid for cid in parts(variant) if cid.startswith("W11.ERR.")}
            self.assertEqual(expected, actual)
        ps = parts("W11.DUT_EO")
        self.assertEqual("1k", ps["W11.ERR.R_EO_G"].value)
        self.assertEqual("999k", ps["W11.ERR.R_EO_FB"].value)
        self.assertEqual("10Meg", parts("W11.DUT_IMINUS")["W11.ERR.R_IM"].value)

    def test_rectifier_is_actual_figure_11_18_not_bridge(self):
        ps = parts("W11.RECT")
        rect = {cid: item for cid, item in ps.items() if cid.startswith("RECT1.")}
        self.assertEqual(7, len(rect))
        self.assertEqual({"A": "RECT1.DRIVE", "K": "RECT1.OUT"}, dict(rect["RECT1.D1"].pins))
        self.assertEqual({"P": "RECT1.OUT", "N": "SGND"}, dict(rect["RECT1.R_LOAD"].pins))
        self.assertEqual(1, sum(item.kind == "diode" for item in rect.values()))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("Figure 11.19", manifest["rectifier_source_correction"])

    def test_week11_is_strict_addition_and_preserves_old_input_resistors(self):
        week = next(item for item in document()["weekly_states"] if item["id"] == "W11")
        self.assertEqual("W10", week["inherits"])
        self.assertEqual([], week["delta"]["remove"])
        self.assertEqual([], week["delta"]["replace"])
        self.assertEqual("persistent-inactive", parts("W11.INT_HOLD")["INT1.RIN"].state_class)
        self.assertEqual("persistent-inactive", parts("W11.INT_HOLD")["INT2.RIN"].state_class)


if __name__ == "__main__":
    unittest.main()
