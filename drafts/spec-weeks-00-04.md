# Phase 1 draft specification: Week 0 and Weeks 1-4

**Status:** Draft for Gate 0 review. This document specifies circuit states; it does not implement a canonical graph, schematic, SVG, or SPICE netlist.

**Binding decisions:** `preflight-decisions.html` and `implementation-plan.html`. In particular, each week is the prior physical chassis plus an explicit delta; ordinary schematic wires and canonical electrical nets remain explicit even though physical patch-cord routing is deferred; hidden op-amp supply pins are permitted only through the Week 0 infrastructure contract; LM301A is the historical baseline; and the future low-voltage redesign remains a separate deferred project.

## Evidence and confidence convention

- **Verified:** stated or visibly shown in Roberge or the TI LM301A datasheet.
- **Derived:** an engineering consequence or proposed value calculated from a verified topology. It still requires Gate 0 approval and later simulation/build validation.
- **TBD:** the current sources do not determine the choice. No drawing or netlist may silently fill it.
- Roberge page references below give both the PDF page number and the printed LibreTexts subsection/page marker visible on that PDF page.

## Cross-week identity and net conventions

Stable module IDs reserved in this range:

| Module ID | Meaning | First present |
|---|---|---:|
| `INF.PWR_ENTRY` | external dual-supply interface and branch protection | W0 |
| `INF.GND_STAR` | signal-ground/power-ground single-point tie | W0 |
| `INF.DECOUP_BOARD` | board bulk bypassing | W0 |
| `AC.INV1` | stock LM301A unity-gain inverter | W1 |
| `AC.SUM1` | stock LM301A weighted inverting summer | W1 |
| `AC.INT1` | stock LM301A inverting integrator | W1 |
| `AC.INT2` | second stock LM301A inverting integrator | W4 |
| `AC.INT3.SOCKET` | reserved, unpopulated future integrator socket | W1 |
| `MEAS.LOOP_INJ1` | temporary loop-injection fixture; not permanent chassis circuitry | W4 |

All op-amp module boundaries expose `IN+`, `IN-`, `OUT`, `V+`, `V-`, `COMP_A`, and `COMP_B`; weekly sheets may hide `V+` and `V-`, but the canonical graph must connect them to `P15_LOCAL` and `N15_LOCAL`. Pin numbers remain package-specific until the exact LM301A package/socket is approved. `SGND` is the SPICE reference node (`0`) in all signal-circuit variants. Stable net names are uppercase and must not be re-used for a different electrical node in later weeks.

Recommended-value tables are part of the specification, not separate authorship: component IDs, values, tolerances, and ratings must ultimately be emitted from the same canonical data as the schematic and SPICE representations.

---

## Week 0 - permanent +/-15 V infrastructure

### End-of-week physical cumulative state

One chassis/backplane exists with an external regulated dual-supply input, protected positive and negative rail branches, a single intentional signal-ground/power-ground tie, board-level bulk bypassing, reserved local-bypass footprints at every future op-amp socket, rail and ground test points, and clearly keyed connectors. No signal-processing op-amp is installed as part of Week 0.

### Active experiment/configuration

Commission the unloaded infrastructure, then test it with a temporary symmetric dummy load. Verify rail polarity, magnitude, ripple/noise, ground continuity, and current limiting before any LM301A is inserted. The physical patch-cord layer is irrelevant this week.

### Inherited circuitry

None.

### Explicit delta

Add `INF.PWR_ENTRY`, `INF.GND_STAR`, `INF.DECOUP_BOARD`, rail/ground test points, and reserved local bypass positions. Establish the hidden-power-pin contract used by all later weekly sheets.

### Sources and evidence

- **Roberge Fig. 11.7 and Sec. 11.3.2, PDF p. 304 (printed 11.3.2):** each amplifier receives 0.1-uF ceramic bypass capacitors from both supply pins to one common input-signal ground point; heavy leads must be short. The figure shows optional approximately 22-ohm series rail resistors and states that board-level solid-tantalum capacitors greater than 1 uF should be used once per circuit board.
- **Roberge Sec. 11.3.1, PDF p. 303 (printed 11.3.1):** excessive supply voltage and reversal are destructive; a resistor-Zener network (Fig. 11.6) is one suggested protection method, while supply crowbar protection is preferable for many amplifiers. The section also recommends antiparallel input clamps where excessive differential input voltage is possible.
- **Roberge Sec. 11.3.3, PDF p. 305 (printed 11.3.3):** signal ground should carry only critical, low-current returns; power ground carries high-current/noncritical returns; the two networks join at one point at the supply return.
- **TI LM101A/LM201A/LM301A datasheet Rev. D, pp. 1-3 and 11-12:** LM301A absolute maximum supply is +/-18 V; normal electrical characteristics are specified at +/-15 V; typical supply current is 1.8 mA and maximum 3.0 mA per channel at +/-15 V; supply reversal greater than 1 V can cause destructive current; bypassing is required at least once per circuit card and may need to be per-amplifier in faster compensation modes. Primary source: <https://www.ti.com/lit/ds/symlink/lm301a-n-mil.pdf>.

