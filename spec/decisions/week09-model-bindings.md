# Week 9 model bindings and provenance decision

Status: **binding architecture decided; realistic historical binding incomplete**  
Date: 2026-08-15  
Scope: `AMP1` active devices and unnamed Figure 9.1 diodes only; this document does not encode the circuit graph.

## Decision

Week 9 will produce two electrically equivalent SPICE projections from the same canonical graph:

- `MODEL_TIER=ideal`: identical, generic ngspice devices with default parameters and no claim of quantitative fidelity. “Ideal” means matched topology proof here; the built-in semiconductor equations are not mathematical ideal transistors. This tier proves instance/pin/net projection and exercises the test harness.
- `MODEL_TIER=realistic`: explicit vendor models or deliberately named generic surrogates with provenance and calibration receipts. This tier alone may support performance comparisons, and its conclusions remain model-conditional.

The historical part number is a component attribute. The simulation binding is a separate attribute. A missing realistic binding is an explicit unsupported state, never an invitation to relabel a convenient model.

## Canonical binding matrix

| Canonical devices | Historical identity | Topology binding | Realistic binding now | Disposition |
|---|---|---|---|---|
| `AMP1.Q1`, `AMP1.Q2` | 2N5963 NPN, selected pair | `MODEL.W09.NPN_BASE` | `MODEL.VENDOR.CENTRAL.2N5963` available only as external candidate | Do not vendor without Central's written permission. Modern Central behavior is not proven historical behavior. |
| `AMP1.Q3`, `AMP1.Q7`, `AMP1.Q9`, `AMP1.Q12` | 2N3707 NPN | `MODEL.W09.NPN_BASE` | `MODEL.VENDOR.CENTRAL.2N3707` available only as external candidate | Same rights and historical-equivalence caveat. |
| `AMP1.Q4`, `AMP1.Q5`, `AMP1.Q6`, `AMP1.Q13` | 2N4250 PNP; Q4/Q5 matched | `MODEL.W09.PNP_BASE` | `UNBOUND.W09.2N4250` | Use no exact-name model until provenance is verified. A future surrogate must retain the 2N4250 BOM identity separately. |
| `AMP1.Q8` | TIS58 N-channel JFET | `MODEL.W09.NJF_BASE` | `UNBOUND.W09.TIS58` | TI historical catalog evidence is not a model. JFET spread requires corners, not one falsely precise card. |
| `AMP1.Q10` | 2N2219 NPN | `MODEL.W09.NPN_BASE` | `MODEL.VENDOR.CENTRAL.2N2219` available only as external candidate | Do not substitute 2N2219A without an explicit design decision. |
| `AMP1.Q11` | 2N2905 PNP | `MODEL.W09.PNP_BASE` | `UNBOUND.W09.2N2905` | An onsemi 2N2905A datasheet does not authorize silent A-suffix substitution. |
| `AMP1.D_DRV_1`, `AMP1.D_DRV_2`, `AMP1.D_BAL`, `AMP1.D_BIAS` | type unstated in source | `MODEL.W09.D_BASE` | `UNBOUND.W09.DIODE` | Orientations are adjudicated; realistic part/model selection remains an electrical-role decision. |

## Matching semantics

- The topology tier binds Q1/Q2 to one nominal model and Q4/Q5 to one nominal model: exact matching is intentional.
- The realistic nominal run also starts from common model cards; it does not obtain matching by selecting two unrelated vendor cards.
- A separate input-pair mismatch campaign must respect the source selection envelope: Q1/Q2 within 3 mV VBE and 10% beta at the operating current. How model parameters are perturbed is an electrical-design choice and cannot be inferred from those two screening limits alone.
- Q4/Q5 are described as matched, but the source map gives no numeric matching envelope. Their mismatch sweep remains unspecified rather than invented.

## Evidence assessment

### Observed

