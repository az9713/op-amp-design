from __future__ import annotations

import tempfile
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import (  # noqa: E402
    ACAnalysis,
    NgspiceError,
    NgspiceRunner,
    OperatingPointAnalysis,
    Probe,
    SimulationCase,
    SimulationPlan,
    TransientAnalysis,
    build_semantic_graph,
    emit_ngspice_deck,
    parse_wrdata,
)


def evidence() -> dict:
    return {"source_id": "SRC.TEST", "claim": "Synthetic RC simulation fixture.", "label": "verified"}


def rc_document() -> dict:
    models = []
    for fidelity, suffix in (("ideal", "I"), ("realistic", "R")):
        models.extend(
            [
                {
                    "id": f"MODEL.V.{suffix}",
                    "fidelity": fidelity,
                    "kind": "primitive",
                    "reference": "V",
                    "pin_names": ["P", "N"],
                    "source_evidence": [evidence()],
                },
                {
                    "id": f"MODEL.R.{suffix}",
                    "fidelity": fidelity,
                    "kind": "primitive",
                    "reference": "R",
                    "pin_names": ["P", "N"],
                    "source_evidence": [evidence()],
                },
                {
                    "id": f"MODEL.C.{suffix}",
                    "fidelity": fidelity,
                    "kind": "primitive",
                    "reference": "C",
                    "pin_names": ["P", "N"],
                    "source_evidence": [evidence()],
                },
            ]
        )

    def component(component_id: str, kind: str, pins: list[tuple[str, str]], value: str, prefix: str) -> dict:
        return {
            "id": component_id,
            "kind": kind,
            "module_id": "MOD.RC",
            "state_class": "persistent-installed",
            "value": value,
            "pins": [{"id": pin, "net": net} for pin, net in pins],
            "model_bindings": {"ideal": f"MODEL.{prefix}.I", "realistic": f"MODEL.{prefix}.R"},
            "model_pin_map": {pin: pin for pin, _ in pins},
            "source_evidence": [evidence()],
        }

    components = [
        component("DEV.V1", "voltage_source", [("P", "NET.VIN"), ("N", "SGND")], "DC 1 AC 1", "V"),
        component("DEV.R1", "resistor", [("P", "NET.VIN"), ("N", "NET.VOUT")], "{RVAL}", "R"),
        component("DEV.C1", "capacitor", [("P", "NET.VOUT"), ("N", "SGND")], "1u", "C"),
    ]
    return {
        "schema_version": "1.0.0",
        "project_id": "TEST.SIMULATION",
        "title": "Synthetic RC simulation",
        "sources": [{"id": "SRC.TEST", "kind": "analysis", "title": "Synthetic fixture", "locator": "tests/simulation"}],
        "nets": [
            {"id": "NET.VIN", "class": "signal", "source_evidence": [evidence()]},
            {"id": "NET.VOUT", "class": "signal", "source_evidence": [evidence()]},
            {"id": "SGND", "class": "ground", "spice_node": 0, "source_evidence": [evidence()]},
        ],
        "modules": [
            {
                "id": "MOD.RC",
                "parent_id": None,
                "ports": [
                    {"id": "PORT.VIN", "direction": "input", "net": "NET.VIN"},
                    {"id": "PORT.VOUT", "direction": "output", "net": "NET.VOUT"},
                    {"id": "PORT.GND", "direction": "power", "net": "SGND"},
                ],
                "component_ids": [item["id"] for item in components],
            }
        ],
        "models": models,
        "components": components,
        "variants": [
            {
                "id": "CFG.RC",
                "description": "Synthetic RC low-pass",
                "connection_overrides": [],
                "state_overrides": [],
                "model_overrides": [],
            }
        ],
        "weekly_states": [
            {
                "id": "W00",
                "title": "Synthetic RC state",
                "learning_objective": "Exercise runnable simulation infrastructure.",
                "inherits": None,
                "configuration_ids": ["CFG.RC"],
                "delta": {
                    "add": [item["id"] for item in components],
                    "remove": [],
                    "replace": [],
                    "state_changes": [],
                    "connection_changes": [],
                },
                "source_evidence": [evidence()],
            }
        ],
    }


def simulation_plan(*, includes: tuple[Path, ...] = (), model_cards: tuple[str, ...] = ()) -> SimulationPlan:
    vout = Probe("vout", "voltage", "NET.VOUT")
    source_current = Probe("isource", "current", "DEV.V1")
    return SimulationPlan(
        name="rc_suite",
        analyses=(
            OperatingPointAnalysis("op", (vout, source_current)),
            ACAnalysis("ac", "dec", 5, "10", "10k", (vout,)),
            TransientAnalysis("tran", "1m", "5m", (vout,)),
        ),
        cases=(
            SimulationCase("r1k", {"RVAL": "1k"}),
            SimulationCase("r2k", {"RVAL": "2k"}),
        ),
        parameters={"UNUSED": 1},
        includes=includes,
        model_cards=model_cards,
    )