### Components, IDs, nets, and boundaries

| ID | Function | Principal nets |
|---|---|---|
| `INF.PWR_ENTRY.J1` | keyed 3-conductor external supply connector | `P15_IN`, `PGND_IN`, `N15_IN` |
| `INF.PWR_ENTRY.FP` / `FN` | replaceable positive/negative branch protection | input rails to `P15_PROT` / `N15_PROT` |
| `INF.PWR_ENTRY.DRP` / `DRN` | reverse-polarity clamp/protection placeholder | **TBD topology**; must not short a correctly connected split supply |
| `INF.GND_STAR.NT1` | sole intentional ground net tie | `PGND_IN`, `PGND`, `SGND` |
| `INF.DECOUP_BOARD.CBP` | positive-rail bulk capacitor | `P15_PROT` to `SGND` |
| `INF.DECOUP_BOARD.CBN` | negative-rail bulk capacitor | `SGND` to `N15_PROT`; polarity explicit |
| `TP.P15`, `TP.N15`, `TP.SGND`, `TP.PGND` | commissioning points | corresponding named nets |
| `DEC.<module>.CP/CN` | reserved local ceramic pair for every op-amp module | `P15_LOCAL`-`SGND`, `SGND`-`N15_LOCAL` |

The local rail aliases map one-to-one to the protected rails unless a module later receives the optional Fig. 11.7 22-ohm isolation resistors. If isolation is fitted, local nets are distinct (`P15_<module>`, `N15_<module>`) and must not be collapsed in either schematic or netlist.

### Symbolic parameters and recommended-value candidates

| Parameter/component | Candidate | Status/rationale |
|---|---:|---|
| External rails | +15.0 V, 0 V, -15.0 V regulated | **Verified baseline** from capstone and TI operating conditions |
| Local ceramics `CP/CN` | 0.1 uF, C0G/X7R, >=50 V | **Verified value** from Fig. 11.7; voltage rating **derived** |
| Board bulk `CBP/CBN` | 10 uF, >=35 V, low-ESR electrolytic; polarity explicit | **Proposed candidate** satisfying Roberge's `>1 uF`; final value and technology require ripple/transient validation |
| Optional rail isolation | 22 ohm, 1%, >=0.25 W per local rail | **Verified nominal** from Fig. 11.7, but use is **TBD** until total current and crosstalk tests are known |
| Branch fuses/current limit | value from worst-case complete-chassis load budget | **TBD**; must be selected after Weeks 5-13 loads are inventoried |
| Overvoltage/reversal network | none selected | **Gate 0 blocker**: source offers alternatives but exact external supply and connector behavior are not specified |

### Practical additions

Keying, branch protection, labeled test points, polarity marks, 35-V capacitor ratings, an enclosure/chassis bond point, and per-socket bypass footprints are implementation additions. Protective earth/chassis bonding is **TBD** because the external supply class (floating SELV bench supply versus mains-powered internal supply) is unspecified. No mains wiring is authorized by this specification.

### Power, test, and loading assumptions

The primary assumption is an external, isolated, regulated, current-limited dual bench supply. Initial current limit should be set just above measured unloaded chassis current and raised only as modules are commissioned. Later high-current regulator/load returns must use `PGND`; signal sources, feedback returns, and op-amp noninverting references use `SGND`. The scope ground may connect to `SGND` only after confirming the bench supply/scope earth relationship.

### Historical and modern notes

Historical implementation follows Fig. 11.7, including solid-tantalum bulk capacitors and optional 22-ohm isolation. The primary modern note is a same-voltage substitution of appropriately rated aluminum/polymer bulk capacitors and keyed shrouded connectors. The deferred low-voltage/rail-to-rail redesign is a separate future project and must not change these rails.

### SPICE verification targets

- **Ideal:** verify +15 V and -15 V polarity at every hidden power-pin endpoint; zero unintended DC path between rails; one and only one `SGND`/SPICE-0 mapping; nominal dummy-load currents.
- **Realistic:** include supply source resistance, fuse/isolation resistance, capacitor ESR/ESL candidates, stepped dummy load, and startup. Confirm local rail droop and cross-rail transient stay within a later-approved tolerance. Protection events cannot be accepted until the protection topology is chosen.

### Expected measurements

`TP.P15 = +15.0 V` and `TP.N15 = -15.0 V` within the supply's verified tolerance; no rail reversal; no continuity between rails with power off other than expected capacitor charging; `SGND` to `PGND` continuity at exactly `NT1`; ripple/noise acceptance **TBD** based on scope bandwidth and future error budget.

### Sheet recommendation