- Current Central product pages expose `.LIB` links for exact names 2N5963, 2N3707, and 2N2219.
- Central's site-use terms say its content may not be copied or redistributed without prior written consent.
- Central's PDN01064 lists 2N4250/2N4250A as end-of-life and gives no replacement.
- A 1969 TI catalog scan lists TIS58 as a silicon field-effect transistor, but supplies no SPICE card or license for one.
- onsemi publishes a current 2N2905A primary datasheet; the source circuit specifies 2N2905.
- ngspice supports built-in BJT and JFET models. The default declarations are lawful for a local topology smoke test, but their default parameters are not evidence about Roberge's devices.

### Inference

A modern exact-name model is more realistic than a parameter-free default for that manufacturer's current implementation, but it is not automatically a reconstruction of a 1970s device. The project must describe such results as **vendor-model-conditional**, not historical validation.

## Admission test for a realistic model

A candidate enters `MODEL_TIER=realistic` only when its receipt records:

1. exact source URL or local primary source;
2. owner/author and model version or retrieval date;
3. explicit redistribution permission, or `external_user_local` status;
4. SHA-256 of the exact file used;
5. declared SPICE dialect and parsed model name;
6. device polarity and terminal-order check;
7. a one-device characterization deck covering the Week 9 current/voltage region;
8. differences between datasheet constraints, fitted parameters, and simulation results.

## Smallest honest route to Gate 2

1. Use the topology tier to prove graph/SVG/SPICE equivalence and harness mechanics.
2. Ask Central for redistribution permission, or implement pinned user-local retrieval for 2N5963, 2N3707, and 2N2219.
3. Create openly distributable, clearly generic PNP and N-JFET surrogates from documented primary-data constraints; do not name them 2N4250 or TIS58.
4. Run nominal and corner results side by side. If only the topology tier is available, Gate 2 may review connectivity, but quantitative transient/compensation claims remain unsupported.

## Primary and local sources

- Local circuit evidence: `week09-source-map.md` and `op_amps_roberge.pdf`, especially Figure 9.1 and pp. 239–255.
- Central 2N5963: <https://my.centralsemi.com/product/partpage2.php?part=2N5963>
- Central 2N3707: <https://my.centralsemi.com/product/partpage2.php?part=2N3707>
- Central 2N2219: <https://my.centralsemi.com/product/partpage2.php?part=2N2219>
- Central model index: <https://my.centralsemi.com/content/engineering/spicemodels/index.php>
- Central site terms: <https://www.centralsemi.com/terms-web>
- Central 2N4250 EOL notice: <https://www.centralsemi.com/docs/ENGINEERING/pdn/PDN01064.PDF>
- TI 1969 catalog scan containing TIS58: <https://www.bitsavers.org/components/ti/_dataBooks/1969_CC202_Preferred_Semiconductors_and_Components_from_Texas_Instruments.pdf>
- onsemi 2N2219 datasheet: <https://www.onsemi.com/download/data-sheet/pdf/2n2219-d.pdf>
- onsemi 2N2905A datasheet: <https://www.onsemi.com/download/data-sheet/pdf/2n2905a-d.pdf>
- ngspice manual: <https://ngspice.sourceforge.io/docs/ngspice-manual.pdf>

## Blockers

- **BLOCKER — rights:** Central model text cannot be committed under the published site terms without written permission.
- **BLOCKER — coverage:** no verified realistic binding yet covers 2N4250, TIS58, exact 2N2905, or the four unnamed diodes.
- **RESOLVED — source transcription:** Transcription B and the A/B adjudication are complete; `circuits/weeks/w09/graph.json` carries the accepted topology.
- **RESOLVED FOR PROVISIONAL PROOF — fixture:** `week09-proof-values.md` selects 4.70 kΩ for `W09.R1`, exact source-defined case capacitors, and a socketed 47 pF retained end state. These remain proposed build/proof values, not historical facts.
- **RESOLVED FOR BASELINE SYNTAX ONLY — simulator:** pinned ngspice 47 at `C:\Users\simon\scoop\apps\ngspice\47\bin\ngspice_con.exe` loaded all four declarations in `w09-topology-baseline.lib` and completed the minimal `.op` smoke deck with exit code 0 and one finite data row. See `../../tests/electrical/smoke/w09-model-load.receipt.json`. This does not resolve any realistic-model blocker.
- **MAJOR — repository rights:** the repository declares no license, so public redistribution terms for project-authored surrogate files are also undecided.
