# Weeks 7–8 cumulative circuit package

`graph.json` extends the accepted Weeks 0–6 chassis and uses the future Figure 9.1 stable component identities for the incremental discrete-amplifier build.

- `W07.PAIR_CHARACTERIZE` is deliberately incomplete: Q1–Q3 and their final bias/balance network exist, but there is no amplifier output and the INT1 feedback path remains isolated.
- `W08.OPEN_LOOP` adds Q4–Q11 for operating-point and crossover inspection.
- `W08.INT1_BRINGUP` connects the inherited 10 kΩ / 1 µF INT1 passive network to the transitional amplifier.

Q12/Q13 current limiting is absent until Week 9. The externally current-limited ±15 V supply is therefore part of the Week 8 safety boundary. Structural SPICE decks and SVGs are matched projections, not realistic semiconductor-performance predictions.
