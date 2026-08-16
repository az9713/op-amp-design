from __future__ import annotations

import copy
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import (  # noqa: E402
    build_connectivity_receipt,
    build_semantic_graph,
    emit_spice,
    emit_svg,
    parse_spice,
    parse_svg,
)


def evidence() -> dict:
    return {
        "source_id": "SRC.TEST",
        "claim": "Synthetic topology used only to exercise the projector.",
        "label": "verified",
    }


def model(model_id: str, fidelity: str, kind: str, reference: str, pins: list[str]) -> dict:
    return {
        "id": model_id,
        "fidelity": fidelity,
        "kind": kind,
        "reference": reference,
        "pin_names": pins,
        "source_evidence": [evidence()],
    }


def component(
    component_id: str,
    kind: str,
    module_id: str,
    pins: list[tuple[str, str | None]],
    ideal_model: str,
    realistic_model: str,
    *,
    value: str | None = None,
    state_class: str = "persistent-installed",
) -> dict:
    result = {
        "id": component_id,
        "kind": kind,
        "module_id": module_id,
        "state_class": state_class,
        "pins": [{"id": pin, "net": net} for pin, net in pins],
        "model_bindings": {"ideal": ideal_model, "realistic": realistic_model},
        "model_pin_map": {pin: pin for pin, _ in pins},
        "source_evidence": [evidence()],
        "render": {"x": 100, "y": 100, "rotation": 0, "style": "active"},
    }
    if value is not None:
        result["value"] = value
    return result


