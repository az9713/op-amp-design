from __future__ import annotations

import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import build_connectivity_receipt, build_semantic_graph, emit_spice, emit_svg, load_layout_overlay, parse_spice, parse_svg  # noqa: E402
from tools.validate_circuit_graph import validate_document  # noqa: E402


GRAPH = ROOT / "circuits" / "weeks" / "w00_04" / "graph.json"
W04_LAYOUT = ROOT / "layout" / "weeks" / "w00_04" / "main-sheet.json"


def load_graph() -> dict:
    return json.loads(GRAPH.read_text(encoding="utf-8"))


class Weeks00To04GraphTests(unittest.TestCase):
    def test_graph_validates(self):
        self.assertEqual([], validate_document(load_graph()))

    def test_all_variants_round_trip_svg_and_spice(self):
        graph = load_graph()
        for variant in graph["variants"]:
            semantic = build_semantic_graph(graph, variant_id=variant["id"], fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, f"{variant['id']}: {receipt.to_json()}")

    def test_week2_is_the_approved_sign_correct_chain(self):
        semantic = build_semantic_graph(load_graph(), variant_id="W02.FIRST_ORDER", fidelity="ideal")
        pins = {component.id: dict(component.pins) for component in semantic.components}
        self.assertEqual("INT1.OUT", pins["SUM1.RIN_A"]["P"])
        self.assertEqual("SUM1.OUT", pins["INV1.RIN"]["P"])
        self.assertEqual("INV1.OUT", pins["INT1.RIN"]["P"])

    def test_week4_has_two_integrators_and_explicit_damping(self):
        semantic = build_semantic_graph(load_graph(), variant_id="W04.SECOND_ORDER_RUN", fidelity="ideal")
        pins = {component.id: dict(component.pins) for component in semantic.components}
        self.assertIn("DEV.U_INT2", pins)
        self.assertEqual("SUM1.OUT", pins["INT1.RIN"]["P"])
        self.assertEqual("INT1.OUT", pins["INT2.RIN"]["P"])
        self.assertEqual({"P": "INV1.OUT", "N": "W04.DAMP"}, pins["W04.RDAMP"])
        self.assertEqual("W04.DAMP", pins["SUM1.RIN_B"]["P"])

    def test_week4_state_nets_have_distinct_visual_channels(self):
        semantic = build_semantic_graph(load_graph(), variant_id="W04.SECOND_ORDER_RUN", fidelity="ideal")
        svg = emit_svg(semantic, layout=load_layout_overlay(W04_LAYOUT))
        root = ET.fromstring(svg)
        trunks = {
            element.attrib["data-net-id"]: element
            for element in root.iter()
            if element.attrib.get("class") == "net-trunk"
            and element.attrib.get("data-net-id") in {"SUM1.OUT", "INT1.OUT"}
        }
        self.assertEqual({"SUM1.OUT", "INT1.OUT"}, set(trunks))
        self.assertEqual(trunks["SUM1.OUT"].attrib["x1"], trunks["SUM1.OUT"].attrib["x2"])
        self.assertEqual(trunks["INT1.OUT"].attrib["x1"], trunks["INT1.OUT"].attrib["x2"])
        separation = abs(float(trunks["SUM1.OUT"].attrib["x1"]) - float(trunks["INT1.OUT"].attrib["x1"]))
        self.assertGreaterEqual(separation, 250.0, "SUM1.OUT and INT1.OUT must not resemble one joined trunk")
        junctions: dict[str, set[tuple[float, float]]] = {"SUM1.OUT": set(), "INT1.OUT": set()}
        for element in root.iter():
            net_id = element.attrib.get("data-net-id")
            if element.attrib.get("class") == "junction" and net_id in junctions:
                junctions[net_id].add((float(element.attrib["cx"]), float(element.attrib["cy"])))
        self.assertTrue(junctions["SUM1.OUT"].isdisjoint(junctions["INT1.OUT"]))

    def test_compensation_variants_are_mutually_exclusive(self):
        graph = load_graph()
        for variant_id, active in (("W03.FIG3_1_REF_12P", "INV1.CC12"), ("W03.FIG3_1_REF_220P", "INV1.CC220"), ("W03.LOOP_CC_12P", "INT1.CC12"), ("W03.LOOP_CC_220P", "INT1.CC220")):
            semantic = build_semantic_graph(graph, variant_id=variant_id, fidelity="ideal")
            ids = {component.id for component in semantic.components}
            self.assertIn(active, ids)
            family = active.split(".CC", 1)[0] + ".CC"
            self.assertEqual([active], sorted(item for item in ids if item.startswith(family)))


if __name__ == "__main__":
    unittest.main()
