from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.build_week09_proof import CASES, GRAPH_PATH, apply_case  # noqa: E402
from tools.circuit_pipeline import Probe, build_semantic_graph  # noqa: E402


class Week09HierarchicalProbeTests(unittest.TestCase):
    def test_internal_chassis_net_uses_hierarchical_ngspice_path(self):
        source = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
        document = apply_case(source, CASES[0])
        graph = build_semantic_graph(
            document, variant_id="W09.INVERTER_TEST", fidelity="ideal"
        )
        expression = Probe("vout", "voltage", "AMP1.OUT").expression(graph)
        self.assertTrue(expression.startswith("v(xiz43484153534953."), expression)
        self.assertIn("NZ414D50312E4F5554", expression)


if __name__ == "__main__":
    unittest.main()
