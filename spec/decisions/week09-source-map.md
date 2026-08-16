# Week 9 Figure 9.1 source-transcription map

Status: **Transcription A / preparation only — not a circuit graph**  
Authority: local `op_amps_roberge.pdf`, `capstone.html`, approved Gate 0 record, and the Week 5–9 annex  
Implementation boundary: this file does not authorize encoding, select substitutes/models, or resolve unclear source junctions by inference.

## 1. Source locators inspected

| Source | Local PDF page | Use |
|---|---:|---|
| Figure 9.1 and §9.1.1 | 239 | Complete amplifier, visible values/types, rails, compensation terminals, quiescent currents |
| §9.1.2 | 240–241 | Device roles, bias rationale, matching, current levels, current limit, bypass rationale |
| Figure 9.6 and §9.2.3 | 247–248 | Resolves compensation boundary: base of Q5 to source of Q8 |
| Figure 9.7 | 249 | 20 pF example and sensitivity to sub-pF/stray feedback |
| Figure 9.8 and Figure 9.9 | 253 | Inverting fixture, attenuation equation, loop-crossover dependence |
| Figure 9.10 | 254 | Small-signal step campaign and capacitor values |
| Figure 9.11 / Figure 9.12 | 254–255 | Attenuation/compensation comparison and large-signal slew campaign |

Evidence labels below:

- **V-TEXT** — explicitly stated in prose.
- **V-FIG** — directly visible in a figure.
- **V-BOTH** — stated and visible.
- **UNCERTAIN** — raster crossing, polarity, tolerance mark, or boundary still needs independent confirmation.

Figure 9.1 is a compact raster schematic. This document is the first transcription pass. Gate 0 requires an independent second pass before any canonical graph is accepted.

## 2. Inherited chassis boundary

Week 9 does not create a separate bench amplifier. It completes `AMP1` in retained `SLOT.INT1`. Any `CORE.*` or `INFRA.*` labels visible in earlier drafts are retired and are not used below.

### Permanent `AMP1` external terminals

| Proposed terminal | Source meaning | End-of-week chassis mapping |
|---|---|---|
| `AMP1.INV_IN` | Q1 base, inverting input | summing-node boundary of `MOD.INT1.NET` in restored integrator configuration; exact local-net ID is assigned during canonical encoding |
| `AMP1.NONINV_IN` | Q2 base, noninverting input | `SGND` in Figure 9.8 and the restored inverting integrator |
| `AMP1.OUT` | junction of the two 22 Ω output resistors | capacitor-return and output-jack boundaries of `MOD.INT1.NET` in restored integrator configuration |
| `AMP1.COMP_A` | Q5 base | one terminal of removable compensation network |
| `AMP1.COMP_B` | Q8 source | other terminal of removable compensation network |
| `AMP1.VP15` | +15 V rail | `P15` |
| `AMP1.VN15` | −15 V rail | `N15` |
| `AMP1.AGND` | circuit common | `SGND` |

`AMP1.COMP_A = base(Q5)` and `AMP1.COMP_B = source(Q8)` are **V-TEXT** from PDF pp. 247–248, not an interpretation of the drawing.

### Retained modules outside `AMP1`

- `DEV.U_INV1`, `DEV.U_SUM1`, `DEV.U_INT2`, `OSC1`, and `REG1` remain physically installed.
- `SLOT.INT1`, `MOD.INT1.NET`, its future component-level feedback-capacitor ID, input network, output jack, and other retained channel hardware remain.
- `DEV.U_INT1_STOCK` stays removed off-circuit. `DEV.U_INT2` remains the stock LM301A comparison channel.
- Week 7/8 temporary parts not present in the accepted Figure 9.1 transcription must be listed as explicit removals; they may not disappear through visual omission.

## 3. Active-device ledger

