from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402

GRAPH = ROOT / "circuits" / "weeks" / "w10" / "graph.json"
MANIFEST = GRAPH.with_name("case-manifest.json")


def document() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


class Week10GraphTests(unittest.TestCase):
    def test_graph_validates(self):
        self.assertEqual([], validate_document(document()))

    def test_all_week10_variants_round_trip(self):
        for variant in ("W10.CR_CHARACTERIZE", "W10.INT1_HOLD", "W10.COMPARE"):
            semantic = build_semantic_graph(document(), variant_id=variant, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_mirror_is_exactly_diode_reference_plus_output_device(self):
        semantic = build_semantic_graph(document(), variant_id="W10.CR_CHARACTERIZE", fidelity="ideal")
        pins = {item.id: dict(item.pins) for item in semantic.components}
        self.assertEqual({"C": "AMP1.N.Q1C_Q4B", "B": "AMP1.N.Q1C_Q4B", "E": "P15"}, pins["AMP1.Q_CR_REF"])
        self.assertEqual({"C": "AMP1.COMP_A", "B": "AMP1.N.Q1C_Q4B", "E": "P15"}, pins["AMP1.Q_CR_OUT"])

    def test_passive_collector_load_is_retained_but_inactive(self):
        semantic = build_semantic_graph(document(), variant_id="W10.CR_CHARACTERIZE", fidelity="ideal")
        states = {item.id: item.state_class for item in semantic.components}
        for cid in ("AMP1.D_BAL", "AMP1.R_BAL_L", "AMP1.R_BAL_R", "AMP1.R_COL_L", "AMP1.R_COL_R"):
            self.assertEqual("persistent-inactive", states[cid])

    def test_hold_has_open_input_capacitor_feedback_and_no_hidden_bleed(self):
        semantic = build_semantic_graph(document(), variant_id="W10.INT1_HOLD", fidelity="ideal")
        parts = {item.id: item for item in semantic.components}
        pins = {item.id: dict(item.pins) for item in semantic.components}
        self.assertEqual("persistent-inactive", parts["INT1.RIN"].state_class)
        self.assertEqual({"P": "AMP1.OUT", "N": "AMP1.INV_IN"}, pins["INT1.CFB"])
        self.assertIn("W10.NONINV_GROUND", parts)
        self.assertNotIn("W09.VSRC", parts)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertFalse(manifest["hold_protocol"]["hidden_bleed_allowed"])

    def test_compare_uses_equal_caps_loads_and_locked_lm301a(self):
        semantic = build_semantic_graph(document(), variant_id="W10.COMPARE", fidelity="ideal")
        parts = {item.id: item for item in semantic.components}
        self.assertEqual("1u", parts["INT1.CFB"].value)
        self.assertEqual("1u", parts["INT2.CFB"].value)
        self.assertEqual("10Meg", parts["W10.R_SCOPE_INT1"].value)
        self.assertEqual("10Meg", parts["W10.R_SCOPE_INT2"].value)
        self.assertIn("LM301A", parts["DEV.U_INT2"].parameters["historical_type"])

    def test_week10_is_strict_addition_with_declared_state_transition(self):
        week = next(item for item in document()["weekly_states"] if item["id"] == "W10")
        self.assertEqual("W09", week["inherits"])
        self.assertEqual({"AMP1.Q_CR_REF", "AMP1.Q_CR_OUT", "W10.R_SCOPE_INT1", "W10.R_SCOPE_INT2", "W10.NONINV_GROUND"}, set(week["delta"]["add"]))
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertIn("separately reviewable", manifest["optional_fig10_25_fet_branch"])


if __name__ == "__main__":
    unittest.main()