def synthetic_graph() -> dict:
    nets = [
        ("P15", "power"),
        ("N15", "power"),
        ("SGND", "ground"),
        ("NET.VIN", "signal"),
        ("NET.SUM", "signal"),
        ("NET.VOUT", "signal"),
        ("NET.CTRL", "control"),
        ("NET.TAIL", "signal"),
        ("NET.C1", "signal"),
        ("NET.C2", "signal"),
    ]
    models = [
        model("MODEL.R.I", "ideal", "primitive", "R", ["P", "N"]),
        model("MODEL.R.R", "realistic", "primitive", "R_REAL", ["P", "N"]),
        model("MODEL.V.I", "ideal", "primitive", "V", ["P", "N"]),
        model("MODEL.V.R", "realistic", "primitive", "V_REAL", ["P", "N"]),
        model("MODEL.OP.I", "ideal", "subcircuit", "OPAMP_IDEAL", ["INP", "INM", "OUT", "VP", "VN"]),
        model("MODEL.OP.R", "realistic", "subcircuit", "OPAMP_REAL", ["INP", "INM", "OUT", "VP", "VN"]),
        model("MODEL.Q.I", "ideal", "primitive", "NPN_IDEAL", ["C", "B", "E"]),
        model("MODEL.Q.R", "realistic", "primitive", "NPN_REAL", ["C", "B", "E"]),
        model("MODEL.S.I", "ideal", "primitive", "SW_IDEAL", ["P", "N", "CTRL_P", "CTRL_N"]),
        model("MODEL.S.R", "realistic", "primitive", "SW_REAL", ["P", "N", "CTRL_P", "CTRL_N"]),
    ]
    components = [
        component("DEV.VIN", "voltage_source", "MOD.ROOT", [("P", "NET.VIN"), ("N", "SGND")], "MODEL.V.I", "MODEL.V.R", value="1"),
        component("DEV.RIN", "resistor", "MOD.ROOT.LOOP", [("P", "NET.VIN"), ("N", "NET.SUM")], "MODEL.R.I", "MODEL.R.R", value="10k"),
        component("DEV.RFB", "resistor", "MOD.ROOT.LOOP", [("P", "NET.VOUT"), ("N", "NET.SUM")], "MODEL.R.I", "MODEL.R.R", value="10k"),
        component(
            "DEV.OP1",
            "opamp",
            "MOD.ROOT.LOOP",
            [("INP", "SGND"), ("INM", "NET.SUM"), ("OUT", "NET.VOUT"), ("VP", "P15"), ("VN", "N15")],
            "MODEL.OP.I",
            "MODEL.OP.R",
        ),
        component("DEV.Q1", "bjt", "MOD.ROOT.DIFF", [("C", "NET.C1"), ("B", "NET.VIN"), ("E", "NET.TAIL")], "MODEL.Q.I", "MODEL.Q.R"),
        component("DEV.Q2", "bjt", "MOD.ROOT.DIFF", [("C", "NET.C2"), ("B", "SGND"), ("E", "NET.TAIL")], "MODEL.Q.I", "MODEL.Q.R"),
        component(
            "DEV.S1",
            "switch",
            "MOD.ROOT.LOOP",
            [("P", "NET.VOUT"), ("N", None), ("CTRL_P", "NET.CTRL"), ("CTRL_N", "SGND")],
            "MODEL.S.I",
            "MODEL.S.R",
            state_class="removed-off-circuit",
        ),
    ]
    modules = [
        {
            "id": "MOD.ROOT",
            "parent_id": None,
            "ports": [
                {"id": "PORT.P15", "direction": "power", "net": "P15"},
                {"id": "PORT.N15", "direction": "power", "net": "N15"},
                {"id": "PORT.GND", "direction": "power", "net": "SGND"},
                {"id": "PORT.VIN", "direction": "input", "net": "NET.VIN"},
                {"id": "PORT.VOUT", "direction": "output", "net": "NET.VOUT"},
                {"id": "PORT.CTRL", "direction": "input", "net": "NET.CTRL"},
            ],
            "component_ids": ["DEV.VIN"],
        },
        {
            "id": "MOD.ROOT.LOOP",
            "parent_id": "MOD.ROOT",
            "ports": [
                {"id": "PORT.P15", "direction": "power", "net": "P15"},
                {"id": "PORT.N15", "direction": "power", "net": "N15"},
                {"id": "PORT.GND", "direction": "power", "net": "SGND"},
                {"id": "PORT.VIN", "direction": "input", "net": "NET.VIN"},
                {"id": "PORT.VOUT", "direction": "output", "net": "NET.VOUT"},
                {"id": "PORT.CTRL", "direction": "input", "net": "NET.CTRL"},
            ],
            "component_ids": ["DEV.RIN", "DEV.RFB", "DEV.OP1", "DEV.S1"],
        },
        {
            "id": "MOD.ROOT.DIFF",
            "parent_id": "MOD.ROOT",
            "ports": [
                {"id": "PORT.GND", "direction": "power", "net": "SGND"},
                {"id": "PORT.VIN", "direction": "input", "net": "NET.VIN"},
            ],
            "component_ids": ["DEV.Q1", "DEV.Q2"],
        },
    ]
    return {
        "schema_version": "1.0.0",
        "project_id": "TEST.PIPELINE",
        "title": "Synthetic projection topology",
        "sources": [{"id": "SRC.TEST", "kind": "analysis", "title": "Synthetic fixture", "locator": "tests/connectivity"}],
        "nets": [
            {"id": net_id, "class": net_class, **({"spice_node": 0} if net_id == "SGND" else {}), "source_evidence": [evidence()]}
            for net_id, net_class in nets
        ],
        "modules": modules,
        "models": models,
        "components": components,
        "variants": [
            {
                "id": "CFG.BASE",
                "description": "Op-amp loop and differential pair",
                "connection_overrides": [],
                "state_overrides": [],
                "model_overrides": [],
            },
            {
                "id": "CFG.SWITCHED",
                "description": "Close the synthetic switch path",
                "connection_overrides": [{"component_id": "DEV.S1", "pin_id": "N", "net": "NET.VIN"}],
                "state_overrides": [{"component_id": "DEV.S1", "state_class": "configuration-only-fixture"}],
                "model_overrides": [],
            },
        ],
        "weekly_states": [
            {
                "id": "W00",
                "title": "Synthetic projection fixture",
                "learning_objective": "Test projection without encoding a project circuit.",
                "inherits": None,
                "configuration_ids": ["CFG.BASE", "CFG.SWITCHED"],
                "delta": {
                    "add": [component["id"] for component in components],
                    "remove": [],
                    "replace": [],
                    "state_changes": [],
                    "connection_changes": [],
                },
                "source_evidence": [evidence()],
            }
        ],
    }


def project(graph: dict, variant: str = "CFG.BASE", fidelity: str = "ideal"):
    semantic = build_semantic_graph(graph, variant_id=variant, fidelity=fidelity)
    svg_text = emit_svg(semantic)
    spice_text = emit_spice(semantic)
    svg_graph = parse_svg(svg_text)
    spice_graph = parse_spice(spice_text)
    receipt = build_connectivity_receipt(semantic, svg_graph, spice_graph)
    return semantic, svg_text, spice_text, svg_graph, spice_graph, receipt


