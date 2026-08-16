from __future__ import annotations

import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import (  # noqa: E402
    build_connectivity_receipt,
    build_semantic_graph,
    emit_spice,
    emit_svg,
    emit_svg_detail,
    load_layout_overlay,
    parse_spice,
    parse_svg,
)
from tools.circuit_pipeline.__main__ import main as pipeline_main  # noqa: E402


GRAPH_PATH = ROOT / "circuits" / "weeks" / "w09" / "graph.json"
MAIN_LAYOUT_PATH = ROOT / "layout" / "weeks" / "w09" / "main-sheet.json"
DETAIL_LAYOUT_PATH = ROOT / "layout" / "weeks" / "w09" / "amp1-detail.json"


def classes(root: ET.Element, name: str) -> list[ET.Element]:
    return [element for element in root.iter() if name in element.attrib.get("class", "").split()]


def assert_no_foreign_terminal_through_wires(test: unittest.TestCase, root: ET.Element) -> None:
    anchors: list[tuple[str, float, float, str]] = []
    for terminal in classes(root, "terminal"):
        if "data-global-x" in terminal.attrib:
            anchors.append((terminal.attrib["data-net-id"], float(terminal.attrib["data-global-x"]), float(terminal.attrib["data-global-y"]), terminal.attrib["data-pin-id"]))
    for port in classes(root, "module-port"):
        if "semantic-ledger" not in port.attrib.get("class", "").split():
            anchors.append((port.attrib["data-net-id"], float(port.attrib["cx"]), float(port.attrib["cy"]), port.attrib["data-port-id"]))
    routed = classes(root, "wire") + classes(root, "port-wire") + classes(root, "net-trunk")
    for route in routed:
        net_id = route.attrib["data-net-id"]
        if route.tag.rsplit("}", 1)[-1] == "line":
            points = [(float(route.attrib["x1"]), float(route.attrib["y1"])), (float(route.attrib["x2"]), float(route.attrib["y2"]))]
        else:
            points = [tuple(float(value) for value in pair.split(",")) for pair in route.attrib["points"].split()]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            for anchor_net, x, y, anchor_id in anchors:
                if anchor_net == net_id:
                    continue
                through = y1 == y2 and abs(y - y1) <= 4 and min(x1, x2) + 4 < x < max(x1, x2) - 4
                through = through or x1 == x2 and abs(x - x1) <= 4 and min(y1, y2) + 4 < y < max(y1, y2) - 4
                test.assertFalse(through, f"{net_id} route passes through {anchor_net} terminal {anchor_id} at {(x, y)}")


def assert_foreign_nets_avoid_collapsed_modules(test: unittest.TestCase, root: ET.Element) -> None:
    obstacles: list[tuple[str, set[str], tuple[float, float, float, float]]] = []
    for module in classes(root, "collapsed-module"):
        boundary = next(child for child in module if "module-boundary" in child.attrib.get("class", "").split())
        left, top = float(boundary.attrib["x"]), float(boundary.attrib["y"])
        rectangle = (left, top, left + float(boundary.attrib["width"]), top + float(boundary.attrib["height"]))
        port_nets = {child.attrib["data-net-id"] for child in module if "module-port" in child.attrib.get("class", "").split()}
        obstacles.append((module.attrib["data-module-id"], port_nets, rectangle))
    for route in classes(root, "wire") + classes(root, "port-wire") + classes(root, "net-trunk"):
        net_id = route.attrib["data-net-id"]
        if route.tag.rsplit("}", 1)[-1] == "line":
            points = [(float(route.attrib["x1"]), float(route.attrib["y1"])), (float(route.attrib["x2"]), float(route.attrib["y2"]))]
        else:
            points = [tuple(float(value) for value in pair.split(",")) for pair in route.attrib["points"].split()]
        for (x1, y1), (x2, y2) in zip(points, points[1:]):
            for module_id, port_nets, (left, top, right, bottom) in obstacles:
                if net_id in port_nets:
                    continue
                enters = y1 == y2 and top < y1 < bottom and max(min(x1, x2), left) < min(max(x1, x2), right)
                enters = enters or x1 == x2 and left < x1 < right and max(min(y1, y2), top) < min(max(y1, y2), bottom)
                test.assertFalse(enters, f"foreign net {net_id} enters collapsed module {module_id}")