One permanent infrastructure sheet plus a small pin-contract inset for a generic `OPAMP_STOCK` module. Later weekly sheets reference `INF-W0` and do not repeat every bypass capacitor visually, although those parts remain in the canonical graph and netlists.

### Incomplete-state handling and open issues

The chassis is intentionally signal-incomplete at Week 0; only power infrastructure is functional. Gate 0 must resolve: external supply type and connector; fuse/current-limit budget; exact reversal/overvoltage protection; chassis/earth treatment; whether Fig. 11.7 22-ohm resistors are per-device, per-board zone, or omitted; and the exact historical package/socket pinout.

---

## Week 1 - computing core installed and tested separately

### End-of-week physical cumulative state

Week 0 infrastructure remains. Install and retain three independent stock-op-amp modules: `AC.INV1`, `AC.SUM1`, and `AC.INT1`. Install empty, labeled, wired socket positions `AC.INT2.SOCKET` and `AC.INT3.SOCKET`; they are not electrically active. No differential-equation loop is connected at the final Week 1 test configuration.

### Active experiment/configurations

Use one cumulative chassis sheet and three electrically complete detail/configuration views sharing the same physical state:

1. `W1.INV_TEST`: drive `AC.INV1.IN`; measure `AC.INV1.OUT/IN`.
2. `W1.SUM_TEST`: drive at least two `AC.SUM1` inputs; verify the weighted algebraic sum.
3. `W1.INT_TEST`: drive `AC.INT1.IN`; verify the inverting integral and time constant.

Only one external source configuration is active at a time. Other installed modules are shown grey but remain connected to Week 0 power and bypassing.

### Inherited circuitry

All Week 0 power, ground, bypass, protection, and test infrastructure.

### Explicit delta

Add `AC.INV1.U1`, `AC.SUM1.U1`, `AC.INT1.U1`, their passive networks, compensation capacitors, signal jacks/test points, output-isolation resistors, and two empty socket footprints. No state-to-state circuit graph may imply that the empty sockets contain op-amps.

### Sources and evidence

- **Roberge Fig. 1.2a, PDF p. 10 (printed 1.2.2), with derivation on pp. 9-12:** inverting op-amp with input impedance `Z1`, feedback impedance `Z2`, noninverting input grounded; ideal gain `-Z2/Z1`.
- **Roberge Fig. 1.4 and Sec. 1.2.3, PDF p. 13 (printed 1.2.5):** inverting weighted summer; ideal output is the negative weighted sum, with each coefficient `Zf/Zi`.
- **Roberge Sec. 1.2.3, PDF p. 14 (printed 1.2.6):** inverting integrator is Fig. 1.2a with `Z2 = 1/(sC)` and `Z1 = R`, giving `Vo/Vi = -1/(RCs)`. Fig. 1.5 on the same page is a different, noninverting integrator and is not the Week 1 topology.
- **TI LM301A datasheet Rev. D, pp. 1, 3, 8, 11-12:** standard single-pole compensation is 30 pF; minimum compensation values assume source resistance below 10 kohm, summing-node stray capacitance below 5 pF, and load capacitance below 100 pF. The device is not internally unity-gain compensated.

### Components/modules and named nets

| Module | Stable parts | Boundary and internal nets |
|---|---|---|
| `AC.INV1` | `U1`, `RIN1`, `RFB1`, `CC1`, `ROUT1`, `TP1I`, `TP1O` | `N_INV1_IN -> RIN1 -> N_INV1_SUM`; `RFB1: N_INV1_OUT-N_INV1_SUM`; `U1.IN+=SGND`; `U1.OUT=N_INV1_OUT`; isolated jack `N_INV1_JACK` |
| `AC.SUM1` | `U2`, `RIN2A/B/C`, `RFB2`, `CC2`, `ROUT2`, test points | `N_SUM1_IN_A/B/C` through distinct resistors to `N_SUM1_SUM`; `RFB2: N_SUM1_OUT-N_SUM1_SUM`; `U2.IN+=SGND`; isolated jack `N_SUM1_JACK` |
| `AC.INT1` | `U3`, `RIN3`, `CFB3`, `RLEAK3` footprint, `CC3`, `ROUT3`, test points | `N_INT1_IN -> RIN3 -> N_INT1_SUM`; `CFB3: N_INT1_OUT-N_INT1_SUM`; `U3.IN+=SGND`; isolated jack `N_INT1_JACK` |
| reserved sockets | `AC.INT2.SOCKET`, `AC.INT3.SOCKET` | rails and `SGND` may be wired; all signal/comp pins are explicit `NC_RESERVED_*` nets, not silently connected |

`RLEAK3` is a normally-open/absent footprint for a later reset or DC-limiting path; if not populated it must not appear as an electrical component in the Week 1 circuit graph.

### Symbolic parameters and recommended-value candidates