| ID | Historical type | Role / verified connectivity anchor | Evidence |
|---|---|---|---|
| `AMP1.Q1` | 2N5963 NPN | inverting-input transistor; base=`INV_IN`; emitter=`N_TAIL`; collector=`N_Q1_COL` | V-BOTH |
| `AMP1.Q2` | 2N5963 NPN | noninverting-input transistor; base=`NONINV_IN`; emitter=`N_TAIL`; collector=`N_Q2_COL_Q5_BASE` | V-BOTH |
| `AMP1.Q3` | 2N3707 NPN | 20 µA tail current source; collector=`N_TAIL`; base=`N_BIAS_NEG` | V-BOTH; emitter-network detail below |
| `AMP1.Q4` | 2N4250 PNP | DC-drift-reducing half of matched Q4/Q5 pair; base driven from Q1 collector; not part of AC signal path | V-TEXT/V-FIG |
| `AMP1.Q5` | 2N4250 PNP | high-gain-stage input; base=`N_Q2_COL_Q5_BASE`; with Q6 forms cascode | V-BOTH |
| `AMP1.Q6` | 2N4250 PNP | common-base/cascode device; collector is high-resistance node | V-BOTH |
| `AMP1.Q7` | 2N3707 NPN | approximately 50 µA current-source load for cascode; collector=`N_HIGH_Z`; base=`N_BIAS_NEG` | V-BOTH |
| `AMP1.Q8` | TIS58 JFET | source follower; gate=`N_HIGH_Z`; drain=`VP15`; source=`N_FET_SOURCE` | V-BOTH |
| `AMP1.Q9` | 2N3707 NPN | approximately 2 mA source/sink for the buffer/output-bias string; base=`N_BIAS_NEG` | V-BOTH |
| `AMP1.Q10` | 2N2219 NPN | positive-output emitter follower; collector=`VP15`; emitter drives upper 22 Ω resistor | V-BOTH |
| `AMP1.Q11` | 2N2905 PNP | negative-output emitter follower; collector=`VN15`; emitter drives lower 22 Ω resistor | V-BOTH |
| `AMP1.Q12` | 2N3707 NPN | positive-current limiter sensing the upper 22 Ω resistor | V-BOTH |
| `AMP1.Q13` | 2N4250 PNP | negative-current limiter sensing the lower 22 Ω resistor | V-BOTH |

Source role summary, PDF pp. 239–241:

- Signal path: Q1/Q2, Q5/Q6, Q8, Q10/Q11.
- Current sources: Q3, Q7, Q9.
- DC drift reduction: Q4 with Q5.
- Output-current limit: Q12/Q13 with the two 22 Ω resistors.

## 4. Provisional internal-net ledger

These names prepare a second transcription; they are not yet canonical IDs.

| Provisional net | Pins/elements that appear connected | Confidence / check |
|---|---|---|
| `N_TAIL` | Q1.E, Q2.E, Q3.C | V-FIG; supported by 20 µA tail description |
| `N_Q1_COL` | Q1.C, Q4.B, lower terminal of left 300 kΩ branch, one terminal of 0.01 µF bypass | V-FIG; exact bypass reference rail must be rechecked |
| `N_Q2_COL_Q5_BASE` | Q2.C, Q5.B, lower terminal of right 300 kΩ branch, `COMP_A` | Q5-base compensation identity V-TEXT; balance-branch junction V-FIG |
| `N_Q45_EMIT` | Q4.E, Q5.E, lower end of 33 kΩ emitter resistor, lower end of 3.3 µF bypass | V-FIG plus §9.1.2 bypass rationale; verify electrolytic polarity |
| `AGND` at Q4 collector | Q4.C to ground | V-FIG; independently confirm transistor symbol orientation |
| `N_Q5C_Q6E` | Q5.C, Q6.E | V-TEXT cascode role and V-FIG |
| `N_Q6_BASE` | Q6.B, lower end of 4.7 kΩ, top of 10 kΩ-to-ground branch, top of 1.0 µF-to-ground branch | V-FIG; distinguish from nearby compensation trace |
| `N_HIGH_Z` | Q6.C, Q7.C, Q8.G | V-TEXT/V-FIG; critical high-impedance node |
| `N_FET_SOURCE` | Q8.S, Q10.B drive, top of diode bias string, Q12 collector/drive-steal path, `COMP_B` | Q8-source compensation identity V-TEXT; limiter junction needs second pass |
| `N_OUT_P_SENSE` | Q10.E, upper end of upper 22 Ω, Q12.B | V-FIG/V-TEXT current-limit explanation |
| `AMP1.OUT` | lower end upper 22 Ω, upper end lower 22 Ω, Q12/Q13 sense-emitter junction | V-FIG; verify limiter emitter orientation |
| `N_OUT_N_SENSE` | Q11.E, lower end of lower 22 Ω, Q13.B | V-FIG/V-TEXT current-limit explanation |
| `N_BIAS_STRING_LOW` | bottom of diode string, Q11.B drive, Q9.C, Q13 collector/drive-steal path | V-FIG; second pass required at crossings |
| `N_BIAS_NEG` | Q3.B, Q7.B, Q9.B, bias diode/resistor/bypass network | V-FIG/V-TEXT common bias network |

