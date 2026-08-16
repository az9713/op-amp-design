# Phase 1 draft electrical specification — Weeks 10–13

Status: **draft for Gate 0 review; not an implementation**  
Scope owner: Weeks 10–13 only  
Binding inputs: `capstone.html`, `preflight-decisions.html`, `implementation-plan.html`, and `op_amps_roberge.pdf`

## 1. Contract and notation

This draft follows DEC-001 through DEC-016. The physical chassis is cumulative. A weekly configuration is an electrically complete view of the experiment selected for that week; installed but inactive modules remain present in grey on the future main sheet. Coral marks the week's physical or configuration delta. Hidden op-amp supply pins are allowed only when the weekly sheet references the permanent Week 0 infrastructure sheet.

The future SVG and SPICE netlist for any configuration must be projections of one canonical component/pin/net graph. Every configuration below therefore needs its own graph identity and matched ideal/realistic SPICE projections. Physical patch-cord paths are not specified, but the electrical nets that those cords realize are explicit.

Evidence labels:

- **Verified**: directly visible in the capstone or cited Roberge page/figure.
- **Derived**: engineering consequence or adaptation of verified material; must be reviewed analytically before release.
- **TBD**: insufficient evidence to freeze a build value or connection.

Proposed global module IDs are stable within this draft but must be reconciled with the Week 0–9 draft before Gate 0:

| Proposed ID | Physical role inherited into Week 10 |
|---|---|
| `CMP-INV1` | Inverter installed Week 1 |
| `CMP-SUM1` | Weighted summer installed Week 1; reconfigurable as an integrating summer in Week 12 |
| `CMP-INT1` | Integrator 1, using the discrete Figure 9.1-era amplifier by Week 9 |
| `CMP-INT2` | Integrator 2, historical stock LM301A baseline |
| `PLANT-REG1` | Figure 5.3 physical voltage regulator and load |
| `SRC-OSC1` | Schmitt-trigger/integrator square/triangle source |
| `RECT-PR1` | Precision-rectifier module, added Week 11 |

Common named nets and boundaries:

- Infrastructure: `VCC_15`, `VEE_15`, `AGND`; physical distribution and decoupling live on the Week 0 sheet.
- Computing ports: `INV1_IN/OUT`, `SUM1_IN1..n/OUT`, `INT1_IN/OUT`, `INT2_IN/OUT`, later `INT3_IN/OUT`.
- Plant ports: `REG1_REF`, `REG1_DIST_I`, `REG1_UNREG`, `REG1_OUT`.
- Source ports: `OSC1_SQUARE`, `OSC1_TRIANGLE`.
- Measurement nodes use `TP_...` names and are real graph nodes; scope/probe models attach to them in realistic SPICE.
- Control nets: `MODE_OPERATE`, `MODE_RESET`; their logic-to-gate interface belongs to the Week 11 detail graph.

## 2. Week 10 — current-repeater discrete channel

### Cumulative end state

Week 9 chassis plus a current-repeater load adaptation in the discrete `CMP-INT1` amplifier. `CMP-INT2` remains the LM301A comparison channel. The optional Figure 10.25 FET input followers are **not yet part of the canonical cumulative baseline** because the capstone says “optional” and no user decision has selected them. If retained, they require a separate `W10-FET-ALT` configuration and cannot silently alter the Week 11 inheritance.

### Active experiment and configurations

- `W10-CR-CHAR`: characterize the current repeater as a module and measure input/output current ratio and compliance.
- `W10-INT1-HOLD`: `CMP-INT1` restored as an integrator, measuring hold drift/bias-current effect after the load change.
- `W10-COMPARE`: electrically complete comparison of `CMP-INT1` and LM301A `CMP-INT2` under equal capacitor, temperature, initial voltage, duration, and instrument loading.
- Optional, nonbaseline `W10-FET-ALT`: Figure 10.25-style source followers in front of `CMP-INT2`, followed by a repeat of the hold test.

### Inherited circuitry

All Week 9 physical modules remain. The future weekly main sheet shows them, but only `CMP-INT1`, `CMP-INT2`, common rails, the selected hold/integrator connections, and measurement loads are active in the above configurations.

### Explicit delta

- Add `LOAD-INT1-CR1`, a matched two-transistor current repeater, at the Week 9 first-stage load interface.
- Add test nodes `TP_CR_IREF`, `TP_CR_IOUT`, `TP_INT1_HOLD`, and `TP_INT2_HOLD`.
- **TBD topology mapping:** Figure 10.9 is a generic current repeater. The capstone's instruction to use it “as the first-stage load” is an adaptation and does not itself identify which Week 9 load transistor(s) are replaced, the current-reference source, polarity, or compliance limits. Final connectivity must be derived against the accepted Week 9 graph, not guessed from Figure 10.9.

### Sources and evidence