| Function | Symbolic relationship | Candidate | Status |
|---|---|---:|---|
| inverter | `K_INV = -RFB1/RIN1` | `RIN1 = RFB1 = 4.7 kohm`, 1%, 0.25 W | **Verified-compatible/derived:** matches Fig. 3.1's later 4.7-kohm unity inverter |
| summer | `Vo = -RFB2 * sum(Vi/RIN2i)` | `RFB2 = RIN2A = RIN2B = RIN2C = 10 kohm`, 1% | **Proposed candidate**; equal weights preserve simple teaching arithmetic but the absolute impedance is not source-derived |
| integrator | `H(s)=-1/(RIN3*CFB3*s)` | `RIN3=10 kohm`, 1%; `CFB3=1.0 uF` film, <=5%, >=35 V; `tau=10 ms` | **Proposed candidate** yielding the calculated `tau=10 ms`; final time scale, dielectric, and loading remain to be validated |
| compensation | single-pole | `CC1=CC2=CC3=30 pF`, C0G | **Verified manufacturer standard**; capstone's “default that keeps the IC alive” |
| output isolation | protect external test point | `ROUT*=100 ohm`, 1% | **Proposed candidate** motivated by TI's recommendation for current-limiting resistance at test points; value not supplied by TI and must be validated |

### Practical additions

Local bypassing, compensation capacitors, output isolation, labeled test points, empty-socket labels, and input return resistors/pull-down footprints are implementation additions. A bias-current compensation resistor at each noninverting input is deferred pending the intended resistance match; grounding `IN+` directly is faithful to the figures but increases bias-current-related offset. Any later addition must be explicit.

### Power, test, and loading assumptions

All LM301As use +/-15 V. Tests use a generator with known 50-ohm source impedance and a scope input of at least 1 Mohm in parallel with its measured capacitance. Keep external capacitive load below 100 pF for the minimum 30-pF compensation assumption, or isolate/overcompensate. Limit outputs to approximately +/-10 V for later comparability with TI characterized conditions; exact safe swing depends on load.

### Historical and modern notes

Primary devices are LM301A with external compensation. A 741-class alternative must be a separately declared device variant because it is normally internally compensated and has different pins/dynamics; it cannot inherit `CC1-CC3` silently. Same-voltage modern substitutes may be noted later, but the low-voltage redesign remains deferred.

### SPICE verification targets

- **Ideal:** `W1.INV_TEST` DC/AC gain -1; `W1.SUM_TEST` each input coefficient -1; `W1.INT_TEST` AC magnitude `1/(omega*tau)`, phase +90 degrees relative to the negative sign convention, and square-wave-to-triangle slope `dVo/dt=-Vi/tau`.
- **Realistic:** use one documented LM301A macro-model with explicit 30-pF compensation; verify stability, bias/offset drift direction, finite gain/bandwidth, slew, output swing into the specified load, and the effect of `ROUT*` plus scope capacitance. A 741 model is a separate comparison variant.

### Expected measurements

Inverter gain approximately -1 at low frequency; summer output approximately `-(VA+VB+VC)` for equal resistors; integrator slope approximately `-Vi/10 ms`. A suggested integrator test is a +/-1-V, 20-Hz square wave, predicting 2.5 V output change per half-cycle before offset/drift; confirm no saturation. Numerical error bands are **TBD** pending resistor/capacitor tolerances and model choice.

### Sheet recommendation

One cumulative main sheet, with three compact active-test details or overlays. The main sheet must show all three installed modules and both empty sockets; the active detail shows source/load connections and explicit nets. This is an approved presentation split, not three different physical builds.

### Incomplete-state handling and open issues

The two reserved sockets are visibly unpopulated. Gate 0 must approve the exact package/socket, integrator time scale and capacitor technology, number of summer inputs, noninverting bias compensation policy, output-isolation value, and what constitutes an acceptable measurement error. Procurement status of LM301A PDIP parts is not established by this draft.

---

## Week 2 - first-order closed loop

### End-of-week physical cumulative state

No new soldered module is added. The entire Week 1 core and empty sockets remain. A complete electrical configuration closes a first-order loop; physical front-panel cord geometry remains deferred, but the corresponding named electrical nets are mandatory in the schematic and netlist.

### Active experiment/configurations

**Provisional configuration requiring Gate 0 approval:** use all three installed blocks to obtain the correct sign without inventing a noninverting summer:

`N_INT1_OUT (= x) -> AC.SUM1 input A -> N_SUM1_OUT (= -x) -> AC.INV1 -> N_INV1_OUT (= +x) -> AC.INT1 input -> N_INT1_OUT`.

With unity `SUM1` and `INV1` gains and `tau=RIN3*CFB3`, the inverting integrator gives `dx/dt=-x/tau`. Unused summer inputs are tied to `SGND` through their normal input resistors or explicitly disconnected according to the final patchbay convention; they must not float ambiguously.

### Inherited circuitry

All Week 1 hardware and its 30-pF LM301A compensation.

### Explicit delta

