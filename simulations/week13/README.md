# Week 13 final functional demonstration

This directory contains a separate, executable ideal-tier SPICE campaign derived from the approved `W13.FINAL_BUILD` netlist. The approved canonical SVG/SPICE pair remains the connectivity authority; this deck adds the explicit models, loads, stimuli, analysis, measurements, assertions, and reporting needed to demonstrate system behavior under ngspice.

## Run it

From the repository root:

```powershell
python simulations/week13/run_final_demo.py
```

The runner uses the pinned ngspice 47 executable recorded in `spec/decisions/dependency-lock.json`, regenerates the waveform CSV and log, evaluates the numerical gates, and writes:

- `w13-final_build-functional.receipt.json` — simulator identity, hashes, calibration, measurements, and pass/fail gates;
- `w13-final_build-functional-results.svg` — oscillator and regulator/twin waveforms;
- `w13-final_build-functional.csv` and `.log` — reproducible scratch outputs, intentionally ignored by Git.

## What the deck demonstrates

1. Project-owned behavioral op-amp and switch models plus generic semiconductor models.
2. Explicit regulator load resistance, switched load, output capacitance, ESR, and isolation resistance.
3. A transient load-step response from the regulator.
4. Extraction of steady droop and the 63.2% time constant.
5. Derivation and checking of the analog-twin resistors.
6. A combined final-machine run containing OSC1, REG1, SUM1, and INT2.
7. Recorded oscillator, physical-regulator, and analog-twin waveforms.
8. Eight numerical assertions covering amplitude, polarity, regulation, calibration, and twin tracking.
9. A deterministic SVG result plot and a hash-bearing JSON receipt.

## Claim boundary and remaining gaps

This is a functional demonstration, not a quantitative model of the historical hardware. OSC1 is represented by behavioral square/triangle sources; the regulator error amplifier is a dominant-pole behavioral model; the pass transistor, zener, and switch use generic project-owned cards. The run therefore proves the assembled mathematical function and the calibration workflow, but not real-device stability margins, temperature behavior, tolerances, saturation recovery, noise, or agreement with a built chassis.

The earlier notation `I_SCALE` was ambiguous. This deck uses `S_VI = 100 V/A` explicitly: one simulated volt represents 10 mA. With droop gain `K_DROOP`, the leaky-twin drive resistor is therefore `R_DRIVE = R_LEAK * S_VI / K_DROOP`.
