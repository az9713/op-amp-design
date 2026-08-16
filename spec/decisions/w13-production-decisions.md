# Week 13 production decisions

Status: implemented for topology and presentation review. Electrical performance is not approved.

## Configuration boundary

Week 13 uses seven separate graphs. Mutually exclusive compensation networks are never overlaid:

1. `W13.LAG_SUM1`
2. `W13.LAG_INV1`
3. `W13.CLOAD_BASE`
4. `W13.CLOAD_COMP`
5. `W13.ONEPOLE_AMP1`
6. `W13.ONEPOLE_INT2`
7. `W13.TWOPOLE_REG1`

## Fixed amplifier dynamics

The SUM1 and INV1 sheets reproduce Figure 13.1's series R-C shunt from the inverting summing node to ground. For input and feedback resistors `R1` and `R2`, the lag zero and pole are

`wz = 1/(Rlag Clag)`

`wp = 1/[(Rlag + R1 || R2) Clag]`.

`Rlag` and `Clag` remain socketed symbolic values because the desired crossover reduction must be derived from the measured uncompensated loop.

REG1 qualifies for the capacitive-load comparison because the accepted plant already includes nonzero `R_EMIT`, selectable `CL_CASE`, and ESR. The compensated graph is explicitly an adaptation of Figure 13.8: existing `R_EMIT` is the isolation resistance, `C_F` returns the pre-isolation `REG1.QEMIT` node to `REG1.SENSE`, and `R_FPATH` returns `REG1.VOUT` to `REG1.SENSE`. It is not represented as a verbatim inverting amplifier.

## Adjustable amplifier dynamics

- Discrete AMP1 uses a break-before-make external selector between its verified compensation terminals. The Week 9 47 pF selection is the starting case; 20 pF, 47 pF, and 100 pF remain the declared sweep.
- LM301A INT2 is temporarily configured as a 4.70 kohm unity inverter. Its 30 pF historical selection is a starting case; 12 pF, 30 pF, and 220 pF remain the declared sweep.
- REG1 two-pole compensation is the exact Figure 13.19 true two-port: C1 and C2 are series elements between the LM301A compensation terminals, and R shunts their midpoint to ground.

Figure 13.21's 30 pF, 15 kohm, 30 pF network is verified only for its 2.2 kohm unity-gain LM301A demonstration. Those numbers are not copied into REG1.

## Measurement gate

No symbolic Week 13 value becomes build-approved until the following are recorded with declared probe/loop-break loading:

- uncompensated return ratio, crossover, phase margin, and gain margin;
- regulator `RL`, `CL`, ESR, device, and temperature envelope;
- selected target crossover and robust minimum phase margin;
- closed-loop overshoot, settling, noise amplification, and overload recovery;
- sensitivity to component tolerances and intermediate-frequency poles.

The canonical graphs, SVGs, and SPICE connectivity decks establish topology only. Ideal structural models cannot approve compensation performance.

## Deferred projects retained

- D-01: physical patch-cord routing.
- D-02: separate low-voltage redesign.
- D-03: parallel modern internally compensated implementations.
- D-04: physical chassis, board, harness, and thermal construction documentation.

`capstone.html` remains unchanged pending approval and final integration.