- `capstone.html`, Chapter 10 step: current repeater on the same discrete amplifier; compare bias current to the LM101A/stock IC in integrator 2; Figure 10.25 is optional.
- Roberge PDF p. 269, §10.3.1, Figure 10.9: matched two-transistor current repeater; equal currents for high beta, valid only while the output device remains forward active; a constant reference current makes the output device a current source to within about 100 mV of the relevant rail.
- Roberge PDF pp. 269–271: finite beta causes transfer error; emitter resistors can reduce sensitivity to VBE mismatch, while Figures 10.11 alternatives reduce beta dependence.
- Roberge PDF p. 290, Figure 10.25: FET source followers can reduce input current to a fraction of a nanoampere but worsen drift and common-mode rejection; cited typical dual-FET drift is 10–100 microvolts/°C; dynamics are usually unchanged unless follower output resistance and amplifier input capacitance matter.
- Historical naming conflict: the capstone text says LM101A in Week 10, while locked DEC-016 requires LM301A as the project baseline. Use LM301A in the canonical graph and document the textbook LM101A relation as historical context.

### Components, symbolic parameters, and recommended-value candidates

| ID / parameter | Purpose | Candidate | Status |
|---|---|---|---|
| `Q-CR-REF`, `Q-CR-OUT` | matched repeater pair | same polarity and matched type required by the finalized Week 9 interface | **TBD**; Figure 10.9 verifies matching/topology, not a discrete part number |
| `I_CR_REF` | repeater reference current | equal to the accepted Week 9 first-stage quiescent/load current | **Derived/TBD** pending Week 9 operating point |
| `R-CR-E1`, `R-CR-E2` | optional emitter degeneration | equal values, sized from allowed headroom and mismatch target | **Derived/TBD**; do not add until transfer/headroom analysis |
| `C_INT1`, `C_INT2` | hold-test capacitors | same measured value for A/B comparison | **Derived**; absolute value inherited from prior weeks |
| `Q-FET-A/B` | optional matched dual source followers | dual JFET compatible with ±15 V and input common-mode range | **TBD**; historical figure gives topology, not a preferred modern stocked part |
| `R_FET_S`, `I_FET_TAIL` | Figure 10.25 bias/balance | determine from JFET IDSS, operating point, headroom, and LM301A input range | **TBD** |

### Named nets and module boundary

`LOAD-INT1-CR1` must expose `CR_REF_IN`, `CR_OUT`, `CR_COMMON`, `VCC_15/VEE_15` as appropriate to finalized polarity. `CR_OUT` connects only to the exact Week 9 first-stage load node. `CMP-INT1` retains `INT1_IN`, `INT1_OUT`, and compensation terminals. The hold comparison uses explicit nets `HOLD_INIT`, `INT1_HOLD_NODE`, `INT2_HOLD_NODE`, and separate high-impedance probe loads.

### Practical additions and assumptions

- Add local test resistors/current sensing only if their loading is included in both graph and SPICE.
- Specify transistor thermal coupling and matching method in later construction documentation; it affects mirror error but belongs partly to D-04.
- Limit test current and output voltage so the repeater output device stays forward active.
- Hold-time comparison must report capacitor leakage, switch leakage, probe resistance/capacitance, ambient temperature, and initial voltage.

### Historical and modern notes

The primary path remains discrete, ±15 V, and LM301A-based. A modern monolithic matched pair can be noted as a same-topology substitution if voltage ratings permit. FET-input or precision CMOS op-amps are not drop-in pedagogical equivalents; a full low-voltage or rail-to-rail version belongs to D-02/D-03.

### SPICE targets

- Ideal: controlled current repeater with exact ratio 1, ideal op-amp blocks, ideal hold capacitors; verify topology and sign.
- Realistic: transistor models with beta, Early effect, mismatch corners, temperature sweep, LM301A model for `CMP-INT2`, accepted discrete model for `CMP-INT1`, capacitor/switch/probe leakage.
- Required checks: `I(CR_OUT)/I(CR_REF)`, compliance sweep, DC operating point/headroom, hold drift slope, and comparison sensitivity to beta/mismatch/temperature.

### Expected measurements

- Repeater current-transfer ratio near unity only in its valid compliance region.
- `dV_HOLD/dt` gives total node leakage divided by capacitance, with sign preserved; it is not by itself a pure input-bias-current measurement.
- Bias-current comparison must use the direct Figure 11.2 method in Week 11 to separate amplifier input current from other hold-node leakage.

### Sheet recommendation

One cumulative Week 10 main sheet plus a pin-for-pin `LOAD-INT1-CR1` detail. Add a separate detail for `W10-FET-ALT` only if the optional branch is approved.

### Open issues

1. Reconcile the exact current-repeater insertion point with the Week 9 canonical amplifier.
2. Decide whether Figure 10.25 is excluded from the baseline or approved as an explicit physical addition.
3. Select transistor parts/current after headroom, dissipation, and model-availability checks.

## 3. Week 11 — three-mode integrators, amplifier measurements, and retained rectifier

### Cumulative end state

Week 10 baseline plus reset/operate/hold switching around both installed integrators, an offset/input-current measurement configuration for the discrete amplifier, and a permanently retained precision-rectifier module. The integrator channels are functional at end of week in all three modes.

### Active experiment and configurations

