"""Build and run the Week 9 topology-tier vertical proof.

Each electrical case is produced by applying explicit value, state, and
connection substitutions to the canonical Week 9 graph before projection.
The source graph remains unchanged.  In particular, an open Ralpha branch is
removed from the semantic graph; it is never approximated by a large resistor.
"""
from __future__ import annotations

import copy
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.circuit_pipeline import (
    ACAnalysis,
    NgspiceRunner,
    OperatingPointAnalysis,
    Probe,
    SimulationCase,
    SimulationPlan,
    TransientAnalysis,
    build_connectivity_receipt,
    build_semantic_graph,
    emit_ngspice_deck,
    emit_spice,
    emit_svg,
    parse_spice,
    parse_svg,
)
from tools.circuit_pipeline.core import ProjectionError


ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "circuits" / "weeks" / "w09" / "graph.json"
MANIFEST_PATH = ROOT / "circuits" / "weeks" / "w09" / "case-manifest.json"
MODEL_LIBRARY = ROOT / "circuits" / "models" / "w09-topology-baseline.lib"
OUTPUT_ROOT = ROOT / "generated" / "week09" / "proof"


def find_ngspice() -> Path:
    """Resolve ngspice without binding the repository to one workstation."""
    explicit = os.environ.get("ROBERGE_NGSPICE")
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file():
            return candidate.resolve()
        raise FileNotFoundError(f"ROBERGE_NGSPICE does not name a file: {candidate}")

    for command in ("ngspice_con", "ngspice"):
        discovered = shutil.which(command)
        if discovered:
            return Path(discovered).resolve()

    raise FileNotFoundError(
        "ngspice was not found on PATH; set ROBERGE_NGSPICE to the executable"
    )

MODULE_STUB = """\
* Inactive retained modules are visible chassis inventory, not active DUTs.
.subckt W09_MODULE_STUB VP VN GND IN OUT
.ends W09_MODULE_STUB
"""


@dataclass(frozen=True)
class ProofCase:
    id: str
    variant: str
    cc: str
    source: str
    analyses: tuple[Any, ...]
    ralpha: str | None = None
    int1: bool = False


VOUT = Probe("vout", "voltage", "AMP1.OUT")
VIN = Probe("vin", "voltage", "W09.VIN")
INT1_IN = Probe("int1_in", "voltage", "MOD.INT1.INPUT")
ISOURCE = Probe("isource", "current", "W09.VSRC")

CASES = (
    ProofCase(
        "INV20",
        "W09.INVERTER_TEST",
        "20p",
        "DC 0 AC 1",
        (
            OperatingPointAnalysis("op", (VOUT, ISOURCE)),
            ACAnalysis("ac", "dec", 100, "1", "100Meg", (VIN, VOUT)),
        ),
    ),
    *(
        ProofCase(
            f"A{cc[:-1].zfill(2)}",
            "W09.CC_SWEEP",
            cc,
            "PULSE(0 -20m 1u 100n 100n 400u 1m)",
            (TransientAnalysis("tran", "20n", "1m", (VIN, VOUT)),),
        )
        for cc in ("47p", "33p", "10p", "5p")
    ),
    ProofCase(
        "B20",
        "W09.CC_SWEEP",
        "20p",
        "PULSE(-10 10 100u 100n 100n 500u 1m)",
        (TransientAnalysis("tran", "100n", "2m", (VIN, VOUT)),),
    ),
    ProofCase(
        "B10",
        "W09.CC_SWEEP",
        "10p",
        "PULSE(-10 10 100u 100n 100n 500u 1m)",
        (TransientAnalysis("tran", "100n", "2m", (VIN, VOUT)),),
        ralpha="2.350k",
    ),
    ProofCase(
        "INT1",
        "W09.INT1_RESTORED",
        "47p",
        "PULSE(0 100m 1m 100n 100n 20m 40m)",
        (TransientAnalysis("tran", "10u", "25m", (INT1_IN, VOUT)),),
        int1=True,
    ),
)


