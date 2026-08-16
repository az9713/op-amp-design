# Phase 1 draft specification — Weeks 5–9

Status: **DRAFT FOR GATE 0 REVIEW. No circuit, renderer, SVG, or SPICE implementation is authorized by this document.**

Scope owner: Weeks 5–9 only. This draft follows `preflight-decisions.html` and `implementation-plan.html` as binding. It reads the current `capstone.html` as the curriculum intent and `op_amps_roberge.pdf` as the primary electrical source.

## Evidence and naming contract

- **VERIFIED** — directly visible in the cited Roberge section/figure or stated in `capstone.html`.
- **DERIVED** — engineering interpretation proposed to make the cited material cumulative, build-ready, measurable, or simulatable. It must be reviewed and validated.
- **TBD** — the current sources do not determine the choice. No drawing may silently resolve it.
- Proposed stable IDs are semantic and must survive the schematic, value table, ideal netlist, realistic netlist, and later weekly states. Source figure designators are preserved inside `AMP1` where doing so improves traceability.
- `INFRA.VP15`, `INFRA.VN15`, and `INFRA.AGND` denote the permanent Week 0 rails and analog ground. Hidden IC power pins may resolve to these nets, but discrete power pins and all ordinary signal nets remain explicit.
- Physical front-panel cable routes remain deferred. Their **electrical nets are not deferred**.
- Inherited modules from the still-unmerged Weeks 0–4 specification are referenced provisionally as `CORE.INV1`, `CORE.SUM1`, `CORE.INT1`, and `CORE.INT2`. The integrator op-amps are `CORE.INT1.U_OP` and `CORE.INT2.U_OP`; they use the historical LM301A baseline. The integrator capacitors are `CORE.INT1.C_INT` and `CORE.INT2.C_INT`.
- `PROJECT_STATE(Wn) = PROJECT_STATE(Wn-1) + DELTA(Wn)`, except for explicitly identified removals/replacements. A module may be electrically inactive yet remain in the physical state.

## Cross-week findings that require Gate 0 decisions

1. **Week 5 is not build-specified by Figure 5.3.** Figure 5.3 is explicitly simplified and symbolic: amplifier `a0`, series transistor, emitter resistor `R`, load `RL || CL`, unregulated source, reference, and a disturbance-current source. Roberge assumes the transistor and op-amp add no relevant dynamics near crossover. A real ±15 V implementation needs voltage/current targets, pass-device polarity, safe operating area, dissipation, and a disturbance injector. All are TBD.
2. **Figures 5.11 and 5.13 are not two-integrator-loop schematics.** They are gain-of-ten amplifier examples. Applying their lead/lag ideas to the Week 4 computer loop is a DERIVED adaptation and must be a separate conditional configuration, not a claim that the figures directly depict the computer.
3. **A persistent Week 6 oscillator conflicts with “reuse an integrator.”** Reusing `CORE.INT1` prevents its Week 7 removal from leaving the oscillator intact; reusing `CORE.INT2` compromises the stock-IC comparator required later. The recommended cumulative interpretation is a dedicated oscillator integrator `OSC1.U_INT`. This is DERIVED and requires approval.
4. **Week 7’s input pair cannot function as an op-amp integrator.** A differential pair plus tail source has no low-impedance op-amp output and cannot close the existing feedback-capacitor loop. The Week 7 channel must be shown nonfunctional. Offset/drift can be measured on the pair; “hold-capacitor wander” cannot honestly be attributed to the unfinished amplifier without an explicit temporary diagnostic circuit.
5. **Weeks 8 and 9 do not form a self-evident topology chain.** Figures 8.8, 8.13, and 8.27 are separate instructional circuits. Their collage is not Figure 9.1. This draft preserves only components that can be mapped honestly into Figure 9.1 and labels other Week 8 parts temporary. A pin/net transition table is required before implementation.
6. **Week 9 compensation is operationally necessary despite the later Chapter 13 campaign.** Chapter 9 deliberately varies `Cc`, and Figure 9.1 exposes compensation terminals. The end-of-week circuit needs a documented provisional/default `Cc`; Chapter 13 later retunes it by application.

---

# Week 5 — physical regulator plant

## Cumulative end state

`PROJECT_STATE(W05)` contains the complete two-integrator computer inherited from Week 4 plus a physically installed regulator plant `REG1` on the same chassis. The two systems are not electrically connected except through `INFRA.VP15`, `INFRA.VN15`, and `INFRA.AGND`. The primary experiment emphasizes `REG1`; inherited computer circuitry remains complete but grey. Any lead/lag network used to quiet the Week 4 loop is a separately identified conditional configuration.

## Active experiment/configurations

1. **W05-A — regulator load sweep (required):** close the Figure 5.3 regulator loop, inject a small-signal loop probe, and compare `-L(jw)` as `REG1.R_LOAD` and `REG1.C_LOAD` change.
2. **W05-B — computer-loop lead (conditional):** if the inherited two-integrator loop rings, place a lead network in that loop only. This is an adaptation of Figure 5.11, not part of `REG1`.
3. **W05-C — computer-loop lag (conditional alternative):** place a lag network in the inherited computer loop only, adapting Figure 5.13. W05-B and W05-C are mutually exclusive experiment configurations unless a selector is explicitly designed.

## Inherited circuitry

- `CORE.INV1`, `CORE.SUM1`, `CORE.INT1`, `CORE.INT2`, their explicit computer-loop nets, and the Week 3 default LM301A compensation parts.
- Week 4’s second-order active-loop configuration and loop-injection/test points, subject to reconciliation with the Weeks 0–4 owner.
- Week 0 infrastructure by reference, including local rail decoupling.

## Explicit delta

- Add module `REG1` with a reference, error amplifier, high-side series pass stage, resistive/capacitive load, and disturbance-current injection port.
- Add named loop-injection break/test points without changing DC bias.
- Add a physical output jack/test point adjacent to—but electrically distinct from—the computer jacks.
- Optionally add one computer-loop compensation network as W05-B or W05-C; do not place it in the regulator loop.

## Primary-source evidence

- **VERIFIED:** `capstone.html` lines 292–296 specifies Figure 5.3, a reference, another IC error amplifier, series transistor, `R || C` load, Figure 5.4 Bode comparison, and optional Figures 5.11/5.13 on the computer loop only.
- **VERIFIED:** Roberge §5.2.2, Figure 5.3, PDF pp. 119–120 (LibreTexts page labels 5.2.3–5.2.4): simplified voltage regulator; the op-amp compares `VR` with output, drives a series transistor with emitter resistor `R`, and drives `RL || CL`; `Id` and `Vu` are disturbance inputs.
- **VERIFIED:** Figure 5.4, PDF p. 120: decreasing `RL` and increasing `CL` change the single-pole loop-transmission plot; the output-load pole is the intended dominant pole.
- **VERIFIED:** Figure 5.11, PDF p. 126: a gain-of-ten amplifier with a capacitor across the upper feedback resistor creates lead in the feedback path.
- **VERIFIED:** Figure 5.13, PDF pp. 127–128: a series `R1-C` network shunted between amplifier inputs produces lag while leaving the ideal closed-loop gain unchanged in that example.
- **UNCERTAINTY:** none of these pages provides a complete physical regulator BOM or maps the lead/lag networks into a two-integrator computer.