### High-risk net checks before encoding

1. Confirm Q4/Q5 emitter-node routing to the 33 kΩ resistor and 3.3 µF capacitor.
2. Confirm `N_Q6_BASE` is isolated from the line leading to `COMP_A`; the raster uses close crossings.
3. Confirm both limiter-transistor collector/emitter pin orientations from symbols and §9.1.2 operation.
4. Confirm the exact diode-string endpoints between `N_FET_SOURCE` and `N_BIAS_STRING_LOW`.
5. Confirm no junction dot is lost where `N_HIGH_Z` routes to the Q8 gate.

## 5. Passive and diode transcription ledger

### Values clearly visible in Figure 9.1

| Proposed part/group | Visible value | Apparent connection/function | Status |
|---|---:|---|---|
| `R_COL1`, `R_COL2` | 300 kΩ each | Q1/Q2 collector/balance loads | V-FIG; both appear precision-marked |
| `R_BAL` | 50 kΩ potentiometer | balance between the two 300 kΩ branches, fed through a diode from +15 V | V-FIG; wiper and diode orientation require second pass |
| `C_Q4BASE_BYP` | 0.01 µF | bypasses Q4 base/first collector node at higher frequency | V-FIG plus prose rationale; exact upper endpoint recheck |
| `R_Q45_EMIT` | 33 kΩ | Q4/Q5 emitter-circuit resistor to +15 V | V-FIG; appears precision-marked |
| `C_Q45_EMIT` | 3.3 µF, 10 V | AC bypass across Q4/Q5 emitter resistor | V-FIG/V-TEXT; polarity appears + at +15 V |
| `R_Q6_BIAS_P` | 4.7 kΩ | +15 V to Q6 base-bias node | V-FIG |
| `R_Q6_BIAS_G` | 10 kΩ | Q6 base-bias node to ground | V-FIG |
| `C_Q6_BIAS` | 1.0 µF | Q6 base-bias node to ground | V-FIG; type/polarity not marked |
| `R_Q3_SET_5K6` | 5.6 kΩ fixed resistor | Q3 emitter-current-setting branch | V-FIG and independently adjudicated against operating prose; only the 1% precision dot remains raster-uncertain |
| `R_Q3_SET` | 180 kΩ | Q3 emitter branch to −15 V | V-FIG; appears precision-marked |
| `C_BIAS_FAST` | 0.1 µF | `N_BIAS_NEG` to ground | V-FIG |
| `R_BIAS_DIODE` | 1.5 kΩ | common-bias temperature-compensation branch | V-FIG; appears precision-marked; diode orientation recheck |
| `C_BIAS_BULK` | 33 µF, 10 V | `N_BIAS_NEG` to −15 V bypass | V-FIG/V-TEXT; + appears at bias node |
| `R_Q7_SET` | 68 kΩ | Q7 emitter to −15 V | V-FIG; appears precision-marked |
| `R_Q9_SET` | 1.5 kΩ | Q9 emitter to −15 V | V-FIG; precision mark not confidently visible |
| `R_OUT_P`, `R_OUT_N` | 22 Ω each | output-current sense/emitter resistors | V-BOTH |
| `D_OUT1`, `D_OUT2` | value/type not stated | two-diode output bias string | V-BOTH topology; type and polarity require exact symbol check |
| `D_BAL_TC` | value/type not stated | temperature compensation in balance/load network | V-TEXT/V-FIG; orientation recheck |
| `D_BIAS_TC` | value/type not stated | common current-source bias temperature compensation | V-TEXT/V-FIG; orientation recheck |

