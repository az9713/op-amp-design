# Electrical verification contract

This directory contains executable ngspice checks and receipts originating with the Week 9 proof. The separate final combined-system campaign lives under `simulations/week13/`; its [complete report](../../docs/final-spice-simulation.html) records the pinned ngspice 47 executable, behavioral/generic models, results, and claim boundary.

## Preconditions

The harness must refuse a run unless all of the following are true:

- the generated deck names a canonical configuration and `MODEL_TIER`;
- every active device has a registry binding admitted for that tier;
- `W09.R1`, source resistance, load, probe capacitance, compensation capacitance, temperature, tolerances, and ngspice version are recorded;
- the netlist parser has checked instance terminal order against the canonical graph;
- no hidden DC bleed, stabilizing capacitor, initial condition, or convergence option has been added without appearing in the test-fixture receipt;
- the exact model files are hashed. External vendor content is not copied into public receipts.

Pinned ngspice 47 is available at `C:\Users\simon\scoop\apps\ngspice\47\bin\ngspice_con.exe`. On 2026-08-15, `smoke/w09-model-load.cir` loaded all four declarations in `circuits/models/w09-topology-baseline.lib`, completed `.op` with exit code 0, and returned one finite data row. Exact inputs, hashes, command, and selected voltages are recorded in `smoke/w09-model-load.receipt.json`. This is a syntax/binding smoke test, not a Week 9 circuit simulation or realistic-model validation. The campaign plan below remains unexecuted.

## Result classes

- **STRUCTURAL PASS:** projection, pin order, case parameters, and model bindings match the graph/registry.
- **IDEAL/TOPOLOGY PASS:** the generic `MODEL_TIER=ideal` deck converges and satisfies polarity/KCL invariants. It is not evidence of historical performance.
- **MODEL-CONDITIONAL PASS:** an admitted realistic tier meets a quantitative or relational check.
- **CHARACTERIZATION:** a reported measurement with no acceptance threshold.
- **UNSUPPORTED:** required model, fixture value, or parasitic is missing. Unsupported is not pass or fail.

Each assertion must carry one of those classes and a basis: `source`, `derived_from_source`, or `engineering_guardrail`.

## Required Week 9 campaigns

### 1. DC operating point — `W09.CC_SWEEP`

Run `.op` for every compensation case even though an ideal capacitor is open at DC. This catches accidental case-dependent wiring.

Hard assertions:

- convergence with finite node voltages/currents and no singular-matrix repair hidden by the harness;
- supplies are `P15=+15 V`, `N15=-15 V`, and `SGND=0 V`;
- Q1 and Q2 conduct in the intended direction; their emitter currents sum to the Q3 tail current within numerical KCL tolerance;
- Q6 and Q7 conduct the same high-impedance branch, and Q8/Q9 conduct the buffer branch, subject to the adjudicated graph;
- zero-input output is not rail-clamped in the resistively closed-loop fixture;
- all Cc cases have identical DC results within numerical tolerance;
- currents through the two 22 ohm output resistors are consistent with the limiter/output-stage KCL.

Source-target characterization (not a hard historical pass): Q1 and Q2 about 10 uA each, Q3 about 20 uA, Q6/Q7 about 50 uA, Q8/Q9 about 2 mA, output capability about plus/minus 10 V, and current limit about 25–30 mA. Because the source warns that transistor-model predictions can be wrong by a factor of two, any factor-of-two window derived from those values must be labeled `derived_from_source`, not quoted as a source tolerance.

Do not require a zero-input `.op` for the restored ideal integrator if its physical graph has no DC feedback path. Do not insert an invisible bleed resistor merely to make `.op` converge. Test that configuration by a declared transient initial state, or make a physical bleed path an explicit design change.

### 2. Closed-loop AC — `W09.CC_SWEEP`

Use the Figure 9.8 resistive fixture, with `AMP1.NONINV_IN=SGND`, equal `W09.RIN=W09.RFB=W09.R1`, and the shunt selected from alpha. An AC source amplitude of 1 V is a test normalization, not a physical component value.

