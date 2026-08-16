from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402

GRAPH = ROOT / "circuits" / "weeks" / "w09_reconciled" / "graph.json"
CASES = GRAPH.with_name("case-manifest.json")


def document() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


class Week09ReconciledGraphTests(unittest.TestCase):
    def test_graph_validates(self):
        self.assertEqual([], validate_document(document()))

    def test_week09_is_strict_q12_q13_permanent_delta(self):
        week = next(item for item in document()["weekly_states"] if item["id"] == "W09")
        permanent = {item for item in week["delta"]["add"] if item.startswith("AMP1.")}
        self.assertEqual({"AMP1.Q12", "AMP1.Q13"}, permanent)
        self.assertEqual("W08", week["inherits"])

    def test_all_week09_variants_round_trip(self):
        for variant in ("W09.CC_SWEEP", "W09.INVERTER_TEST", "W09.INT1_RESTORED"):
            semantic = build_semantic_graph(document(), variant_id=variant, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_complete_amp_has_q1_through_q13(self):
        semantic = build_semantic_graph(document(), variant_id="W09.INVERTER_TEST", fidelity="ideal")
        ids = {item.id for item in semantic.components}
        self.assertTrue({f"AMP1.Q{index}" for index in range(1, 14)} <= ids)

    def test_inverter_fixture_values_and_alpha_open(self):
        semantic = build_semantic_graph(document(), variant_id="W09.INVERTER_TEST", fidelity="ideal")
        parts = {item.id: item for item in semantic.components}
        self.assertEqual("4.70k", parts["W09.RIN"].value)
        self.assertEqual("4.70k", parts["W09.RFB"].value)
        self.assertEqual("50", parts["W09.RSOURCE"].value)
        self.assertEqual("10Meg", parts["W09.LOAD"].value)
        self.assertNotIn("W09.RALPHA", parts)

    def test_restored_int1_has_exact_feedback_and_no_source_fixture(self):
        semantic = build_semantic_graph(document(), variant_id="W09.INT1_RESTORED", fidelity="ideal")
        parts = {item.id: item for item in semantic.components}
        pins = {item.id: dict(item.pins) for item in semantic.components}
        self.assertEqual("AMP1.INV_IN", pins["INT1.RIN"]["N"])
        self.assertEqual({"P": "AMP1.OUT", "N": "AMP1.INV_IN"}, pins["INT1.CFB"])
        self.assertEqual("AMP1.OUT", pins["INT1.ROUT"]["P"])
        self.assertNotIn("W09.VSRC", parts)
        self.assertNotIn("W09.RIN", parts)
        self.assertEqual("47p", parts["AMP1.CC"].value)

    def test_case_manifest_has_six_source_cases_and_one_socket(self):
        manifest = json.loads(CASES.read_text(encoding="utf-8"))
        self.assertEqual(
            {"CASE.W09.A47", "CASE.W09.A33", "CASE.W09.A10", "CASE.W09.A05", "CASE.W09.B20", "CASE.W09.B10"},
            {case["id"] for case in manifest["cases"]},
        )
        self.assertIn("single physical AMP1.CC socket", manifest["authority_note"])
        self.assertFalse(manifest["claim_boundary"]["hidden_bleed_allowed"])


if __name__ == "__main__":
    unittest.main()
