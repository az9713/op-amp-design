from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import (  # noqa: E402
    build_connectivity_receipt,
    build_semantic_graph,
    emit_spice,
    emit_svg,
    parse_spice,
    parse_svg,
)
from tools.validate_circuit_graph import validate_document  # noqa: E402


GRAPH_PATH = ROOT / "circuits" / "weeks" / "w09" / "graph.json"
CASE_MANIFEST_PATH = ROOT / "circuits" / "weeks" / "w09" / "case-manifest.json"


def load_graph() -> dict:
    return json.loads(GRAPH_PATH.read_text(encoding="utf-8"))


def load_case_manifest() -> dict:
    return json.loads(CASE_MANIFEST_PATH.read_text(encoding="utf-8"))


def components(graph: dict) -> dict[str, dict]:
    return {component["id"]: component for component in graph["components"]}


def pin_map(component: dict) -> dict[str, str | None]:
    return {pin["id"]: pin["net"] for pin in component["pins"]}


class Week09GraphTests(unittest.TestCase):
    def test_graph_validates_and_uses_no_retired_aliases(self):
        graph = load_graph()
        self.assertEqual([], validate_document(graph))
        serialized = json.dumps(graph, sort_keys=True)
        self.assertNotIn("CORE.", serialized)
        self.assertNotIn("INFRA.", serialized)

    def test_full_active_device_terminal_ledger(self):
        graph_components = components(load_graph())
        expected = {
            "AMP1.Q1": {"C":"AMP1.N.Q1C_Q4B","B":"AMP1.INV_IN","E":"AMP1.N.TAIL"},
            "AMP1.Q2": {"C":"AMP1.COMP_A","B":"AMP1.NONINV_IN","E":"AMP1.N.TAIL"},
            "AMP1.Q3": {"C":"AMP1.N.TAIL","B":"AMP1.N.BIAS_NEG","E":"AMP1.N.Q3E_SERIES"},
            "AMP1.Q4": {"C":"SGND","B":"AMP1.N.Q1C_Q4B","E":"AMP1.N.Q45E"},
            "AMP1.Q5": {"C":"AMP1.N.Q5C_Q6E","B":"AMP1.COMP_A","E":"AMP1.N.Q45E"},
            "AMP1.Q6": {"C":"AMP1.N.HIGH_Z","B":"AMP1.N.Q6B","E":"AMP1.N.Q5C_Q6E"},
            "AMP1.Q7": {"C":"AMP1.N.HIGH_Z","B":"AMP1.N.BIAS_NEG","E":"AMP1.N.Q7E"},
            "AMP1.Q8": {"D":"P15","G":"AMP1.N.HIGH_Z","S":"AMP1.COMP_B"},
            "AMP1.Q9": {"C":"AMP1.N.DRV_N_Q9C","B":"AMP1.N.BIAS_NEG","E":"AMP1.N.Q9E"},
            "AMP1.Q10":{"C":"P15","B":"AMP1.COMP_B","E":"AMP1.N.OUT_P_SENSE"},
            "AMP1.Q11":{"C":"N15","B":"AMP1.N.DRV_N_Q9C","E":"AMP1.N.OUT_N_SENSE"},
            "AMP1.Q12":{"C":"AMP1.COMP_B","B":"AMP1.N.OUT_P_SENSE","E":"AMP1.OUT"},
            "AMP1.Q13":{"C":"AMP1.N.DRV_N_Q9C","B":"AMP1.N.OUT_N_SENSE","E":"AMP1.OUT"},
        }
        self.assertEqual(set(expected), {item for item in graph_components if item.startswith("AMP1.Q")})
        for component_id, pins in expected.items():
            self.assertEqual(pins, pin_map(graph_components[component_id]), component_id)

    def test_adjudicated_diode_orientation_and_unresolved_types(self):
        graph_components = components(load_graph())
        expected = {
            "AMP1.D_BAL":{"A":"P15","K":"AMP1.N.BAL_W"},
            "AMP1.D_BIAS":{"A":"AMP1.N.BIAS_DIODE_A","K":"N15"},
            "AMP1.D_DRV_1":{"A":"AMP1.COMP_B","K":"AMP1.N.DRV_DIODE_MID"},
            "AMP1.D_DRV_2":{"A":"AMP1.N.DRV_DIODE_MID","K":"AMP1.N.DRV_N_Q9C"},
        }
        for component_id, pins in expected.items():
            component = graph_components[component_id]
            self.assertEqual(pins, pin_map(component))
            self.assertEqual("TBD", component["parameters"]["historical_type"])

    def test_source_tbd_fields_remain_explicit(self):
        graph_components = components(load_graph())
        self.assertEqual("TBD", graph_components["AMP1.R_Q3_5K6"]["parameters"]["tolerance"])
        self.assertEqual("TBD", graph_components["AMP1.C_Q6_BYP"]["parameters"]["technology"])
        self.assertEqual("TBD", graph_components["AMP1.C_Q6_BYP"]["parameters"]["polarity"])
        self.assertEqual("R1_TBD", graph_components["W09.RIN"]["value"])
        self.assertEqual("TBD_FROM_W09_EXPERIMENT", graph_components["AMP1.CC"]["parameters"]["end_state_value"])
        for component_id in ("W09.LOAD", "W09.CPROBE_OUT", "W09.CPAR_HIGHZ", "W09.CPAR_COMPA", "W09.CPAR_COMPB"):
            self.assertEqual("deferred", graph_components[component_id]["state_class"])
        for component_id in ("W09.LOAD", "W09.CPAR_HIGHZ", "W09.CPAR_COMPA", "W09.CPAR_COMPB"):
            self.assertEqual("TBD", graph_components[component_id]["parameters"]["numeric_value"])
        for index in range(1, 14):
            self.assertEqual("TBD", graph_components[f"AMP1.Q{index}"]["parameters"]["package_pin_map"])

    def test_sweep_cases_are_parameters_not_extra_configurations(self):
        graph = load_graph()
        case_ids = [case["id"] for case in components(graph)["AMP1.CC"]["parameters"]["cases"]]
        self.assertEqual(
            ["CASE.W09.A47","CASE.W09.A33","CASE.W09.A10","CASE.W09.A05","CASE.W09.B20","CASE.W09.B10"],
            case_ids,
        )
        self.assertEqual(
            {"W09.CC_SWEEP", "W09.INVERTER_TEST", "W09.INT1_RESTORED"},
            {variant["id"] for variant in graph["variants"]},
        )

    def test_case_manifest_has_exact_source_cases_and_no_hidden_bleed(self):
        manifest = load_case_manifest()
        self.assertFalse(manifest["claim_boundary"]["hidden_bleed_allowed"])
        self.assertEqual("unsupported_missing_realistic_models", manifest["assumption_profiles"]["REALISTIC_FIRST_PASS"]["projection_status"])
        cases = {case["id"]: case for case in manifest["cases"]}
        self.assertEqual(
            {"CASE.W09.A47","CASE.W09.A33","CASE.W09.A10","CASE.W09.A05","CASE.W09.B20","CASE.W09.B10"},
            set(cases),
        )
        self.assertEqual({"A47":"47p","A33":"33p","A10":"10p","A05":"5p"}, {
            suffix: cases[f"CASE.W09.{suffix}"]["cc"] for suffix in ("A47","A33","A10","A05")
        })
        self.assertEqual("20p", cases["CASE.W09.B20"]["cc"])
        self.assertEqual("10p", cases["CASE.W09.B10"]["cc"])
        self.assertEqual("2.350k", cases["CASE.W09.B10"]["ralpha"]["value"])
        for case_id in ("CASE.W09.A47","CASE.W09.A33","CASE.W09.A10","CASE.W09.A05","CASE.W09.B20"):
            self.assertEqual({"value":"OPEN","state":"removed-off-circuit"}, cases[case_id]["ralpha"])
        self.assertNotIn("bleed", json.dumps(manifest["component_bindings"]).lower())
        embedded = {case["id"]: case for case in components(load_graph())["AMP1.CC"]["parameters"]["cases"]}
        for case_id, case in cases.items():
            self.assertEqual(case["cc"], embedded[case_id]["cc"])
            self.assertEqual(case["alpha"], embedded[case_id]["alpha"])

    def test_case_manifest_targets_exist_and_profiles_declare_loading(self):
        graph_components = components(load_graph())
        manifest = load_case_manifest()
        for binding in manifest["component_bindings"].values():
            self.assertIn(binding["component_id"], graph_components)
        topology = manifest["assumption_profiles"]["TOPOLOGY"]
        realistic = manifest["assumption_profiles"]["REALISTIC_FIRST_PASS"]
        self.assertEqual("10Meg", topology["W09.LOAD"]["value"])
        self.assertEqual("OPEN", topology["W09.CPROBE_OUT"]["value"])
        self.assertEqual("12p", realistic["W09.CPROBE_OUT"]["value"])
        for component_id in ("W09.CPAR_HIGHZ","W09.CPAR_COMPA","W09.CPAR_COMPB"):
            self.assertEqual("OPEN", topology[component_id]["value"])
            self.assertEqual(["0.5p","1p","2p"], realistic[component_id]["required_sweep"])

    def test_source_resistance_is_an_explicit_series_component(self):
        graph_components = components(load_graph())
        self.assertEqual({"P":"W09.GEN","N":"W09.VIN"}, pin_map(graph_components["W09.RSOURCE"]))
        self.assertEqual({"P":"W09.GEN","N":"SGND"}, pin_map(graph_components["W09.VSRC"]))

    def test_variants_round_trip_through_both_projections(self):
        graph = load_graph()
        for variant_id in ("W09.CC_SWEEP", "W09.INVERTER_TEST", "W09.INT1_RESTORED"):
            with self.subTest(variant_id=variant_id):
                semantic = build_semantic_graph(graph, variant_id=variant_id, fidelity="ideal")
                svg = emit_svg(semantic)
                spice = emit_spice(semantic)
                receipt = build_connectivity_receipt(semantic, parse_svg(svg), parse_spice(spice))
                self.assertTrue(receipt.passed, receipt.to_json())

    def test_test_fixture_and_restored_integrator_do_not_coexist_electrically(self):
        graph = load_graph()
        sweep = build_semantic_graph(graph, variant_id="W09.CC_SWEEP", fidelity="ideal")
        sweep_components = {component.id: component for component in sweep.components}
        self.assertEqual({"P":None,"N":None}, dict(sweep_components["MOD.INT1.CFB"].pins))
        self.assertIn("W09.RFB", sweep_components)
        restored = build_semantic_graph(graph, variant_id="W09.INT1_RESTORED", fidelity="ideal")
        restored_components = {component.id: component for component in restored.components}
        self.assertNotIn("W09.RFB", restored_components)
        self.assertEqual({"P":"AMP1.OUT","N":"AMP1.INV_IN"}, dict(restored_components["MOD.INT1.CFB"].pins))

    def test_all_week9_variants_ground_the_named_noninverting_terminal(self):
        graph = load_graph()
        for variant_id in ("W09.CC_SWEEP", "W09.INVERTER_TEST", "W09.INT1_RESTORED"):
            with self.subTest(variant_id=variant_id):
                semantic = build_semantic_graph(graph, variant_id=variant_id, fidelity="ideal")
                linked = {component.id: dict(component.pins) for component in semantic.components}
                self.assertEqual(
                    {"P":"AMP1.NONINV_IN", "N":"SGND"},
                    linked["W09.NONINV_GROUND"],
                )


if __name__ == "__main__":
    unittest.main()
