"""Runnable ngspice deck emission, execution, and deterministic receipts."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from .core import SemanticGraph
from .encoding import encode_id, encode_net
from .equivalence import build_connectivity_receipt
from .spice import emit_spice, parse_spice
from .svg import emit_svg, parse_svg


SAFE_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
SPICE_NUMBER = re.compile(r"^[+\-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+\-]?\d+|[A-Za-z]+)?$")
ERROR_LINE = re.compile(r"(?im)^\s*(?:error|fatal)(?::|\s)")


class NgspiceError(RuntimeError):
    """Emission or execution failed and results must not be accepted."""


@dataclass(frozen=True)
class Probe:
    name: str
    kind: str
    target: str

    def expression(self, graph: SemanticGraph) -> str:
        if not SAFE_NAME.fullmatch(self.name):
            raise NgspiceError(f"invalid probe name {self.name!r}")
        if self.kind == "voltage":
            return f"v({_voltage_node_expression(graph, self.target, self.name)})"
        if self.kind == "current":
            component = next((item for item in graph.components if item.id == self.target), None)
            if component is None:
                raise NgspiceError(f"unknown current-probe component {self.target!r}")
            if component.kind not in {"voltage_source", "current_source"}:
                raise NgspiceError(
                    "current probes currently require a voltage/current source branch; "
                    f"got {component.kind!r}"
                )
            modules = {item.id: item for item in graph.modules}
            chain: list[str] = []
            module_id: str | None = component.module_id
            while module_id is not None:
                chain.append(module_id)
                module_id = modules[module_id].parent_id
            chain.reverse()
            hierarchy = ["x" + encode_id("I", module_id).lower() for module_id in chain]
            designator = "v" if component.kind == "voltage_source" else "i"
            element = designator + encode_id("I", self.target).lower()
            return "v." + ".".join([*hierarchy, element]) + "#branch"
        raise NgspiceError(f"unsupported probe kind {self.kind!r}")


def _voltage_node_expression(graph: SemanticGraph, target: str, probe_name: str) -> str:
    """Resolve a canonical net to its actual ngspice hierarchical node.

    A child-module port is emitted as a node in its parent subcircuit.  A net
    that is not a port remains local to the component's own module.  The old
    implementation emitted every voltage probe as though the net existed at
    the top level, which fails for the Week 9 chassis hierarchy.
    """
    modules = {item.id: item for item in graph.modules}

    def chain(module_id: str) -> list[str]:
        result: list[str] = []
        current: str | None = module_id
        while current is not None:
            result.append(current)
            current = modules[current].parent_id
        result.reverse()
        return result

    port_owners = [
        module
        for module in graph.modules
        if any(net == target for _, net in module.ports)
    ]
    if port_owners:
        port_owners.sort(key=lambda item: (len(chain(item.id)), item.id))
        port_owner = port_owners[0]
        scope_id = port_owner.parent_id
    else:
        component_modules = sorted(
            {
                component.module_id
                for component in graph.components
                if any(net == target for _, net in component.pins)
            },
            key=lambda item: (len(chain(item)), item),
        )
        if not component_modules:
            raise NgspiceError(f"unknown voltage-probe net {target!r}")
        scope_id = component_modules[0]

    node = encode_net(target, "PROBE", probe_name)
    if scope_id is None:
        return node
    hierarchy = ["x" + encode_id("I", module_id).lower() for module_id in chain(scope_id)]
    return ".".join([*hierarchy, node])


@dataclass(frozen=True)
class OperatingPointAnalysis:
    name: str
    probes: tuple[Probe, ...]


@dataclass(frozen=True)
class ACAnalysis:
    name: str
    sweep: str
    points: int
    start: str
    stop: str
    probes: tuple[Probe, ...]


@dataclass(frozen=True)
class TransientAnalysis:
    name: str
    step: str
    stop: str
    probes: tuple[Probe, ...]
    start: str = "0"
    uic: bool = False


Analysis = OperatingPointAnalysis | ACAnalysis | TransientAnalysis


@dataclass(frozen=True)
class SimulationCase:
    id: str
    parameters: Mapping[str, str | float | int] = field(default_factory=dict)


@dataclass(frozen=True)
class SimulationPlan:
    name: str
    analyses: tuple[Analysis, ...]
    cases: tuple[SimulationCase, ...] = (SimulationCase("nominal"),)
    parameters: Mapping[str, str | float | int] = field(default_factory=dict)
    includes: tuple[Path, ...] = ()
    model_cards: tuple[str, ...] = ()


@dataclass(frozen=True)
class TableResult:
    columns: tuple[str, ...]
    rows: tuple[tuple[float, ...], ...]

    def as_dict(self) -> dict[str, Any]:
        return {"columns": list(self.columns), "rows": [list(row) for row in self.rows]}

    def scalar(self, column: str) -> float:
        """Return one operating-point scalar and reject ambiguous tables."""
        if len(self.rows) != 1:
            raise NgspiceError(f"table has {len(self.rows)} rows; scalar result requires exactly one")
        try:
            index = self.columns.index(column)
        except ValueError as exc:
            raise NgspiceError(f"unknown result column {column!r}") from exc
        return self.rows[0][index]


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    parameters: Mapping[str, str | float | int]
    deck_sha256: str
    command_sha256: str
    returncode: int
    tables: Mapping[str, TableResult]

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "parameters": dict(sorted(self.parameters.items())),
            "deck_sha256": self.deck_sha256,
            "command_sha256": self.command_sha256,
            "returncode": self.returncode,
            "tables": {name: table.as_dict() for name, table in sorted(self.tables.items())},
        }


@dataclass(frozen=True)
class SimulationReceipt:
    passed: bool
    executable: str
    executable_sha256: str
    version: str
    version_sha256: str
    include_sha256: Mapping[str, str]
    connectivity_sha256: str
    cases: tuple[CaseResult, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "executable": self.executable,
            "executable_sha256": self.executable_sha256,
            "version": self.version,
            "version_sha256": self.version_sha256,
            "include_sha256": dict(sorted(self.include_sha256.items())),
            "connectivity_sha256": self.connectivity_sha256,
            "cases": [case.as_dict() for case in self.cases],
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":")) + "\n"


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _validate_value(value: str | float | int, label: str) -> str:
    rendered = str(value)
    if not SPICE_NUMBER.fullmatch(rendered):
        raise NgspiceError(f"{label} is not a safe SPICE scalar: {rendered!r}")
    return rendered


def _analysis_file(name: str) -> str:
    if not SAFE_NAME.fullmatch(name):
        raise NgspiceError(f"invalid analysis name {name!r}")
    return f"result_{name}.dat"


def _control_lines(graph: SemanticGraph, analyses: Sequence[Analysis]) -> list[str]:
    lines = [".control", "set wr_singlescale", "set wr_vecnames"]
    for analysis in analyses:
        output = _analysis_file(analysis.name)
        expressions = [probe.expression(graph) for probe in analysis.probes]
        if not expressions:
            raise NgspiceError(f"analysis {analysis.name!r} has no probes")
        if isinstance(analysis, OperatingPointAnalysis):
            lines.extend(["op", "wrdata " + " ".join([output, *expressions])])
        elif isinstance(analysis, ACAnalysis):
            if analysis.sweep not in {"dec", "oct", "lin"} or analysis.points <= 0:
                raise NgspiceError(f"invalid AC sweep for {analysis.name!r}")
            start = _validate_value(analysis.start, f"{analysis.name}.start")
            stop = _validate_value(analysis.stop, f"{analysis.name}.stop")
            lines.extend(
                [
                    f"ac {analysis.sweep} {analysis.points} {start} {stop}",
                    "wrdata " + " ".join([output, "frequency", *expressions]),
                ]
            )
        elif isinstance(analysis, TransientAnalysis):
            step = _validate_value(analysis.step, f"{analysis.name}.step")
            stop = _validate_value(analysis.stop, f"{analysis.name}.stop")
            start = _validate_value(analysis.start, f"{analysis.name}.start")
            lines.extend(
                [
                    f"tran {step} {stop} {start}" + (" uic" if analysis.uic else ""),
                    "wrdata " + " ".join([output, "time", *expressions]),
                ]
            )
        else:
            raise NgspiceError(f"unsupported analysis {analysis!r}")
    lines.extend(["quit", ".endc"])
    return lines


def _provided_models(plan: SimulationPlan) -> tuple[set[str], set[str]]:
    subcircuits: set[str] = set()
    cards: set[str] = set()
    patterns = (
        (re.compile(r"(?im)^\s*\.subckt\s+(\S+)"), subcircuits),
        (re.compile(r"(?im)^\s*\.model\s+(\S+)"), cards),
    )
    texts = list(plan.model_cards)
    for path in plan.includes:
        try:
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
        except OSError as exc:
            raise NgspiceError(f"cannot read include {path}: {exc}") from exc
    for text in texts:
        for pattern, target in patterns:
            target.update(match.group(1).upper() for match in pattern.finditer(text))
    return subcircuits, cards


def _validate_model_material(graph: SemanticGraph, plan: SimulationPlan) -> None:
    subcircuits, cards = _provided_models(plan)
    no_card = {"resistor", "capacitor", "inductor", "voltage_source", "current_source"}
    for component in graph.components:
        reference = component.model_reference.upper()
        if component.model_kind == "subcircuit" and reference not in subcircuits:
            raise NgspiceError(f"{component.id}: no .subckt body supplied for {component.model_reference!r}")
        if component.model_kind == "primitive" and component.kind not in no_card and reference not in cards:
            raise NgspiceError(f"{component.id}: no .model card supplied for {component.model_reference!r}")


def emit_ngspice_deck(
    graph: SemanticGraph,
    plan: SimulationPlan,
    *,
    case: SimulationCase,
) -> str:
    """Emit a runnable batch deck; never emit empty model-interface stubs."""
    _validate_model_material(graph, plan)
    base = emit_spice(graph, include_model_interfaces=False).splitlines()
    if not base or base[-1].strip().lower() != ".end":
        raise NgspiceError("semantic SPICE projection has no final .end")
    parameters = dict(plan.parameters)
    parameters.update(case.parameters)
    additions: list[str] = []
    for path in sorted(plan.includes, key=lambda item: str(item).lower()):
        additions.append(f'.include "{path.resolve()}"')
    for name, value in sorted(parameters.items()):
        if not SAFE_NAME.fullmatch(name):
            raise NgspiceError(f"invalid parameter name {name!r}")
        additions.append(f".param {name}={_validate_value(value, name)}")
    additions.extend(card.strip() for card in plan.model_cards if card.strip())
    return "\n".join([base[0], *additions, *base[1:-1], *_control_lines(graph, plan.analyses), ".end"]) + "\n"


def parse_wrdata(path: Path) -> TableResult:
    """Parse ngspice `wrdata` whitespace tables, including vector-name header."""
    try:
        lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except OSError as exc:
        raise NgspiceError(f"missing/unreadable result table {path}: {exc}") from exc
    if not lines:
        raise NgspiceError(f"empty result table {path}")
    first = lines[0].split()
    has_header = any(not _is_float(token) for token in first)
    if has_header:
        columns = tuple(first)
        data_lines = lines[1:]
    else:
        columns = tuple(f"column_{index}" for index in range(len(first)))
        data_lines = lines
    rows: list[tuple[float, ...]] = []
    for line_number, line in enumerate(data_lines, start=2 if has_header else 1):
        tokens = line.split()
        if len(tokens) != len(columns):
            raise NgspiceError(f"{path}:{line_number}: expected {len(columns)} columns, got {len(tokens)}")
        try:
            rows.append(tuple(float(token) for token in tokens))
        except ValueError as exc:
            raise NgspiceError(f"{path}:{line_number}: nonnumeric result") from exc
    if not rows:
        raise NgspiceError(f"result table {path} has no data rows")
    return TableResult(columns, tuple(rows))


def _is_float(value: str) -> bool:
    try:
        float(value)
    except ValueError:
        return False
    return True


class NgspiceRunner:
    def __init__(self, executable: str | Path | None = None):
        selected = str(executable) if executable is not None else shutil.which("ngspice")
        if not selected:
            raise NgspiceError("ngspice executable was not provided and is not on PATH")
        self.executable = Path(selected).resolve()
        if not self.executable.is_file():
            raise NgspiceError(f"ngspice executable does not exist: {self.executable}")

    def version(self) -> str:
        completed = subprocess.run(
            [str(self.executable), "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
        output = (completed.stdout + completed.stderr).replace("\r\n", "\n").strip()
        if completed.returncode != 0 or "ngspice" not in output.lower():
            raise NgspiceError(f"cannot identify ngspice: {output}")
        return output

    def run(self, graph: SemanticGraph, plan: SimulationPlan) -> SimulationReceipt:
        semantic_svg = emit_svg(graph)
        semantic_spice = emit_spice(graph)
        connectivity = build_connectivity_receipt(
            graph, parse_svg(semantic_svg), parse_spice(semantic_spice)
        )
        if not connectivity.passed:
            raise NgspiceError("connectivity equivalence failed before simulation")
        version = self.version()
        include_hashes = {str(path.resolve()): _sha256_file(path) for path in plan.includes}
        case_results: list[CaseResult] = []
        with tempfile.TemporaryDirectory(prefix="roberge-ngspice-") as temporary:
            work = Path(temporary)
            for case in plan.cases:
                if not SAFE_NAME.fullmatch(case.id):
                    raise NgspiceError(f"invalid case ID {case.id!r}")
                deck_text = emit_ngspice_deck(graph, plan, case=case)
                case_work = work / case.id
                case_work.mkdir()
                deck_path = case_work / f"{case.id}.cir"
                log_path = case_work / f"{case.id}.log"
                deck_path.write_text(deck_text, encoding="utf-8", newline="\n")
                command = [str(self.executable), "-b", "-o", str(log_path), str(deck_path)]
                normalized_command = [str(self.executable), "-b", "-o", "<LOG>", "<DECK>"]
                completed = subprocess.run(
                    command,
                    cwd=case_work,
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=120,
                )
                log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
                diagnostics = "\n".join([completed.stdout, completed.stderr, log])
                if completed.returncode != 0 or ERROR_LINE.search(diagnostics):
                    raise NgspiceError(
                        f"ngspice failed for case {case.id!r} (exit {completed.returncode}):\n{diagnostics.strip()}"
                    )
                tables = {
                    analysis.name: parse_wrdata(case_work / _analysis_file(analysis.name))
                    for analysis in plan.analyses
                }
                parameters = dict(plan.parameters)
                parameters.update(case.parameters)
                case_results.append(
                    CaseResult(
                        case_id=case.id,
                        parameters=parameters,
                        deck_sha256=_sha256_bytes(deck_text.encode("utf-8")),
                        command_sha256=_sha256_bytes(
                            json.dumps(normalized_command, separators=(",", ":")).encode("utf-8")
                        ),
                        returncode=completed.returncode,
                        tables=tables,
                    )
                )
        return SimulationReceipt(
            passed=True,
            executable=str(self.executable),
            executable_sha256=_sha256_file(self.executable),
            version=version,
            version_sha256=_sha256_bytes(version.encode("utf-8")),
            include_sha256=include_hashes,
            connectivity_sha256=connectivity.canonical_sha256,
            cases=tuple(case_results),
        )