## Modules, components, and proposed stable IDs

| Stable ID | Function | Status |
|---|---|---|
| `REG1.V_REF_SRC` | reference source `VR` | TBD physical realization |
| `REG1.U_ERR` | error amplifier | LM301A historical baseline; VERIFIED curriculum intent |
| `REG1.Q_PASS` | series pass transistor | polarity/type/Thermal SOA TBD |
| `REG1.R_EMIT` | Figure 5.3 emitter/source degeneration resistor `R` | VERIFIED topology; value TBD |
| `REG1.V_UNREG_SRC` | unregulated input `Vu` or input jack | source range/current limit TBD |
| `REG1.R_LOAD` | selectable load resistance `RL` | VERIFIED topology |
| `REG1.C_LOAD` | selectable load capacitance `CL` | VERIFIED topology |
| `REG1.I_DIST_PORT` | load-current disturbance injection port | VERIFIED analytical role; physical injector TBD |
| `REG1.TP_LOOP_IN/OUT` | noninvasive loop-injection points | DERIVED practical addition |
| `CORE.COMP_LEAD1` | optional computer-loop lead network | DERIVED mapping from Fig. 5.11 |
| `CORE.COMP_LAG1` | optional computer-loop lag network | DERIVED mapping from Fig. 5.13 |

## Named nets and module boundary

- `REG1.VREF`, `REG1.VUNREG`, `REG1.ERR_OUT`, `REG1.PASS_IN`, `REG1.VOUT`, `REG1.IDIST`, `REG1.LOOP_SENSE`, `REG1.LOOP_RETURN`, plus infrastructure nets.
- External `REG1` pins: `VUNREG`, `VREF_MON`, `VOUT`, `IDIST_INJ`, `LOOP_INJ_P`, `LOOP_INJ_N`, `AGND`, `VP15`, `VN15`.
- `REG1.VOUT` must not share a canonical net with any `CORE.*` jack in W05.

## Symbolic parameters and recommended-value candidates

| Parameter | Meaning | Candidate/status |
|---|---|---|
| `V_U`, `V_R` | unregulated input and reference | **TBD**; select after pass topology and safe output range are fixed |
| `R_E` | pass-transistor emitter resistor | **TBD**; source only requires it be large relative to `1/gm` for the simplified model |
| `R_L` | load sweep | **PROPOSED starting set:** 470 ohm, 1 kohm, 2.2 kohm; not yet power- or loop-validated |
| `C_L` | dominant-pole sweep | **PROPOSED starting set:** 10 uF, 47 uF, 100 uF, voltage rating >= 25 V; ESR must be modeled |
| `a0` | ideal error-amplifier DC gain | **VERIFIED symbolic** in Figure 5.3; bind to an ideal parameter in the ideal model |
| lead `R,C` | computer-loop phase lead | **TBD** from measured Week 4 crossover; Figure 5.11 values cannot be copied blindly |
| lag `R1,C` | computer-loop gain reduction | **TBD** from measured Week 4 loop; use Figure 5.13 synthesis only after target crossover is known |

## Practical additions; power, test, and loading assumptions

- **DERIVED:** current-limit `V_UNREG_SRC`, fuse or resettable protection, reverse-discharge protection for `C_LOAD`, pass-device heatsink/thermal calculation, and a discharge/bleeder path are required before construction.
- **DERIVED:** measure loop transmission with an injection transformer or high-value injection network that preserves DC feedback. The exact method and source impedance are TBD.
- Scope/probe loading must be recorded at `REG1.VOUT` and loop test points. Use 10x probes as the minimum assumption; the model must include the declared load for correlation.
- `I_DIST_PORT` may be a current-pulse sink rather than an ideal current source. Its compliance, edge rate, and isolation are TBD.
- Local `0.1 uF` ceramic decoupling at `U_ERR` is inherited from Week 0; bulk rail decoupling belongs on the infrastructure sheet.

## Historical and modern notes

- Historical primary: LM301A error amplifier on ±15 V. A 741-class alternative may be documented but is not the baseline.
- Modern ±15 V substitute candidates may be noted only after input common-mode range, output swing, stability with capacitive load, and compensation behavior are checked.
- A low-voltage/rail-to-rail redesign remains the deferred second project; it must not alter this primary regulator.

## SPICE targets

- **Ideal:** same `REG1` graph with an ideal finite-gain amplifier model, idealized transistor model, and parameterized `RL`, `CL`, and disturbances. Run `.op`, loop-gain `.ac`, line-step, and load-current-step analyses.
- **Realistic:** same graph with selected LM301A macro-model, selected pass-transistor model, capacitor ESR/leakage, source resistance, disturbance-sink dynamics, and probe loads.
- Acceptance: component IDs/pins/nets match the schematic; DC regulation is plausible; the output-load pole trend agrees with Figure 5.4 in the regime where the simplifying assumptions hold; deviations from op-amp/pass-transistor dynamics are explained rather than hidden.

## Expected measurements

- `VOUT` settles near `VREF` within the implemented loop’s offset/headroom limits.
- Measured output pole begins near `1/(RL*CL)`; this is an approximation because capacitor ESR, pass-device output resistance, and external loading remain.
- Increasing `CL` lowers the output pole; decreasing `RL` changes both pole and low-frequency loop magnitude as Figure 5.4 indicates.
- Record phase margin, gain margin, crossover, DC load regulation, and load-step recovery for every `RL/CL` combination.

## Sheet/detail recommendation

- One large cumulative W05 sheet: inherited computer grey, `REG1` active, additions coral.
- One pin-for-pin `REG1` detail sheet once the physical pass stage is resolved.
- Separate W05-B and W05-C configuration details if either is built; never overlay both networks as if simultaneous.

## Incomplete-state handling and open issues

- Until `REG1.Q_PASS`, `V_U`, and protection are selected, the regulator is a specification, not a safe build.
- **W05-OPEN-01:** choose output voltage/current and unregulated source.
- **W05-OPEN-02:** choose pass-device polarity/type, resistor, SOA, thermal protection, and load-discharge path.
- **W05-OPEN-03:** define a loop-injection method compatible with the actual circuit.
- **W05-OPEN-04:** decide whether conditional computer lead or lag hardware becomes persistent, switchable, or is removed after measurement.

---

# Week 6 — persistent Schmitt–integrator test oscillator

## Cumulative end state

`PROJECT_STATE(W06)` contains the complete W05 computer and regulator plus a persistent square/triangle generator `OSC1`. `OSC1` is a dedicated module in this draft so Week 7 can remove `CORE.INT1.U_OP` without destroying the test source and so `CORE.INT2` remains a stock-LM301A comparison channel.

## Active experiment/configuration

