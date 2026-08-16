# Week 9 proof values and fixture assumptions

Status: **selected provisional values for the Phase 3 proof; not historical reconstruction**  
Date: 2026-08-15  
Scope: numeric substitutions for Week 9 projection and ngspice harnesses. The canonical graph remains unchanged by this decision.

## Evidence labels

- **SOURCE** — stated or drawn in Roberge and preserved by the adjudicated Week 9 transcription.
- **INHERITED PROPOSAL** — already selected for the cumulative teaching chassis in the Weeks 0–4 specification.
- **DERIVED** — follows arithmetically from a source equation, source operating point, or an approved proposal.
- **PROPOSED** — an engineering fixture assumption needed for a deterministic proof; it is not historical evidence.

## Binding table

| Graph field / fixture quantity | Topology-tier value | Realistic first-pass proposal | Status |
|---|---:|---:|---|
| `W09.RIN` | 4.70 kΩ | 4.70 kΩ, 1% | **PROPOSED**, reusing the earlier Figure 3.1-compatible chassis inverter value |
| `W09.RFB` | 4.70 kΩ | 4.70 kΩ, 1%; preferably ratio-matched to `W09.RIN` | **PROPOSED**; equality is **SOURCE** |
| `W09.RALPHA`, alpha 1/2 | open; omit the element | open | **SOURCE** |
| `W09.RALPHA`, alpha 1/4 | 2.350 kΩ | 2.350 kΩ, 0.1% or a characterized ratio network | **DERIVED** from `R=R1/2` |
| signal-generator series impedance | 0 Ω | 50 Ω | **PROPOSED**; source gives none |
| output resistive load | 10 MΩ to `SGND` | 10 MΩ to `SGND` | **PROPOSED** 10x-scope input; no other functional load |
| output probe capacitance | 0 pF | 12 pF to `SGND` | **PROPOSED** generic 10x-probe starting value; replace by measured probe data |
| `MOD.INT1.RIN` | 10.0 kΩ | 10.0 kΩ, 1% | **INHERITED PROPOSAL** |
| `MOD.INT1.CFB` | 1.00 µF ideal C | 1.00 µF film, ≤5%, ≥35 V | **INHERITED PROPOSAL** |
| retained `AMP1.CC` | 47 pF | 47 pF C0G/NP0, socketed | **PROPOSED conservative end-state**; 47 pF is itself a **SOURCE** test value |
| rails | ideal +15 V / −15 V | ideal +15 V / −15 V for this proof | **SOURCE** values; infrastructure impedance remains a separate-sheet problem |
| temperature | 27 °C | 27 °C nominal, then declared corners | **PROPOSED** ngspice nominal |

Values in this table are projector substitutions, not changes to source evidence labels in `graph.json`.

## Why `R1 = 4.70 kΩ`

Figure 9.8 determines only that `W09.RIN = W09.RFB = R1`. The absolute value is absent. The proof adopts 4.70 kΩ for four explicit reasons:

1. The Weeks 0–4 specification already uses 4.7 kΩ for the source-compatible unity inverter experiment. Reusing it reduces the physical values inventory.
2. At the source's intended approximately ±10 V output, feedback-resistor current is

   `10 V / 4.70 kΩ = 2.13 mA`.

   This is well below the source's approximate 25–30 mA output-current limit while still giving the output stage a non-negligible test current.
3. A −20 mV small step produces an ideal input-resistor current magnitude

   `20 mV / 4.70 kΩ = 4.26 µA`.

   The topology baseline's default BJT beta is 100, so a 10 µA input-transistor collector current corresponds to roughly 0.10 µA base current before balance effects: about 2.35% of the test current. For the source's high-beta selected 2N5963 pair the ratio should be smaller, but that is model-conditional and is not asserted here.
4. A proposed 50 Ω physical generator impedance is `50/4700 = 1.06%` of R1. The topology tier uses zero source impedance so the source's exact alpha equation remains exact. Physical/realistic results record the small external-source perturbation rather than silently absorbing it into R1.

The source equation is

`alpha = (R1 || R) / (R1 + (R1 || R))`.

For alpha 1/4, `R = R1/2 = 2.350 kΩ`; then `R1 || R = R1/3`, and alpha is `(R1/3)/(4R1/3)=1/4`. Use the exact numeric value in SPICE. A physical 2.35 kΩ 0.1% part or characterized resistor network is preferable because ratio error directly changes alpha.

## Source-preserving Cc cases

No sweep value may be rounded to a preferred substitute:

| Case | Input | Alpha fixture | `AMP1.CC` | Status |
|---|---|---|---:|---|
| `CASE.W09.A47` | −20 mV step | `Ralpha=open`, alpha 1/2 | 47 pF | **SOURCE** |
| `CASE.W09.A33` | −20 mV step | `Ralpha=open`, alpha 1/2 | 33 pF | **SOURCE** |
| `CASE.W09.A10` | −20 mV step | `Ralpha=open`, alpha 1/2 | 10 pF | **SOURCE** |
| `CASE.W09.A05` | −20 mV step | `Ralpha=open`, alpha 1/2 | 5 pF | **SOURCE** |
| `CASE.W09.B20` | 20 Vpp square | `Ralpha=open`, alpha 1/2 | 20 pF | **SOURCE** |
| `CASE.W09.B10` | 20 Vpp square | `Ralpha=2.350 kΩ`, alpha 1/4 | 10 pF | **SOURCE/DERIVED** |

