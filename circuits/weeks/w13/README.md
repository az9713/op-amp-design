# Week 13 canonical package

`graph.json` is the electrical authority for seven mutually exclusive compensation experiments plus one concluding normal-operation configuration. Each published SVG and SPICE connectivity deck is generated from that graph and has a matching connectivity receipt.

`W13.FINAL_BUILD` is the explicit end state. It preserves the approved Week 12 regulator-and-analog-twin machine, selects the external 47 pF one-pole capacitor on AMP1, restores REG1's accepted 30 pF one-pole capacitor, and disconnects temporary scope loads, loop injection, and compensation-campaign sources.

The package deliberately separates:

- Figure 13.1 lag compensation on SUM1 and INV1;
- the accepted REG1 capacitive-load baseline and a regulator-specific Figure 13.8 adaptation;
- one-pole compensation on discrete AMP1 and LM301A INT2;
- Figure 13.19 two-port compensation on `REG1.U_ERR`.

The physical Week 13 delta adds socketed/selectable compensation parts and test fixtures without removing Week 12 hardware. Only the active experiment is electrically present on each configuration sheet.

Symbolic values (`R_LAG_*`, `C_LAG_*`, `R_FPATH`, `C_F`, `C1_2P`, `R_2P`, `C2_2P`) are intentional stop conditions. They require measured loop dynamics and an approved tolerance/performance target. Figure 13.21's 30 pF–15 kohm–30 pF values apply only to its historical 2.2 kohm unity-inverter demonstration and are not regulator values.