def validate_case_manifest() -> None:
    """Fail if executable source cases drift from the reviewed manifest."""
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    declared = {item["id"].removeprefix("CASE.W09."): item for item in manifest["cases"]}
    executable = {item.id: item for item in CASES if item.id.startswith(("A", "B"))}
    if set(declared) != set(executable):
        raise RuntimeError(
            f"case manifest mismatch: declared={sorted(declared)}, executable={sorted(executable)}"
        )
    waveforms = manifest["waveforms"]
    for case_id, item in executable.items():
        source = declared[case_id]
        expected_ralpha = None if source["ralpha"]["value"] == "OPEN" else source["ralpha"]["value"]
        expected_waveform = waveforms[source["waveform_id"]]["spice"]
        if (item.cc, item.ralpha, item.source) != (
            source["cc"],
            expected_ralpha,
            expected_waveform,
        ):
            raise RuntimeError(f"{case_id}: executable values drift from case-manifest.json")
    if manifest["claim_boundary"]["hidden_bleed_allowed"] is not False:
        raise RuntimeError("Week 9 proof forbids a hidden integrator bleed")


def _index(document: dict[str, Any], key: str) -> dict[str, dict[str, Any]]:
    return {item["id"]: item for item in document[key]}


def _set_state_override(variant: dict[str, Any], component_id: str, state: str) -> None:
    existing = next(
        (item for item in variant["state_overrides"] if item["component_id"] == component_id),
        None,
    )
    if existing is None:
        variant["state_overrides"].append(
            {"component_id": component_id, "state_class": state}
        )
    else:
        existing["state_class"] = state


def _set_connection_override(
    variant: dict[str, Any], component_id: str, pin_id: str, net: str | None
) -> None:
    existing = next(
        (
            item
            for item in variant["connection_overrides"]
            if item["component_id"] == component_id and item["pin_id"] == pin_id
        ),
        None,
    )
    if existing is None:
        variant["connection_overrides"].append(
            {"component_id": component_id, "pin_id": pin_id, "net": net}
        )
    else:
        existing["net"] = net


def apply_case(source: dict[str, Any], case: ProofCase) -> dict[str, Any]:
    document = copy.deepcopy(source)
    components = _index(document, "components")
    variants = _index(document, "variants")
    variant = variants[case.variant]

    components["AMP1.CC"]["value"] = case.cc
    components["W09.RIN"]["value"] = "4.70k"
    components["W09.RFB"]["value"] = "4.70k"
    components["W09.VSRC"]["value"] = case.source
    components["W09.LOAD"]["value"] = "10Meg"
    _set_state_override(variant, "W09.LOAD", "configuration-only-fixture")
    # Topology tier has an ideal (zero-ohm) generator.  Express that as a
    # direct net connection, not as ngspice's hidden minimum resistor value.
    _set_state_override(variant, "W09.RSOURCE", "removed-off-circuit")
    _set_connection_override(variant, "W09.RSOURCE", "P", None)
    _set_connection_override(variant, "W09.RSOURCE", "N", None)
    _set_connection_override(variant, "W09.VSRC", "P", "W09.VIN")
    _set_connection_override(variant, "W09.VSRC", "N", "SGND")

    if case.ralpha is None:
        _set_state_override(variant, "W09.RALPHA", "removed-off-circuit")
        _set_connection_override(variant, "W09.RALPHA", "P", None)
        _set_connection_override(variant, "W09.RALPHA", "N", None)
    else:
        components["W09.RALPHA"]["value"] = case.ralpha
        _set_state_override(variant, "W09.RALPHA", "configuration-only-fixture")
        _set_connection_override(variant, "W09.RALPHA", "P", "AMP1.INV_IN")
        _set_connection_override(variant, "W09.RALPHA", "N", "SGND")

    if case.int1:
        components["MOD.INT1.RIN"]["value"] = "10k"
        components["MOD.INT1.CFB"]["value"] = "1u"
        fixture = _index(document, "modules")["W09.FIXTURE"]
        next(port for port in fixture["ports"] if port["id"] == "VIN")["net"] = (
            "MOD.INT1.INPUT"
        )
        _set_state_override(variant, "W09.VSRC", "configuration-only-fixture")
        _set_connection_override(variant, "W09.VSRC", "P", "MOD.INT1.INPUT")
        _set_connection_override(variant, "W09.VSRC", "N", "SGND")
    else:
        # Persistent-inactive is a rendering state.  A disconnected symbolic
        # passive must be absent from an executable electrical case.
        _set_state_override(variant, "MOD.INT1.RIN", "removed-off-circuit")
        _set_state_override(variant, "MOD.INT1.CFB", "removed-off-circuit")
    return document