- **W06-A — free-running function generator:** `OSC1` closes the triangle output into a Schmitt trigger and the square output into an inverting integrator. Both `OSC1.SQUARE` and `OSC1.TRIANGLE` are explicit nets and test outputs.
- Optional modulation input `OSC1.VC` from Figure 12.8 is exposed but grounded for the required symmetric experiment. Duty-cycle modulation is out of scope for this week unless explicitly enabled as a separate configuration.

## Inherited circuitry

- All W05 physical state, including `REG1` and any explicitly retained computer-loop compensation network.
- The analog-computer modules remain installed and electrically unchanged; they are grey unless they supply a declared test load.

## Explicit delta

- Add `OSC1.U_SCHMITT`, `OSC1.U_INT`, hysteresis network, integrator `R/C`, a defined output-limiting method, output test points, and a start-up condition.
- Add `OSC1.VC` as a real canonical net tied to `AGND` in W06-A; do not omit it from the netlist if it is shown.
- Recommended state decision: use a dedicated LM301A integrator rather than reusing `CORE.INT1` or `CORE.INT2`.

## Primary-source evidence

- **VERIFIED:** `capstone.html` lines 305–309 requires Figure 6.14/Figure 12.8, a Schmitt trigger (Figure 12.7), square/triangle outputs, and a persistent test source; it says an existing integrator “can be reused.”
- **VERIFIED:** Figure 6.14, PDF p. 165 (LibreTexts 6.3.11), depicts the abstract loop `Schmitt -> 1/s -> Schmitt`; both outputs are 2 V peak-to-peak, the period is 4 s, and their zero crossings are displaced by 1 s.
- **VERIFIED:** Figure 12.7 and §12.2.1, PDF p. 337, give the positive-feedback Schmitt circuit and thresholds `+/- (R1/R2) VM`. The text discusses three limiting choices: natural amplifier saturation, diode clamps on LM101A compensation terminals, or a precision limiter.
- **VERIFIED:** Figure 12.8 and §12.2.1, PDF p. 338, state the oscillator period is `tau = 4RC` for the illustrated symmetric case and frequency is `1/(4RC)`; `VC` changes duty cycle.
- **UNCERTAINTY:** the capstone does not resolve which installed integrator is reused or how the persistent oscillator survives Week 7.

## Modules, components, and proposed stable IDs

| Stable ID | Function | Status |
|---|---|---|
| `OSC1.U_SCHMITT` | positive-feedback comparator/LM301A | historical LM301A proposed |
| `OSC1.R_HYS_IN` | Figure 12.7 `R1` | VERIFIED topology |
| `OSC1.R_HYS_FB` | Figure 12.7 `R2` | VERIFIED topology |
| `OSC1.LIMIT1` | defines `+/-VM` | TBD implementation |
| `OSC1.U_INT` | dedicated inverting integrator | DERIVED persistence decision |
| `OSC1.R_INT` | square-to-integrator input resistor | VERIFIED topology |
| `OSC1.C_INT` | integrator feedback capacitor | VERIFIED topology |
| `OSC1.R_BLEED` | optional very-large DC/startup bias path | TBD; practical addition only if needed |
| `OSC1.TP_SQ`, `OSC1.TP_TRI` | square/triangle test points | DERIVED practical addition |

## Named nets and module boundary

- `OSC1.SCHMITT_IN`, `OSC1.SQUARE`, `OSC1.INT_SUM`, `OSC1.TRIANGLE`, `OSC1.VC`, `OSC1.VM_POS`, `OSC1.VM_NEG`, infrastructure nets.
- External pins: `SQUARE`, `TRIANGLE`, `VC`, `SYNC/START` only if realized, `AGND`, `VP15`, `VN15`.
- Required connectivity: `TRIANGLE -> Schmitt input`; Schmitt positive feedback returns from `SQUARE`; `SQUARE -> R_INT -> INT_SUM`; `C_INT` returns from `TRIANGLE` to `INT_SUM`; integrator noninverting input is `AGND`.

## Symbolic parameters and recommended-value candidates

| Parameter | Meaning | Candidate/status |
|---|---|---|
| `R1/R2` | threshold ratio | **VERIFIED symbolic**; `V_TRI,pk = (R1/R2) VM` |
| `R_INT*C_INT` | integration time constant | **VERIFIED relation:** `T = 4 R_INT C_INT` for the Figure 12.8 symmetric case |
| `R1`, `R2` | hysteresis resistors | **DERIVED candidate:** 100 kohm/100 kohm only if `VM` is also the desired triangle peak |
| `R_INT`, `C_INT` | oscillator timing | **DERIVED slow-demo candidate:** 100 kohm, 10 uF gives about 4 s; leakage/ESR make this unsuitable as a precision reference |
| `VM` | Schmitt limited output | **TBD:** natural LM301A saturation is simplest but is supply-, load-, and model-dependent |

## Practical additions; power, test, and loading assumptions

- If reproducible amplitude is required, choose an explicit limiter. Natural saturation preserves the simplest historical circuit but cannot be treated as a precise value.
- Use a comparator only as a documented modern alternative; the primary path remains LM301A on ±15 V.
- A symmetric ideal simulation may remain at zero forever. Use a declared capacitor initial condition or a physical-scale asymmetry; this is a simulation/test condition, not a hidden SVG-only component.
- Record output loading. A 10x probe is assumed; any front-panel termination or later driven load must be in both graph and netlist.
- Electrolytic `C_INT` makes polarity, leakage, dielectric absorption, and tolerance visible; a film-capacitor decade option is preferable for quantitative comparison.

## Historical and modern notes

- Historical primary: two LM301A-class amplifiers, ±15 V, with their required default compensation.
- Modern note: a real comparator improves Schmitt switching speed but materially changes saturation/recovery behavior; it is an alternative, not a silent substitute.
- Low-voltage rail-to-rail redesign remains deferred as a second project.

## SPICE targets

- **Ideal:** identical `OSC1` graph using ideal high-gain limited amplifier primitives and an ideal integrator amplifier model; transient analysis with a declared initial condition. Verify threshold crossings, polarity, amplitude relationship, and `T = 4RC`.
- **Realistic:** same graph with LM301A macro-models, chosen limiter, saturation/recovery, slew rate, input bias currents, capacitor leakage/ESR, and probe loads.
- Sweep `R_INT`, `C_INT`, `R1/R2`, and `VC`; record startup time and failure-to-start cases.

## Expected measurements

- Complementary square and triangle outputs; triangle reverses slope at the Schmitt thresholds.
- Symmetric case: period near `4 R_INT C_INT`; amplitude near the selected threshold ratio times the measured square limit.
- Figure 6.14 reference behavior is 2 Vpp at both outputs with a 4 s period. Reproducing both amplitudes requires a defined limiter and ratio, not LM301A saturation alone.
- Measure frequency, square/triangle peak values, duty cycle, zero-crossing displacement, and startup transient.

## Sheet/detail recommendation

- One large cumulative sheet with `OSC1` active and prior modules grey.
- One pin-for-pin `OSC1` detail sheet showing limiter, hidden LM301A power-pin references, and every feedback junction.

## Incomplete-state handling and open issues

