from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402

GRAPH = ROOT / "circuits" / "weeks" / "w07_08" / "graph.json"


def document() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


class Weeks07To08GraphTests(unittest.TestCase):
    def test_graph_validates(self):
        self.assertEqual([], validate_document(document()))

    def test_all_variants_round_trip(self):
        for variant in ("W07.PAIR_CHARACTERIZE", "W08.OPEN_LOOP", "W08.INT1_BRINGUP"):
            semantic = build_semantic_graph(document(), variant_id=variant, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_week7_is_honestly_incomplete(self):
        semantic = build_semantic_graph(document(), variant_id="W07.PAIR_CHARACTERIZE", fidelity="ideal")
        ids = {item.id for item in semantic.components}
        self.assertTrue({"AMP1.Q1", "AMP1.Q2", "AMP1.Q3"} <= ids)
        self.assertFalse(any(item in ids for item in {"AMP1.Q4", "AMP1.Q8", "AMP1.Q10", "AMP1.Q11", "AMP1.CC"}))
        self.assertFalse(any(net == "AMP1.OUT" for item in semantic.components for _, net in item.pins))
        self.assertNotIn("DEV.U_INT1_STOCK", ids)

    def test_week8_uses_exact_future_subset_without_limiters(self):
        semantic = build_semantic_graph(document(), variant_id="W08.OPEN_LOOP", fidelity="ideal")
        ids = {item.id for item in semantic.components}
        self.assertTrue({f"AMP1.Q{index}" for index in range(1, 12)} <= ids)
        self.assertNotIn("AMP1.Q12", ids)
        self.assertNotIn("AMP1.Q13", ids)
        cc = next(item for item in semantic.components if item.id == "AMP1.CC")
        self.assertEqual("47p", cc.value)

    def test_closed_week8_connects_inherited_int1_network_to_amp1(self):
        semantic = build_semantic_graph(document(), variant_id="W08.INT1_BRINGUP", fidelity="ideal")
        pins = {item.id: dict(item.pins) for item in semantic.components}
        self.assertEqual("AMP1.INV_IN", pins["INT1.RIN"]["N"])
        self.assertEqual({"P": "AMP1.OUT", "N": "AMP1.INV_IN"}, pins["INT1.CFB"])
        self.assertEqual("AMP1.OUT", pins["INT1.ROUT"]["P"])


if __name__ == "__main__":
    unittest.main()