Record:

- low-frequency complex gain and inversion;
- -3 dB bandwidth, peaking, and phase versus frequency;
- optional loop return ratio from a documented injection fixture that restores the exact DC operating point.

Assertions:

- the low-frequency closed-loop gain approaches -1 for both alpha settings;
- each case contains exactly one compensation capacitor between `AMP1.COMP_A` and `AMP1.COMP_B` with the requested value;
- for one admitted model set and identical declared parasitics, decreasing Cc produces the source's qualitative transition from slower/near-first-order toward underdamped/oscillatory behavior;
- no absolute phase-margin or unity-gain threshold is a source claim until a model/parasitic set is admitted and the analysis method is frozen.

The numeric value of `W09.R1` is still unresolved. AC results produced before it is selected may be used only for harness development, because input-current loading and device capacitances can make absolute resistance matter even when the ideal alpha equation does not.

### 3. Small-signal transient compensation sweep — `W09.CC_SWEEP`

Run the source-defined cases:

| Case | Input | alpha | Cc |
|---|---:|---:|---:|
| `CASE.W09.A47` | -20 mV step | 1/2 | 47 pF |
| `CASE.W09.A33` | -20 mV step | 1/2 | 33 pF |
| `CASE.W09.A10` | -20 mV step | 1/2 | 10 pF |
| `CASE.W09.A05` | -20 mV step | 1/2 | 5 pF |

Extract final value, 10–90% rise time, first-peak overshoot, peak count after the edge, and settling time using one declared band and observation window. Store raw vectors, not screenshots alone.

Relational assertions for an admitted realistic tier:

- the settled response has inverting sign;
- `A47` is slower and closer to first order than `A33`;
- `A10` is more underdamped than `A33`;
- `A05` has more persistent ringing than `A10`.

These are ordering checks, not waveform-identity checks. If a lawful model/parasitic set does not reproduce the order, report a model-conditional failure; do not tune hidden capacitance until the picture looks right.

### 4. Large-signal slew campaign

Run the source-defined 20 V peak-to-peak square-wave cases:

- `CASE.W09.B20`: alpha 1/2, Cc 20 pF;
- `CASE.W09.B10`: alpha 1/4 (`W09.RALPHA=W09.R1/2`), Cc 10 pF.

Extract positive and negative maximum sustained slope over a declared linear-fit window, clipping duration, recovery, and peak output current. Assert finite/bounded output and verify that the 10 pF case has the larger measured slew magnitude for the same admitted model/parasitic family. The source motivates inverse dependence on Cc; an exact 2:1 ratio is not asserted.

### 5. Limiter and robustness characterization

Use a separate, explicitly named test load; it is not part of the end-of-week circuit. Sweep load demand in both polarities and measure where Q12/Q13 divert drive. Compare the observed limit to the source's approximate 25–30 mA statement. Also run model/parasitic corners only after their provenance and ranges are recorded.

## Compensation-sweep controls

For all A/B comparisons, freeze every variable except the named `Cc` and alpha change. At minimum, pin:

- model-file hashes and model tier;
- temperature and tolerance/mismatch corner;
- `W09.R1`, generator impedance, output load;
- capacitance at `N_HIGH_Z`, `AMP1.COMP_A`, and `AMP1.COMP_B`;
- time step, integration method, tolerances, and initial-condition policy.

ngspice convergence options are part of the receipt. A result that appears only after changing `gmin`, source stepping, `reltol`, or integration method is a sensitivity result, not silently equivalent evidence.

## Required receipt fields

Every run emits machine-readable data containing:

- graph hash, deck hash, model hashes, generator version, and ngspice version;
- configuration ID, case ID, model tier, model binding IDs, and parameter table;
- command line, analysis directives, convergence diagnostics, assertions, and classifications;
- raw-output paths and deterministic plot-data paths;
- explicit `unsupported_reasons` and whether any result is source-observed, derived, or inferred.

Gate 2 must distinguish structural success from electrical fidelity. An ideal/topology-tier pass cannot authorize build-ready compensation values.