- **W06-OPEN-01 (approval required):** accept the dedicated `OSC1.U_INT` as the cumulative interpretation instead of reusing a computer integrator.
- **W06-OPEN-02:** choose amplitude limiter and target output amplitudes.
- **W06-OPEN-03:** reconcile the Figure 6.14 2 Vpp/4 s target with the Figure 12.8 practical ±10 V-style example.
- **W06-OPEN-04:** decide whether `VC` is a grounded exposed jack or omitted from the physical module. If omitted physically, it must also be absent from the canonical graph.

---

# Week 7 — intentionally incomplete INT1 discrete input stage

## Cumulative end state

`PROJECT_STATE(W07)` retains all W06 hardware. `CORE.INT1.U_OP` is physically removed from its socket and retained off-circuit as an artifact. The empty socket and its pins remain visible. A discrete matched input pair and transistor tail-current source are installed at the INT1 location, but the channel has no complete gain/output path and is explicitly **NONFUNCTIONAL AS AN INTEGRATOR**. `CORE.INT2` and the dedicated `OSC1` remain operational.

## Active experiment/configurations

1. **W07-A — input-stage balance/offset/drift:** measure the differential pair through an explicit temporary collector-load/trim network adapted from Figures 7.4 and 7.10.
2. **W07-B — honest INT1 hold-state observation:** isolate INT1 input as the existing hold mode requires and observe `CORE.INT1.C_INT` only through a declared high-impedance instrument. This measurement primarily captures capacitor, switch, board, and probe leakage because the unfinished pair cannot close the integrator loop.

W07-A’s temporary diagnostic network must either be shown on a separate configuration sheet or be present in the cumulative graph as installed removable hardware. It may not disappear between SVG and SPICE.

## Inherited circuitry

- W06 computer, regulator, and persistent oscillator.
- `CORE.INT1` socket, feedback capacitor, input resistor/switching hardware, and jacks remain physically installed.
- `CORE.INT1.U_OP` is removed; this is an explicit state transition, not visual suppression.

## Explicit delta

- Remove electrical instance `CORE.INT1.U_OP` while retaining `CORE.INT1.SOCKET` and annotating “LM301A removed.”
- Add `AMP1.Q1`/`AMP1.Q2` matched NPN differential pair and `AMP1.Q3` NPN tail-current source at the future Figure 9.1 amplifier location.
- Add the current-source bias components needed to establish about 20 uA total tail current if the Figure 9.1 path is approved.
- Add temporary, explicitly removable collector loads and equal-`VBE` balance trim for W07-A.
- Leave `AMP1.OUT` absent/unconnected. Do not connect the existing feedback capacitor to a fictitious output.

## Primary-source evidence

- **VERIFIED:** `capstone.html` lines 312–316 requires pulling the INT1 IC, building only the Figure 7.4 input pair with a transistor current source, balancing with equal `VBE` per Figure 7.10, measuring input-referred offset/drift, and observing the hold capacitor.
- **VERIFIED:** §7.2 and Figure 7.1, PDF p. 177, define input-referred drift as the input change required to return output to zero after an external variable changes.
- **VERIFIED:** §7.3.1 and Figure 7.4, PDF pp. 180–181, show the NPN differential pair, two collector loads, common emitter resistance, differential/single-ended outputs, and two input bases.
- **VERIFIED:** Figure 7.10 and discussion, PDF p. 186, show equal-base-voltage balancing with a potentiometer between the collector-load branches; bases are shorted and the pot is adjusted for zero differential output. Roberge says this is a final trim after careful matching, not a substitute for matching.
- **VERIFIED:** Figure 9.1 and §9.1.2, PDF pp. 239–240, use matched 2N5963 devices as `Q1/Q2`, operated near 10 uA each from `Q3`’s 20 uA current source.
- **CONTRADICTION:** no cited source supports a complete op-amp or integrator made from only this input stage.

## Modules, components, and proposed stable IDs

| Stable ID | Function | Status |
|---|---|---|
| `CORE.INT1.SOCKET` | retained LM301A socket footprint/pins | retained, annotated empty |
| `AMP1.Q1`, `AMP1.Q2` | matched NPN input pair | 2N5963 historical Figure 9.1 choice |
| `AMP1.Q3` | NPN tail current source | 2N3707 historical Figure 9.1 choice |
| `AMP1.BIAS_NEG.*` | shared negative-rail bias network begun for Q3 | exact component boundary must follow Figure 9.1 |
| `AMP1.W07_RCL1`, `AMP1.W07_RCL2` | temporary collector loads | DERIVED diagnostic parts |
| `AMP1.W07_RBAL` | equal-`VBE` balance pot | Figure 7.10 method; value TBD |
| `AMP1.W07_BUF` | optional high-impedance differential measurement buffer | TBD temporary fixture, not part of AMP1 signal path |

## Named nets and module boundary

- Permanent emerging amplifier nets: `AMP1.INV_IN`, `AMP1.NONINV_IN`, `AMP1.TAIL`, `AMP1.Q1_COL`, `AMP1.Q2_COL`, `AMP1.BIAS_NEG`, infrastructure nets.
- Temporary W07 diagnostic nets: `AMP1.W07_DIFF_P`, `AMP1.W07_DIFF_N`, `AMP1.W07_BAL_WIPER`, `AMP1.W07_MEAS_OUT` if a buffer is used.
- INT1 retained nets: `CORE.INT1.SUM`, `CORE.INT1.CAP_RETURN`, `CORE.INT1.OUT_JACK`. `CAP_RETURN` has no valid discrete amplifier output connection in W07 and must be shown open/safed.
- Proposed future `AMP1` external pins are `INV_IN`, `NONINV_IN`, `OUT`, `COMP_A`, `COMP_B`, `VP15`, `VN15`, `AGND`; in W07, `OUT`, `COMP_A`, and `COMP_B` do not yet exist electrically.

## Symbolic parameters and recommended-value candidates

| Parameter | Meaning | Candidate/status |
|---|---|---|
| `I_TAIL` | pair tail current | **VERIFIED Figure 9.1 target:** 20 uA total, about 10 uA per side |
| `Q1/Q2` | matched input pair | **VERIFIED historical:** 2N5963 selected within 3 mV `VBE` and 10% beta at operating current; availability TBD |
| `Q3` | tail source | **VERIFIED historical:** 2N3707 |
| `RCL1`, `RCL2`, `RBAL` | Week 7 temporary loads/trim | **TBD:** derive from target collector voltage and Figure 7.10 measurement range |
| thermal coupling | Q1/Q2 bond | **VERIFIED source recommendation:** close thermal proximity; winding wire or drilled aluminum block are examples |
| `C_INT1` | retained integrator capacitor | inherited value; do not claim pair-induced drift without a complete output path |

## Practical additions; power, test, and loading assumptions