Electrical-only reconfiguration: add named configuration connections `W2_FB_X_TO_SUM`, `W2_SUM_TO_INV`, and `W2_INV_TO_INT`. No permanent component is added. The Week 1 test-source nets are disconnected or set to zero explicitly in this configuration.

### Sources and evidence

- **Roberge Fig. 2.2, PDF pp. 23-24 (printed 2.2.1 and 2.3.1):** a generic negative-feedback block diagram, not a construction schematic for `dx/dt=-x`.
- **Roberge Fig. 2.3 and Sec. 2.3.1, PDF p. 25 (printed 2.3.2):** compares open-loop gain 10 with a high-forward-gain closed-loop system producing approximately 9.9 and desensitizing gain variation. It does not prescribe this analog-computer wiring.
- **Roberge Fig. 2.9 and Sec. 2.4.1, PDF pp. 32-34 (printed 2.4.3-2.4.5):** detailed model and block diagram of an inverting amplifier including input/output impedance and a disturbance source; again, not the first-order ODE circuit.
- **Roberge Sec. 1.2.3, PDF p. 14:** supplies the actual integrator relationship required to derive the loop equation.

### Components/modules and named nets

No new permanent component IDs. The active boundary contains `AC.SUM1`, `AC.INV1`, and `AC.INT1`. `N_INT1_OUT` is the state `x`; `N_SUM1_OUT` is `-x`; `N_INV1_OUT` is the integrator drive `+x`; `N_INT1_SUM` is the integrator summing junction and is never exported to a jack. `N_INT1_JACK` may be loaded only through `ROUT3`.

### Symbolic parameters and recommended-value candidates

`K_SUM=RFB2/RIN2A`, `K_INV=RFB1/RIN1`, and `tau=RIN3*CFB3`; the loop realizes `dx/dt=-(K_SUM*K_INV/tau)x`. Provisional values inherit Week 1 (`K_SUM=K_INV=1`, `tau=10 ms`). A configurable initial-condition injection mechanism is **TBD**; without an initial condition or external impulse, the ideal homogeneous loop remains at zero.

### Practical additions

A loop-break/injection point and initial-condition injection are necessary for repeatable teaching measurements but are not supplied by the cited figures. They may be temporary measurement connections, not new permanent chassis circuits. The schematic must show them only in the configuration that uses them.

### Power, test, and loading assumptions

All three op amps remain at +/-15 V with Week 0 bypassing. Scope loading is applied at isolated output jacks, not at summing nodes. “Loading from the next jack” is **not yet electrically defined**: a 1-Mohm scope load should not materially change a 10-ms active integrator time constant, while a deliberately low resistance at an op-amp output mainly stresses the output stage rather than changing ideal `RC`.

### Historical and modern notes

LM301A remains primary with 30-pF standard compensation; 741-class comparison stays separate. No modern or low-voltage topology is introduced.

### SPICE verification targets

- **Ideal:** verify the exact closed-loop characteristic pole at `s=-(K_SUM*K_INV)/tau`; run an initial-condition transient and compare fitted decay constant to the formula. Sweep a deliberately parameterized forward-gain model to reproduce Fig. 2.3 desensitivity as a teaching-only model variant, not as a different physical topology.
- **Realistic:** use LM301A models and 30-pF compensation; fit decay, quantify finite-gain/time-delay error, test declared jack loads, and confirm adequate phase/gain margin. Explicitly separate loop-injection fixtures from the permanent graph.

### Expected measurements

For unity gains and `tau=10 ms`, ideal state decay is `x(t)=x(0)e^(-t/10 ms)`. Measure the 36.8% point at one time constant and fit the full decay. Closed/open comparison and loading acceptance are **TBD** until the measurement topology and load are defined.

### Sheet recommendation

One cumulative main sheet showing the complete Week 1 hardware, with all three active blocks normal-weight and the configuration connections coral. Empty sockets remain grey. No separate detail is needed if the full transistor-independent circuit remains readable.

### Incomplete-state handling and open issues

There is no physically incomplete module. There are three Gate 0 blockers:

1. The capstone says “using only the summer and integrator,” but two cascaded inverting blocks form the wrong sign for stable `dx/dt=-x`. The provisional three-block chain above gives the correct sign. A direct self-loop around the integrator is a simpler correct alternative but does not use the summer. One must be approved.
2. Figures 2.2 and 2.9 are explanatory block/model diagrams, not wiring authorities; calling the weekly circuit “drawn as” either figure overstates the source.
3. “Closed-loop gain vs open-loop” and “loading from the next jack changes the time constant” lack safe, unambiguous hardware definitions.

---

## Week 3 - transient and compensation characterization

### End-of-week physical cumulative state

All Week 2 hardware and loop-capable wiring remain. No new functional module is added. `AC.INT1.CC3` becomes a deliberately selectable/measured compensation element. The end-of-week installed value is `CC3_SELECTED`, chosen from the experiment by a declared criterion and recorded; the rejected value is not shown as simultaneously connected.