- `W11-INT-MODES`: both integrators shown in complete three-mode topology, with the same explicit mode-control state.
- `W11-DUT-EO`: Figure 11.2a offset-voltage measurement of the discrete `CMP-INT1` amplifier.
- `W11-DUT-IMINUS`: Figure 11.2b inverting-input-current measurement.
- `W11-DUT-IPLUS`: Figure 11.2c noninverting-input-current measurement.
- `W11-RECT`: complete Figure 11.18 bridge precision rectifier driving an explicit floating load.

The four measurement configurations are mutually exclusive views of the same physical state. No single SPICE deck may combine the three Figure 11.2 test connections around one DUT.

### Inherited circuitry

All Week 10 baseline modules remain. The regulator and oscillator are installed but inactive for these tests. `CMP-INT1` retains the Week 10 repeater; `CMP-INT2` remains LM301A.

### Explicit delta

- Around each integrator add a three-mode module: `MODE-INT1` and `MODE-INT2`.
- Each practical Figure 12.18 implementation adds an operate switch, reset switch, reset follower, diode clamps, and logic-level gate drivers. Proposed IDs are suffixed `_I1` and `_I2`.
- Add `RECT-PR1`, whose canonical source topology is Figure 11.18: op-amp plus diode bridge plus floating load and sense resistor.
- Add measurement test points `TP_EO`, `TP_I_MINUS`, `TP_I_PLUS`, `TP_RECT_LOAD_P`, `TP_RECT_LOAD_N`.

### Sources and evidence

- `capstone.html`, Chapter 11 step: convert both integrators to Figure 12.17 using Figure 12.18 practical drive; measure offset and bias current with Figure 11.2; retain Figure 11.18.
- Roberge PDF p. 300, Figure 11.2: offset circuit uses `999R` feedback and `R` to ground, giving approximately 1000× offset gain when loop gain is adequate; separate `R1` connections measure the two input currents.
- Roberge PDF p. 313, Figure 11.18: precision rectifier is an op-amp driving a diode bridge and a **floating load**; this is not the simple grounded half-wave “superdiode” described immediately afterward.
- Roberge PDF p. 323, Figure 11.34: sample-and-hold topology and leakage/loading rationale; related pedagogically but not the Week 11 three-mode implementation.
- Roberge PDF p. 348, Figure 12.17: switch truth table is reset = switch 1 open/switch 2 closed; operate = switch 1 closed/switch 2 open; hold = both open.
- Roberge PDF p. 349, Figure 12.18: practical circuit uses 2N4391 operate FET, 2N4091 reset FET, 2N2907 control transistors, +15 V/-15 V rails, 10 kΩ/100 kΩ driver resistors, 15 kΩ negative-rail resistors, diode clamps, and `R1` reduced by about the 25 Ω on-resistance of the operate FET.

### Components, symbolic parameters, and recommended-value candidates

| ID / parameter | Purpose | Candidate | Status |
|---|---|---|---|
| `S-OP_I1/I2` | operate switches | 2N4391 | **Verified** from Figure 12.18; availability/modern equivalent TBD |
| `S-RST_I1/I2` | reset switches | 2N4091 | **Verified** from Figure 12.18; availability/modern equivalent TBD |
| `Q-DRV-OP_*`, `Q-DRV-RST_*` | logic-to-FET gate drivers | 2N2907 | **Verified** |
| driver resistors | Figure 12.18 gate drive | 10 kΩ, 100 kΩ, and 15 kΩ as drawn | **Verified**; diode type and power ratings TBD |
| `R_INT_EFFECTIVE` | integration input resistance | `R1 - 25 Ω` in the historical circuit | **Verified rationale**, exact nominal `R1` inherited/TBD |
| `R_RESET_A/B` | initial-condition/reset divider | equal `R2` values | **Verified symbolic**; numeric value TBD |
| `C_INT1/2` | integrating capacitors | inherited values; matched/characterized | **Derived** |
| `R_EO_LOW` | Figure 11.2a lower resistor | choose build-friendly `R`; feedback is `999R` | **Verified ratio**, numeric value TBD from output range/loading |
| `R_IB` | Figure 11.2b/c current-to-voltage resistor | choose so `|I_B R_IB| >> |E_O|` and output remains linear | **Verified criterion**, numeric value TBD after expected bias range |
| `D-RECT1..4` | bridge rectifier | low-leakage matched small-signal diodes | **TBD**; source does not prescribe type |
| `R_RECT` | bridge return/sense resistor | symbolic `R` | **Verified symbolic**, numeric value/load rating TBD |

### Named nets and mode boundaries

Each `MODE-INTx` exposes `INTx_SIGNAL_IN`, `INTx_IC_IN`, `INTx_SUM_NODE`, `INTx_CAP_NODE`, `INTx_OUT`, `MODE_OPERATE`, and `MODE_RESET`. The practical driver nets must distinguish logic input from FET gate (`OP_GATE_Ix`, `RST_GATE_Ix`). Initial-condition inputs are `ICOND_I1` and `ICOND_I2`.

Mode graph states:

| Mode | `S-OP` | `S-RST` | Required electrical consequence |
|---|---:|---:|---|
| Reset | open | closed | output tends to `-ICOND_Ix` |
| Operate | closed | open | ordinary inverting integration |
| Hold | open | open | capacitor current limited to amplifier/FET/capacitor/probe leakage |

