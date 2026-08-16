# Week 9 Figure 9.1 — Transcription A/B adjudication

Status: **source comparison complete; unresolved source omissions remain blocked**  
Compared files: `week09-source-map.md` (A) and `week09-transcription-b.md` (B)  
Adjudication source: local `op_amps_roberge.pdf`; no circuit was encoded

## 1. Independence note

Transcription B was written as a source-only pass before the line-by-line comparison recorded here. Both passes agree on the amplifier topology, all Q1–Q13 historical types and roles, compensation endpoints, visible passive values, rails, quiescent annotations, and Figure 9.8/9.10/9.12 fixtures.

## 2. Terminal and active-device comparison

| Item | A | B | Adjudication |
|---|---|---|---|
| external inputs/output | Q1.B / Q2.B / midpoint of 22 Ω pair | same | **AGREE** |
| compensation A | Q5 base | Q5 base | **AGREE; verified by §9.2.3 text** |
| compensation B | Q8 source | Q8 source | **AGREE; verified by §9.2.3 text** |
| supply/ground ports | `AMP1.VP15`, `AMP1.VN15`, `AMP1.AGND` → `P15/N15/SGND` | normalized to same | **AGREE** |
| Q1/Q2 | matched 2N5963 NPN input pair | same, full B/C/E map | **AGREE** |
| Q3/Q7/Q9/Q12 | 2N3707 | same | **AGREE** |
| Q4/Q5/Q6/Q13 | 2N4250 | same | **AGREE** |
| Q8 | TIS58 JFET source follower | same | **AGREE** |
| Q10/Q11 | 2N2219 NPN / 2N2905 PNP | same | **AGREE** |
| Q4 terminal map | A notes base=Q1 collector and collector=ground but requested confirmation | B maps B=`Q1C`, C=`SGND`, E=Q4/Q5 common emitter | **RESOLVED** by Figure 9.1 symbol plus §9.1.2 statement that Q4 forms the DC differential pair and is not in the AC signal path |
| Q6 terminal map | A identifies cascode/high-Z role | B maps B=bias divider, E=Q5 collector, C=high-Z | **RESOLVED/AGREE** from cascode prose and Figure 9.1 |
| Q8 terminal map | A requested gate-route confirmation | B maps G=high-Z, D=`P15`, S=buffer/COMP_B | **RESOLVED/AGREE** from source-follower prose and §9.2.3 |
| Q12 limiter | A role/nodes, pin orientation requested | B maps B=upper sense, C=Q10 drive, E=OUT | **RESOLVED** by §9.1.2: positive sense drop turns Q12 on and removes Q10 base drive |
| Q13 limiter | A role/nodes, pin orientation requested | B maps B=lower sense, C=Q11 drive, E=OUT | **RESOLVED** by negative-limit symmetry and Figure 9.1 |

Canonical encoding may use different internal net names, but it must preserve the B terminal sets after normalization.

## 3. Passive/value comparison

| Source element | A | B | Adjudication |
|---|---|---|---|
| collector loads | 300 kΩ ×2 | same | **AGREE** |
| balance control | 50 kΩ potentiometer; exact wiper/diode requested | 50 kΩ, ends feed 300 kΩ branches, wiper fed from `P15` through diode | **RESOLVED**: §9.1.2 explicitly calls it a 50 kΩ potentiometer; Figure 9.1 shows the supply-fed wiper |
| Q4-base bypass | 0.01 µF, upper endpoint to verify | `P15` to Q1-collector/Q4-base node | **RESOLVED** by Figure 9.1 and prose that Q4 base is bypassed at moderate/high frequency |
| Q4/Q5 emitter branch | 33 kΩ + 3.3 µF/10 V to `P15` | same; electrolytic positive=`P15` | **AGREE/RESOLVED** |
| Q6 base | 4.7 kΩ to `P15`; 10 kΩ and 1.0 µF to ground | same | **AGREE**; 1.0 µF polarity/type remains absent |
| Q3 emitter branch | A labels 5.6 kΩ as a potentiometer and asks to recheck series topology with 180 kΩ | B sees series 5.6 kΩ + 180 kΩ but blocks fixed/adjustable form | **A CORRECTION**: Figure 9.1 shows an ordinary 5.6 kΩ resistor, while the prose names only the 50 kΩ balance element as a potentiometer. Treat 5.6 kΩ as fixed unless a higher-authority edition proves otherwise. Both are in series from Q3 emitter to `N15`. |
| bias bypass | 0.1 µF to ground; 33 µF/10 V to `N15` | same | **AGREE**; 33 µF positive at bias node |
| bias branch | 1.5 kΩ + diode to `N15` | same | **AGREE** |
| Q7 emitter | 68 kΩ to `N15` | same | **AGREE** |
| Q9 emitter | 1.5 kΩ to `N15` | same | **AGREE** |
| output sense | 22 Ω ×2 | same | **AGREE** |
| rail bypass | each rail 0.1 µF + 15 µF/20 V to `SGND` | same | **AGREE**; polarities agree with rail voltage |

## 4. Diode orientation adjudication

A recorded the three diode groups but intentionally left orientation for the second pass. B recorded the following source-consistent directions:

| Diode/group | Adjudicated orientation | Basis |
|---|---|---|
| balance temperature diode | anode=`P15`, cathode=50 kΩ balance wiper | visible symbol/current path and required collector-load feed |
| common-bias diode | anode toward the 1.5 kΩ/bias node, cathode=`N15` | visible symbol and downward current-source bias path |
| two output-bias diodes | both anodes upward toward Q8 source, cathodes downward toward Q9 collector | quiescent current flows from Q8 source through both diodes into Q9 current sink |

