#!/usr/bin/env python3
"""Run and grade the W13 final-build ideal-tier ngspice demonstration."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DECK = HERE / "w13-final_build-functional.cir"
CSV = HERE / "w13-final_build-functional.csv"
LOG = HERE / "w13-final_build-functional.log"
RECEIPT = HERE / "w13-final_build-functional.receipt.json"
PLOT = HERE / "w13-final_build-functional-results.svg"
LOCK = ROOT / "spec" / "decisions" / "dependency-lock.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def window(rows: list[list[float]], start: float, stop: float, column: int) -> list[float]:
    return [row[column] for row in rows if start <= row[0] <= stop]


def first_crossing(rows: list[list[float]], start: float, stop: float, column: int, target: float, rising: bool) -> float:
    for row in rows:
        if start <= row[0] <= stop and ((row[column] >= target) if rising else (row[column] <= target)):
            return row[0]
    raise RuntimeError(f"no {'rising' if rising else 'falling'} crossing of {target:g}")


def parse_csv(path: Path) -> list[list[float]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    rows = [[float(item) for item in line.split()] for line in lines[1:] if line.strip()]
    if not rows or any(len(row) != 6 for row in rows):
        raise RuntimeError("unexpected ngspice wrdata table")
    return rows


def parse_param(deck: str, name: str) -> float:
    match = re.search(rf"\b{name}=([0-9.eE+-]+)", deck)
    if not match:
        raise RuntimeError(f"missing numeric deck parameter {name}")
    return float(match.group(1))


def polyline(rows: list[list[float]], x0: float, x1: float, column: int, y0: float, y1: float, left: float, top: float, width: float, height: float) -> str:
    selected = [row for row in rows if x0 <= row[0] <= x1]
    stride = max(1, len(selected) // 1200)
    points = []
    for row in selected[::stride]:
        x = left + width * (row[0] - x0) / (x1 - x0)
        y = top + height * (1 - (row[column] - y0) / (y1 - y0))
        points.append(f"{x:.2f},{y:.2f}")
    return " ".join(points)


def write_plot(rows: list[list[float]], baseline: float) -> None:
    transformed = [row[:] + [1000 * (baseline - row[4]), 1000 * row[5]] for row in rows]
    osc_square = polyline(rows, 0, 0.35, 2, -5.5, 5.5, 75, 75, 1050, 250)
    osc_triangle = polyline(rows, 0, 0.35, 3, -5.5, 5.5, 75, 75, 1050, 250)
    reg_droop = polyline(transformed, 0.045, 0.105, 6, -5, 110, 75, 430, 1050, 250)
    twin = polyline(transformed, 0.045, 0.105, 7, -5, 110, 75, 430, 1050, 250)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="760" viewBox="0 0 1200 760">
<rect width="1200" height="760" fill="#f8fafc"/>
<style>text{{font-family:Arial,sans-serif;fill:#17202a}} .axis{{stroke:#64748b;stroke-width:1}} .grid{{stroke:#d8dee6;stroke-width:1}} .legend{{font-size:15px}} .title{{font-size:22px;font-weight:700}} .label{{font-size:14px}}</style>
<text x="75" y="38" class="title">W13.FINAL_BUILD ideal-tier functional demonstration</text>
<text x="75" y="63" class="label">OSC1 outputs and calibrated REG1 load-step twin · ngspice 47</text>
<rect x="75" y="75" width="1050" height="250" fill="white" stroke="#94a3b8"/>
<line x1="75" y1="200" x2="1125" y2="200" class="grid"/><text x="15" y="205" class="label">0 V</text>
<polyline points="{osc_square}" fill="none" stroke="#d85c41" stroke-width="2"/>
<polyline points="{osc_triangle}" fill="none" stroke="#216e45" stroke-width="2"/>
<text x="85" y="100" class="legend" fill="#d85c41">square 0–5 V</text><text x="230" y="100" class="legend" fill="#216e45">triangle ±5 V</text>
<text x="75" y="355" class="label">0</text><text x="1085" y="355" class="label">350 ms</text>
<rect x="75" y="430" width="1050" height="250" fill="white" stroke="#94a3b8"/>
<line x1="75" y1="669" x2="1125" y2="669" class="grid"/>
<polyline points="{reg_droop}" fill="none" stroke="#284f76" stroke-width="3"/>
<polyline points="{twin}" fill="none" stroke="#d85c41" stroke-width="2" stroke-dasharray="7 4"/>
<text x="85" y="455" class="legend" fill="#284f76">REG1 measured droop</text><text x="290" y="455" class="legend" fill="#d85c41">INT2 analog twin</text>
<text x="15" y="675" class="label">0 mV</text><text x="5" y="448" class="label">110 mV</text>
<text x="75" y="710" class="label">45 ms</text><text x="1065" y="710" class="label">105 ms</text>
<text x="75" y="742" class="label">Topology/function demonstration only; not a historical-device performance prediction.</text>
</svg>'''
    PLOT.write_text(svg, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ngspice", type=Path)
    args = parser.parse_args()
    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    executable = args.ngspice or Path(lock["dependencies"]["ngspice"]["installed_binary"])

    run = subprocess.run([str(executable), "-b", str(DECK)], cwd=ROOT, capture_output=True, text=True)
    combined = run.stdout + run.stderr
    LOG.write_text(combined, encoding="utf-8", newline="\n")
    if run.returncode or re.search(r"(^|\n)\s*(error|fatal)\b", combined, re.I):
        raise SystemExit(f"ngspice failed; see {LOG.relative_to(ROOT)}")

    rows = parse_csv(CSV)
    deck_text = DECK.read_text(encoding="utf-8")
    reg_off = mean(window(rows, 0.035, 0.045, 4))
    reg_on = mean(window(rows, 0.085, 0.095, 4))
    twin_off = mean(window(rows, 0.035, 0.045, 5))
    twin_on = mean(window(rows, 0.085, 0.095, 5))
    droop = reg_off - reg_on
    twin_step = twin_on - twin_off
    reg_target = reg_off - 0.6321205588 * droop
    twin_target = twin_off + 0.6321205588 * twin_step
    reg_tau = first_crossing(rows, 0.05, 0.06, 4, reg_target, False) - 0.05
    twin_tau = first_crossing(rows, 0.05, 0.06, 5, twin_target, True) - 0.05
    high_rows = [row for row in rows if 0.05 <= row[0] <= 0.095]
    errors = [(reg_off - row[4]) - row[5] for row in high_rows]
    rms_error = math.sqrt(mean([value * value for value in errors]))
    peak_error = max(abs(value) for value in errors)
    osc_low = min(row[2] for row in rows)
    osc_high = max(row[2] for row in rows)
    tri_low = min(row[3] for row in rows)
    tri_high = max(row[3] for row in rows)

    configured_leak = parse_param(deck_text, "R_TWIN_LEAK")
    configured_drive = parse_param(deck_text, "R_TWIN_DRIVE")
    configured_ctwin = parse_param(deck_text, "C_TWIN") * 1e-6
    derived_leak = reg_tau / configured_ctwin
    derived_drive = derived_leak / droop

    gates = {
        "oscillator_square": abs(osc_low) <= 0.01 and 4.99 <= osc_high <= 5.01,
        "oscillator_triangle": tri_low <= -4.9 and tri_high >= 4.9,
        "regulated_output": 9.0 <= reg_on <= reg_off <= 11.0 and 0.05 <= droop <= 0.2,
        "positive_load_droop_polarity": droop > 0 and twin_step > 0,
        "steady_twin_tracking": abs(twin_step - droop) <= 0.0005,
        "transient_twin_tracking": rms_error <= 0.003 and peak_error <= 0.006,
        "time_constant_tracking": abs(twin_tau - reg_tau) <= 0.0001,
        "calibration_resistors": abs(configured_leak / derived_leak - 1) <= 0.02 and abs(configured_drive / derived_drive - 1) <= 0.02,
    }
    write_plot(rows, reg_off)
    version = subprocess.run([str(executable), "--version"], capture_output=True, text=True).stdout.strip()
    receipt = {
        "schema_version": 1,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "claim_boundary": "Ideal-tier functional demonstration; not historical-device or constructed-hardware prediction.",
        "canonical_source": "generated/week13/w13-final_build-ideal.cir",
        "deck": str(DECK.relative_to(ROOT)).replace("\\", "/"),
        "simulator": {"path": str(executable), "sha256": sha256(executable), "version": version},
        "hashes": {"deck_sha256": sha256(DECK), "csv_sha256": sha256(CSV), "log_sha256": sha256(LOG), "plot_sha256": sha256(PLOT)},
        "assumptions": {"model_tier": "project-owned behavioral/generic", "S_VI_V_per_A": 100, "RL_MAIN_ohm": 1000, "RL_STEP_ohm": 1000, "CL_OUT_F": 47e-6, "C_TWIN_F": configured_ctwin},
        "calibration": {"reg_off_V": reg_off, "reg_on_V": reg_on, "droop_V": droop, "reg_tau_s": reg_tau, "derived_R_TWIN_LEAK_ohm": derived_leak, "derived_R_TWIN_DRIVE_ohm": derived_drive, "configured_R_TWIN_LEAK_ohm": configured_leak, "configured_R_TWIN_DRIVE_ohm": configured_drive},
        "results": {"twin_step_V": twin_step, "twin_tau_s": twin_tau, "steady_error_V": twin_step - droop, "rms_tracking_error_V": rms_error, "peak_tracking_error_V": peak_error, "oscillator_square_min_V": osc_low, "oscillator_square_max_V": osc_high, "oscillator_triangle_min_V": tri_low, "oscillator_triangle_max_V": tri_high},
        "gates": gates,
        "simulation_passed": all(gates.values()),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"simulation_passed": receipt["simulation_passed"], "gates": gates, "receipt": str(RECEIPT.relative_to(ROOT)), "plot": str(PLOT.relative_to(ROOT))}, indent=2))
    return 0 if receipt["simulation_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
