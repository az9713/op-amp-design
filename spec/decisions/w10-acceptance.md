# Week 10 topology acceptance

Status: approved by the user on 2026-08-15.

The approved scope is the Week 10 chronological topology and presentation in `week10-review.html`:

- the derived Figure 10.9 PNP current-mirror insertion map;
- QCR-REF diode-connected at the Q1 collector node;
- QCR-OUT connected to Q2 collector / COMP_A;
- the former 300 kΩ collector-load and balance components physically retained but electrically inactive;
- the discrete INT1 hold configuration;
- the equal-condition discrete INT1 versus LM301A INT2 comparison;
- exclusion of the optional Figure 10.25 FET branch from the cumulative baseline.

This approval does not approve ideal or realistic electrical performance. The inherited Week 9 balance, inverter-gain, and integrator-polarity failures remain open. Exact realistic device models, package pin maps, matching, leakage, and thermal behavior also remain unresolved.

`capstone.html` remains unchanged pending the later integration gate.
