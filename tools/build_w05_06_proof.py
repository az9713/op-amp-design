"""Build deterministic topology-tier ngspice proof receipts for Weeks 5 and 6."""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.circuit_pipeline import (
    ACAnalysis,
    NgspiceRunner,
    OperatingPointAnalysis,
    Probe,
    SemanticGraph,
    SimulationCase,
    SimulationPlan,
    TransientAnalysis,
    build_semantic_graph,
    emit_ngspice_deck,
)


GRAPH_PATH = ROOT / "circuits" / "weeks" / "w05_06" / "graph.json"
MANIFEST_PATH = ROOT / "circuits" / "weeks" / "w05_06" / "case-manifest.json"
OUTPUT = ROOT / "generated" / "weeks05_06" / "proof"

OPAMP_BODY = """.subckt W00_04_IDEAL_OPAMP INP INM OUT VP VN COMPA COMPB
BOUT OUT 0 V=13*tanh(1e4*(V(INP)-V(INM)))
RINP INP 0 1G
RINM INM 0 1G
RCOMPA COMPA 0 1T
RCOMPB COMPB 0 1T
.ends W00_04_IDEAL_OPAMP"""


def selected_semantic(document: dict, variant_id: str, module_root: str) -> SemanticGraph:
    full = build_semantic_graph(document, variant_id=variant_id, fidelity="ideal")
    modules = {item.id: item for item in full.modules}

    def in_tree(module_id: str) -> bool:
        current: str | None = module_id
        while current is not None:
            if current == module_root:
                return True
            current = modules[current].parent_id
        return False

    keep_modules = tuple(item for item in full.modules if item.id in {"CHASSIS", "INF.PWR_ENTRY"} or in_tree(item.id))
    keep_components = tuple(item for item in full.components if item.module_id == "INF.PWR_ENTRY" or in_tree(item.module_id))
    proof_contract = {
        "canonical_sha256": hashlib.sha256(full.canonical_json.encode("utf-8")).hexdigest(),
        "variant_id": variant_id,
        "selected_module": module_root,
        "included_components": [item.id for item in keep_components],
    }
    return SemanticGraph(
        project_id=full.project_id + ".PROOF." + module_root,
        variant_id=variant_id,
        fidelity=full.fidelity,
        components=keep_components,
        modules=keep_modules,
        canonical_json=json.dumps(proof_contract, sort_keys=True, separators=(",", ":")),
    )


def replace_values(graph: SemanticGraph, values: dict[str, str]) -> SemanticGraph:
    return replace(graph, components=tuple(replace(item, value=values.get(item.id, item.value)) for item in graph.components))


def write_proof(name: str, graph: SemanticGraph, plan: SimulationPlan) -> None:
    target = OUTPUT / name
    target.mkdir(parents=True, exist_ok=True)
    for case in plan.cases or (SimulationCase("default", {}),):
        (target / f"{case.id}.cir").write_text(emit_ngspice_deck(graph, plan, case=case), encoding="utf-8", newline="\n")
    receipt = NgspiceRunner().run(graph, plan)
    (target / "simulation-receipt.json").write_text(receipt.to_json() + "\n", encoding="utf-8", newline="\n")


def table_rows(receipt_path: Path, case_id: str, analysis: str) -> list[list[float]]:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    case = next(item for item in receipt["cases"] if item["case_id"] == case_id)
    return case["tables"][analysis]["rows"]