### Active experiment/configurations

Keep the approved Week 2 loop topology electrically unchanged and run separate source/model configurations for step, ramp, `CC3=220 pF`, and `CC3=12 pF`. A temporary stimulus/initial-condition connection may change between runs; the feedback path does not. “Better” must be defined before selection (recommended criteria: stable nonoscillatory decay, no sustained ringing, acceptable rise/settling time, and no slew-induced corruption).

### Inherited circuitry

All Week 2 physical circuitry. The pre-Week-3 compensation value is the 30-pF manufacturer-standard candidate from Week 1.

### Explicit delta

Add a safe compensation-selection mechanism or socketed capacitor position for `CC3`; characterize 220 pF and 12 pF one at a time; replace 30 pF with the measured `CC3_SELECTED` at the end of the week. This is a documented value replacement, not a strict component superset.

### Sources and evidence

- **Roberge Fig. 3.1 and Sec. 3.1, PDF pp. 49-50 (printed 3.1.1-3.1.2):** LM301A unity-gain inverter with two 4.7-kohm resistors, driven by a -50-mV step; responses are compared for 220-pF and 12-pF compensation. Roberge describes the former as approximately first-order and the latter as approximately second-order/ringing.
- **Roberge Secs. 3.3.1-3.3.2, PDF pp. 58-59 (printed 3.3.1-3.3.2):** step/ramp test selection and approximation of transient responses.
- **TI LM301A datasheet Rev. D, pp. 1, 8, 11-12:** 30 pF is the standard single-pole compensation; smaller minimum values require source resistance below 10 kohm, summing-node stray capacitance below 5 pF, and capacitive load below 100 pF; overcompensation may be necessary otherwise.

### Components/modules and named nets

The only new stable hardware identity is `AC.INT1.CCSEL3` if a selector/socket is approved. Its mutually exclusive states connect `AC.INT1.U3.COMP_A` to `COMP_B` through exactly one of `CC3_12P`, `CC3_30P`, or `CC3_220P`. The canonical configuration must reject multiple simultaneous capacitors unless their parallel sum is explicitly intended. `N_W3_STIM` and `N_W3_RAMP` are temporary source nets; `N_INT1_OUT` remains state `x`.

### Symbolic parameters and recommended-value candidates

| Item | Candidate | Status |
|---|---:|---|
| slow/overcompensated case | 220 pF C0G | **Verified** from Fig. 3.1 |
| fast/underdamped case | 12 pF C0G | **Verified** from Fig. 3.1 |
| prior baseline | 30 pF C0G | **Verified** from TI standard compensation |
| end-of-week default | `CC3_SELECTED in {12 pF, 220 pF}` | **TBD by measurement criterion**; likely 220 pF for stability, but not preselected |
| exact Fig. 3.1 test resistors/input | 4.7 kohm/4.7 kohm, -50 mV step | **Verified**; applies to the reference inverter, not automatically to the Week 2 loop |

### Practical additions

Power-off-only capacitor selection, ESD-safe handling of compensation pins, a selector that adds minimal stray capacitance, and explicit labeling are required. A relay or switch may itself invalidate the 12-pF experiment through parasitics; a socketed capacitor with power removed is the preferred provisional approach.

### Power, test, and loading assumptions

Same +/-15 V rails and scope-loading limits as Weeks 1-2. For faithful comparison, record generator edge rate, amplitude, scope probe capacitance, output amplitude, temperature, and supply. Never move a compensation capacitor while powered.

### Historical and modern notes

This week is specifically LM301A behavior. A 741-class device cannot reproduce external 12/220-pF compensation without becoming a different experiment; document it as a qualitative internally compensated comparator only. Low-voltage redesign remains deferred.

### SPICE verification targets

- **Ideal:** ideal op amps have no meaningful compensation pins; use the unchanged Week 2 ideal topology solely to verify stimulus and first-order equation.
- **Realistic:** run separate LM301A 12-pF, 30-pF, and 220-pF variants from the same canonical topology; compare overshoot, ringing frequency, 2% settling time, fitted dominant pole, slew rate, and stability. Confirm each netlist differs only in the declared compensation state and stimulus.

### Expected measurements

Reference expectation from Fig. 3.1: 220 pF is slower and approximately first-order; 12 pF is faster and visibly underdamped. The actual Week 2 loop will not numerically reproduce Fig. 3.1 because its topology and excitation differ. Record step/ramp tracking error and select `CC3_SELECTED` by the approved criterion.

### Sheet recommendation

One cumulative Week 3 main sheet plus a small mutually-exclusive compensation-state inset/table. Do not draw three capacitors as though connected in parallel. A separate reference detail may reproduce the Fig. 3.1 inverter only if clearly labeled “reference test circuit, not cumulative chassis configuration.”

### Incomplete-state handling and open issues

