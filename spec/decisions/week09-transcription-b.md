# Week 9 Figure 9.1 — Transcription B

Status: **source-only second pass; not a circuit graph**  
Pass basis: local `op_amps_roberge.pdf`, especially PDF pp. 239–241, 247–249, and 253–255  
Canonical naming: `P15`, `N15`, and `SGND`; physical amplifier `AMP1` in `SLOT.INT1`

This pass was written from the PDF before the comparison phase. Items the raster cannot resolve are marked **BLOCKED** rather than inferred into a circuit.

## 1. External boundary

| Port | Source terminal | Source-only result |
|---|---|---|
| `AMP1.INV_IN` | Q1 base | verified |
| `AMP1.NONINV_IN` | Q2 base | verified |
| `AMP1.OUT` | midpoint of the two 22 Ω resistors | verified |
| `AMP1.COMP_A` | Q5 base | verified by §9.2.3 prose/model |
| `AMP1.COMP_B` | Q8 source | verified by §9.2.3 prose/model |
| `AMP1.VP15` | +15 V | `P15` |
| `AMP1.VN15` | −15 V | `N15` |
| `AMP1.AGND` | circuit common | `SGND` |

## 2. Provisional source-net names

These names make the terminal ledger readable. They are not an encoding commitment.

| Net | Meaning |
|---|---|
| `A_TAIL` | Q1/Q2 common emitters and Q3 collector |
| `A_Q1C_Q4B` | Q1 collector / Q4 base / left collector-load branch |
| `A_Q2C_Q5B_COMPA` | Q2 collector / Q5 base / right collector-load branch / compensation A |
| `A_Q45E` | common emitters of matched Q4/Q5 pair |
| `A_Q5C_Q6E` | Q5 collector / Q6 emitter cascode junction |
| `A_Q6B` | Q6 fixed-bias base node |
| `A_HIGHZ` | Q6 collector / Q7 collector / Q8 gate |
| `A_Q8S_COMPB_DRV_P` | Q8 source / compensation B / Q10 base / top of bias-diode string |
| `A_OUT_P_SENSE` | Q10 emitter / upper 22 Ω top / Q12 base |
| `A_OUT` | output / two 22 Ω midpoint / Q12 emitter / Q13 emitter |
| `A_OUT_N_SENSE` | Q11 emitter / lower 22 Ω bottom / Q13 base |
| `A_DRV_N_Q9C` | bottom of bias-diode string / Q11 base / Q9 collector |
| `A_BIAS_NEG` | common bases of Q3/Q7/Q9 and their shared bias network |
| `A_BAL_L`, `A_BAL_W`, `A_BAL_R` | left end, supply-fed wiper, and right end of 50 kΩ balance control |

## 3. Q1–Q13 terminal ledger

| Device | Type | Base/gate | Collector/drain | Emitter/source | Source confidence |
|---|---|---|---|---|---|
| `AMP1.Q1` | 2N5963 NPN | `AMP1.INV_IN` | `A_Q1C_Q4B` | `A_TAIL` | verified figure + prose |
| `AMP1.Q2` | 2N5963 NPN | `AMP1.NONINV_IN` | `A_Q2C_Q5B_COMPA` | `A_TAIL` | verified figure + prose |
| `AMP1.Q3` | 2N3707 NPN | `A_BIAS_NEG` | `A_TAIL` | to `N15` through the 5.6 kΩ + 180 kΩ emitter branch | topology visible; exact 5.6 kΩ element form BLOCKED |
| `AMP1.Q4` | 2N4250 PNP | `A_Q1C_Q4B` | `SGND` | `A_Q45E` | verified by symbol/prose role |
| `AMP1.Q5` | 2N4250 PNP | `A_Q2C_Q5B_COMPA` | `A_Q5C_Q6E` | `A_Q45E` | verified; matched with Q4 |
| `AMP1.Q6` | 2N4250 PNP | `A_Q6B` | `A_HIGHZ` | `A_Q5C_Q6E` | verified cascode role |
| `AMP1.Q7` | 2N3707 NPN | `A_BIAS_NEG` | `A_HIGHZ` | to `N15` through 68 kΩ | verified |
| `AMP1.Q8` | TIS58 JFET | `A_HIGHZ` | `P15` | `A_Q8S_COMPB_DRV_P` | verified source-follower role and compensation prose |
| `AMP1.Q9` | 2N3707 NPN | `A_BIAS_NEG` | `A_DRV_N_Q9C` | to `N15` through 1.5 kΩ | verified |
| `AMP1.Q10` | 2N2219 NPN | `A_Q8S_COMPB_DRV_P` | `P15` | `A_OUT_P_SENSE` | verified |
| `AMP1.Q11` | 2N2905 PNP | `A_DRV_N_Q9C` | `N15` | `A_OUT_N_SENSE` | verified |
| `AMP1.Q12` | 2N3707 NPN | `A_OUT_P_SENSE` | `A_Q8S_COMPB_DRV_P` | `A_OUT` | verified by positive-current-limit operation in §9.1.2 |
| `AMP1.Q13` | 2N4250 PNP | `A_OUT_N_SENSE` | `A_DRV_N_Q9C` | `A_OUT` | verified by negative-current-limit symmetry and figure |

