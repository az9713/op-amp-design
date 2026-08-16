# Week 11 production decisions

Status: implemented for topology and presentation review. Electrical performance remains unapproved.

## Source corrections

- Roberge Figure 11.18 is the grounded half-wave precision rectifier: one op amp, one series diode, feedback sensed after the diode, and a ground-referenced load.
- Roberge Figure 11.19 is the floating-load full-wave bridge. The older local file `figures/book/fig-11.18.png` depicts Figure 11.19 and is therefore mislabeled; it is not an electrical authority for Week 11.
- Figures 12.17 and 12.18 define the reset/operate/hold integrator and its practical switching implementation. Figure 11.2 defines the three mutually exclusive offset/input-current measurement fixtures.

## Installed topology

- Both computing channels receive independent Figure 12.18 hardware. Neither the reset follower nor the mode-control driver is shared.
- Each channel uses a 2N4391 operate switch, 2N4091 reset switch, duplicated LM301A reset follower, duplicated 2N2907 control pair, and the Figure 12.18 diode/resistor network.
- The existing 1 uF integrating capacitors are retained. The prior 10 kohm direct input resistors remain physically installed but disconnected and grey in Week 11 mode configurations.
- A separate permanent `RECT1` module implements the actual Figure 11.18 grounded half-wave rectifier. The Figure 11.19 bridge is deferred.

## Selected build values

- Operate path resistance: 9.975 kohm nominal, implemented initially as 9.76 kohm plus 215 ohm. Adjust so resistor plus measured 2N4391 on-resistance equals 10.000 kohm.
- Reset divider: two matched 10.0 kohm, 0.1% resistors per channel.
- Logic-input pull-downs: 100 kohm, project-added so both unconnected controls produce HOLD.
- LM301A compensation: 30 pF C0G. Local bypass: 0.1 uF per rail at every added amplifier.
- Figure 11.2 offset test: 1 kohm to ground and 999 kohm feedback. Input-current tests: 10 Mohm. Declared output load: 10 Mohm.
- Rectifier load: 10 kohm; diode: proposed 1N4148 pending final historical-device choice.

## Mode contract

| Configuration | Operate switch | Reset switch | Meaning |
|---|---:|---:|---|
| OPERATE | closed/high | open/low | integrate the declared input |
| RESET | open/low | closed/high | drive the output toward negative `V_IC` |
| HOLD | open/low | open/low | retain capacitor charge |
| forbidden | closed/high | closed/high | never generated; hardware sequencing must be break-before-make |

The 100 kohm pull-downs make HOLD the power-up default. The logic sources in the netlists are declared fixtures, not permanent chassis wiring.

## Claim boundary and deferred work

- Every review SVG and SPICE deck is projected from the same canonical graph and has a passing connectivity receipt.
- These are structural decks. No Week 11 realistic switch/leakage, offset-current, or rectifier-recovery performance claim is made.
- Realistic 2N4391/2N4091 models, package pin maps, diode selection, break-before-make hardware interlock, and Figure 11.19 are deferred.
- The inherited Week 9/10 electrical-performance failures remain open; topology approval does not erase them.
- `capstone.html` remains unchanged pending weekly approval and final integration.