For a generic deterministic harness where the source gives no timing:

- **PROPOSED small-step waveform:** `PULSE(0 -20m 1u 100n 100n 400u 1m)`; simulate at least 1 ms and reduce the maximum step until every oscillation is resolved.
- **PROPOSED slew waveform:** `PULSE(-10 10 100u 100n 100n 500u 1m)`; simulate at least two periods. Its 20 Vpp amplitude is **SOURCE**; edge and period are fixture choices.
- **PROPOSED AC normalization:** 0 V DC, 1 V AC. The amplitude is only linear-analysis normalization.

The harness must override `AMP1.CC` per case. It must not represent an open alpha branch with a huge resistor while claiming graph identity; omit/open `W09.RALPHA` for alpha 1/2.

## Provisional retained Cc: 47 pF

The end-of-week integrator retains a socketed 47 pF C0G/NP0 capacitor between `AMP1.COMP_A` and `AMP1.COMP_B`.

This is **PROPOSED**, not the historical final value. It is selected because:

- 47 pF is the most conservative source-defined Figure 9.10 case and is described qualitatively as the slowest/closest-to-first-order response;
- the restored integrator's high-frequency noise gain approaches unity, a more demanding feedback condition than the Figure 9.8 unity inverter's noise gain of two;
- a stable, deliberately slow first bring-up is preferable to selecting the source's 20 pF worked example before the real amplifier, wiring, and probe capacitance are measured.

The capacitor must remain removable. Gate 2 records the 47/33/20/10/5 pF measured campaign, and Week 13 may replace the provisional value through its explicit compensation-design process. No simulation result from the topology-default transistor models can promote 47 pF from provisional to validated.

This supersedes the untested 20 pF end-state candidate in `drafts/spec-weeks-05-09.md`. The source's 20 pF worked example remains the default `W09.INVERTER_TEST` AC case; it is not used as evidence that an integrator with high-frequency noise gain approaching one is stable.

## Restored INT1 values

Restore the cumulative chassis proposal rather than inventing a Week 9 scale:

- `MOD.INT1.RIN = 10.0 kΩ`, 1%;
- `MOD.INT1.CFB = 1.00 µF` film, ≤5%, ≥35 V;
- `tau = RC = 10.0 ms` (**DERIVED**);
- ideal transfer `Vout/Vin = -1/(sRC) = -100/s` (**DERIVED**);
- integrator magnitude is unity at `1/(2*pi*RC) = 15.9 Hz` (**DERIVED**).

For a safe topology-tier transient, use a **PROPOSED** 100 mV input pulse and a declared zero initial output. The ideal ramp magnitude is `0.1 V / 10 ms = 10 V/s`, so a 20 ms pulse changes output by only 0.2 V and avoids confusing integrator action with the source's approximately ±10 V output limit.

A pure integrating-feedback capacitor is open at DC. The restored graph must not acquire an invisible bleed resistor merely to force `.op` convergence. Use:

- `W09.INVERTER_TEST` or a specific `W09.CC_SWEEP` case for the required closed-loop `.op` and `.ac` operating-point proof;
- the restored integrator with an explicit ground-referenced source at `MOD.INT1.INPUT`, declared capacitor/output initial state, and `.tran` for integration proof;
- restored-integrator `.ac` only after the declared input source is attached; do not describe its DC point as hold-drift evidence.

Week 11's later reset/operate/hold switch is not back-ported into Week 9 to solve a simulator convenience.

## Topology-tier analysis coverage

| Analysis | Configuration and numeric fixture | Claim boundary |
|---|---|---|
| `.op` | `W09.INVERTER_TEST`; source DC 0 V; RIN/RFB 4.70 kΩ; Ralpha open; Cc 20 pF; load 10 MΩ | Required finite bias point and KCL checks. Cc has no ideal DC effect. |
| `.ac` | same configuration; source AC 1 V; proposed `.ac dec 100 1 100Meg` | Harness bandwidth/phase data only; default zero intrinsic device capacitances prevent historical interpretation. |
| `.tran` small signal | `W09.CC_SWEEP`; A47/A33/A10/A05 with the exact table and proposed step timing above | Check source-defined qualitative ordering, not waveform identity. |
| `.tran` large signal | `W09.CC_SWEEP`; B20/B10 with exact amplitude/alpha/Cc and proposed timing above | Check boundedness and slew ordering; no absolute historical slew claim. |
| `.tran` restored | `W09.INT1_RESTORED`; 10 kΩ/1 µF, Cc 47 pF, explicit 100 mV fixture pulse and zero initial state | Verify sign and nominal 10 ms integration scale without adding a DC bleed. |