def main() -> None:
    document = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    model_common = (
        OPAMP_BODY,
        ".model W0506_NPN_BASE NPN(BF=100 VAF=100 IS=1e-14)",
        ".model W0506_Z10 D(IS=1e-12 N=1.5 BV=10 IBV=10m)",
        ".model W0506_Z5V1 D(IS=1e-12 N=1.5 BV=5.1 IBV=5m)",
        ".model W0506_RECT D(IS=1e-9 N=1.8)",
    )

    regulator = selected_semantic(document, "W05.REGULATOR_SWEEP", "REG1")
    regulator = replace_values(regulator, {"REG1.R_LOAD": "{RL}", "REG1.C_LOAD": "{CL}"})
    cases = tuple(
        SimulationCase("rl" + r["id"][2:].lower() + "_cl" + c["id"][2:].lower(), {"RL": r["value"], "CL": c["value"]})
        for r in manifest["load_resistance_cases"]
        for c in manifest["load_capacitance_cases"]
    )
    regulator_plan = SimulationPlan(
        name="w05_regulator_topology",
        analyses=(
            OperatingPointAnalysis("op", (Probe("vout", "voltage", "REG1.VOUT"), Probe("vref", "voltage", "REG1.VREF"))),
            ACAnalysis("ac", "dec", 10, "0.1", "100k", (Probe("voutac", "voltage", "REG1.VOUT"),)),
            TransientAnalysis("tran", "100u", "200m", (Probe("vouttran", "voltage", "REG1.VOUT"),)),
        ),
        cases=cases,
        model_cards=model_common,
    )
    write_proof("w05-regulator", regulator, regulator_plan)

    oscillator = selected_semantic(document, "W06.OSCILLATOR", "OSC1")
    oscillator_plan = SimulationPlan(
        name="w06_oscillator_topology",
        analyses=(TransientAnalysis("tran", "2m", "12", (Probe("square", "voltage", "OSC1.SQUARE"), Probe("triangle", "voltage", "OSC1.TRIANGLE")), uic=True),),
        cases=(SimulationCase("nominal", {}),),
        model_cards=model_common,
    )
    write_proof("w06-oscillator", oscillator, oscillator_plan)

    regulator_receipt = OUTPUT / "w05-regulator" / "simulation-receipt.json"
    regulator_data = json.loads(regulator_receipt.read_text(encoding="utf-8"))
    regulator_metrics = []
    for case in regulator_data["cases"]:
        row = case["tables"]["op"]["rows"][0]
        regulator_metrics.append({"case_id": case["case_id"], "vout_v": row[-2], "vref_v": row[-1]})
    if not all(9.0 <= item["vout_v"] <= 11.0 for item in regulator_metrics):
        raise RuntimeError("Week 5 topology proof failed its 9-11 V operating-point envelope")

    oscillator_rows = table_rows(OUTPUT / "w06-oscillator" / "simulation-receipt.json", "nominal", "tran")
    square = [row[2] for row in oscillator_rows]
    triangle = [row[3] for row in oscillator_rows]
    crossing_times = []
    for prior, current in zip(oscillator_rows, oscillator_rows[1:]):
        if prior[2] <= 0.0 < current[2]:
            crossing_times.append(current[0])
    periods = [later - earlier for earlier, later in zip(crossing_times, crossing_times[1:])]
    oscillator_metrics = {
        "square_min_v": min(square),
        "square_max_v": max(square),
        "triangle_min_v": min(triangle),
        "triangle_max_v": max(triangle),
        "positive_crossing_times_s": crossing_times,
        "measured_periods_s": periods,
    }
    if max(square) - min(square) < 8.0 or max(triangle) - min(triangle) < 8.0 or len(crossing_times) < 2:
        raise RuntimeError("Week 6 topology proof did not sustain the required square/triangle oscillation")
    if periods and not all(3.0 <= period <= 5.0 for period in periods):
        raise RuntimeError("Week 6 topology proof period is outside the source-derived 4 s neighborhood")

    summary = {
        "claim_boundary": "Topology-tier only: generic behavioral op amps and generic semiconductor models; not LM301A/BD139 performance validation.",
        "week05": {"passed": True, "operating_points": regulator_metrics},
        "week06": {"passed": True, **oscillator_metrics},
    }
    (OUTPUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("PASS: wrote Weeks 5-6 topology-tier ngspice proof decks and receipts")


if __name__ == "__main__":
    main()
