# Weeks 7–8 production decisions

## Progression rule

Weeks 7 and 8 use stable component identities from the independently transcribed Week 9 Figure 9.1 circuit. This is an explicit project interpretation because Roberge Chapters 7 and 8 teach precursor stages rather than a pin-for-pin assembly sequence for Figure 9.1.

## Week 7

- remove the stock LM301A occupant from SLOT.INT1 and preserve it as an off-circuit artifact;
- install the final `AMP1.Q1/Q2` 2N5963 matched pair and `AMP1.Q3` 2N3707 tail source;
- install their final Figure 9.1 collector/balance and common-bias parts rather than temporary parts that would immediately be discarded;
- tie both bases to the same declared 0 V fixture for the balance measurement and load both collector measurements with declared 10 MΩ instruments;
- leave `AMP1.OUT` electrically absent and the INT1 feedback capacitor isolated;
- label the channel prominently as incomplete and prohibit a computer-loop or integrator-function claim.

Temperature points of 25, 35, and 45 °C are a proposed teaching protocol. They do not imply that generic topology-only transistor models predict the historical drift.

## Week 8

- retain every Week 7 permanent component;
- add the exact Figure 9.1 `Q4–Q11` gain, FET-buffer, bias, output, decoupling, and 22 Ω output-path subset;
- install a socketed 47 pF provisional compensation capacitor as a conservative bring-up choice, explicitly subject to reselection during Week 9;
- provide separate matched configurations for open-loop operating-point/crossover inspection and closed INT1 integrator bring-up;
- reconnect the inherited 10 kΩ / 1 µF INT1 passive network only in the closed-loop configuration;
- keep `Q12/Q13` current limiting absent until Week 9 and require externally current-limited ±15 V rails; no short-circuit test is authorized.

The open-loop fixture is a microvolt stimulus/operating-point diagram. Practical gain extraction still requires a centering/null method and must not be inferred from ordinary saturated open-loop drive.

## Deferred boundaries

- historical-package pin numbers and lawfully sourced realistic models;
- exact diode types and the unresolved 5.6 kΩ tolerance dot;
- thermal construction and output-bias tracking;
- patch-cord and physical panel routing;
- the separate low-voltage modern redesign.
