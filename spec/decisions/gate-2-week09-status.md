# Gate 2 — Week 9 vertical-proof status

Status: **BLOCKED — GATE 2 NOT APPROVED**  
Snapshot date: 2026-08-15  
Review surface: `../../docs/gate-2-week09-proof.html`

## Current project context

This remains the authoritative historical Week 9 vertical-proof result: its electrical gate is still blocked. Later user decisions separately authorized weekly production and publication. The completed project now also has a [final ideal-tier functional simulation](../../docs/final-spice-simulation.html) using behavioral/generic models; its 8/8 pass demonstrates final-system signal flow and regulator-twin calibration, not the transistor-level claims that failed here.

## Boundary

This record evaluates the Week 9 vertical proof only. At this historical gate it did not authorize Week 0–13 production, construction release, realistic-model claims, or integration into `capstone.html`. Later explicit approvals changed the production/publication state, not this gate's electrical verdict.

## Independent gate scorecard

| Gate | Score | Status | Evidence | What remains |
|---|---:|---|---|---|
| Schema | 2/2 | **PASS** | Current graph SHA-256 `506362af3509b1f2226d413898b15f832bbc1979c2b4e9087ad7613b1d395dbe`; graph validator PASS; full discovery suite 60/60 PASS | Re-run after graph, layout, renderer, or test changes |
| Connectivity | 2/2 | **PASS** | Six Gate 2 projections (three main plus three AMP1 detail) and all eight executable proof cases have matching graph↔SVG/SPICE receipts | Re-run after graph, layout, or projection changes |
| Visual | 2/2 | **PASS** | Final main and AMP1-detail SVGs exist for all three variants; publication-scale human review passed the final resolved INV20, INT1, and AMP1-detail views | Re-run visual review after any layout or renderer change |
| Electrical | 0/2 | **FAIL / BLOCKED** | All eight topology-tier decks executed, but all three quantitative acceptance assertions failed | Lawful characterized device models or measurements; then rerun and reassess |

The component scores are deliberately not converted into approval. **Gate 2 is not approved.**

## Matched publication projections

The authoritative publication candidates are under `generated/week09/gate2/`. The older files directly under `generated/week09/` are stale and are not Gate 2 evidence. Every receipt below records the current canonical SHA and empty SVG/SPICE difference lists.

| Variant / view | SVG | SPICE | Receipt | SVG SHA-256 | SPICE SHA-256 |
|---|---|---|---|---|---|
| CC sweep / main | [SVG](../../generated/week09/gate2/w09-cc_sweep-ideal.svg) | [CIR](../../generated/week09/gate2/w09-cc_sweep-ideal.cir) | [JSON](../../generated/week09/gate2/w09-cc_sweep-ideal.connectivity.json) | `9cad91f0b9ba38cbf960efc6727b7eaea474858832b3ae943cb596f8991a07d1` | `7116c03e5b5a513c340c6fbe23f54f36c39902422282e83f15c52e4e57489974` |
| CC sweep / AMP1 detail | [SVG](../../generated/week09/gate2/w09-cc_sweep-ideal-amp1-detail.svg) | [CIR](../../generated/week09/gate2/w09-cc_sweep-ideal-amp1-detail.cir) | [JSON](../../generated/week09/gate2/w09-cc_sweep-ideal-amp1-detail.connectivity.json) | `ebada11100fe23d8b984a7e3f5a61db8829dc07c01bd7cedfdabfd1d78b692e1` | `8bdf5e7d726b1d4acd79c84e9619e3e33184acc0affc047ec60b4dc550ccd6a4` |
| Inverter test / main | [SVG](../../generated/week09/gate2/w09-inverter_test-ideal.svg) | [CIR](../../generated/week09/gate2/w09-inverter_test-ideal.cir) | [JSON](../../generated/week09/gate2/w09-inverter_test-ideal.connectivity.json) | `f6baff3cf250d644fd369465143862ee4bad38bbf8eeda5894a138bade011aa1` | `9ba05e9eca75a8d84dab67e6c2d58dceb32e7e8127e47573edc2ae9e9bfaec34` |
| Inverter test / AMP1 detail | [SVG](../../generated/week09/gate2/w09-inverter_test-ideal-amp1-detail.svg) | [CIR](../../generated/week09/gate2/w09-inverter_test-ideal-amp1-detail.cir) | [JSON](../../generated/week09/gate2/w09-inverter_test-ideal-amp1-detail.connectivity.json) | `5c5a3370b14d47069d76ba51c6419627e2083527556abd3a5258aaee58f25f07` | `8bdf5e7d726b1d4acd79c84e9619e3e33184acc0affc047ec60b4dc550ccd6a4` |
| Restored INT1 / main | [SVG](../../generated/week09/gate2/w09-int1_restored-ideal.svg) | [CIR](../../generated/week09/gate2/w09-int1_restored-ideal.cir) | [JSON](../../generated/week09/gate2/w09-int1_restored-ideal.connectivity.json) | `2b978c381c889bd59e3c64c168cd0483fa6d58c4ee9d9d289a81ecab7af42d8b` | `e5496f705d80060d5817f15d57f4246259d23b784354825f3a0efc858259ecf8` |
| Restored INT1 / AMP1 detail | [SVG](../../generated/week09/gate2/w09-int1_restored-ideal-amp1-detail.svg) | [CIR](../../generated/week09/gate2/w09-int1_restored-ideal-amp1-detail.cir) | [JSON](../../generated/week09/gate2/w09-int1_restored-ideal-amp1-detail.connectivity.json) | `c1245a0cfe620fdc1ead883e2425772efd8fe795787de26e3a99952cc880e0e4` | `8bdf5e7d726b1d4acd79c84e9619e3e33184acc0affc047ec60b4dc550ccd6a4` |

