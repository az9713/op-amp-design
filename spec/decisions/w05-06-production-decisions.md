# Weeks 5–6 production decisions

Status: implementation decision record for the first review batch; not yet approved for `capstone.html`.

## Week 5 regulator

Roberge Figure 5.3 is a symbolic teaching plant rather than a safe physical BOM. The project therefore binds it to this explicit low-power envelope:

- regulated output: 10 V nominal;
- plant input: external isolated 18 V bench channel, current limited to 35 mA;
- error amplifier: LM301A on the permanent ±15 V rails, 30 pF compensation;
- reference: 1N4740A 10 V Zener, fed from +15 V through 330 Ω / 0.5 W and bypassed by 10 µF;
- pass device: BD139 NPN emitter follower;
- Figure 5.3 series emitter resistance: 100 Ω / 0.25 W;
- output load cases: 470 Ω, 1 kΩ, 2.2 kΩ, each rated at least 0.5 W;
- capacitive load cases: 10 µF, 47 µF, 100 µF, at least 25 V, with a declared 0.30 Ω ESR seed until measured parts are selected;
- 10 kΩ output bleeder and 1N4002 reverse-discharge diode;
- explicit zero-DC/AC-1 loop-injection source and 0→10 mA load-current step fixture.

At 10 V, the three load currents are approximately 21.3 mA, 10 mA, and 4.55 mA. The 470 Ω load dissipates about 0.213 W. At the heaviest nominal load, the 100 Ω series resistor dissipates about 0.045 W and the BD139 remains in a low-power regime. These calculations do not authorize a short-circuit test: the 35 mA external current limit is part of the circuit’s safety boundary.

Optional Figure 5.11/5.13 adaptations are not installed in Week 5. They remain conditional experiments requiring measured Week 4 crossover data; copying their example values into the computer loop would be unjustified.

## Week 6 oscillator

- populate the reserved INT3 socket with a dedicated LM301A integrator;
- add a separate LM301A Schmitt stage;
- use equal 100 kΩ Schmitt input/feedback resistors;
- limit the square node with a 1 kΩ series resistor and two back-to-back 1N4733A 5.1 V Zeners;
- use 1 MΩ and 1 µF film for the dedicated integrator, giving `RC = 1 s` and the source’s nominal symmetric relation `T ≈ 4RC ≈ 4 s`;
- expose square and triangle outputs with declared 10 MΩ scope loading;
- retain `VC` as a named, grounded reserved control for this week; duty-cycle modulation is not implemented in the required configuration;
- use a declared 10 mV capacitor initial condition or model offset only in ideal simulation. No hidden bleed resistor is introduced.

The Zener clamp amplitude is nominal rather than precision. It must be measured at the actual few-milliamp operating current; the triangle threshold follows the measured limited square amplitude.

## Historical and modern boundaries

The historical primary remains LM301A on ±15 V. BD139 and the explicit Zener limiters are documented engineering completions of symbolic source circuits, not claims that Roberge specified those parts. A modern comparator/reference implementation may be proposed later as a parallel note. The low-voltage rail-to-rail redesign remains a separate deferred project.

## Deferred physical work

- patch-cord and jack-panel routing;
- PCB and enclosure layout;
- heatsink/airflow placement;
- exact selected capacitor ESR/leakage and Zener dynamic resistance;
- realistic, lawfully sourced LM301A and diode models;
- regulator loop-compensation retuning after measurements.