- Use current-limited ±15 V rails for first power-up. Add base/emitter protection only if it does not corrupt the intended input behavior; any addition must be called out.
- A differential instrumentation amplifier or two-channel scope subtraction may measure collector imbalance. Its input bias and common-mode range must be specified.
- Offset/drift measurement requires a temperature stimulus, settling protocol, and zeroing definition consistent with Figure 7.1. Record temperature at the matched pair, not only ambient.
- The empty INT1 socket and feedback capacitor need a safe-state rule so no node can drive a rail or exceed capacitor rating.

## Historical and modern notes

- Primary: source-specified 2N5963 matched pair and 2N3707 current source on ±15 V.
- Modern candidates (for later validation): a currently obtainable matched dual NPN plus a modern low-leakage current-source transistor. Substitution affects beta, capacitance, `VBE` matching, noise, and drift and therefore needs a separate realistic model binding.
- Do not substitute an integrated op-amp or monolithic instrumentation amplifier for the unfinished stage.

## SPICE targets

- **Ideal:** identical W07 graph with matched idealized BJT models; `.op` and temperature/DC sweeps for pair balance. No functional-integrator acceptance test.
- **Realistic:** same graph with selected Q1/Q2 mismatch corners, beta mismatch, Early effect, source mismatch, resistor tempcos, capacitor leakage, and measurement loading.
- Acceptance is faithful topology and expected non-operation: `AMP1.OUT` absent, INT1 loop open, no fabricated feedback path. Simulations should demonstrate sensitivity of collector balance and input-referred offset, not pretend closed-loop integration.

## Expected measurements

- Tail current near 20 uA and collector currents near 10 uA each after balance, subject to actual transistor/model choices.
- Record input voltage required to restore differential output to zero versus temperature and time.
- INT1 hold capacitor may wander, but the report must separate capacitor/switch/probe leakage from any unfinished-pair contribution. A causal claim about amplifier input bias requires a defined complete current path.

## Sheet/detail recommendation

- One large cumulative sheet with all prior modules grey, INT1 socket/removal and new pair coral.
- One pin-for-pin W07 INT1 detail showing the open socket pins, retained `C_INT1`, explicit open `CAP_RETURN`, discrete pair/current source, and diagnostic configuration.
- If `W07_BUF` is used, show it as a temporary measurement fixture on its own detail and include it in the matching netlist configuration.

## Incomplete-state handling and open issues

- Prominent state label: **INT1 INCOMPLETE — NO AMPLIFIER OUTPUT — DO NOT RUN COMPUTER LOOP.**
- **W07-OPEN-01:** approve using Figure 9.1 Q1/Q2/Q3 values/types now, rather than an unrelated generic Figure 7.4 pair.
- **W07-OPEN-02:** specify the temporary Figure 7.10 collector-load/trim network and whether it is removed in Week 8 or retained as test hardware.
- **W07-OPEN-03:** rewrite or constrain the “hold capacitor wander” acceptance claim so it remains electrically honest.
- **W07-OPEN-04:** define safe treatment of the disconnected feedback-capacitor terminal and output jack.

---

# Week 8 — completed but transitional discrete two-stage channel

## Cumulative end state

`PROJECT_STATE(W08)` retains W07 hardware and adds enough circuitry behind the matched pair to create a complete discrete feedback amplifier at the INT1 socket. It contains a high-gain second stage, an active current-source load, a complementary output stage, an output node connected to the retained INT1 feedback capacitor, and explicit provisional stabilization. It is a **transitional implementation**, not yet silently equated with Figure 9.1.

## Active experiment/configurations

1. **W08-A — open-loop characterization:** measure DC operating points and estimate/open-loop gain using a controlled servo or tiny differential stimulus; observe output-stage crossover distortion at low-frequency drive.
2. **W08-B — closed INT1 integrator:** after safe stability verification, connect `AMP1.OUT` to the retained INT1 output/capacitor node and operate the channel as an integrator.

The phrase “measure open-loop gain” must not mean simply driving the uncompensated high-gain amplifier open-loop with ordinary bench voltages; a null/servo method is required.

## Inherited circuitry

- All W07 hardware and state, including `AMP1.Q1/Q2/Q3` and the empty LM301A socket.
- Any W07 temporary collector-load/balance parts are removed only if the W08 topology replaces them; the removal is an explicit delta.
- Computer/regulator/oscillator remain installed. `CORE.INT2` stays stock LM301A.

## Explicit delta

- Add a second voltage-gain stage derived from Figure 8.8.
- Replace its passive collector load with a current-source load derived from Figure 8.13.
- Add a complementary emitter-follower output stage derived from Figure 8.27, including bias diodes, 4.7 kohm bias resistors, and 22 ohm emitter/output resistors where the final design preserves that topology.
- Add a defined provisional stabilization/compensation element before closing the INT1 loop.
- Connect `AMP1.INV_IN`, `AMP1.NONINV_IN`, and `AMP1.OUT` pin-for-pin to the retained INT1 socket/interface.

## Primary-source evidence

- **VERIFIED:** `capstone.html` lines 319–323 asks for the Figure 8.8 second stage, Figure 8.13 current-source load, Figure 8.27 complementary output, feedback-capacitor acceptance, open-loop gain/crossover-distortion measurements, and an otherwise minimally compensated state.
- **VERIFIED:** Figure 8.8, PDF p. 215, shows a basic two-stage amplifier: `Q1/Q2` differential pair, a second transistor stage, and a unity-gain output buffer. The text states the topology can be stable in direct feedback due to dominant energy storage around the high-gain stage.
- **VERIFIED:** Figure 8.13, PDF pp. 220–221, is a generic current-source-loaded common-emitter stage and explains its high gain.
- **VERIFIED:** Figure 8.27, PDF p. 231, is a resistively biased complementary emitter follower on ±15 V with 4.7 kohm bias feeds, four diodes, and 22 ohm output/emitter resistors.
- **UNCERTAINTY:** Roberge does not present these three figures as one complete circuit. Their bias levels, polarities, interfaces, and stability cannot be obtained by concatenating the drawings.

## Modules, components, and proposed stable IDs

Permanent IDs should be assigned only where a part maps pin-for-pin into Figure 9.1:

| Stable ID | Function | Week 9 mapping/status |
|---|---|---|
| `AMP1.Q1/Q2/Q3` | inherited input pair/tail source | maps to Figure 9.1 |
| `AMP1.Q6` | high-gain/cascode-stage transistor candidate | final role must be verified against Figure 9.1 |
| `AMP1.Q7` | second-stage current source candidate | maps to Figure 9.1 if exact bias network used |
| `AMP1.Q10/Q11` | NPN/PNP output followers | Figure 9.1 uses 2N2219/2N2905 |
| `AMP1.R_OUT_P/N` | 22 ohm output resistors | Figure 9.1-compatible |
| `AMP1.W08_BIAS.*` | Figure 8.27 diode/resistor bias parts | temporary unless exact Figure 9.1 mapping is proven |
| `AMP1.W08_CSAFE` | provisional safety compensation | value/location TBD; may become `AMP1.CC` |

## Named nets and module boundaries