def build_case(source: dict[str, Any], case: ProofCase, runner: NgspiceRunner) -> dict[str, Any]:
    document = apply_case(source, case)
    graph = build_semantic_graph(document, variant_id=case.variant, fidelity="ideal")
    svg = emit_svg(graph)
    spice = emit_spice(graph)
    connectivity = build_connectivity_receipt(graph, parse_svg(svg), parse_spice(spice))
    if not connectivity.passed:
        raise RuntimeError(f"{case.id}: connectivity equivalence failed")

    plan = SimulationPlan(
        name=f"w09_{case.id.lower()}",
        analyses=case.analyses,
        cases=(SimulationCase("nominal"),),
        includes=(MODEL_LIBRARY,),
        model_cards=(MODULE_STUB,),
    )
    simulation = runner.run(graph, plan)
    deck = emit_ngspice_deck(graph, plan, case=plan.cases[0])

    case_dir = OUTPUT_ROOT / "cases" / case.id.lower()
    case_dir.mkdir(parents=True, exist_ok=True)
    (case_dir / "graph.resolved.json").write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (case_dir / "schematic.svg").write_text(svg, encoding="utf-8", newline="\n")
    (case_dir / "connectivity.cir").write_text(spice, encoding="utf-8", newline="\n")
    (case_dir / "connectivity.receipt.json").write_text(
        connectivity.to_json(), encoding="utf-8", newline="\n"
    )
    (case_dir / "simulation.cir").write_text(deck, encoding="utf-8", newline="\n")
    (case_dir / "simulation.receipt.json").write_text(
        simulation.to_json(), encoding="utf-8", newline="\n"
    )
    tables = simulation.cases[0].tables
    metrics: dict[str, Any] = {}
    if "op" in tables:
        # OP writes an implicit scale followed by the requested VOUT and
        # source-current expressions.
        metrics["dc_output_v"] = tables["op"].rows[0][-2]
    if "ac" in tables:
        first = tables["ac"].rows[0]
        metrics["low_frequency_gain_magnitude"] = (first[-2] ** 2 + first[-1] ** 2) ** 0.5
    if "tran" in tables:
        rows = tables["tran"].rows
        outputs = [row[-1] for row in rows]
        metrics.update(
            {
                "output_min_v": min(outputs),
                "output_max_v": max(outputs),
                "output_peak_to_peak_v": max(outputs) - min(outputs),
                "output_final_v": outputs[-1],
            }
        )
        if case.int1:
            def nearest(time_s: float) -> tuple[float, ...]:
                return min(rows, key=lambda row: abs(row[0] - time_s))

            start_output = nearest(0.001)[-1]
            end_output = nearest(0.021)[-1]
            metrics["integrator_20ms_delta_v"] = end_output - start_output
    return {
        "case": case.id,
        "variant": case.variant,
        "connectivity_passed": connectivity.passed,
        "simulation_passed": simulation.passed,
        "connectivity_sha256": connectivity.canonical_sha256,
        "deck_sha256": simulation.cases[0].deck_sha256,
        "result_tables": sorted(simulation.cases[0].tables),
        "metrics": metrics,
    }


