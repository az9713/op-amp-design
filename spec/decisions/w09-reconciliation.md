# Week 9 chronological reconciliation

Status: review package produced; topology awaiting user acceptance; electrical Gate 2 remains failed/blocked.

## Permanent progression

The accepted Week 8 graph is the parent authority. Week 8 already contains the final Figure 9.1 Q1–Q11 subset, so Week 9 adds only Q12 and Q13 as permanent hardware. The old isolated Week 9 vertical-proof graph is retained as historical evidence but is no longer the chronological cumulative authority.

## Configurations

- `W09.CC_SWEEP`: Figure 9.8 compensation campaign with the complete Q1–Q13 amplifier. One physical `AMP1.CC` socket receives the A47/A33/A10/A05/B20/B10 substitutions recorded in the case manifest. The canonical end-state sheet shows the retained provisional 47 pF value.
- `W09.INVERTER_TEST`: RIN = RFB = 4.70 kΩ, 50 Ω declared generator source impedance, alpha shunt open, 10 MΩ declared output load, grounded noninverting input.
- `W09.INT1_RESTORED`: resistive characterization fixture removed; inherited 10 kΩ / 1 µF INT1 feedback restored around AMP1; 47 pF remains socketed.

Patch-cord physical routing remains deferred. Every electrical connection is explicit in the graph.

## Gate boundary

The generated SVG and SPICE for this review are connectivity-equivalent projections of the reconciled graph. They do not claim realistic device performance. The earlier ideal-model Gate 2 results remain failures: balance output 5.22185024 V against a 0.1 V limit, 1 Hz inverter gain 0.0349075907 against 0.9–1.1, and integrator output +0.08338962 V against expected −0.2 V ±10%. These must be diagnosed and rerun before electrical approval.

No change to `capstone.html` is authorized by this record.