- `AMP1.INV_IN`, `AMP1.NONINV_IN`, `AMP1.TAIL`, `AMP1.STAGE1_OUT`, `AMP1.HIGH_GAIN`, `AMP1.BUFFER_DRIVE`, `AMP1.OUT_BIAS_P`, `AMP1.OUT_BIAS_N`, `AMP1.OUT`, `AMP1.COMP_A`, `AMP1.COMP_B`, infrastructure nets.
- `AMP1.OUT` must resolve to both `CORE.INT1.CAP_RETURN` and `CORE.INT1.OUT_JACK` in W08-B; the schematic and netlist must show the same junction.
- Any temporary Week 8 nodes use the `AMP1.W08_*` prefix so the Week 9 delta can mechanically report their removal.

## Symbolic parameters and recommended-value candidates

| Parameter | Meaning | Candidate/status |
|---|---|---|
| input currents | Q1/Q2 quiescent current | inherit Figure 9.1 target about 10 uA each if W07 choice approved |
| `I_STAGE2` | second-stage/source-load current | **TBD:** Figure 8.13 is generic; Figure 9.1 labels about 50 uA in its cascode branch |
| `Q10/Q11` | output pair | **VERIFIED Figure 9.1 historical candidates:** 2N2219/2N2905 |
| `R_OUT_P/N` | current-sharing/output resistance | **VERIFIED source candidate:** 22 ohm each in Figures 8.27 and 9.1 |
| output bias | crossover/distortion compromise | **TBD:** must be set from actual diode/transistor thermal tracking |
| `C_SAFE` | provisional stability capacitor | **TBD:** begin conservatively only after loop model; do not copy a Week 9 test value without topology equivalence |

## Practical additions; power, test, and loading assumptions

- Add current-limited rail bring-up, emitter/current test resistors as needed, and staged power-up checkpoints. All electrically retained parts require IDs.
- Thermal coupling between bias diodes and output devices may be needed; Figure 8.27 does not supply a construction layout.
- Output current limiting is absent from Figure 8.27. Until Week 9’s limiting circuitry exists, use a bench current limit and prohibit short-circuit tests.
- Open-loop gain measurement requires an output-centering servo or closed-loop extraction technique. Define the fixture, injection amplitude, and instrument loading.
- Do not close the feedback capacitor until DC output centering and provisional stability have passed.

## Historical and modern notes

- Historical candidate set should converge on Figure 9.1 types where available: 2N5963, 2N3707, 2N4250, TIS58, 2N2219, 2N2905.
- Modern substitutes must be separately model-bound and checked for polarity, breakdown, capacitance, beta, FET pinch-off/current, and thermal behavior.
- A modern monolithic op-amp would defeat the Week 8 teaching goal and is not an alternative implementation of this stage.

## SPICE targets

- **Ideal:** identical transistor graph with simplified matched BJT/FET models; `.op`, differential DC transfer, open-loop `.ac` under a valid bias/servo fixture, and low-frequency output crossover transient.
- **Realistic:** same graph with available device models, mismatch/corners, junction capacitances, output loading, thermal-sensitive bias approximations, and provisional compensation.
- Acceptance: valid quiescent operating point; output centered with stated trim; no destructive currents; predictable sign from differential input to output; stable W08-B integrator for the declared load; visible crossover distortion before/after bias adjustment.

## Expected measurements

- Record every transistor’s quiescent `VBE/VCE` and current before closing the loop.
- Measure low-frequency open-loop gain only with a defined extraction method; compare order of magnitude, not false precision.
- Observe crossover notch in the output stage at low bias and its reduction after bias adjustment.
- After closing INT1, verify correct integrator polarity and time constant and record overshoot/ringing under the provisional compensation.

## Sheet/detail recommendation

- One cumulative main sheet with `AMP1` active and earlier subsystems grey.
- One full pin-for-pin W08 `AMP1` detail; a block labeled “second stage” is insufficient unless expanded on the same package.
- One measurement-fixture detail for open-loop/servo testing and crossover-distortion drive.

## Incomplete-state handling and open issues

- W08 is functional but transitional. It must be labeled “not yet Figure 9.1” until the transition table is approved.
- **W08-OPEN-01 (critical):** define the coherent single circuit produced from Figures 8.8, 8.13, and 8.27.
- **W08-OPEN-02:** define the exact W08-to-W09 preservation/removal map.
- **W08-OPEN-03:** choose provisional stabilization and a safe closed-loop bring-up procedure.
- **W08-OPEN-04:** specify output bias/thermal strategy and pre-Week-9 current protection.

---

# Week 9 — Figure 9.1 illustrative amplifier and vertical proof

## Cumulative end state

`PROJECT_STATE(W09)` retains the complete W08 chassis and converts `AMP1` into the full Figure 9.1 discrete-component operational amplifier at the INT1 interface. Temporary W07/W08 parts not present in Figure 9.1 are explicitly removed. `AMP1` operates from ±15 V, has exposed compensation terminals, drives `CORE.INT1.C_INT`, and leaves `CORE.INT2` as the stock LM301A comparison channel. A documented provisional `Cc` remains installed at end of week.

This week is the required vertical proof for the future implementation pipeline: one canonical graph must produce/validate the cumulative schematic, pin-for-pin amplifier detail, recommended-values table, ideal netlist, realistic netlist, and connectivity-equivalence receipt.

## Active experiment/configurations

1. **W09-A — Figure 9.8 inverter / small-signal step campaign:** equal input and feedback resistors `R1`; optional shunt `R` controls attenuation `alpha`; sweep `Cc = 47, 33, 10, 5 pF` at `R = infinity` (`alpha = 1/2`) as Figure 9.10.
2. **W09-B — Figure 9.8 inverter / slew campaign:** 20 Vpp square input; compare `(alpha=1/2, Cc=20 pF)` and `(alpha=1/4, Cc=10 pF)` as Figure 9.12.
3. **W09-C — restored INT1 integrator:** remove the temporary inverter resistive configuration, reconnect the inherited `R_INT1/C_INT1`, repeat the Week 2 `xdot = -x` response, and compare hold behavior against the recorded former-INT1 baseline and/or the still-installed stock `CORE.INT2`.

These are separate matched schematic/netlist configurations over the same physical state. Do not overlay `R1` inverter feedback and `C_INT1` integration feedback as one circuit.

## Inherited circuitry

- All W08 physical modules and infrastructure.
- `AMP1.Q1/Q2/Q3` and any W08 devices that map exactly to Figure 9.1 retain IDs.
- `CORE.INT1.SOCKET`, `C_INT1`, input network, and jacks remain; the removed LM301A remains off-circuit.
- `CORE.INT2`, `OSC1`, `REG1`, and other computer modules remain installed.

## Explicit delta

- Complete/replace the transitional amplifier so the resulting graph matches Figure 9.1: differential input pair; current-source network; drift-reducing differential/cascode structures; current-source-loaded high-gain cascode; FET source follower; complementary output pair; biasing; output current limit; compensation terminals; source-specified decoupling.
- Remove every `AMP1.W07_*`/`AMP1.W08_*` temporary component not present in the approved Figure 9.1 implementation.
- Add configuration-specific Figure 9.8 resistors and test source for W09-A/B, then return to INT1 integration feedback for W09-C.
- Select and record the provisional end-state `AMP1.CC` after the Chapter 9 campaign.