The source gives no diode part numbers. Package-band orientation remains a construction check even though the logical anode/cathode nets are resolved.

## 5. Precision-dot adjudication

The caption states that a dot indicates a 1% metal-film resistor.

| Resistor | A | B | Result |
|---|---|---|---|
| 300 kΩ left/right | visible | visible | **1% metal film** |
| 33 kΩ | apparent | visible | **1% metal film** |
| 5.6 kΩ | not included in A's exhaustive candidate list | least-legible visible dot in B | **BLOCKED at source-resolution level**; do not silently mark or unmark in graph |
| 180 kΩ | apparent | visible | **1% metal film** |
| shared-bias 1.5 kΩ | apparent | visible | **1% metal film** |
| 68 kΩ | apparent | visible | **1% metal film** |
| 4.7 kΩ, 10 kΩ, Q9 1.5 kΩ, 22 Ω ×2, 50 kΩ control | no confident dot | no confident dot | **not marked 1% in this transcription** |

The 5.6 kΩ dot is the only unresolved tolerance mark after comparison. The electrical value is not blocked; only its source-specified tolerance class is.

## 6. Net-set comparison

After normalizing A's `N_*` names and B's `A_*` names, the terminal sets agree:

1. Q1/Q2 common tail with Q3 collector.
2. Q1 collector with Q4 base, left 300 kΩ, and 0.01 µF.
3. Q2 collector with Q5 base/COMP_A and right 300 kΩ.
4. Q4/Q5 common emitters with the 33 kΩ/3.3 µF branch.
5. Q5 collector with Q6 emitter.
6. Q6 base with 4.7 kΩ/10 kΩ/1.0 µF bias network.
7. Q6 collector with Q7 collector and Q8 gate at the high-impedance node.
8. Q8 source/COMP_B with Q10 base, upper bias diode, and Q12 collector.
9. Q10 emitter/upper 22 Ω with Q12 base.
10. output midpoint with Q12/Q13 emitters.
11. Q11 emitter/lower 22 Ω with Q13 base.
12. lower bias diode with Q11 base, Q9 collector, and Q13 collector.
13. Q3/Q7/Q9 common-base bias node and its resistor/diode/capacitor network.

No true junction/crossing conflict remains in this normalized logical set. The renderer must nevertheless avoid reproducing Figure 9.1's close visual crossings ambiguously.

## 7. Figure 9.8 and experiment-case comparison

| Item | A | B | Adjudication |
|---|---|---|---|
| equal input/feedback resistors | symbolic `R1` | same | **AGREE** |
| shunt | `R` from sum node to ground | same | **AGREE** |
| gain | −1 independent of `R` | same | **AGREE** |
| alpha | `(R1 || R)/(R1 + (R1 || R))` | same | **AGREE** |
| `alpha=1/2` | `R=∞` | same | **AGREE** |
| `alpha=1/4` | `R=R1/2` | same | **AGREE** |
| Fig. 9.10 | −20 mV; 47/33/10/5 pF at alpha 1/2 | same | **AGREE** |
| Fig. 9.12 | 20 Vpp; 20 pF at 1/2 and 10 pF at 1/4 | same | **AGREE** |
| Fig. 9.11 intermediate cases | not enumerated in A | B adds 20 pF at 1/4 plus the common 20 pF/1/2 and 10 pF/1/4 cases | **B SOURCE-SUPERSET; accepted** |
| numeric `R1` | absent/TBD | absent/TBD | **BLOCKED by source; derive later, do not transcribe** |

For canonical configuration identity, the shared Figure 9.8 electrical graph should be one configuration with parameterized test cases. B's figure-part labels are source cases, not separate physical configurations.

## 8. Remaining true blocks before encoding

These are not A/B disagreements that can be solved from the cited pages:

1. Whether the 5.6 kΩ resistor carries the Figure 9.1 1% dot.
2. Diode part numbers and electrical models.
3. Capacitor dielectric/tolerance/ESR and whether the unpolarized-looking 1.0 µF part was intended as a specific technology.
4. Historical-package pin numbering; logical B/C/E and G/D/S must be kept separate from later package maps.
5. Numeric Figure 9.8 `R1`, source/generator impedance, explicit output load, and instrument models.
6. Historical-device SPICE models, substitution decisions, and parasitics.
7. Week 8-to-Week 9 retained/removed object mapping and provisional end-state `Cc`; these are design/state decisions, not source transcription.

## 9. Adjudication outcome

- **Topology:** A and B agree after resolving the limiter, Q4/Q5, Q6, and Q8 terminal checks from prose/figure evidence.
- **Values:** all visible numeric values agree. A's “5.6 kΩ potentiometer” label is corrected to a fixed 5.6 kΩ resistor.
- **Orientations:** logical diode and electrolytic orientations are resolved except the source-unspecified 1.0 µF capacitor type/polarity.
- **Tolerance marks:** all agree except the 5.6 kΩ dot, which remains blocked.
- **Fixtures:** Figures 9.8, 9.10, and 9.12 agree exactly; B adds the source-supported Figure 9.11 intermediate case.

This diff is sufficient to prepare encoding only if the implementation preserves every remaining block explicitly. It is not itself a canonical graph, SVG, or SPICE netlist.