Receipt SHA-256 values are identical for main/detail of a variant because each pair attests the same canonical connectivity: CC sweep `b38cc449b6d8303383a0054596bac9f553b06f034b7ab541f2283ad89d9b2459`, inverter `c6ba5a9fdbbd6fbb40230826459ef686e610c99f15d998015acaf267ef0c83aa`, restored INT1 `cfe23da69408bdb6236e36f3a459e033a609d2730ae6043413007e07849eeb50`.

## Executable resolved-case receipts

Authoritative run summary: [summary.json](../../generated/week09/proof/summary.json), SHA-256 `84e18375e660e3211132d69228ca28a0e0ca2cf0582f212b44dba93e24e2f399`. It records `pipeline_execution: PASS`, `electrical_acceptance: FAIL`, and `status: BLOCKED`.

Each case directory contains the exact resolved graph, generated schematic, canonical connectivity deck and receipt, executed simulation deck and receipt. `simulation_passed=true` means ngspice completed and results were parsed; it does **not** mean the circuit passed electrical acceptance.

| Case | Variant | Resolved graph / SVG | Connectivity deck / receipt | Simulation deck / receipt | Canonical connectivity SHA-256 | Executed deck SHA-256 |
|---|---|---|---|---|---|---|
| INV20 | `W09.INVERTER_TEST` | [graph](../../generated/week09/proof/cases/inv20/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/inv20/schematic.svg) | [CIR](../../generated/week09/proof/cases/inv20/connectivity.cir) / [receipt](../../generated/week09/proof/cases/inv20/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/inv20/simulation.cir) / [receipt](../../generated/week09/proof/cases/inv20/simulation.receipt.json) | `d0becce85dbe9a06bc985d290c7c1651432c4e8ca7bd07ffa94da1beb1e5b0eb` | `cd83b8cf88ddddb2f5f60e96b79d54f86aff96b65f7bead721376c0ea96a0dd6` |
| A47 | `W09.CC_SWEEP` | [graph](../../generated/week09/proof/cases/a47/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/a47/schematic.svg) | [CIR](../../generated/week09/proof/cases/a47/connectivity.cir) / [receipt](../../generated/week09/proof/cases/a47/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/a47/simulation.cir) / [receipt](../../generated/week09/proof/cases/a47/simulation.receipt.json) | `8744ce9805f111ac69e9477e13a09abaaf9efe03da8f3997841e5a4f88643dfb` | `813f8678cf025dc6c4e1de3179d36be2467ddd998a6282789e731c0a8c69965d` |
| A33 | `W09.CC_SWEEP` | [graph](../../generated/week09/proof/cases/a33/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/a33/schematic.svg) | [CIR](../../generated/week09/proof/cases/a33/connectivity.cir) / [receipt](../../generated/week09/proof/cases/a33/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/a33/simulation.cir) / [receipt](../../generated/week09/proof/cases/a33/simulation.receipt.json) | `fbf9a5fba516080fcd461879e8f08fed2569349c94418702f4b4824685d40357` | `779099df0ead606496dd969d32efa18e904f4d8f2789622bf707dc193ab582b8` |
| A10 | `W09.CC_SWEEP` | [graph](../../generated/week09/proof/cases/a10/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/a10/schematic.svg) | [CIR](../../generated/week09/proof/cases/a10/connectivity.cir) / [receipt](../../generated/week09/proof/cases/a10/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/a10/simulation.cir) / [receipt](../../generated/week09/proof/cases/a10/simulation.receipt.json) | `35b4e62bee4028be2b3ccc16ccb3f9caf0ce6521002e08f96cf172706a75951f` | `033671d5100ec009d608f414d140fb3f4b5e98bcfd0dbeee6e3e831ce3f036b9` |
| A05 | `W09.CC_SWEEP` | [graph](../../generated/week09/proof/cases/a05/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/a05/schematic.svg) | [CIR](../../generated/week09/proof/cases/a05/connectivity.cir) / [receipt](../../generated/week09/proof/cases/a05/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/a05/simulation.cir) / [receipt](../../generated/week09/proof/cases/a05/simulation.receipt.json) | `e977161d29da432ff6d2db64a1fa4281d94539fc0929d5c3dd665cbe9231d674` | `73fa31e2e250cb7b32db744242f7d6cf5fc11a52193cc3594eb21ec150840ff9` |
| B20 | `W09.CC_SWEEP` | [graph](../../generated/week09/proof/cases/b20/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/b20/schematic.svg) | [CIR](../../generated/week09/proof/cases/b20/connectivity.cir) / [receipt](../../generated/week09/proof/cases/b20/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/b20/simulation.cir) / [receipt](../../generated/week09/proof/cases/b20/simulation.receipt.json) | `66734f54860655fd6615796ecf3ba6fbb2e89ef1d15ff185d30fcd5dad460f16` | `fe0593e09d30fa65883b9369cc7012be6fc3f00ba74de6e06529dc3e992afd22` |
| B10 | `W09.CC_SWEEP` | [graph](../../generated/week09/proof/cases/b10/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/b10/schematic.svg) | [CIR](../../generated/week09/proof/cases/b10/connectivity.cir) / [receipt](../../generated/week09/proof/cases/b10/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/b10/simulation.cir) / [receipt](../../generated/week09/proof/cases/b10/simulation.receipt.json) | `845e4f37759b3ab98691850d3a306987b6b2623afaf4ec37c4a7a30fd2b60129` | `c9a0442bc0a8a4b3de63308d96ed685f0020203ab1829e8256fbd862c3b48c71` |
| INT1 | `W09.INT1_RESTORED` | [graph](../../generated/week09/proof/cases/int1/graph.resolved.json) / [SVG](../../generated/week09/proof/cases/int1/schematic.svg) | [CIR](../../generated/week09/proof/cases/int1/connectivity.cir) / [receipt](../../generated/week09/proof/cases/int1/connectivity.receipt.json) | [deck](../../generated/week09/proof/cases/int1/simulation.cir) / [receipt](../../generated/week09/proof/cases/int1/simulation.receipt.json) | `4260d00d717d8bf3ba578559f43174902982096f8f5f37b78091736a69412851` | `d3d81ace1c241249adc464860a0a3404575b4dc09de73566a9b7c2884802df6f` |