No module is incomplete, but the final value is empirically unresolved until the experiment. Gate 0 must resolve whether Week 3 is (a) an adaptation on the unchanged Week 2 loop, as the capstone demands, or (b) an exact temporary Fig. 3.1 unity-inverter configuration followed by restoration of the loop. It cannot be described as an exact repeat while also leaving the loop unchanged.

---

## Week 4 - second integrator and second-order loop

### End-of-week physical cumulative state

Retain all Week 3 hardware and its recorded `CC3_SELECTED`. Populate `AC.INT2` in the reserved Week 1 socket as a second stock LM301A inverting integrator with its own input resistor, feedback capacitor, compensation capacitor, bypass pair, isolated output jack, and test points. `AC.INT3.SOCKET` remains visibly empty. Configure `AC.SUM1`, `AC.INT1`, and `AC.INT2` as one second-order loop; retain `AC.INV1` physically and show it grey unless the approved sign/damping topology uses it.

### Active experiment/configurations

**Provisional minimal configuration:** harmonic-oscillator loop

`N_INT2_OUT (=x) -> AC.SUM1 input A -> N_SUM1_OUT -> AC.INT1 -> N_INT1_OUT -> AC.INT2 -> N_INT2_OUT`.

For two equal inverting integrators with `tau1`, `tau2` and an inverting summer coefficient `Kx`, the ideal characteristic equation is `s^2 + Kx/(tau1*tau2)=0`, so `omega0=sqrt(Kx/(tau1*tau2))`. A temporary `MEAS.LOOP_INJ1` breaks one named intermodule net for Bode injection while preserving DC operating conditions. The measurement configuration and the free-run/initial-condition configuration are separate canonical states sharing the same permanent hardware.

### Inherited circuitry

All Week 3 circuitry. Week 2/3 first-order patch connections are not simultaneously active if they would short module outputs or create an additional loop; their physical cable routing is deferred, while their disconnected electrical state is explicit.

### Explicit delta

Populate `AC.INT2.U4`, `RIN4`, `CFB4`, `CC4`, `ROUT4`, local bypassing, and test points. Replace the first-order active configuration with the second-order named connections. Add only temporary `MEAS.LOOP_INJ1` during loop-gain measurement.

### Sources and evidence

- **Roberge Fig. 4.21 and Sec. 4.4.2, PDF p. 105 (printed 4.4.6):** defines phase margin, gain margin, and unity-gain/crossover frequency from loop transmission. It is a loop-quantity diagram, not a two-integrator circuit.
- **Roberge Sec. 4.4.2, PDF pp. 104-105:** provides Bode stability rules for systems without right-half-plane loop singularities and with conventional negative feedback.
- **Roberge Sec. 1.2.3, PDF p. 14:** supplies each inverting-integrator relationship.
- The capstone supplies no actual second-order differential equation, damping term, feedback coefficient, injection method, or component values.

### Components/modules and named nets

| Module/part | Stable identity | Principal nets |
|---|---|---|
| second integrator | `AC.INT2.U4`, `RIN4`, `CFB4`, `CC4`, `ROUT4` | `N_INT2_IN`, `N_INT2_SUM`, `N_INT2_OUT`, `N_INT2_JACK`; hidden rails per Week 0 |
| second-order state 1 | `AC.INT1` | `N_INT1_OUT`, provisionally proportional to `-dx/dt` under the stated sign convention |
| second-order state 2 | `AC.INT2` | `N_INT2_OUT = x` |
| feedback coefficient | existing `AC.SUM1.RIN2A/RFB2` or approved selectable resistor | `N_INT2_OUT` to `N_SUM1_SUM` |
| injection fixture | `MEAS.LOOP_INJ1` | `N_LOOP4_RETURN_A`, `N_LOOP4_RETURN_B`; never collapse these while injection is active |

Every loop diagram must state the adopted sign convention and verify it algebraically. Labels `x`, `dx/dt`, and `d2x/dt2` must follow measured node equations rather than decorative left-to-right assumptions.

### Symbolic parameters and recommended-value candidates

| Item | Candidate | Status |
|---|---:|---|
| `RIN4`, `CFB4` | 10 kohm, 1%; 1.0 uF film, <=5%, >=35 V | **Proposed candidate** matching the provisional INT1 scale; calculated `tau2=10 ms` |
| `CC4` | 30 pF C0G initially | **Verified manufacturer-standard candidate**; whether it should equal Week 3's selected `CC3` is **TBD** |
| oscillator coefficient `Kx` | 1.0 nominal, adjustable around unity | **Proposed candidate**; exact range/implementation **TBD** |
| ideal natural frequency | `omega0=sqrt(Kx/(tau1*tau2))` | **Derived**; with equal 10-ms constants and `Kx=1`, `f0 ~=15.9 Hz` |
| loop-injection network | topology/value not selected | **Gate 0 blocker**; must not disturb bias or create unsafe open-loop saturation |

### Practical additions

