from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.validate_circuit_graph import canonical_json, validate_document  # noqa: E402


def minimal_graph() -> dict:
    """A synthetic topology fixture; it is not a project-week circuit."""
    evidence = {
        "source_id": "SRC.DECISION",
        "claim": "Synthetic test topology only.",
        "label": "verified",
    }
    return {
        "schema_version": "1.0.0",
        "project_id": "TEST.GRAPH",
        "title": "Synthetic validator fixture",
        "sources": [
            {
                "id": "SRC.DECISION",
                "kind": "project-decision",
                "title": "Synthetic test source",
                "locator": "tests/schema/test_validate_circuit_graph.py",
            }
        ],
        "nets": [
            {"id": "NET.IN", "class": "signal", "source_evidence": [evidence]},
            {"id": "NET.OUT", "class": "signal", "source_evidence": [evidence]},
            {"id": "SGND", "class": "ground", "spice_node": 0, "source_evidence": [evidence]},
        ],
        "modules": [
            {
                "id": "MOD.TEST",
                "parent_id": None,
                "ports": [
                    {"id": "PORT.IN", "direction": "input", "net": "NET.IN"},
                    {"id": "PORT.OUT", "direction": "output", "net": "NET.OUT"},
                ],
                "component_ids": ["DEV.R1"],
            }
        ],
        "models": [
            {
                "id": "MODEL.R.IDEAL",
                "fidelity": "ideal",
                "kind": "primitive",
                "reference": "R",
                "pin_names": ["P", "N"],
                "source_evidence": [evidence],
            },
            {
                "id": "MODEL.R.REALISTIC",
                "fidelity": "realistic",
                "kind": "primitive",
                "reference": "R_WITH_TOLERANCE",
                "pin_names": ["P", "N"],
                "source_evidence": [evidence],
            },
        ],
        "components": [
            {
                "id": "DEV.R1",
                "kind": "resistor",
                "module_id": "MOD.TEST",
                "state_class": "persistent-installed",
                "value": "1 kohm",
                "pins": [
                    {"id": "P", "net": "NET.IN"},
                    {"id": "N", "net": "NET.OUT"},
                ],
                "model_bindings": {
                    "ideal": "MODEL.R.IDEAL",
                    "realistic": "MODEL.R.REALISTIC",
                },
                "model_pin_map": {"P": "P", "N": "N"},
                "source_evidence": [evidence],
                "render": {"x": 1.0, "y": 2.0, "rotation": 0, "style": "active"},
            }
        ],
        "variants": [
            {
                "id": "CFG.TEST",
                "description": "Synthetic active configuration",
                "connection_overrides": [],
                "state_overrides": [],
                "model_overrides": [],
            }
        ],
        "weekly_states": [
            {
                "id": "W00",
                "title": "Synthetic initial state",
                "learning_objective": "Exercise schema cross-references.",
                "inherits": None,
                "configuration_ids": ["CFG.TEST"],
                "delta": {
                    "add": ["DEV.R1"],
                    "remove": [],
                    "replace": [],
                    "state_changes": [],
                    "connection_changes": [],
                },
                "source_evidence": [evidence],
            }
        ],
    }