`RECT-PR1` exposes only `RECT_IN`, `RECT_LOAD_P`, and `RECT_LOAD_N` until a ground-referenced interface is deliberately added. The load remains floating in the Figure 11.18-faithful graph.

### Practical additions and assumptions

- Add break-before-make control or a documented safe sequence; reset and operate must not be simultaneously asserted without analysis.
- Gate-drive high/low thresholds and power-up defaults must guarantee a known hold state.
- Model FET off leakage, charge injection, and on resistance. State whether control transitions are observed before or after settling.
- Figure 12.18 uses extra follower amplifiers; allocate one reset follower per integrator unless a shared-driver design is separately analyzed.
- For Figure 11.2, include meter/probe impedance and optional noise-filter capacitors in the canonical realistic graph.
- **Source correction:** existing simplified drawings that show Figure 11.18 as a diode-feedback half-wave rectifier are not electrically faithful to the cited figure.

### Historical and modern notes

The 2N4391/2N4091/2N2907 network is the historical ±15 V implementation. Modern analog switches could reduce driver complexity but would materially change leakage, charge injection, resistance, logic supply, and pedagogy; full modern circuits belong to D-03. A same-function note may identify candidates only after ±15 V signal/rail capability is verified.

### SPICE targets

- Ideal: ideal switches and op amps; verify the three mode equations, Figure 11.2 gain/sign relationships, and full-wave bridge rectification.
- Realistic: accepted discrete `CMP-INT1`, LM301A `CMP-INT2`, JFET/driver/diode models, leakage, charge injection approximation, capacitor dielectric leakage, probe loading, and control transitions.
- Required checks: reset settling, operate scale factor `-1/(RCs)`, hold droop, unsafe control combinations, `E_O/I+/I-` extraction, bridge load current vs input polarity and near zero.

### Expected measurements

- Reset output converges to the negative initial-condition voltage.
- Operate mode integrates with measured time constant adjusted for switch on resistance.
- Hold mode droop separates total node leakage from independently measured DUT input current.
- Figure 11.2 yields `V_O ≈ 1000 E_O`, `V_O = I_- R_IB`, and `V_O = -I_+ R_IB` under the stated conditions and polarity conventions.
- Figure 11.18 load current is nominally `|v_i|/R` with direction through the floating load fixed; threshold error is reduced by loop gain.

### Sheet recommendation

One cumulative Week 11 main sheet with `MODE-INT1`, `MODE-INT2`, and `RECT-PR1` as named hierarchical blocks. Pin-for-pin detail sheets: one reusable Figure 12.18 channel detail, one Figure 11.2 three-configuration measurement sheet, and one exact Figure 11.18 bridge sheet.

### Open issues

1. Decide whether the reset follower is duplicated per channel or shared; default is duplicated for unambiguous independent graphs.
2. Resolve historical FET/diode availability and model fidelity.
3. Decide whether `RECT-PR1` remains a floating-load teaching module or gains a separately identified ground-referenced output interface. Do not silently replace Figure 11.18 with another rectifier topology.

## 4. Week 12 — cumulative machine with separate complete problem configurations

### Cumulative physical end state shared by all Week 12 configurations

Week 11 baseline plus:

- Populate the last reserved integrator position as `CMP-INT3`.
- Install two multiplier modules, `MUL1` and `MUL2`, each with a declared four-quadrant transfer interface.
- Add the analog regulator-twin module group `TWIN-REG1`.

Hardware-count evidence: through Week 11 the chassis has `CMP-INV1`, `CMP-SUM1`, `CMP-INT1`, and `CMP-INT2`, with one integrator position reserved since Week 1. Roberge PDF pp. 343–344 states Figure 12.13 needs four integrators and one inverter, with the summation folded into the first integrator. Therefore, in `W12-BW`, reconfigure `CMP-SUM1` as the first integrating summer, use `CMP-INT1` and `CMP-INT2` as the middle integrators, populate `CMP-INT3` as the fourth, and retain `CMP-INV1`. This requires **one** new integrator channel, not two. The physical state is a superset; the SUM-to-integrating-SUM change is configuration wiring, not removal.

### Configuration A — `W12-BW`, fourth-order Butterworth

#### Active circuit and explicit connectivity

Use Figure 12.13 as the complete electrical configuration. Proposed state nets:

- `BW_D3_NEG`: first integrating-summer output, representing `-d³x/dt³`.
- `BW_D2`: second integrator output, `d²x/dt²`.
- `BW_D1_NEG`: third integrator output, `-dx/dt`.
- `BW_X`: fourth integrator output, `x`.
- `BW_COMB`: inverter output representing `-x - 3.42 d²x/dt²`.
- `BW_DRIVE`: source `f(t)`.
- `BW_SUM_NODE`: first integrating-summer node receiving all explicit coefficient paths.

No path may be represented by a label without a canonical net endpoint. Physical patch-cord routing remains deferred under D-01.

#### Source and values

