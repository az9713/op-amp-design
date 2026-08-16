# Week 12 production decisions

Status: implemented for topology and presentation review. Electrical performance is not approved.

## Configuration boundary

Week 12 has three separate active electrical graphs on one cumulative chassis:

1. `W12.BW` — Figure 12.13 fourth-order Butterworth computation.
2. `W12.VDP` — Figure 12.14 Van der Pol computation.
3. `W12.REG_TWIN` — the built Figure 5.3 regulator beside a calibrated first-order analog twin.

These circuits are not simultaneously wired. Previously installed modules remain on the chassis and are shown collapsed or electrically disconnected when they are not part of the selected experiment.

## Figure 12.13 Butterworth realization

- SUM1 becomes the first integrating summer; AMP1, INT2, and the repurposed INT3 channel complete the four-integrator chain. INV1 computes `-x - 3.42 x''`.
- The implemented equation is `x'''' + 2.61x''' + 3.42x'' + 2.61x' + x = f(t)`.
- State outputs alternate signs exactly as Roberge indicates: `-x'''`, `x''`, `-x'`, `x`.
- Roberge's 1 Mohm / 1 uF network is uniformly impedance-scaled to 100 kohm / 10 uF. The one-second integration constant and every coefficient ratio are preserved while reducing LM301A input-current sensitivity.
- Selected 0.1% coefficient values are 38.3 kohm for `100k/2.61` and 29.2 kohm for `100k/3.42`. Final builds should use measured series/parallel combinations or trim networks to reach the target ratios.

## Figure 12.14 Van der Pol realization

- The baseline is `mu=1`, `RC=1 s`, with AMP1 and INT2 as the two integrators and SUM1 producing `-x + mu dx/dt`.
- Two multipliers are required. Figure 11.28 is not accepted because it is two-quadrant while both Van der Pol state variables are bipolar.
- The primary build uses two AD633 four-quadrant multipliers. The manufacturer specifies `W=(X1-X2)(Y1-Y2)/10V+Z`, matching Roberge's assumed divide-by-10 multiplier law. Rated operation is on +/-15 V rails, with differential X/Y inputs and a summing Z input. See the [Analog Devices AD633 data sheet](https://www.analog.com/media/en/technical-documentation/data-sheets/AD633.pdf).
- M1 forms `x^2/10`; M2 forms `-x^2(dx/dt)/100`. The 10 kohm nonlinear input resistor restores the factor of 100 at `mu=1`.
- Roberge Figure 12.9 remains the historical time-division alternative. It is deferred as a separate implementation because it requires a carrier, switching network, reference, filtering, and carrier-feedthrough validation.

## Figure 5.3 regulator twin

Roberge gives the load-disturbance transfer function

`Vl/Id = (R/a0) / [R CL s/a0 + 1 + R/(a0 RL)]`.

The build does not invent a numerical `a0`. The twin is calibrated from the actual assembled regulator:

- `K_DROOP = |delta Vout| / delta Iload` from the steady load-step response.
- `TAU_MEAS` from the first-order step trace.
- With selected `C_TWIN = 1 uF`, choose `R_TWIN_LEAK = TAU_MEAS/C_TWIN`.
- For current scale `I_SCALE` volts per ampere, choose `R_TWIN_DRIVE = R_TWIN_LEAK/(K_DROOP*I_SCALE)`.

The Week 6 oscillator controls both the physical 1 kohm switched load and the twin input scaler. REG1 and twin outputs receive equal declared 10 Mohm scope loading. The ordinary Week 5 independent current-pulse fixture is disconnected in this configuration.

## Claim boundary and deferred work

- The canonical graph, every SVG, and every SPICE connectivity deck agree pin-for-pin/net-for-net.
- The AD633 graph uses a structural interface, not a realistic manufacturer macro-model. Multiplier error, bandwidth, feedthrough, offsets, and saturation are not yet proven.
- The regulator-twin resistor values remain symbolic until the physical regulator's droop and time constant are measured.
- The Week 9/10 performance failures remain inherited and open.
- Deferred: Figure 12.9 historical multiplier, realistic AD633 model/error budget, automated reset sequencing, physical patch-cord drawings, and the separate low-voltage redesign.
- `capstone.html` remains unchanged pending approval and final integration.