## Primary-source evidence

- **VERIFIED:** `capstone.html` lines 326–330 requires Figure 9.1 in the INT1 socket, temporary Figure 9.8 inverter tests, Figure 9.10 `Cc` steps, Figure 9.12 slew, restoration of the integrator, and comparison with the pulled IC.
- **VERIFIED:** Figure 9.1 and §9.1.1, PDF p. 239: full discrete amplifier on ±15 V, designed for about ±10 V maximum output, with rail bypassing, compensation terminals, `Q1/Q2` input pair, `Q5/Q6` cascode, `Q8` FET buffer, and `Q10/Q11` complementary output.
- **VERIFIED:** §9.1.2, PDF pp. 240–241: Q1/Q2 each operate near 10 uA from Q3’s 20 uA source; 2N5963 pair selection/matching and thermal proximity are described; Q4/Q5 improve DC performance; output limiting and overload recovery are discussed.
- **VERIFIED:** §9.2.3, PDF pp. 247–249: the compensation network connects between the marked terminals and closes a minor loop around the high-gain stage; 20 pF compensation gives useful direct-feedback phase margin in the example; stray capacitance matters even near 1 pF.
- **VERIFIED:** Figure 9.8, PDF p. 253: equal `R1` input/feedback resistors produce ideal gain -1; shunt `R` changes `alpha`; `Cc` connects at the compensation terminals.
- **VERIFIED:** Figure 9.10, PDF p. 254: `-20 mV` input step, `R=infinity`, and `Cc` values 47, 33, 10, 5 pF; smaller `Cc` is faster and less stable, with 5 pF highly oscillatory.
- **VERIFIED:** Figure 9.12, PDF p. 255: 20 Vpp square-wave input; `(Cc=20 pF, alpha=1/2)` and `(Cc=10 pF, alpha=1/4)` show slew rate inversely proportional to `Cc`.
- **UNCERTAINTY:** the PDF does not supply modern SPICE model files or guarantee historical devices are obtainable.

## Modules, components, and proposed stable IDs

Use source designators inside `AMP1`:

| Stable IDs | Historical part/function | Evidence/status |
|---|---|---|
| `AMP1.Q1`, `AMP1.Q2` | matched 2N5963 input pair | VERIFIED Figure 9.1/§9.1.2 |
| `AMP1.Q3`, `AMP1.Q7`, `AMP1.Q9`, `AMP1.Q12` | 2N3707 current-source/limiting roles | VERIFIED Figure 9.1 |
| `AMP1.Q4`, `AMP1.Q5`, `AMP1.Q6`, `AMP1.Q13` | 2N4250 drift/cascode/limit roles | VERIFIED Figure 9.1 |
| `AMP1.Q8` | TIS58 FET source follower | VERIFIED Figure 9.1 |
| `AMP1.Q10` | 2N2219 NPN output follower | VERIFIED Figure 9.1 |
| `AMP1.Q11` | 2N2905 PNP output follower | VERIFIED Figure 9.1 |
| `AMP1.R_BAL`, `AMP1.R_300K_A/B` | 50 kohm trim and two 300 kohm collector/balance branches | VERIFIED visible Figure 9.1; starred precision parts must be transcribed exactly during graph authoring |
| `AMP1.R_OUT_P/N` | 22 ohm each | VERIFIED Figure 9.1 |
| `AMP1.CC` | removable compensation capacitor between `COMP_A/B` | VERIFIED topology; end value pending campaign |
| `AMP1.DEC_VP_FAST/BULK`, `AMP1.DEC_VN_FAST/BULK` | 0.1 uF plus 15 uF/20 V at each rail | VERIFIED Figure 9.1 and text |
| `AMP1.BIAS_*`, `AMP1.C_BYP_*`, remaining resistors/diodes | exact Figure 9.1 bias, bypass, and limit network | values visible in source; require independent double-entry transcription before implementation |

Figure 9.1 visible candidates to transcribe and verify include 33 kohm, 4.7 kohm, 10 kohm trim, 5.6 kohm, 180 kohm, 1.5 kohm, 68 kohm, 1.5 kohm, 0.01 uF, 0.1 uF, 1.0 uF, 3.3 uF/10 V, 33 uF/10 V, and the starred 1% metal-film resistors. This list is not a substitute for a pin-by-pin source transcription.

## Named nets and module boundary

- External: `AMP1.INV_IN`, `AMP1.NONINV_IN`, `AMP1.OUT`, `AMP1.COMP_A`, `AMP1.COMP_B`, `INFRA.VP15`, `INFRA.VN15`, `INFRA.AGND`.
- Internal minimum set: `AMP1.TAIL_Q1Q2`, `AMP1.Q1_COL`, `AMP1.Q2_COL`, `AMP1.Q4Q5_EMIT`, `AMP1.CASCODE_IN`, `AMP1.HIGH_Z`, `AMP1.FET_SRC`, `AMP1.OUT_DRIVE_P`, `AMP1.OUT_DRIVE_N`, `AMP1.BIAS_NEG`, `AMP1.LIMIT_P`, `AMP1.LIMIT_N`.
- W09-A/B configuration nets: `W09.VIN`, `W09.SUM`, `W09.VOUT`, `W09.ALPHA_SHUNT`; `AMP1.INV_IN = W09.SUM`, `AMP1.NONINV_IN = AGND`, `AMP1.OUT = W09.VOUT`.
- W09-C configuration: `AMP1.INV_IN = CORE.INT1.SUM`, `AMP1.NONINV_IN = AGND`, `AMP1.OUT = CORE.INT1.CAP_RETURN = CORE.INT1.OUT_JACK`; `C_INT1` returns from output to sum node.

## Symbolic parameters and recommended-value candidates

| Parameter | Meaning | Candidate/status |
|---|---|---|
| supplies/output | amplifier range | **VERIFIED:** ±15 V rails; design target about ±10 V maximum output |
| `I_E1` | each input-transistor quiescent current | **VERIFIED:** about 10 uA |
| `Cc` small-signal campaign | compensation | **VERIFIED:** 47, 33, 10, 5 pF for Figure 9.10 |
| `Cc` slew campaign | compensation | **VERIFIED:** 20 pF at `alpha=1/2`; 10 pF at `alpha=1/4` |
| `R1` | equal inverter input/feedback resistors | **TBD numeric:** choose large enough not to overload, small enough to dominate input bias/probe leakage; preserve equality |
| `R` | shunt setting `alpha` | **VERIFIED relation:** `alpha = (R1 || R)/(R1 + (R1 || R))`; `R=infinity` gives 1/2 |
| provisional end `Cc` | safe INT1 default | **DERIVED candidate:** 20 pF pending W09-C stability/settling results; must be recorded, not assumed |
| `R_INT1`, `C_INT1` | restored integrator | inherited Week 1/2 values; no change unless separately approved |

## Practical additions; power, test, and loading assumptions