### Role cross-check from prose

- Q1/Q2 are the input differential pair.
- Q5/Q6 are the signal-path cascode; Q4 reduces DC drift.
- Q8 is the high-impedance-node source follower.
- Q10/Q11 form the complementary output follower.
- Q3, Q7, and Q9 are current sources.
- Q12 and Q13 limit output current.

## 4. Passive ledger and endpoints

### Input, balance, and Q4/Q5 stage

| ID | Value | Endpoint 1 | Endpoint 2 | Orientation/marking |
|---|---:|---|---|---|
| `AMP1.R_COL_L` | 300 kΩ | `A_BAL_L` | `A_Q1C_Q4B` | precision dot visible |
| `AMP1.R_COL_R` | 300 kΩ | `A_BAL_R` | `A_Q2C_Q5B_COMPA` | precision dot visible |
| `AMP1.R_BAL` | 50 kΩ variable | `A_BAL_L` | `A_BAL_R` | wiper=`A_BAL_W`; variable-element symbol/details are raster-small but three-node intent is visible |
| `AMP1.D_BAL` | value/type unstated | `P15` | `A_BAL_W` | conducts from `P15` toward wiper/load; anode=`P15`, cathode=`A_BAL_W`; verify band in physical part later |
| `AMP1.C_Q4B_BYP` | 0.01 µF | `P15` | `A_Q1C_Q4B` | nonpolar symbol |
| `AMP1.R_Q45_E` | 33 kΩ | `P15` | `A_Q45E` | precision dot visible |
| `AMP1.C_Q45_E` | 3.3 µF, 10 V | `P15` | `A_Q45E` | electrolytic; positive=`P15`, negative=`A_Q45E` |

### Q6 bias and high-gain stage

| ID | Value | Endpoint 1 | Endpoint 2 | Orientation/marking |
|---|---:|---|---|---|
| `AMP1.R_Q6_BP` | 4.7 kΩ | `P15` | `A_Q6B` | no precision dot confidently visible |
| `AMP1.R_Q6_BG` | 10 kΩ | `A_Q6B` | `SGND` | no precision dot confidently visible |
| `AMP1.C_Q6_BYP` | 1.0 µF | `A_Q6B` | `SGND` | polarity not marked; do not assign polarized part from source alone |
| `AMP1.R_Q7_E` | 68 kΩ | Q7 emitter | `N15` | precision dot visible |

### Shared negative-bias/current-source network

| ID | Value | Endpoint 1 | Endpoint 2 | Orientation/marking |
|---|---:|---|---|---|
| `AMP1.R_Q3_TRIM` | 5.6 kΩ | Q3 emitter | intermediate series node | precision dot appears visible; whether fixed/adjustable is BLOCKED by raster |
| `AMP1.R_Q3_E` | 180 kΩ | intermediate series node | `N15` | precision dot visible |
| `AMP1.C_BIAS_G` | 0.1 µF | `A_BIAS_NEG` | `SGND` | nonpolar |
| `AMP1.R_BIAS_TC` | 1.5 kΩ | `A_BIAS_NEG` | anode of `D_BIAS` | precision dot visible |
| `AMP1.D_BIAS` | value/type unstated | after 1.5 kΩ | `N15` | anode toward resistor/bias node, cathode=`N15`; supports downward bias current |
| `AMP1.C_BIAS_N` | 33 µF, 10 V | `A_BIAS_NEG` | `N15` | electrolytic; positive=`A_BIAS_NEG`, negative=`N15` |
| `AMP1.R_Q9_E` | 1.5 kΩ | Q9 emitter | `N15` | no precision dot visible |

### Output driver and limiter

| ID | Value | Endpoint 1 | Endpoint 2 | Orientation/marking |
|---|---:|---|---|---|
| `AMP1.D_DRV_1` | value/type unstated | `A_Q8S_COMPB_DRV_P` | diode midpoint | anode above, cathode below; conducts downward |
| `AMP1.D_DRV_2` | value/type unstated | diode midpoint | `A_DRV_N_Q9C` | anode above, cathode below; conducts downward |
| `AMP1.R_OUT_P` | 22 Ω | `A_OUT_P_SENSE` | `A_OUT` | no precision dot visible |
| `AMP1.R_OUT_N` | 22 Ω | `A_OUT` | `A_OUT_N_SENSE` | no precision dot visible |

### Local rail bypass shown in Figure 9.1