This matrix satisfies the Phase 3 need for `.op`, `.ac`, and `.tran` harness inputs collectively. It deliberately does not promise a meaningful standalone `.op` acceptance test for a pure restored integrator.

## Loading and probe contract

### Topology tier

- Signal source: ideal zero impedance.
- Output load: explicit 10 MΩ resistor representing the scope's resistive input.
- Output probe capacitance: zero.
- Do not probe `AMP1.N.HIGH_Z`, `AMP1.COMP_A`, or `AMP1.COMP_B` in the response campaign.
- All device capacitances remain whatever the admitted topology model declares; the current ngspice-default wrappers have zero junction capacitances and zero transit times, which is a major non-fidelity limitation.

The 10 MΩ load draws 1 µA at 10 V. The dominant Figure 9.8 large-signal fixture load remains the 4.70 kΩ feedback resistor, not the scope.

### Realistic first-pass proposal

- Generator: 50 Ω series impedance, measured and replaced in the receipt if the actual generator differs.
- Output instrument: 10 MΩ in parallel with 12 pF, replaced by the selected probe's datasheet/measured value.
- No external functional load during Figure 9.10/9.12 correlation. A limiter test uses a separately named load fixture.
- Critical internal nodes are not contacted by an ordinary passive probe. If they must be observed, create a separate active-probe configuration with its measured impedance.

## Parasitic budget

| Quantity | Topology tier | Realistic first-pass proposal | Meaning |
|---|---:|---:|---|
| `W09.CPAR_HIGHZ`, `AMP1.N.HIGH_Z` to ground | open / 0 pF | 1.0 pF | board/socket stray; **PROPOSED** |
| `W09.CPAR_COMPA`, `AMP1.COMP_A` to ground | open / 0 pF | 1.0 pF | board/socket stray; **PROPOSED** |
| `W09.CPAR_COMPB`, `AMP1.COMP_B` to ground | open / 0 pF | 1.0 pF | board/socket stray; **PROPOSED** |
| Cc socket/wiring, `COMP_A` to `COMP_B` | 0 pF beyond selected Cc | 1.0 pF parallel stray | **PROPOSED**; record as parasitic, not by changing the printed Cc value |
| output jack/probe to ground | 0 pF | 12 pF | **PROPOSED** instrument load |
| resistor parasitic C/L | zero | initially zero; add only from construction measurement/model | not usefully determined yet |
| integrating capacitor ESR/leakage/DA | zero | unselected pending actual 1 µF film part | do not invent a universal film-capacitor model |
| rail-source impedance | zero | zero in the Week 9 proof | deferred to the separate infrastructure sheet |

The three 1 pF internal values are sensitivity seeds, not historical estimates. The realistic campaign must repeat them at 0.5 pF and 2.0 pF individually and together. Because the source warns that sub-pF feedback can change the response, a conclusion that changes over this sweep is reported as parasitic-sensitive, not tuned to match a figure.

## Harness substitution set

The pipeline may consume the following named values without editing `graph.json`:

```text
W09_R1=4.70k
W09_RALPHA_HALF=OPEN
W09_RALPHA_QUARTER=2.350k
W09_RLOAD=10Meg
W09_SOURCE_R_IDEAL=0
W09_SOURCE_R_REALISTIC=50
W09_OUTPUT_C_IDEAL=0
W09_OUTPUT_C_REALISTIC=12p
W09_CPAR_HIGHZ_IDEAL=0
W09_CPAR_COMPA_IDEAL=0
W09_CPAR_COMPB_IDEAL=0
W09_CPAR_HIGHZ_REALISTIC=1p
W09_CPAR_COMPA_REALISTIC=1p
W09_CPAR_COMPB_REALISTIC=1p
INT1_RIN=10k
INT1_CFB=1u
W09_CC_RETAINED=47p
```

Case-specific Cc still comes from `AMP1.CC.parameters.cases`; `W09_CC_RETAINED` applies only to `W09.INT1_RESTORED`.

## What this decision does not establish

- It does not validate any historical transistor/JFET model or reproduce the source waveforms.
- It does not authorize a hidden DC-stabilizing resistor, probe, load, or parasitic.
- It does not select physical package pinouts, a PCB layout, or the separate power-infrastructure impedance.
- It does not claim the proposed 50 Ω, 10 MΩ/12 pF, or 1 pF parasitics match the user's instruments or construction.
- It does not replace the requirement to measure the real generator, probe, 1 µF capacitor, board, and completed amplifier before correlation.

## Local evidence

- `week09-source-map.md` — source cases, alpha equation, operating points, and explicit omissions.
- `week09-transcription-b.md` and `week09-transcription-diff.md` — independently checked fixture topology and unresolved numeric R1/load/parasitics.
- `../../drafts/spec-weeks-00-04.md` — inherited 4.7 kΩ inverter precedent and 10 kΩ/1.0 µF INT1 proposal.
- `week09-model-bindings.md` — topology-versus-realistic model claim boundary.
- `../../circuits/weeks/w09/graph.json` — canonical IDs and symbolic/deferred fields to which these substitutions bind.