def run_balance_scan(source: dict[str, Any], runner: NgspiceRunner) -> dict[str, Any]:
    """Exercise the source's physical 50 k balance control before DC rejection."""
    case = next(item for item in CASES if item.id == "INV20")
    points: list[dict[str, Any]] = []
    plan = SimulationPlan(
        name="w09_balance_scan",
        analyses=(OperatingPointAnalysis("op", (VOUT,)),),
        cases=(SimulationCase("nominal"),),
        includes=(MODEL_LIBRARY,),
        model_cards=(MODULE_STUB,),
    )
    for fraction in (0.01, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 0.99):
        document = apply_case(source, case)
        components = _index(document, "components")
        left = 50.0 * fraction
        right = 50.0 * (1.0 - fraction)
        components["AMP1.R_BAL_L"]["value"] = f"{left:.6g}k"
        components["AMP1.R_BAL_R"]["value"] = f"{right:.6g}k"
        graph = build_semantic_graph(
            document, variant_id=case.variant, fidelity="ideal"
        )
        receipt = runner.run(graph, plan)
        output = receipt.cases[0].tables["op"].rows[0][-1]
        points.append(
            {
                "wiper_fraction_left": fraction,
                "left_segment_kohm": left,
                "right_segment_kohm": right,
                "dc_output_v": output,
                "deck_sha256": receipt.cases[0].deck_sha256,
                "connectivity_sha256": receipt.connectivity_sha256,
            }
        )
    best = min(points, key=lambda item: abs(item["dc_output_v"]))
    result = {
        "status": "PASS" if abs(best["dc_output_v"]) <= 0.1 else "FAIL",
        "criterion": "physical 50 k balance sweep can reduce zero-input output magnitude to <=0.1 V",
        "best": best,
        "points": points,
    }
    (OUTPUT_ROOT / "balance-trim-scan.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return result


def main() -> int:
    validate_case_manifest()
    source = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    runner = NgspiceRunner(find_ngspice())
    results = [build_case(source, case, runner) for case in CASES]
    balance_scan = run_balance_scan(source, runner)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    by_case = {item["case"]: item for item in results}
    inv = by_case["INV20"]["metrics"]
    int1 = by_case["INT1"]["metrics"]
    acceptance = [
        {
            "id": "W09-EL-01",
            "criterion": balance_scan["criterion"],
            "observed": balance_scan["best"]["dc_output_v"],
            "passed": balance_scan["status"] == "PASS",
        },
        {
            "id": "W09-EL-02",
            "criterion": "1 Hz closed-loop inverter gain magnitude within 0.9 to 1.1",
            "observed": inv["low_frequency_gain_magnitude"],
            "passed": 0.9 <= inv["low_frequency_gain_magnitude"] <= 1.1,
        },
        {
            "id": "W09-EL-03",
            "criterion": "10 ms ideal-scale integrator changes -0.2 V +/-10% during +100 mV for 20 ms",
            "observed": int1["integrator_20ms_delta_v"],
            "passed": -0.22 <= int1["integrator_20ms_delta_v"] <= -0.18,
        },
    ]
    electrical_passed = all(item["passed"] for item in acceptance)
    summary = {
        "status": "PASS" if electrical_passed else "BLOCKED",
        "pipeline_execution": "PASS",
        "electrical_acceptance": "PASS" if electrical_passed else "FAIL",
        "claim_boundary": (
            "topology-tier execution only; generic ngspice device defaults are not "
            "historical or realistic models"
        ),
        "blocker": None
        if electrical_passed
        else (
            "The generic default semiconductor cards execute but do not bias or amplify "
            "the Figure 9.1 circuit plausibly. Quantitative acceptance requires lawful, "
            "characterized device models or measurements; topology defaults cannot be tuned "
            "and promoted as historical evidence."
        ),
        "acceptance": acceptance,
        "balance_scan": "balance-trim-scan.json",
        "cases": results,
    }
    (OUTPUT_ROOT / "summary.json").write_text(
        json.dumps(summary, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    realistic_blocker: dict[str, Any]
    try:
        build_semantic_graph(
            source, variant_id="W09.INVERTER_TEST", fidelity="realistic"
        )
    except ProjectionError as exc:
        realistic_blocker = {
            "status": "BLOCKED",
            "requested_projection": "W09.INVERTER_TEST realistic",
            "reason": str(exc),
            "policy": (
                "No ideal/default semiconductor card may be relabeled realistic. "
                "A realistic netlist requires lawful model provenance and explicit bindings."
            ),
        }
    else:
        realistic_blocker = {
            "status": "UNEXPECTEDLY_AVAILABLE",
            "requested_projection": "W09.INVERTER_TEST realistic",
            "reason": "Review model provenance before accepting this projection.",
        }
    (OUTPUT_ROOT / "realistic-projection.json").write_text(
        json.dumps(realistic_blocker, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
