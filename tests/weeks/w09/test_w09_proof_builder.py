from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.build_week09_proof import (  # noqa: E402
    CASES,
    GRAPH_PATH,
    apply_case,
    validate_case_manifest,
)
from tools.circuit_pipeline import build_semantic_graph  # noqa: E402


class Week09ProofBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        cls.cases = {item.id: item for item in CASES}

    def test_executable_cases_match_reviewed_manifest(self):
        validate_case_manifest()

    def test_open_alpha_case_has_no_resistor_instance(self):
        document = apply_case(self.source, self.cases["A47"])
        graph = build_semantic_graph(
            document, variant_id="W09.CC_SWEEP", fidelity="ideal"
        )
        components = {item.id: item for item in graph.components}
        self.assertNotIn("W09.RALPHA", components)
        self.assertEqual("47p", components["AMP1.CC"].value)

    def test_quarter_alpha_case_has_exact_derived_shunt(self):
        document = apply_case(self.source, self.cases["B10"])
        graph = build_semantic_graph(
            document, variant_id="W09.CC_SWEEP", fidelity="ideal"
        )
        components = {item.id: item for item in graph.components}
        self.assertEqual("2.350k", components["W09.RALPHA"].value)
        self.assertEqual("10p", components["AMP1.CC"].value)

    def test_integrator_case_uses_inherited_values_and_fixture_port(self):
        document = apply_case(self.source, self.cases["INT1"])
        components = {item["id"]: item for item in document["components"]}
        modules = {item["id"]: item for item in document["modules"]}
        fixture_vin = next(
            port for port in modules["W09.FIXTURE"]["ports"] if port["id"] == "VIN"
        )
        self.assertEqual("MOD.INT1.INPUT", fixture_vin["net"])
        self.assertEqual("10k", components["MOD.INT1.RIN"]["value"])
        self.assertEqual("1u", components["MOD.INT1.CFB"]["value"])
        self.assertEqual("47p", components["AMP1.CC"]["value"])


if __name__ == "__main__":
    unittest.main()