### Rail bypass, inside `AMP1` source implementation

| Part | Value | Connection | Status |
|---|---:|---|---|
| `DEC_VP_FAST` | 0.1 µF | +15 V to ground | V-BOTH |
| `DEC_VP_BULK` | 15 µF, 20 V | +15 V to ground | V-BOTH; + at +15 V |
| `DEC_VN_FAST` | 0.1 µF | −15 V to ground | V-BOTH |
| `DEC_VN_BULK` | 15 µF, 20 V | −15 V to ground | V-BOTH; + at ground, − at −15 V |

These local bypass parts are shown in Figure 9.1 even though the chassis also has a permanent infrastructure sheet. They must not be deleted as “duplicate infrastructure” without an explicit design decision.

### Precision-mark uncertainty

Figure 9.1 states that a dot denotes a 1% metal-film resistor. Dots appear next to the two 300 kΩ resistors and several bias resistors, apparently including 33 kΩ, 180 kΩ, the bias 1.5 kΩ, and 68 kΩ. Raster ambiguity prevents a release-quality exhaustive list here. The second transcription must record the dot/non-dot state for every resistor.

## 6. Verified quiescent/design targets

| Quantity | Source value / statement | Evidence |
|---|---|---|
| Rails | ±15 V | V-BOTH |
| Intended maximum output | approximately ±10 V | V-TEXT |
| Q1/Q2 current | approximately 10 µA each | V-BOTH |
| Q3 tail current | approximately 20 µA total | V-BOTH |
| Q6/Q7 cascode branch | approximately 50 µA | V-FIG and analysis context |
| Q8/Q9 buffer branch | approximately 2 mA | V-FIG |
| Output current limit | approximately 25–30 mA | V-TEXT; set by ~600 mV across 22 Ω |
| Q1/Q2 matching | 2N5963 pair selected within 3 mV VBE and 10% beta at operating current; close thermal proximity | V-TEXT |
| Q4/Q5 | matched 2N4250 pair | V-BOTH |
| Cascode contribution | source discussion estimates gain about 180,000 in this portion | V-TEXT; not a build acceptance value by itself |

The source explicitly warns that detailed analytical predictions can be wrong by a factor of two or more because transistor parameters and high-frequency models are uncertain. These targets cannot substitute for operating-point verification.

## 7. Figure 9.8 measurement graph transcription

Figure 9.8 is a temporary measurement configuration over the same physical `AMP1`.

### Fixture nets/components

| Item | Exact source connection |
|---|---|
| `W09.VIN` | source referenced to ground |
| `W09.RIN` | `R1` from `VIN` to `W09.SUM` |
| `W09.RFB` | equal `R1` from `AMP1.OUT` to `W09.SUM` |
| `W09.RALPHA` | `R` from `W09.SUM` to ground; may be open/infinite |
| `AMP1.INV_IN` | `W09.SUM` |
| `AMP1.NONINV_IN` | ground |
| `AMP1.CC` | capacitor between `AMP1.COMP_A` and `AMP1.COMP_B` |
| `W09.VOUT` | `AMP1.OUT` |

Ideal closed-loop gain is −1 independent of `R`. The source defines

`alpha = (R1 || R) / (R1 + (R1 || R))`.

- `R = infinity` gives `alpha = 1/2`.
- `R = R1/2` gives `alpha = 1/4`.
- The numeric value of `R1` is **not specified** by Figures 9.8–9.12 and must not be invented during transcription.

### Test cases within canonical configuration `W09.CC_SWEEP`

| Case label (not a configuration ID) | Source stimulus | `alpha` / `R` | `Cc` | Source |
|---|---|---|---|---|
| `CASE.W09.A47` | −20 mV step | 1/2; `R` open | 47 pF | Fig. 9.10 |
| `CASE.W09.A33` | −20 mV step | 1/2; `R` open | 33 pF | Fig. 9.10 |
| `CASE.W09.A10` | −20 mV step | 1/2; `R` open | 10 pF | Fig. 9.10 |
| `CASE.W09.A05` | −20 mV step | 1/2; `R` open | 5 pF | Fig. 9.10 |
| `CASE.W09.B20` | 20 V peak-to-peak square wave | 1/2; `R` open | 20 pF | Fig. 9.12a |
| `CASE.W09.B10` | 20 V peak-to-peak square wave | 1/4; `R=R1/2` | 10 pF | Fig. 9.12b |