class Week09LayoutProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        cls.semantic = build_semantic_graph(cls.document, variant_id="W09.INVERTER_TEST", fidelity="ideal")
        cls.main_layout = load_layout_overlay(MAIN_LAYOUT_PATH)
        cls.detail_layout = load_layout_overlay(DETAIL_LAYOUT_PATH)

    def test_main_collapses_amp1_but_full_connectivity_still_round_trips(self):
        text = emit_svg(self.semantic, layout=self.main_layout)
        root = ET.fromstring(text)
        collapsed = [item for item in classes(root, "collapsed-module") if item.attrib["data-module-id"] == "AMP1"]
        self.assertEqual(1, len(collapsed))
        self.assertEqual("W09.AMP1_DETAIL", collapsed[0].attrib["data-detail-ref"])
        visible_amp_symbols = [item for item in classes(root, "component") if item.attrib.get("data-module-id") == "AMP1" and "collapsed-member" not in item.attrib.get("class", "")]
        self.assertEqual([], visible_amp_symbols)
        self.assertEqual(41, len([item for item in classes(root, "collapsed-member") if item.attrib["data-module-id"] == "AMP1"]))
        receipt = build_connectivity_receipt(self.semantic, parse_svg(text), parse_spice(emit_spice(self.semantic)))
        self.assertTrue(receipt.passed, receipt.to_json())

    def test_main_consumes_fixture_positions_and_avoids_external_bus_wall(self):
        root = ET.fromstring(emit_svg(self.semantic, layout=self.main_layout))
        groups = {item.attrib["data-component-id"]: item for item in classes(root, "component") if "collapsed-member" not in item.attrib.get("class", "")}
        self.assertEqual("translate(350.0 400.0) rotate(0)", groups["W09.RIN"].attrib["transform"])
        self.assertEqual("translate(570.0 500.0) rotate(90)", groups["W09.LOAD"].attrib["transform"])
        self.assertIn("inactive", groups["MOD.INT1.RIN"].attrib["class"].split())
        amp = next(item for item in classes(root, "collapsed-module") if item.attrib["data-module-id"] == "AMP1")
        hidden_ports = {item.attrib["data-port-id"] for item in amp if "semantic-ledger" in item.attrib.get("class", "").split()}
        self.assertTrue({"COMP_A", "COMP_B"}.issubset(hidden_ports))
        vertical_trunks = [item for item in classes(root, "net-trunk") if item.tag.endswith("line") and item.attrib["x1"] == item.attrib["x2"]]
        self.assertFalse(any(float(item.attrib["x1"]) > 1490 for item in vertical_trunks))
        self.assertGreater(len(classes(root, "port-wire")), 0)

    def test_amp1_detail_consumes_every_intentional_position(self):
        text = emit_svg_detail(self.semantic, "AMP1", layout=self.detail_layout)
        root = ET.fromstring(text)
        self.assertEqual("W09.AMP1_DETAIL", root.attrib["data-layout-id"])
        self.assertEqual(4, len(classes(root, "zone")))
        parsed = parse_svg(text)
        expected = {component.id: dict(component.pins) for component in self.semantic.components if component.module_id == "AMP1"}
        self.assertEqual(set(expected), set(parsed["components"]))
        for component_id, pins in expected.items():
            self.assertEqual(pins, parsed["components"][component_id]["pins"])
        groups = {item.attrib["data-component-id"]: item for item in classes(root, "component")}
        self.assertEqual("translate(220.0 280.0) rotate(0)", groups["AMP1.Q1"].attrib["transform"])
        self.assertEqual("translate(1360.0 320.0) rotate(90)", groups["AMP1.R_OUT_P"].attrib["transform"])
        self.assertEqual(41, len(groups))
        self.assertGreater(len(classes(root, "port-wire")), 0)

    def test_layout_projection_is_deterministic(self):
        first = emit_svg_detail(self.semantic, "AMP1", layout=self.detail_layout)
        second = emit_svg_detail(self.semantic, "AMP1", layout=load_layout_overlay(DETAIL_LAYOUT_PATH))
        self.assertEqual(first, second)

    def test_strict_detail_layout_rejects_missing_component(self):
        broken = json.loads(json.dumps(self.detail_layout))
        del broken["components"]["AMP1.Q1"]
        with self.assertRaisesRegex(ValueError, "strict layout omits visible components"):
            emit_svg_detail(self.semantic, "AMP1", layout=broken)

    def test_resolved_inv20_and_int1_have_no_foreign_terminal_through_wires(self):
        cases = (("inv20", "W09.INVERTER_TEST"), ("int1", "W09.INT1_RESTORED"))
        for case_id, variant in cases:
            with self.subTest(case=case_id):
                resolved_path = ROOT / "generated" / "week09" / "proof" / "cases" / case_id / "graph.resolved.json"
                document = json.loads(resolved_path.read_text(encoding="utf-8"))
                semantic = build_semantic_graph(document, variant_id=variant, fidelity="ideal")
                text = emit_svg(semantic, layout=self.main_layout)
                root = ET.fromstring(text)
                assert_no_foreign_terminal_through_wires(self, root)
                assert_foreign_nets_avoid_collapsed_modules(self, root)
                receipt = build_connectivity_receipt(semantic, parse_svg(text), parse_spice(emit_spice(semantic)))
                self.assertTrue(receipt.passed, receipt.to_json())

    def test_cli_emits_main_and_detail_views(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            main_code = pipeline_main([
                str(GRAPH_PATH), "--variant", "W09.INVERTER_TEST", "--fidelity", "ideal",
                "--layout", str(MAIN_LAYOUT_PATH), "--view", "main", "--output-dir", str(output),
            ])
            detail_code = pipeline_main([
                str(GRAPH_PATH), "--variant", "W09.INVERTER_TEST", "--fidelity", "ideal",
                "--layout", str(DETAIL_LAYOUT_PATH), "--view", "detail", "--detail-module", "AMP1",
                "--output-dir", str(output),
            ])
            self.assertEqual(0, main_code)
            self.assertEqual(0, detail_code)
            self.assertTrue((output / "w09-inverter_test-ideal.svg").is_file())
            self.assertTrue((output / "w09-inverter_test-ideal-amp1-detail.svg").is_file())


if __name__ == "__main__":
    unittest.main()