- Roberge PDF pp. 343–344, §12.3.1, Figure 12.13: fourth-order Butterworth equation, four integrators plus one inverter; summing occurs in the first integrator.
- **Verified from Figure 12.13:** four `1 µF` feedback capacitors and nominal `1 MΩ` interstage/input resistors; coefficient resistors shown as `(1/2.61) MΩ` and `(1/3.42) MΩ`; the bottom amplifier combines `x` and `d²x/dt²`.
- **Derived candidates:** `(1/2.61) MΩ = 383.1 kΩ`; `(1/3.42) MΩ = 292.4 kΩ`. Use series/parallel precision networks or trimmed values only after tolerance analysis.
- Roberge warns on PDF p. 343 that the shown 1 MΩ impedance level is high for LM101A-class devices; all impedances may be scaled together because ratios establish the transfer function. For the LM301A baseline, a lower common impedance scale is a recommended **derived** build option, with capacitors increased inversely to preserve every `RC` and coefficient ratio.

#### SPICE and expected measurement

- Ideal: ideal integrators/summer; verify characteristic polynomial and transfer function of the fourth-order Butterworth equation.
- Realistic: one accepted discrete amplifier channel, LM301A channels for stock blocks, switch/on-resistance/leakage, component tolerances, finite gain-bandwidth, slew/saturation, and probe loads.
- Measure frequency response, step response, all four state nodes, coefficient sensitivity, and maximum stable time-scale factor `alpha`.
- Acceptance must compare polynomial coefficients extracted from the graph/netlist with the intended `1, 2.61, 3.42, 2.61, 1` coefficients.

#### Sheet recommendation

One complete large `W12-BW` electrical sheet. A detail sheet expands the reconfigured `CMP-SUM1` integrating summer and coefficient network if the large sheet becomes unclear.

### Configuration B — `W12-VDP`, Van der Pol oscillator

#### Active circuit and explicit connectivity

Use two three-mode integrators, an inverting/summing amplifier, and two multiplier blocks to realize

`d²x/dt² = -mu*x²*(dx/dt) + mu*(dx/dt) - x`.

Named state/product nets:

- `VDP_D1_NEG`: `-dx/dt` from the first integrator.
- `VDP_X`: `x` from the second integrator.
- `VDP_X2_DIV10`: first multiplier output `x²/10`.
- `VDP_X2DX_DIV100`: second multiplier output `x²(dx/dt)/100`, with sign explicitly determined by its input nets.
- `VDP_ACCEL_SUM`: inverter/summer result applied to the first integrator.
- `VDP_IC_X`, `VDP_IC_D1`: explicit initial-condition nets; this problem is undriven after reset.

#### Source and multiplier correction

- Roberge PDF p. 344, Figure 12.14: two integrators, one summing/inverting amplifier, and two multipliers whose nominal transfer is product divided by 10 V; shown nominal parts include `1 µF`, `1 MΩ`, `10 kΩ`, and coefficient-dependent `1 MΩ/mu` paths.
- Roberge PDF p. 345: for `mu = 1`, the limit cycle converges to about 4 peak-to-peak for the shown initial-condition examples.
- Roberge PDF pp. 345–347, §12.3.2 and Figure 12.16: recommends amplitude/time scaling; the example uses 3 V per unit for `x` and `dx/dt`, 2 V per unit for `d²x/dt²`, multiplier outputs divided by 10, and `RC = 1 s` for real-time or `RC = 1 ms` for approximately 1000 rad/s oscillation.
- Roberge PDF pp. 319–320 states Figure 11.28 is **two-quadrant** because its `vY` control cannot be negative. Van der Pol state variables change sign, so Figure 11.28 alone is not an electrically adequate generic replacement for the two four-quadrant multiplier blocks drawn in Figure 12.14.
- Roberge PDF p. 339, Figure 12.9: time-division multiplier gives `vO = vX*vY/VR` by switching between `+vY` and `-vY`; this is a plausible historical four-quadrant route if the duty-cycle modulator, switch, reference range, carrier rejection, and output filter are fully specified.

#### Recommended-value candidates

| Parameter | Candidate | Status |
|---|---|---|
| `C_VDP1/2` | 1 µF for unscaled Figure 12.14 | **Verified** |
| `R_VDP_BASE` | 1 MΩ for unscaled Figure 12.14 | **Verified**, but bias-current error requires analysis |
| multiplier scale | `vO = vX*vY/(10 V)` | **Verified** assumption in Figures 12.14/12.16 |
| `mu` | start with 1 | **Derived teaching default** supported by source plots/scaling example |
| time scale | `RC = 1 s` or `1 ms` | **Verified examples**; final value must respect realistic amplifier/multiplier bandwidth |
| multiplier implementation | Figure 12.9-derived time-division or other four-quadrant ±15 V module | **TBD**; must be one canonical implementation, not an abstract block in the build-ready release |

#### SPICE and expected measurement