- Stage the first power-up with low rail-current limits and inspect all quiescent nodes before closing feedback.
- Provide test points at inputs, output, compensation terminals, high-impedance cascode output, FET source, and bias node. High-impedance-node probe capacitance can materially alter behavior and must be declared.
- Use low-capacitance probes for Chapter 9 steps. A nominal 10x passive probe may be too capacitive at `HIGH_Z`; model the actual probe.
- Figure 9.1 includes overload protection, but safe output-current limits still require verification with actual parts and board thermal conditions.
- The source warns that approximately 1 pF of stray capacitance can modify the “uncompensated” response. Layout parasitics belong in the realistic model and validation receipt.

## Historical and modern notes

- Historical Figure 9.1 parts are the primary implementation. Exact substitutions require an equivalence table and separate realistic model bindings.
- Likely difficult parts are 2N5963, 2N4250, and TIS58. Modern substitutes must preserve polarity and be checked for beta, capacitances, noise, breakdown, transconductance/current, pinout, and thermal coupling.
- A modern integrated op-amp is only a comparison channel; it is not a replacement for `AMP1`.
- The low-voltage/rail-to-rail redesign remains a deferred second project.

## Ideal and realistic SPICE targets

### Ideal model variant

- Preserve every Figure 9.1 transistor, resistor, capacitor, diode, and net; substitute simplified matched device models only. Do not collapse `AMP1` into an ideal op-amp symbol.
- Analyses: `.op`; differential DC sweep; open-loop/return-ratio `.ac` with valid injection; W09-A small-step `.tran` for every `Cc`; W09-B large-step `.tran`; W09-C integrator step/hold.
- Assertions: correct output sign; all devices in plausible active regions at quiescence; no destructive currents; monotonic reduction of crossover/slew with increasing `Cc`; W09-C integrates with the inherited `R_INT1*C_INT1` sign/time constant.

### Realistic model variant

- Same graph with documented source/vendor models or characterized substitutes, Q1/Q2 and Q4/Q5 mismatch, resistor tolerance/tempco, capacitor parasitics, rail/source impedance, socket/board capacitance, and instrument loads.
- Run nominal, mismatch, supply, temperature, and selected component-corner sweeps.
- Do not claim realistic agreement until model provenance and licensing are recorded. Missing device models are a blocker, not permission to rename generic models as historical parts.

## Expected measurements and proof acceptance

- Quiescent input-stage currents near 10 uA each and total tail current near 20 uA; record measured deviations.
- DC output trim near zero before feedback closure; output swing target about ±10 V on ±15 V rails under the stated load.
- Figure 9.10 qualitative order: 47 pF slow/near first-order; 33 pF faster; 10 pF underdamped; 5 pF strongly oscillatory. Exact waveform matching is not required without matching device/parasitic conditions.
- Slew rate should scale approximately inversely with `Cc`; expected order is about 0.5 V/us at 20 pF for 10 uA available charging current and about 1 V/us at 10 pF, subject to the exact source convention/current factor.
- W09-C: verify correct `xdot=-x` response, `R_INT1*C_INT1`, stability, saturation recovery, and hold drift. Compare against recorded former-INT1 LM301A data and simultaneously measurable `CORE.INT2`; do not reinsert the pulled LM301A into INT1 for the final state.
- **Connectivity gate:** schematic and both netlists have the same component IDs, terminal maps, and nets except documented model/subcircuit internals and test directives.
- **Electrical gate:** all above assertions and saved plots/tables pass or have an explicit failure explanation.
- **Visual/source gate:** a human compares the pin-for-pin detail against Figure 9.1 and configurations against Figure 9.8; no hidden junctions, crossed-wire ambiguity, or premature Week 10/13 circuitry.

## Sheet/detail recommendation

1. One cumulative W09 main sheet: complete chassis state, `AMP1` and active W09 configuration emphasized, inactive retained modules grey.
2. One pin-for-pin Figure 9.1 `AMP1` detail with all power, bias, compensation, limit, and test-point nets.
3. Separate W09-A, W09-B, and W09-C configuration sheets/netlists over the same physical state; A and B may share the Figure 9.8 drawing with different test/value tables if their graph is identical.
4. One values/source/provenance table and one equivalence receipt generated from the canonical graph.

## Incomplete-state handling and open issues

- Week 9 is not complete until the W08-to-W09 component/net transition table is approved and Figure 9.1 has been independently transcribed twice.
- **W09-OPEN-01:** select/verifiably source historical device models or approve clearly named generic realistic substitutes.
- **W09-OPEN-02:** choose numeric `R1` for Figure 9.8 and calculate `R` for `alpha=1/4`.
- **W09-OPEN-03:** select the provisional end-state `Cc` from measured/simulated W09-C behavior.
- **W09-OPEN-04:** define the loop-gain/open-loop extraction fixtures without altering the device under test.
- **W09-OPEN-05:** define realistic parasitic targets for socket, board, wiring, and probes; source warns compensation is sensitive at the ~1 pF scale.

---

# Handoff issue ledger for integration

| ID | Severity | Decision needed before | Issue |
|---|---:|---|---|
| `X05-01` | blocker | regulator graph | Figure 5.3 physical output/current/pass-device/protection design is unspecified |
| `X05-02` | high | W05 variants | Figure 5.11/5.13 must be synthesized into the actual computer loop, not copied |
| `X06-01` | blocker | W06 graph | approve dedicated oscillator integrator to preserve the cumulative machine |
| `X06-02` | high | W06 graph | choose limiter/amplitude target and reconcile Figures 6.14 and 12.8 |
| `X07-01` | blocker | W07 acceptance | input pair cannot cause a functional INT1 integrator; revise hold-wander claim/fixture |
| `X07-02` | high | W07 graph | define temporary Figure 7.10 load/trim and its removal |
| `X08-01` | blocker | W08 graph | synthesize one coherent circuit from Figures 8.8, 8.13, 8.27 |
| `X08-02` | blocker | W08/W09 state | approve pin-by-pin preservation/removal map into Figure 9.1 |
| `X09-01` | blocker | Week 9 proof | double-transcribe Figure 9.1 and bind exact component/pin/net graph |
| `X09-02` | high | realistic SPICE | obtain and document lawful device models or explicit generic substitutes |
| `X09-03` | high | W09 end state | select provisional `Cc`; Chapter 9 necessarily uses compensation before Chapter 13 |

## Deferred items carried forward

- Physical patch-cord routes and front-panel cable drawings remain deferred; all electrical configuration nets are explicit here.
- Full modern alternative schematics remain deferred unless a substitute changes topology/operation materially; modern ±15 V notes remain required.
- The low-voltage/rail-to-rail redesign remains a named second project and is not allowed to disappear from later handoffs.
- Board placement, harness routing, front-panel mechanics, thermal layout, and construction photography remain deferred. Their omission does not waive electrical SOA, decoupling, loading, or parasitic assumptions.

## Draft completion statement

This specification intentionally stops before tool selection and circuit implementation. Weeks 5–9 cannot pass Gate 0 until the blocker-class issues above are resolved or converted into explicit approved design tasks with acceptance criteria.