Provide a controlled initial-condition mechanism, loop-break/injection point, selectable gain with a bounded safe range, output isolation, and clear state-node test points. These are build additions absent from Fig. 4.21. A reset/hold switch is not yet installed; the full three-mode system belongs to Week 11, so any Week 4 initial-condition mechanism must be explicitly temporary.

### Power, test, and loading assumptions

Both integrators use +/-15 V and Week 0 bypassing. Scope/generator loading must be included in the loop model. Limit initial conditions to prevent outputs exceeding approximately +/-10 V under characterized loads. A frequency-response analyzer or two-channel generator/scope method is assumed but not selected; injection must maintain the loop's DC path.

### Historical and modern notes

Both integrators use LM301A as the historical baseline. `AC.INT1` retains its Week 3 selected compensation, while `AC.INT2` begins with 30 pF unless Gate 0 chooses matched compensation. A 741-class pair is a documented alternative experiment only. No low-voltage redesign is introduced.

### SPICE verification targets

- **Ideal:** derive and numerically confirm the characteristic polynomial; for the provisional oscillator, poles at `+/-j*sqrt(Kx/(tau1*tau2))`; verify state-node phase/amplitude relations and exact loop-net continuity. Demonstrate that changing `Kx` changes frequency, not ideal damping.
- **Realistic:** use two declared LM301A models and their actual compensation values; inject AC at the approved break; compute loop gain with an explicit sign convention; extract crossover, phase margin, and gain margin; sweep `Kx` to find the measured/modelled marginal-stability point; run startup/initial-condition transients and distinguish saturation/slew from small-signal stability.

### Expected measurements

For the provisional equal-10-ms, unity-coefficient loop, ideal frequency is about 15.9 Hz and ideal damping is zero. Real hardware will grow or decay depending on excess phase/gain and nonlinear limits. Record `L(jw)`, crossover, phase margin, gain margin, oscillation frequency, amplitude envelope, and critical gain under a specified injection/sign convention. Acceptance bands are **TBD** until the circuit and instrument are fixed.

### Sheet recommendation

One cumulative main sheet should remain readable at this stage. Show `SUM1 -> INT1 -> INT2 -> SUM1` in normal weight, Week 4 additions in coral, `INV1` and the empty `INT3` position grey, and explicit named state/test nets. Add one measurement detail sheet for `MEAS.LOOP_INJ1` if the injection circuitry would obscure the loop.

### Incomplete-state handling and open issues

`AC.INT3.SOCKET` remains unpopulated; no future reset/hold hardware may be anticipated. Gate 0 must resolve:

1. the actual second-order ODE/characteristic equation and whether damping feedback is required;
2. the sign assignment and whether `AC.INV1` participates;
3. the meaning of “find the gain that puts the computer on the j-omega axis,” because the provisional ideal two-integrator oscillator is on that axis for every positive `Kx` and gain changes frequency rather than damping;
4. a safe loop-injection method and instrument assumptions;
5. `AC.INT2` compensation relative to Week 3's selected `AC.INT1` compensation.

---

## Gate 0 blockers and decisions requested from the integrator/user

1. **Week 0 protection authority:** specify external supply type, connector, load budget, and reversal/overvoltage strategy; do not improvise mains or crowbar circuitry.
2. **Week 1 build constants:** approve socket/package, summer input count, 10-ms integrator candidate, capacitor technology, and bias/output protection policy.
3. **Week 2 sign/topology:** choose the provisional three-block stable loop, the direct integrator self-loop, or revise the learning objective. The current capstone wording and a two-block inverting SUM+INT chain cannot all be true simultaneously.
4. **Week 2 measurements:** define a safe “open-loop” comparison and the exact load whose effect is to be measured.
5. **Week 3 fidelity:** choose unchanged-loop adaptation versus exact temporary Fig. 3.1 inverter test, and define “better” compensation.
6. **Week 4 mathematics:** choose the concrete second-order equation, damping/gain parameter, sign convention, and loop-injection method.
7. **Model source:** ideal primitive and realistic LM301A/741 macro-model sources remain intentionally open under `OPEN-04`; no model has been selected or installed.

## Deferred-project carry-forward

- `D-01`: physical patch-cord routing/labels/drawings; electrical nets are not deferred.
- `D-02`: separate low-voltage/rail-to-rail redesign.
- `D-03`: full parallel modern schematics unless topology materially changes; same-voltage substitutions may be noted.
- `D-04`: chassis placement, harness routing, grounding geometry, thermal layout, and construction photographs. Week 0 electrical infrastructure remains in scope.

## Source limitations

The LibreTexts PDF preserves the relevant Roberge text and figures, but equation text extraction is incomplete; figures and equations cited above were visually inspected on the stated PDF pages. Figures 2.2, 2.3, 2.9, and 4.21 are conceptual/model/measurement references, not finished weekly construction schematics. Recommended component values beyond those explicitly cited are candidates, not claims that Roberge specified them.