- Ideal: exact four-quadrant behavioral multipliers with `/10 V` scale, ideal integrators, and explicit reset initial conditions; confirm bounded limit cycle and state-node signs.
- Realistic: selected physical multiplier topology, carrier/filter dynamics if Figure 12.9 is used, amplifier limits, offsets, mode switches, tolerances, and initial-condition transient.
- Measure phase plane `x` vs `dx/dt`, convergence from at least two initial conditions, limit-cycle amplitude/frequency, multiplier residual/feedthrough, and time-scale dependence.
- The realistic netlist must not use a behavioral multiplier if the rendered build-ready schematic shows a transistor/switch implementation, except as an explicitly labeled validation-only abstraction.

#### Sheet recommendation

One complete large `W12-VDP` electrical sheet plus a pin-for-pin multiplier detail. Do not reuse the Butterworth netlist with conditional comments; each configuration gets a distinct graph and matched netlist.

### Configuration C — `W12-REG-TWIN`, physical regulator and analog twin

#### Active circuit

Show `PLANT-REG1` and `TWIN-REG1` together, both driven by the same explicitly modeled load-disturbance waveform from `SRC-OSC1`, with separate output probes `REG1_OUT` and `TWIN_REG_OUT`.

Proposed twin modules: `TWIN-SUM1`, `TWIN-INT1`, coefficient elements `K_TWIN_RL`, `K_TWIN_CL`, `K_TWIN_G`, and scaling block `K_TWIN_SCALE`. These names are provisional because the exact state equation and signs must be derived from the accepted Figure 5.3 plant graph.

#### Source and uncertainty

- Capstone Week 12 explicitly requires a first-order analog model of Figure 5.3 beside the real regulator and an overlay of two load steps; Week 6 oscillator is the test input.
- Roberge PDF pp. 119–120, Figure 5.3: op amp compares output with a fixed reference, drives a series transistor, and supplies an `R_L || C_L` load with a disturbing current source; the load pole is assumed dominant.
- **TBD/required derivation:** freeze the twin equation, coefficient polarities, disturbance injection sign, transistor/common-base approximation, and amplitude/time scaling from the accepted physical plant values. The figure's block diagram is the source; a generic first-order low-pass is insufficient.

#### SPICE and expected measurement

- Ideal: ideal first-order twin derived from the same `R_L`, `C_L`, and loop-gain assumptions as the source model.
- Realistic: physical regulator transistor/op-amp/load model and realizable analog-computer twin with LM301A/discrete channels and measured component values.
- Apply the same source waveform and scope loading. Overlay DC value, first-order time constant, rise/settling, and residual error; explicitly report where the twin departs because Figure 5.3's simplifying assumptions fail.

#### Sheet recommendation

One complete `W12-REG-TWIN` sheet. It is separate from both `W12-BW` and `W12-VDP`; conflating the twin, Butterworth, and Van der Pol signal paths would obscure three different electrical configurations.

### Week 12 practical additions and historical/modern notes

- Add test points for every state variable and multiplier input/output.
- Recommended resistor tables must state tolerance, temperature coefficient, and measured value; polynomial coefficients are ratio-sensitive.
- `CMP-INT3` should use LM301A for historical consistency unless the integration team identifies an already installed compatible stock channel.
- Modern analog multiplier ICs may be noted as ±15 V substitutions, but a lower-voltage part is not a drop-in. A materially different multiplier design belongs to D-03; a low-voltage redesign belongs to D-02.

### Week 12 open issues

1. Select and fully specify a four-quadrant multiplier implementation. Figure 11.28 alone is rejected for bipolar Van der Pol state products.
2. Derive and review the regulator twin from the accepted Week 5 plant graph and measured parameters.
3. Determine whether the Figure 12.13 1 MΩ scale is acceptable with measured bias currents or adopt a uniformly scaled impedance set.
4. Allocate physical mode controls and initial-condition sources for the newly populated `CMP-INT3` if it needs three-mode operation.

## 5. Week 13 — two separate compensation campaigns

### Cumulative end state

Same physical chassis as Week 12 plus selectable compensation components and test points. No computing, plant, multiplier, rectifier, or source module is removed. Compensation networks that are mutually exclusive are installed through explicit selection points and appear in separate complete configuration graphs/netlists.

### Campaign A — `W13-FIXED-AS`, compensate around fixed amplifier dynamics

#### Configurations

- `W13-FIXED-LAG`: Figure 13.1 input-lag network on the selected inverting summer/inverter path. This network changes loop transmission without changing ideal closed-loop gain.
- `W13-FIXED-CLOAD`: Figure 13.7 capacitively loaded inverter baseline and Figure 13.8 compensated feedback-network comparison, but only if the selected regulator/output path actually has capacitive loading matching the model assumptions.

The baseline and compensated capacitive-load cases require separate matched netlists because the feedback topology differs.

#### Sources and connectivity

- Roberge PDF p. 372, §13.2.1, Figure 13.1: add series `R-C` from the inverting summing node to ground while retaining input `R1` and feedback `R2`; pole is at `1/[(R1 || R2)C]`, zero at `1/(RC)` under negligible loading.
- Roberge PDF p. 376, Figure 13.7: capacitive load introduces a loop pole through nonzero amplifier output resistance.
- Roberge PDF pp. 377–378, Figure 13.8: a second feedback path containing `C_F`, `R`, and output isolation `R_C` can improve stability under stated high-frequency/path assumptions while preserving ideal inversion where path 1 is negligible.

