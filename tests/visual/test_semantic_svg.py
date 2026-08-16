from __future__ import annotations

import copy
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

from connectivity.test_circuit_pipeline import component, model, synthetic_graph  # noqa: E402
from tools.circuit_pipeline import (  # noqa: E402
    build_connectivity_receipt,
    build_semantic_graph,
    emit_spice,
    emit_svg,
    emit_svg_detail,
    parse_spice,
    parse_svg,
)


SVG = {"svg": "http://www.w3.org/2000/svg"}


def visual_graph() -> dict:
    graph = synthetic_graph()
    graph["models"].extend(
        [
            model("MODEL.C.I", "ideal", "primitive", "C", ["P", "N"]),
            model("MODEL.C.R", "realistic", "primitive", "C_REAL", ["P", "N"]),
            model("MODEL.D.I", "ideal", "primitive", "D_IDEAL", ["A", "K"]),
            model("MODEL.D.R", "realistic", "primitive", "D_REAL", ["A", "K"]),
            model("MODEL.PNP.I", "ideal", "primitive", "PNP_IDEAL", ["C", "B", "E"]),
            model("MODEL.PNP.R", "realistic", "primitive", "PNP_REAL", ["C", "B", "E"]),
            model("MODEL.J.I", "ideal", "primitive", "NJF_IDEAL", ["D", "G", "S"]),
            model("MODEL.J.R", "realistic", "primitive", "NJF_REAL", ["D", "G", "S"]),
            model("MODEL.I.I", "ideal", "primitive", "I", ["P", "N"]),
            model("MODEL.I.R", "realistic", "primitive", "I_REAL", ["P", "N"]),
            model("MODEL.X.I", "ideal", "subcircuit", "GENERIC_IDEAL", ["IN", "OUT"]),
            model("MODEL.X.R", "realistic", "subcircuit", "GENERIC_REAL", ["IN", "OUT"]),
        ]
    )
    additions = [
        component("DEV.C1", "capacitor", "MOD.ROOT", [("P", "NET.VOUT"), ("N", "SGND")], "MODEL.C.I", "MODEL.C.R", value="100p"),
        component("DEV.D1", "diode", "MOD.ROOT", [("A", "NET.VOUT"), ("K", "SGND")], "MODEL.D.I", "MODEL.D.R", value="1N4148"),
        component("DEV.Q3", "pnp_bjt", "MOD.ROOT.DIFF", [("C", "NET.C1"), ("B", "NET.VIN"), ("E", "P15")], "MODEL.PNP.I", "MODEL.PNP.R"),
        component("DEV.J1", "n_jfet", "MOD.ROOT.DIFF", [("D", "NET.C2"), ("G", "NET.CTRL"), ("S", "N15")], "MODEL.J.I", "MODEL.J.R"),
        component("DEV.I1", "current_source", "MOD.ROOT", [("P", "P15"), ("N", "NET.TAIL")], "MODEL.I.I", "MODEL.I.R", value="1m"),
        component("DEV.X1", "subcircuit", "MOD.ROOT", [("IN", "NET.VIN"), ("OUT", "NET.VOUT")], "MODEL.X.I", "MODEL.X.R", value="BLOCK"),
    ]
    graph["components"].extend(additions)
    graph["modules"][0]["component_ids"].extend(["DEV.C1", "DEV.D1", "DEV.I1", "DEV.X1"])
    graph["modules"][2]["component_ids"].extend(["DEV.Q3", "DEV.J1"])
    graph["weekly_states"][0]["delta"]["add"].extend(item["id"] for item in additions)

    positions = {
        "DEV.VIN": (100, 150, 0, False, "active"),
        "DEV.C1": (270, 150, 90, False, "changed"),
        "DEV.D1": (440, 150, 0, True, "inactive"),
        "DEV.I1": (610, 150, 0, False, "active"),
        "DEV.X1": (790, 150, 0, False, "active"),
        "DEV.RIN": (120, 360, 0, False, "active"),
        "DEV.RFB": (300, 360, 90, False, "changed"),
        "DEV.OP1": (500, 360, 0, False, "active"),
        "DEV.S1": (650, 360, 0, False, "inactive"),
        "DEV.Q1": (140, 590, 0, False, "active"),
        "DEV.Q2": (300, 590, 0, False, "active"),
        "DEV.Q3": (460, 590, 0, False, "active"),
        "DEV.J1": (620, 590, 270, False, "active"),
    }
    for item in graph["components"]:
        x, y, rotation, mirror, style = positions[item["id"]]
        item["render"] = {"x": x, "y": y, "rotation": rotation, "mirror": mirror, "style": style}
    return graph


