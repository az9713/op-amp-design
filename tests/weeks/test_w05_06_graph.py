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


GRAPH_PATH = ROOT / "circuits" / "weeks" / "w05_06" / "graph.json"
CASE_PATH = ROOT / "circuits" / "weeks" / "w05_06" / "case-manifest.json"
PROOF_PATH = ROOT / "generated" / "weeks05_06" / "proof" / "summary.json"
W05_LAYOUT = ROOT / "layout" / "weeks" / "w05_06" / "w05-main-sheet.json"
W06_LAYOUT = ROOT / "layout" / "weeks" / "w05_06" / "w06-main-sheet.json"


def graph() -> dict:
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def pin_map(component: dict) -> dict[str, str | None]:
    return {pin["id"]: pin["net"] for pin in component["pins"]}


class Weeks05To06GraphTests(unittest.TestCase):
    def test_graph_validates(self):
        self.assertEqual([], validate_document(graph()))

    def test_both_variants_round_trip_svg_and_spice(self):
        document = graph()
        for variant_id in ("W05.REGULATOR_SWEEP", "W06.OSCILLATOR"):
            semantic = build_semantic_graph(document, variant_id=variant_id, fidelity="ideal")
            receipt = build_connectivity_receipt(semantic, parse_svg(emit_svg(semantic)), parse_spice(emit_spice(semantic)))
            self.assertTrue(receipt.passed, receipt.to_json())

    def test_regulator_operating_envelope_and_source_limit_are_explicit(self):
        components = {item["id"]: item for item in graph()["components"]}
        self.assertEqual("18", components["REG1.V_UNREG"]["value"])
        self.assertEqual("35mA", components["REG1.V_UNREG"]["parameters"]["current_limit"])
        self.assertEqual("100", components["REG1.R_EMIT"]["value"])
        self.assertEqual("BD139", components["REG1.Q_PASS"]["parameters"]["historical_type"])
        self.assertEqual({"C": "REG1.VUNREG", "B": "REG1.QBASE", "E": "REG1.QEMIT"}, pin_map(components["REG1.Q_PASS"]))
        self.assertEqual({"P": "REG1.VOUT", "N": "REG1.SENSE"}, pin_map(components["REG1.V_LOOP_INJ"]))

    def test_regulator_case_manifest_has_all_nine_combinations(self):
        manifest = json.loads(CASE_PATH.read_text(encoding="utf-8"))
        self.assertEqual(3, len(manifest["load_resistance_cases"]))
        self.assertEqual(3, len(manifest["load_capacitance_cases"]))
        self.assertEqual(9, len(manifest["load_resistance_cases"]) * len(manifest["load_capacitance_cases"]))
        self.assertEqual("35mA", manifest["plant_input"]["current_limit"])

    def test_oscillator_is_dedicated_int3_and_has_true_back_to_back_zeners(self):
        components = {item["id"]: item for item in graph()["components"]}
        self.assertEqual("DEV.INT3", components["DEV.U_INT3_OSC"]["module_id"])
        self.assertEqual({"A": "OSC1.ZMID", "K": "OSC1.SQUARE"}, pin_map(components["OSC1.D_ZP"]))
        self.assertEqual({"A": "OSC1.ZMID", "K": "SGND"}, pin_map(components["OSC1.D_ZN"]))
        self.assertEqual("100k", components["OSC1.R_TRI"]["value"])
        self.assertEqual("100k", components["OSC1.R_HYS"]["value"])
        self.assertEqual("1Meg", components["OSC1.R_INT"]["value"])
        self.assertEqual("1u", components["OSC1.C_INT"]["value"])
        self.assertEqual("10m", components["OSC1.C_INT"]["parameters"]["simulation_initial_condition"])

    def test_checked_topology_proof_meets_weekly_claims(self):
        proof = json.loads(PROOF_PATH.read_text(encoding="utf-8"))
        self.assertTrue(proof["week05"]["passed"])
        self.assertEqual(9, len(proof["week05"]["operating_points"]))
        self.assertTrue(all(9.0 <= item["vout_v"] <= 11.0 for item in proof["week05"]["operating_points"]))
        self.assertTrue(proof["week06"]["passed"])
        self.assertGreater(proof["week06"]["square_max_v"] - proof["week06"]["square_min_v"], 8.0)
        self.assertGreater(proof["week06"]["triangle_max_v"] - proof["week06"]["triangle_min_v"], 8.0)
        self.assertTrue(all(3.0 <= period <= 5.0 for period in proof["week06"]["measured_periods_s"]))

    def test_main_views_hide_descendants_of_collapsed_retained_modules(self):
        document = graph()
        cases = (("W05.REGULATOR_SWEEP", W05_LAYOUT), ("W06.OSCILLATOR", W06_LAYOUT))
        for variant_id, layout_path in cases:
            svg = emit_svg(build_semantic_graph(document, variant_id=variant_id, fidelity="ideal"), layout=load_layout_overlay(layout_path))
            root = ET.fromstring(svg)
            visible_component_ids = {
                item.attrib["data-component-id"]
                for item in root.iter()
                if item.attrib.get("data-component-id") and "semantic-ledger" not in item.attrib.get("class", "") and "collapsed-member" not in item.attrib.get("class", "")
            }
            self.assertNotIn("DEV.U_SUM1", visible_component_ids)
            self.assertNotIn("DEV.U_INV1", visible_component_ids)
            self.assertNotIn("DEV.U_INT1_STOCK", visible_component_ids)
            self.assertNotIn("DEV.U_INT2", visible_component_ids)

    def test_oscillator_zener_symbols_are_drawn_opposed(self):
        layout = load_layout_overlay(W06_LAYOUT)
        self.assertEqual(270, layout["components"]["OSC1.D_ZP"]["rotation"])
        self.assertEqual(90, layout["components"]["OSC1.D_ZN"]["rotation"])


if __name__ == "__main__":
    unittest.main()