Proposed IDs/nets: `COMP-LAG-SUM1` (`R_LAG`, `C_LAG`, net `LAG_SHUNT`), `COMP-CLOAD-REG1` (`R_CISO`, `C_F`, `R_FPATH`, `C_LOAD_TEST`, nodes `REG1_OUT_INT`, `REG1_OUT_LOAD`, `REG1_FB_AUX`). Exact pin mapping must use the selected active Week 12 path, not a free-standing scrap inverter.

#### Values and assumptions

| Parameter | Candidate | Status |
|---|---|---|
| `R_LAG`, `C_LAG` | choose pole/zero from measured uncompensated loop `L(s)` | **Derived/TBD**; Figure 13.1 supplies equations, not universal values |
| `C_LOAD_TEST` | measured/declared regulator load capacitance | **TBD** |
| `R_CISO`, `C_F`, `R_FPATH` | solve Figure 13.8 assumptions at measured crossover | **Derived/TBD** |

Power/load assumptions must include probe capacitance, regulator `R_L/C_L` range, and the amplifier output resistance/model. The main test varies time scale `alpha` only after phase/gain margins are measured.

#### SPICE and expected measurements

- Ideal: fixed `a(s)` macro-model plus exact passive compensation; verify unchanged ideal closed-loop gain and intended pole/zero placement.
- Realistic: selected LM301A/discrete/fixed-amplifier model, output resistance, load capacitance, parasitics, and measured component values.
- Measure loop Bode/return ratio, phase margin, gain margin, closed-loop step/ramp, noise amplification, and maximum stable `alpha` before/after each network.

#### Sheet recommendation

One campaign overview with two complete details: `W13-FIXED-LAG` and `W13-FIXED-CLOAD`. If the regulator load does not satisfy Figure 13.7/13.8 assumptions, the capacitive-load detail remains a documented nonapplicable experiment, not an installed network.

### Campaign B — `W13-VARY-AS`, change amplifier open-loop dynamics

#### Configurations

- `W13-ONEPOLE-INT1`: select a single compensation capacitor on the discrete Figure 9.1/Week 10 integrator channel appropriate to its feedback factor and active integrator configuration.
- `W13-ONEPOLE-LM301A`: select a separate capacitor for an LM301A summer/inverter configuration; do not assume the integrator and summer require the same `C_C`.
- `W13-TWOPOLE-REG1`: Figure 13.19 true two-port network connected to the compensation terminals of the regulator error amplifier, with values derived from the measured regulator loop.

These are separate complete configuration graphs. In particular, `W13-TWOPOLE-REG1` cannot share a netlist with a one-pole capacitor simultaneously connected to the same compensation terminals.

#### Sources and connectivity

- Roberge PDF pp. 383–388, §13.3.2 and Figures 13.13–13.17: one-pole compensation is general-purpose; closed-loop bandwidth depends on feedback factor and compensation capacitance. Changing capacitor with feedback factor can retain bandwidth/stability; optimum values depend on the individual amplifier and strays.
- Roberge PDF p. 383: an LM101A with a 30 pF capacitor is described as approximately equivalent to common internally compensated parts near 1 MHz; this is a historical reference, not an automatic value for every capstone configuration.
- Roberge PDF pp. 389–390, §13.3.3 and Figure 13.19: two-pole compensation uses a true two-port `C1-R-C2` network and is not general-purpose. Its zero and gain must be selected for the specific feedback attenuation.
- Roberge PDF pp. 390–393 warns that two-pole compensation is intolerant of additional intermediate-frequency poles/load capacitance and can show poor overload recovery/marginal damping.
- Roberge PDF p. 391, Figure 13.21, historical example: LM301A unity-gain inverter with 2.2 kΩ input/feedback resistors, two 30 pF capacitors, and 15 kΩ shunt resistor; LM310 buffers the summing node for measurement. These values are **verified for that unity-gain demonstration only** and must not be copied to the regulator.

Proposed IDs/nets: `CC-INT1-1P`, `CC-LM301A-1P`, `COMP-REG1-2P` containing `C_2P_1`, `R_2P`, `C_2P_2`; compensation-port nodes `INT1_COMP_A/B`, `LM301A_COMP_A/B`, `REG1_COMP_A/B`; measurement break `REG1_LOOP_BREAK` and buffered sense `REG1_SUM_SENSE`.

#### Values and recommended procedure

| Parameter | Candidate | Status |
|---|---|---|
| `C_C` initial reference | 30 pF on LM301A-like unity-gain case | **Verified historical reference**, not final |
| `C_C_INT1`, `C_C_SUM` | choose from measured `a(s)`, feedback factor `f0`, phase margin, and step response; keep `C_C/|f0|` approximately constant as a first estimate | **Derived**, then tune/verify |
| Figure 13.21 network | 30 pF, 15 kΩ, 30 pF with 2.2 kΩ inverter resistors | **Verified example only** |
| regulator two-pole values | solve `tau = R(C1 + C2)` and `K' = K/(R C1 C2)` against measured loop and target crossover/zero | **Derived/TBD** |

#### SPICE and expected measurements