def elements_with_class(root: ET.Element, class_name: str) -> list[ET.Element]:
    return [element for element in root.iter() if class_name in element.attrib.get("class", "").split()]


class SemanticSvgTests(unittest.TestCase):
    def setUp(self) -> None:
        self.semantic = build_semantic_graph(visual_graph(), variant_id="CFG.SWITCHED", fidelity="ideal")
        self.text = emit_svg(self.semantic)
        self.root = ET.fromstring(self.text)

    def test_conventional_symbol_catalog_is_semantically_identifiable(self):
        for class_name in (
            "resistor-body",
            "capacitor-plate",
            "diode-body",
            "diode-bar",
            "opamp-body",
            "transistor-arrow",
            "jfet-arrow",
            "source-body",
            "source-arrow",
            "switch-contact",
            "subcircuit-body",
            "voltage-polarity",
            "ground-symbol",
            "power-arrow",
        ):
            self.assertTrue(elements_with_class(self.root, class_name), class_name)
        polarities = {item.attrib["data-polarity"] for item in elements_with_class(self.root, "transistor-arrow")}
        self.assertEqual({"npn", "pnp"}, polarities)

    def test_render_position_rotation_mirror_and_style_are_honored(self):
        groups = {item.attrib["data-component-id"]: item for item in elements_with_class(self.root, "component")}
        self.assertEqual("translate(270.0 150.0) rotate(90)", groups["DEV.C1"].attrib["transform"])
        self.assertEqual("translate(440.0 150.0) rotate(0) scale(-1 1)", groups["DEV.D1"].attrib["transform"])
        self.assertIn("changed", groups["DEV.C1"].attrib["class"].split())
        self.assertIn("inactive", groups["DEV.D1"].attrib["class"].split())

    def test_wires_are_orthogonal_and_junctions_and_crossings_are_explicit(self):
        for wire in elements_with_class(self.root, "wire"):
            points = [tuple(float(value) for value in pair.split(",")) for pair in wire.attrib["points"].split()]
            for first, second in zip(points, points[1:]):
                self.assertTrue(first[0] == second[0] or first[1] == second[1], wire.attrib["points"])
        self.assertTrue(elements_with_class(self.root, "junction"))
        crossings = elements_with_class(self.root, "crossing")
        self.assertTrue(crossings)
        self.assertTrue(all(item.attrib["data-connected"] == "false" for item in crossings))

    def test_power_ground_ports_and_main_detail_boundaries(self):
        self.assertTrue(elements_with_class(self.root, "port-line"))
        self.assertEqual(3, len(elements_with_class(self.root, "module-boundary")))
        detail_text = emit_svg_detail(self.semantic, "MOD.ROOT.LOOP")
        detail_root = ET.fromstring(detail_text)
        self.assertEqual("detail", detail_root.attrib["data-view"])
        self.assertEqual("MOD.ROOT.LOOP", detail_root.attrib["data-detail-module-id"])
        self.assertEqual(1, len(elements_with_class(detail_root, "module-boundary")))
        parsed = parse_svg(detail_text)
        self.assertEqual({"MOD.ROOT.LOOP"}, set(parsed["modules"]))
        self.assertEqual({"DEV.RIN", "DEV.RFB", "DEV.OP1", "DEV.S1"}, set(parsed["components"]))

    def test_main_svg_preserves_connectivity_and_is_deterministic(self):
        parsed_svg = parse_svg(self.text)
        parsed_spice = parse_spice(emit_spice(self.semantic))
        receipt = build_connectivity_receipt(self.semantic, parsed_svg, parsed_spice)
        self.assertTrue(receipt.passed, receipt.to_json())
        other = build_semantic_graph(copy.deepcopy(visual_graph()), variant_id="CFG.SWITCHED", fidelity="ideal")
        self.assertEqual(self.text, emit_svg(other))

    def test_labels_include_stable_designators_values_and_pin_names(self):
        designators = {item.text for item in elements_with_class(self.root, "designator")}
        values = {item.text for item in elements_with_class(self.root, "value")}
        pins = {item.text for item in elements_with_class(self.root, "pin-label")}
        self.assertIn("DEV.OP1", designators)
        self.assertIn("1N4148", values)
        self.assertTrue({"INP", "INM", "OUT", "VP", "VN"}.issubset(pins))

    def test_detail_rejects_unknown_module(self):
        with self.assertRaisesRegex(ValueError, "unknown detail module"):
            emit_svg_detail(self.semantic, "MOD.MISSING")


if __name__ == "__main__":
    unittest.main()