## Electrical acceptance failures

| Criterion | Required | Observed | Result |
|---|---|---:|---|
| `W09-EL-01` physical 50 kΩ balance sweep can reduce zero-input output | magnitude ≤ 0.1 V | 5.22185024 V | **FAIL** |
| `W09-EL-02` 1 Hz closed-loop inverter gain magnitude | 0.9–1.1 | 0.0349075907 | **FAIL** |
| `W09-EL-03` ideal-scale INT1 change during +100 mV for 20 ms | −0.2 V ±10% | +0.08338962 V | **FAIL** |

## Source, value, and model limitations

- Historical package pin numbers and four diode types remain unresolved; Figure 9.8 omits numeric R1, generator impedance, output load, and probe/parasitic values.
- The proof uses documented proposed/derived/inherited values: R1 4.70 kΩ, alpha-quarter shunt 2.350 kΩ, inherited INT1 10 kΩ/1 µF, explicit source/load/probe assumptions, exact source Cc cases, and provisional retained Cc 47 pF. These are build-oriented proof choices, not historical claims.
- The executable cases use generic ngspice topology-default semiconductor cards. Their successful execution establishes pipeline operation only. Their bias, gain, compensation, and transient results are nonpredictive.
- [realistic-projection.json](../../generated/week09/proof/realistic-projection.json) is correctly `BLOCKED`: no ideal/default card may be relabeled realistic, and AMP1 lacks lawful realistic model bindings.
- Exact realistic bindings for several historical parts remain unavailable for redistribution or characterization. Do not tune the topology defaults and promote the result as historical evidence.

## Snapshot verification

```text
python tools/validate_circuit_graph.py circuits/weeks/w09/graph.json
PASS: circuits\weeks\w09\graph.json

python -m unittest discover -s tests -v
Ran 60 tests in 3.982s
OK

python -m compileall -q tools tests
exit 0
```

## Close-out conditions

- [x] Current graph validates.
- [x] Three main and three AMP1-detail graph↔SVG↔SPICE projections match canonical connectivity.
- [x] Eight exact resolved topology-tier cases execute under ngspice and have receipts.
- [x] Electrical assertions run and report failures without being misrepresented as passes.
- [x] Full 60-test suite passes, including resolved INV20/INT1 foreign-terminal through-wire regression coverage.
- [x] Publication-scale human review passed: INT1 input routes above collapsed AMP1; rail-trunk crossings are explicitly insulated; no foreign-terminal or module intrusion remains.
- [ ] Obtain lawful characterized device models or measurement evidence and pass electrical acceptance.
- [ ] Obtain the user's explicit Gate 2 decision.

## Capstone integration hold

Do not edit or embed into `capstone.html` during this proof phase. A later successful Gate 2 decision authorizes only the next expressly agreed production phase; it does not silently authorize capstone integration.