| ID | Value | Endpoint 1 | Endpoint 2 | Orientation |
|---|---:|---|---|---|
| `AMP1.C_VP_FAST` | 0.1 µF | `P15` | `SGND` | nonpolar |
| `AMP1.C_VP_BULK` | 15 µF, 20 V | `P15` | `SGND` | positive=`P15`, negative=`SGND` |
| `AMP1.C_VN_FAST` | 0.1 µF | `N15` | `SGND` | nonpolar |
| `AMP1.C_VN_BULK` | 15 µF, 20 V | `N15` | `SGND` | positive=`SGND`, negative=`N15` |

## 5. Precision-dot inventory

The Figure 9.1 caption says the dot indicates a 1% metal-film resistor.

### Dots visible in this pass

- both 300 kΩ collector resistors;
- 33 kΩ Q4/Q5 emitter resistor;
- 5.6 kΩ item in the Q3 emitter branch;
- 180 kΩ Q3 emitter resistor;
- 1.5 kΩ resistor in the shared bias/diode branch;
- 68 kΩ Q7 emitter resistor.

### No dot confidently visible

- 50 kΩ balance control;
- 4.7 kΩ and 10 kΩ Q6-bias resistors;
- Q9 1.5 kΩ emitter resistor;
- both 22 Ω output resistors.

The 5.6 kΩ mark is the least legible of the visible-dot set and remains **BLOCKED pending direct second-person/source adjudication**.

## 6. Rails, grounds, and quiescent annotations

- Q8.D, Q10.C, the upper balance/bias branches, and positive bypass parts terminate on `P15`.
- Q11.C, Q3/Q7/Q9 emitter branches, the negative-bias diode branch, and negative bypass parts terminate on `N15`.
- Q4.C, the 10 kΩ and 1.0 µF Q6-base branches, and both fast/bulk rail reference capacitors terminate on `SGND` as drawn.
- Figure labels approximately 10 µA in each input collector branch, 20 µA total tail current, 50 µA in the Q6/Q7 high-gain branch, and 2 mA in the Q8/Q9 buffer branch.
- The design uses ±15 V supplies and targets about ±10 V maximum output.
- §9.1.2 describes output-current limiting at roughly 25–30 mA through the 22 Ω sense resistors.

## 7. Compensation terminal and element cases

The source text removes drawing ambiguity:

- `AMP1.COMP_A = A_Q2C_Q5B_COMPA = Q5 base`.
- `AMP1.COMP_B = A_Q8S_COMPB_DRV_P = Q8 source`.
- A compensation network closes a minor loop around the high-gain stage.
- Figure 9.7 uses 20 pF as a worked example; this is not a universal end-state value.
- PDF p. 249 warns that compensation above roughly 0.1 pF can modify the amplifier and that unavoidable stray feedback can be around 1 pF.

## 8. Figure 9.8 configuration ledger

| Component/net | Exact source relation |
|---|---|
| input resistor | `R1` from grounded source `W09.VIN` to `W09.SUM` |
| feedback resistor | equal `R1` from `AMP1.OUT` to `W09.SUM` |
| attenuation shunt | `R` from `W09.SUM` to `SGND` |
| amplifier inputs | `AMP1.INV_IN=W09.SUM`; `AMP1.NONINV_IN=SGND` |
| compensation | `Cc` between `AMP1.COMP_A` and `AMP1.COMP_B` |
| output | `W09.VOUT=AMP1.OUT` |

The ideal gain is −1 independent of shunt `R`. The figure gives

`alpha = (R1 || R) / (R1 + (R1 || R))`.

| Case | Stimulus | `R` / `alpha` | `Cc` |
|---|---|---|---:|
| Figure 9.10a | −20 mV step | `R=∞`, `alpha=1/2` | 47 pF |
| Figure 9.10b | −20 mV step | `R=∞`, `alpha=1/2` | 33 pF |
| Figure 9.10c | −20 mV step | `R=∞`, `alpha=1/2` | 10 pF |
| Figure 9.10d | −20 mV step | `R=∞`, `alpha=1/2` | 5 pF |
| Figure 9.11a / 9.12a | small step / 20 Vpp square | `R=∞`, `alpha=1/2` | 20 pF |
| Figure 9.11b | −20 mV step | `R=R1/2`, `alpha=1/4` | 20 pF |
| Figure 9.11c / 9.12b | small step / 20 Vpp square | `R=R1/2`, `alpha=1/4` | 10 pF |

The source does not provide a numeric `R1` on these pages.

## 9. True source blocks after this pass

1. Exact graphical form of the 5.6 kΩ Q3-branch element: fixed resistor versus adjustable element.
2. The 5.6 kΩ precision dot is less legible than the other marks.
3. Diode part numbers are absent; only circuit orientation/function can be transcribed.
4. Capacitor dielectric, tolerance, ESR, and the 1.0 µF polarity/type are absent.
5. Package pinouts for every historical transistor are absent from the circuit figure and must remain separate from logical pins.
6. Figure 9.8 gives no numeric `R1` and no generator/source impedance or output load.
7. Historical device SPICE models and layout/parasitic values are not supplied.

No value or model is selected in this pass.