- Ideal: parameterized one-pole and two-pole `a(s)` models, exact feedback factors, and loop-break analysis.
- Realistic: accepted discrete amplifier and LM301A transistor/macromodels with compensation pins, regulator plant/load dynamics, saturation/overload recovery, parasitic capacitance, and buffered/probe loading.
- Sweep `C_C`, feedback factor, `R_L`, `C_L`, and time-scale `alpha`. Record phase/gain margin, crossover, closed-loop bandwidth, overshoot, settling, slew, error/desensitivity, overload recovery, and stable `alpha`.
- Two-pole acceptance requires robustness across declared plant/load tolerances; a nominal-only stable simulation is insufficient.

#### Sheet recommendation

One campaign overview plus pin-for-pin one-pole details for `CMP-INT1` and the selected LM301A channel, and a separate regulator two-pole detail. Figure 13.21 may appear as a source/reference inset but not as the regulator circuit.

### Week 13 practical additions and historical/modern notes

- Add compensation selection with explicit jumper/switch states, break-before-make behavior, and safe default capacitance.
- Add buffered loop/summing-node measurement where probe capacitance would change the result; Figure 13.21 used an LM310 specifically for this reason.
- Historical primary remains LM301A/discrete ±15 V. Modern internally compensated devices may make Campaign B impossible or pedagogically different; list them as alternatives, not equivalent replacements.
- A modern low-voltage stability curriculum is a separate D-02 project.

### Week 13 open issues

1. Measure or model the regulator loop before selecting any Figure 13.19 values.
2. Define the exact compensation terminals and uncompensated `a(s)` of the Week 10 discrete amplifier.
3. Define pass/fail stability margins and the `alpha` sweep range.
4. Decide applicability of Figure 13.8 after declaring actual regulator output capacitance and error-amplifier topology.

## 6. Cross-week matched-graph acceptance for this range

For every configuration ID above:

1. The canonical manifest lists every component ID, pin, named net, parameter, module port, and active/inactive state.
2. The SVG projection and both SPICE projections are generated from that manifest.
3. Connectivity comparison is exact after an explicit allow-list for presentation-only hidden power pins; no unconnected label may masquerade as a wire.
4. Ideal SPICE verifies topology/sign/equations. Realistic SPICE verifies operating point, headroom, loading, stability, saturation/slew, and component/device nonidealities relevant to the week.
5. Visual review compares the detail sheet to the cited Roberge figure and labels all implementation additions.
6. A configuration delta report proves physical inheritance from the preceding week and lists every configuration-only reroute.

Minimum configuration set for Weeks 10–13:

`W10-CR-CHAR`, `W10-INT1-HOLD`, `W10-COMPARE`; `W11-INT-MODES`, `W11-DUT-EO`, `W11-DUT-IMINUS`, `W11-DUT-IPLUS`, `W11-RECT`; `W12-BW`, `W12-VDP`, `W12-REG-TWIN`; `W13-FIXED-LAG`, conditional `W13-FIXED-CLOAD`, `W13-ONEPOLE-INT1`, `W13-ONEPOLE-LM301A`, and `W13-TWOPOLE-REG1`.

## 7. Deferred ledger preserved

- **D-01 — physical patch-cord drawings:** defer cable paths, labels, and routing only. Every electrical connection remains explicit in the canonical graph, SVG, and netlist. Trigger after weekly nets and connectors stabilize.
- **D-02 — low-voltage redesign:** separate future project; do not alter the primary ±15 V curriculum. Trigger after the historical reference is stable and new rail/signal goals are written.
- **D-03 — full modern alternatives:** record substitutions now; create complete parallel schematics only when topology, operating range, compensation, or teaching outcome changes. Historical implementation must be verified first.
- **D-04 — physical chassis/construction documentation:** board placement, harnesses, panel, grounding geometry, thermal layout, and photographs remain deferred. Trigger after circuit, connector, grounding, and parts definitions stabilize.

## 8. Gate 0 blockers and integration questions

1. **Week 10 insertion:** the exact Figure 10.9 current-repeater mapping into the accepted Week 9 amplifier must be resolved from the Week 9 graph and operating point.
2. **Week 10 optional branch:** decide whether Figure 10.25 is excluded from the cumulative baseline or becomes an explicit physical addition with a separate configuration.
3. **Week 11 rectifier interface:** Figure 11.18 is a floating-load bridge. Decide whether that exact module is sufficient for the stated future Wien-control purpose or whether a separately sourced ground-referenced interface is required.
4. **Week 12 multiplier:** select a buildable four-quadrant `/10 V` multiplier. Figure 11.28 alone does not meet the bipolar-state requirement.
5. **Week 12 regulator twin:** derive and approve the exact state equation, sign convention, and scale from Figure 5.3 plus the built plant values.
6. **Week 13 compensation:** no two-pole regulator values may be frozen before the loop/plant model and tolerance envelope exist.
7. **Cross-range IDs:** reconcile the proposed inherited IDs and ports with Weeks 0–9 before any canonical graph is created.

No drawing, netlist, simulator input, toolchain choice, or dependency installation is authorized by this draft.