def diode_document() -> dict:
    document = rc_document()
    document["components"] = [item for item in document["components"] if item["id"] != "DEV.C1"]
    document["models"] = [item for item in document["models"] if not item["id"].startswith("MODEL.C.")]
    for fidelity, suffix in (("ideal", "I"), ("realistic", "R")):
        document["models"].append(
            {
                "id": f"MODEL.D.{suffix}",
                "fidelity": fidelity,
                "kind": "primitive",
                "reference": "DTEST",
                "pin_names": ["A", "K"],
                "source_evidence": [evidence()],
            }
        )
    diode = {
        "id": "DEV.D1",
        "kind": "diode",
        "module_id": "MOD.RC",
        "state_class": "persistent-installed",
        "pins": [{"id": "A", "net": "NET.VOUT"}, {"id": "K", "net": "SGND"}],
        "model_bindings": {"ideal": "MODEL.D.I", "realistic": "MODEL.D.R"},
        "model_pin_map": {"A": "A", "K": "K"},
        "source_evidence": [evidence()],
    }
    document["components"].append(diode)
    document["modules"][0]["component_ids"] = ["DEV.V1", "DEV.R1", "DEV.D1"]
    document["weekly_states"][0]["delta"]["add"] = ["DEV.V1", "DEV.R1", "DEV.D1"]
    return document


class NgspicePipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runner = NgspiceRunner()

    def test_deck_contains_parameters_and_all_analysis_commands(self):
        semantic = build_semantic_graph(rc_document(), variant_id="CFG.RC", fidelity="ideal")
        plan = simulation_plan(model_cards=(".model UNUSED_D D(Is=1e-12)",))
        deck = emit_ngspice_deck(semantic, plan, case=plan.cases[0])
        self.assertIn(".param RVAL=1k", deck)
        self.assertIn(".model UNUSED_D D(Is=1e-12)", deck)
        self.assertIn("\nop\n", deck)
        self.assertIn("\nac dec 5 10 10k\n", deck)
        self.assertIn("\ntran 1m 5m 0\n", deck)
        self.assertNotIn("interface stub", deck.lower())

    def test_transient_uic_is_explicit_and_opt_in(self):
        semantic = build_semantic_graph(rc_document(), variant_id="CFG.RC", fidelity="ideal")
        vout = Probe("vout", "voltage", "NET.VOUT")
        plan = SimulationPlan(
            name="uic_startup",
            analyses=(TransientAnalysis("tran", "1m", "5m", (vout,), uic=True),),
        )
        deck = emit_ngspice_deck(semantic, plan, case=plan.cases[0])
        self.assertIn("\ntran 1m 5m 0 uic\n", deck)

    def test_runner_executes_op_ac_tran_and_parameterized_cases(self):
        semantic = build_semantic_graph(rc_document(), variant_id="CFG.RC", fidelity="ideal")
        receipt = self.runner.run(semantic, simulation_plan())
        self.assertTrue(receipt.passed)
        self.assertIn("ngspice-47", receipt.version)
        self.assertEqual(64, len(receipt.executable_sha256))
        self.assertEqual(2, len(receipt.cases))
        self.assertNotEqual(receipt.cases[0].deck_sha256, receipt.cases[1].deck_sha256)
        self.assertEqual(receipt.cases[0].command_sha256, receipt.cases[1].command_sha256)
        for case in receipt.cases:
            self.assertEqual({"op", "ac", "tran"}, set(case.tables))
            self.assertGreaterEqual(len(case.tables["op"].rows), 1)
            self.assertGreater(len(case.tables["ac"].rows), 1)
            self.assertGreater(len(case.tables["tran"].rows), 1)
        self.assertEqual(receipt.to_json(), receipt.to_json())
        op_table = receipt.cases[0].tables["op"]
        if len(op_table.rows) == 1:
            self.assertIsInstance(op_table.scalar(op_table.columns[-1]), float)

    def test_include_is_emitted_hashed_and_accepted(self):
        semantic = build_semantic_graph(diode_document(), variant_id="CFG.RC", fidelity="ideal")
        with tempfile.TemporaryDirectory() as temporary:
            include = Path(temporary) / "models.lib"
            include.write_text("* deterministic include\n.model DTEST D(Is=1e-12)\n", encoding="utf-8")
            plan = simulation_plan(includes=(include,))
            deck = emit_ngspice_deck(semantic, plan, case=plan.cases[0])
            self.assertIn(f'.include "{include.resolve()}"', deck)
            receipt = self.runner.run(semantic, plan)
            self.assertEqual(64, len(receipt.include_sha256[str(include.resolve())]))

    def test_required_model_card_cannot_be_omitted(self):
        semantic = build_semantic_graph(diode_document(), variant_id="CFG.RC", fidelity="ideal")
        plan = simulation_plan()
        with self.assertRaisesRegex(NgspiceError, "no .model card supplied"):
            emit_ngspice_deck(semantic, plan, case=plan.cases[0])

    def test_ngspice_errors_fail_the_run(self):
        semantic = build_semantic_graph(rc_document(), variant_id="CFG.RC", fidelity="ideal")
        broken = simulation_plan(model_cards=("THIS_IS_NOT_A_SPICE_DIRECTIVE",))
        with self.assertRaises(NgspiceError):
            self.runner.run(semantic, broken)

    def test_wrdata_parser_reads_header_and_numeric_table(self):
        with tempfile.TemporaryDirectory() as temporary:
            table = Path(temporary) / "result.dat"
            table.write_text("time v(out)\n0.0 1.0\n1e-3 0.5\n", encoding="utf-8")
            parsed = parse_wrdata(table)
            self.assertEqual(("time", "v(out)"), parsed.columns)
            self.assertEqual(((0.0, 1.0), (0.001, 0.5)), parsed.rows)


if __name__ == "__main__":
    unittest.main()