Expected qualitative order from Figure 9.10: larger capacitors are slower and closer to first order; 10 pF is more underdamped; 5 pF is highly oscillatory. Figure 9.12 demonstrates inverse slew-rate dependence on `Cc`. Do not demand waveform identity without matching the source device parameters, layout capacitance, probe loading, and generator/load conditions.

## 8. Restored Week 9 end-state configuration

After the Figure 9.8 experiments:

1. Remove/open the temporary `R1` input/feedback fixture and `R` shunt as an explicit configuration change.
2. Connect `AMP1.INV_IN` to the summing-node boundary of `MOD.INT1.NET`.
3. Connect `AMP1.NONINV_IN` to `SGND`.
4. Connect `AMP1.OUT` to the capacitor-return and output-jack boundaries of `MOD.INT1.NET`.
5. Restore the retained `MOD.INT1.NET` feedback capacitor from `AMP1.OUT` to its summing node and restore the inherited input network into that node; assign exact component and local-net IDs during canonical encoding.
6. Leave one documented provisional `Cc` between `COMP_A/B`; its value is selected from the Week 9 experiment and is not fixed by this transcription.

The Figure 9.8 resistive feedback and restored integrating feedback are separate complete graphs. They must not be overlaid on one schematic/netlist.

## 9. Measurement and probe constraints from the source

- A 20 pF capacitor is the source's worked compensation example, but not an automatic Week 9 end-state choice.
- Figure 9.1 parameters imply even about 0.1 pF may begin to modify the transfer function; unavoidable feedback/stray capacitance is commonly on the order of 1 pF (PDF p. 249).
- Probe and wiring capacitance at `N_HIGH_Z`, `COMP_A`, and `COMP_B` must be declared. A generic oscilloscope icon cannot represent a zero-load measurement.
- First power-up needs rail-current limiting and quiescent-node checks before closing feedback. This is a practical addition, not a Roberge component.
- Figure 9.1 includes output current limiting, but no source construction layout, transistor heatsinking arrangement, or SOA proof.

## 10. Independent double-check queue

The second transcriber must work from the PDF figure, not from this file, then diff results for:

1. Every Q1–Q13 B/C/E (or G/D/S) terminal-to-net assignment.
2. Balance potentiometer endpoints, wiper, feeding diode orientation, and the two 300 kΩ branches.
3. Q4/Q5 common-emitter node and 33 kΩ/3.3 µF connections/polarity.
4. Q6 base divider/bypass versus the nearby `COMP_A` trace.
5. Q8 gate/source/drain mapping and exact `COMP_B` junction.
6. Both output-bias diodes and Q12/Q13 limiter terminal orientation.
7. Common negative-bias network: fixed 5.6 kΩ, 180 kΩ, 0.1 µF, 1.5 kΩ plus diode, 33 µF polarity, 68 kΩ, and Q9 1.5 kΩ.
8. Every 1% metal-film dot.
9. All electrolytic polarity markings and all ground/rail endpoints.
10. Figure 9.8 `alpha` equation and the exact `R=R1/2` condition for `alpha=1/4`.

## 11. Stop conditions before circuit encoding

Do not encode the Week 9 graph until:

- Transcription B exists and every pin/net/value difference is adjudicated against the PDF.
- The Week 8-to-Week 9 retained/removed component map is explicit.
- Numeric `R1` for the Figure 9.8 fixture is derived under input-current, loading, noise, and generator constraints.
- Historical-device model availability and any clearly named substitute bindings are separately decided.
- A provisional end-state `Cc` selection rule and safe bring-up procedure are approved.
- Probe/socket/board parasitic assumptions are declared for the realistic projection.

No toolchain choice, circuit graph, SVG, or SPICE deck is created by this source map.