class CircuitPipelineTests(unittest.TestCase):
    def test_op_amp_feedback_loop_round_trips(self):
        _, _, _, svg_graph, spice_graph, receipt = project(synthetic_graph())
        self.assertTrue(receipt.passed, receipt.to_json())
        expected = {"INP": "SGND", "INM": "NET.SUM", "OUT": "NET.VOUT", "VP": "P15", "VN": "N15"}
        self.assertEqual(expected, svg_graph["components"]["DEV.OP1"]["pins"])
        self.assertEqual(expected, spice_graph["components"]["DEV.OP1"]["pins"])
        self.assertEqual("NET.SUM", spice_graph["components"]["DEV.RFB"]["pins"]["N"])

    def test_transistor_differential_pair_uses_actual_q_terminals(self):
        _, _, spice_text, _, spice_graph, receipt = project(synthetic_graph(), fidelity="realistic")
        self.assertTrue(receipt.passed, receipt.to_json())
        q_lines = [line for line in spice_text.splitlines() if line.startswith("QI")]
        self.assertEqual(2, len(q_lines))
        self.assertEqual({"C": "NET.C1", "B": "NET.VIN", "E": "NET.TAIL"}, spice_graph["components"]["DEV.Q1"]["pins"])
        self.assertEqual("NET.TAIL", spice_graph["components"]["DEV.Q2"]["pins"]["E"])

    def test_switch_variant_applies_state_and_connection(self):
        semantic, _, spice_text, svg_graph, spice_graph, receipt = project(synthetic_graph(), "CFG.SWITCHED")
        self.assertTrue(receipt.passed, receipt.to_json())
        switch = next(component for component in semantic.components if component.id == "DEV.S1")
        self.assertEqual("configuration-only-fixture", switch.state_class)
        self.assertEqual("NET.VIN", dict(switch.pins)["N"])
        self.assertIn("DEV.S1", svg_graph["components"])
        self.assertIn("DEV.S1", spice_graph["components"])
        self.assertTrue(any(line.startswith("SI") for line in spice_text.splitlines()))

    def test_hierarchy_boundaries_round_trip_pin_for_pin(self):
        semantic, _, spice_text, svg_graph, spice_graph, receipt = project(synthetic_graph())
        self.assertTrue(receipt.passed, receipt.to_json())
        expected_modules = {module.id: module.as_dict() for module in semantic.modules}
        self.assertEqual(expected_modules, svg_graph["modules"])
        self.assertEqual(expected_modules, spice_graph["modules"])
        self.assertRegex(spice_text, r"(?m)^\.subckt MZ[0-9A-F]+ PZ[0-9A-F]+")
        self.assertRegex(spice_text, r"(?m)^XIZ[0-9A-F]+ .* MZ[0-9A-F]+$")

    def test_emitters_and_receipt_are_deterministic(self):
        first = project(synthetic_graph())
        second = project(copy.deepcopy(synthetic_graph()))
        self.assertEqual(first[1], second[1])
        self.assertEqual(first[2], second[2])
        self.assertEqual(first[5].to_json(), second[5].to_json())

    def test_deliberate_svg_terminal_mismatch_fails(self):
        semantic, svg_text, spice_text, _, _, _ = project(synthetic_graph())
        bad_svg = svg_text.replace('data-pin-id="INM" data-net-id="NET.SUM"', 'data-pin-id="INM" data-net-id="NET.BAD"', 1)
        bad_svg = bad_svg.replace('data-terminal-ref="DEV.OP1::INM" data-net-id="NET.SUM"', 'data-terminal-ref="DEV.OP1::INM" data-net-id="NET.BAD"', 1)
        receipt = build_connectivity_receipt(semantic, parse_svg(bad_svg), parse_spice(spice_text))
        self.assertFalse(receipt.passed)
        self.assertTrue(any("DEV.OP1" in item and "INM" in item for item in receipt.svg_differences), receipt.svg_differences)

    def test_svg_parser_rejects_terminal_wire_disagreement(self):
        _, svg_text, _, _, _, _ = project(synthetic_graph())
        bad_svg = svg_text.replace('data-pin-id="INM" data-net-id="NET.SUM"', 'data-pin-id="INM" data-net-id="NET.VOUT"', 1)
        with self.assertRaisesRegex(ValueError, "wire membership"):
            parse_svg(bad_svg)

    def test_deliberate_spice_terminal_mismatch_fails_without_comments(self):
        semantic, svg_text, spice_text, _, _, _ = project(synthetic_graph())
        lines = spice_text.splitlines()
        rin_index = next(index for index, line in enumerate(lines) if line.startswith("RI") and "10k" in line)
        tokens = lines[rin_index].split()
        tokens[2] = "0"
        lines[rin_index] = " ".join(tokens)
        bad_spice = "\n".join(lines) + "\n"
        receipt = build_connectivity_receipt(semantic, parse_svg(svg_text), parse_spice(bad_spice))
        self.assertFalse(receipt.passed)
        self.assertTrue(receipt.spice_differences)

    def test_spice_parser_rejects_wrong_subcircuit_terminal_count(self):
        _, _, spice_text, _, _, _ = project(synthetic_graph())
        lines = spice_text.splitlines()
        op_index = next(index for index, line in enumerate(lines) if line.startswith("XI") and line.endswith("OPAMP_IDEAL"))
        tokens = lines[op_index].split()
        del tokens[2]
        lines[op_index] = " ".join(tokens)
        with self.assertRaisesRegex(ValueError, "expects 5 pins, got 4"):
            parse_spice("\n".join(lines) + "\n")


if __name__ == "__main__":
    unittest.main()
