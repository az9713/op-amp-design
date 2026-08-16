# Week 10 production decisions

Status: topology and presentation approved by the user on 2026-08-15; quantitative electrical proof remains blocked by inherited Week 9 failures.

## Figure 10.9 insertion

Figure 10.9 is a generic PNP current repeater, not a literal wiring diagram for the Figure 9.1 amplifier. The canonical Week 10 adaptation is:

- `AMP1.Q_CR_REF`: PNP emitter to P15; base and collector tied to `AMP1.N.Q1C_Q4B` (Q1 collector).
- `AMP1.Q_CR_OUT`: matched PNP emitter to P15; base tied to the reference node; collector to `AMP1.COMP_A` (Q2 collector and the next-stage interface).
- The Week 9 `AMP1.R_COL_L`, `AMP1.R_COL_R`, two balance-pot segments, and balance diode remain physically installed but are electrically inactive. This is a functional replacement, not a parallel addition.

The source verifies the current-repeater principle and forward-active/compliance condition. Its use at these exact amplifier nodes is a project-derived adaptation. A thermally coupled 2N4250 pair is a proposed historical-style implementation; package pin maps and realistic model provenance remain TBD.

## Hold comparison

The discrete INT1 and stock LM301A INT2 retain equal 1 µF integrating capacitors and receive equal 10 MΩ measurement loading. During the active hold interval both 10 kΩ input resistors are electrically inactive/open. Precharge both outputs to +5.00 V with a temporary external fixture, remove it, then measure at least 60 seconds at recorded temperature. Compute `I_EQ = C_F × dV_OUT/dt`, report sign and magnitude, exchange probes, and separately characterize capacitor leakage/dielectric absorption. No hidden bleed resistor is allowed.

The capstone's LM101A wording is historical context; the locked project baseline remains LM301A.

## Excluded branch

Figure 10.25 FET followers are not included in the cumulative baseline. They remain a separately reviewable optional branch so they cannot silently alter Week 11 inheritance.

## Gate boundary

The Week 10 SVG/SPICE pairs may pass structural connectivity equivalence. No ideal or realistic performance approval is claimed until the inherited Week 9 failures are diagnosed and the reconciled Week 9/10 graphs are rerun with adequate device models.