class CircuitGraphValidatorTests(unittest.TestCase):
    def assert_valid(self, graph: dict) -> None:
        issues = validate_document(graph)
        self.assertEqual([], issues, "\n".join(map(str, issues)))

    def test_minimal_graph_is_valid(self):
        self.assert_valid(minimal_graph())

    def test_unknown_pin_net_is_rejected(self):
        graph = minimal_graph()
        graph["components"][0]["pins"][1]["net"] = "NET.MISSING"
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("unknown net 'NET.MISSING'" in message for message in messages), messages)

    def test_duplicate_component_identity_is_rejected(self):
        graph = minimal_graph()
        graph["components"].append(copy.deepcopy(graph["components"][0]))
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("duplicate ID 'DEV.R1'" in message for message in messages), messages)

    def test_id_cannot_be_shared_across_object_kinds(self):
        graph = minimal_graph()
        graph["nets"][0]["id"] = "DEV.R1"
        graph["components"][0]["pins"][0]["net"] = "DEV.R1"
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("shared by net and component" in message for message in messages), messages)

    def test_model_fidelity_and_pin_map_are_checked(self):
        graph = minimal_graph()
        graph["components"][0]["model_bindings"]["ideal"] = "MODEL.R.REALISTIC"
        graph["components"][0]["model_pin_map"]["N"] = "MISSING"
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("has fidelity 'realistic'" in message for message in messages), messages)
        self.assertTrue(any("model pin 'MISSING'" in message for message in messages), messages)

    def test_week_inheritance_must_be_strict_and_present(self):
        graph = minimal_graph()
        graph["weekly_states"].append(
            {
                "id": "W02",
                "title": "Skipped state",
                "learning_objective": "Exercise inheritance checks.",
                "inherits": "W00",
                "configuration_ids": [],
                "delta": {
                    "add": [],
                    "remove": [],
                    "replace": [],
                    "state_changes": [],
                    "connection_changes": [],
                },
                "source_evidence": graph["weekly_states"][0]["source_evidence"],
            }
        )
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("must be 'W01'" in message for message in messages), messages)

    def test_delta_replay_rejects_double_add_and_missing_remove(self):
        graph = minimal_graph()
        graph["weekly_states"].append(
            {
                "id": "W01",
                "title": "Invalid cumulative delta",
                "learning_objective": "Exercise inventory replay.",
                "inherits": "W00",
                "configuration_ids": [],
                "delta": {
                    "add": ["DEV.R1"],
                    "remove": [],
                    "replace": [],
                    "state_changes": [],
                    "connection_changes": [],
                },
                "source_evidence": graph["weekly_states"][0]["source_evidence"],
            }
        )
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("already in the cumulative inventory" in message for message in messages), messages)

        graph["weekly_states"][1]["delta"]["add"] = []
        graph["weekly_states"][1]["delta"]["remove"] = ["DEV.R1"]
        graph["weekly_states"].append(
            {
                "id": "W02",
                "title": "Second invalid removal",
                "learning_objective": "Exercise inventory replay.",
                "inherits": "W01",
                "configuration_ids": [],
                "delta": {
                    "add": [],
                    "remove": ["DEV.R1"],
                    "replace": [],
                    "state_changes": [],
                    "connection_changes": [],
                },
                "source_evidence": graph["weekly_states"][0]["source_evidence"],
            }
        )
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("is not in the cumulative inventory" in message for message in messages), messages)

    def test_derived_evidence_requires_derivation(self):
        graph = minimal_graph()
        graph["components"][0]["source_evidence"][0]["label"] = "derived"
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("requires a derivation object" in message for message in messages), messages)

    def test_variant_references_component_pin_and_net(self):
        graph = minimal_graph()
        graph["variants"][0]["connection_overrides"].append(
            {"component_id": "DEV.R1", "pin_id": "MISSING", "net": "NET.MISSING"}
        )
        messages = [str(issue) for issue in validate_document(graph)]
        self.assertTrue(any("unknown pin" in message for message in messages), messages)
        self.assertTrue(any("unknown net" in message for message in messages), messages)

    def test_render_hints_do_not_affect_canonical_connectivity(self):
        first = minimal_graph()
        second = copy.deepcopy(first)
        second["components"][0]["render"] = {"x": 99, "y": -4, "rotation": 180, "style": "inactive"}
        self.assert_valid(first)
        self.assert_valid(second)
        self.assertNotEqual(canonical_json(first), canonical_json(second))
        self.assertEqual(
            first["components"][0]["pins"],
            second["components"][0]["pins"],
        )

    def test_canonical_json_is_stable(self):
        graph = minimal_graph()
        encoded = canonical_json(graph)
        self.assertTrue(encoded.endswith("\n"))
        self.assertEqual(encoded, canonical_json(json.loads(encoded)))


if __name__ == "__main__":
    unittest.main()
