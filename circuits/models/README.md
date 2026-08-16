# Circuit-model provenance policy

This directory separates four claims that must never be collapsed:

1. **Historical identity** — the part number printed in Roberge Figure 9.1.
2. **Ideal/topology baseline** — a matched generic device that lets ngspice exercise connectivity.
3. **Realistic surrogate** — a deliberately named, calibrated approximation.
4. **Vendor exact-name model** — a model carrying the historical part number, but not necessarily the historical die/process.

`model-registry.json` is the inventory. `w09-topology-baseline.lib` contains only project-authored declarations that invoke ngspice's built-in defaults. Generated artifacts call this `MODEL_TIER=ideal` to match the project deliverable name. “Ideal” here means nominally matched, generic topology proof; ngspice's default semiconductor equations are not mathematical ideal transistors. The file carries no copied vendor parameters and makes no performance claim.

The library has been syntax/load tested with pinned ngspice 47. The minimal `.op` deck at `../../tests/electrical/smoke/w09-model-load.cir` bound the NPN, PNP, N-JFET, and diode declarations and converged with one finite data row. Its receipt is beside the deck. This validates library mechanics only.

## Rules

- The schematic/BOM keeps the historical type even when simulation uses another binding.
- Every generated deck records `binding_id`, source URL, retrieval date, SHA-256, model name, and simulator version in its receipt.
- BJT instances are projected in SPICE `C B E` order and JFET instances in `D G S` order. Package lead numbers are a separate physical-layout concern.
- A substitute is named `GENERIC_*` or `SURROGATE_*`; it must not be renamed to a historical part number.
- Q1/Q2 and Q4/Q5 share nominal models when testing ideal matching. Mismatch campaigns are explicit corners, not accidental use of unrelated model cards.
- Do not download or commit a vendor model merely because a public URL exists. First verify an explicit license covering redistribution of that exact file.
- If redistribution is forbidden or unclear, an optional user-local acquisition step may download outside the repository, verify a pinned SHA-256, and bind it at run time. Generated public artifacts must not embed that file's text.

## Current result

Central Semiconductor publishes exact-name model links for 2N5963, 2N3707, and 2N2219. Its site terms reserve the content and prohibit copying or redistribution without written consent. Those three entries are therefore discoverable external candidates, not repository assets.

No lawfully redistributable exact model has been verified for 2N4250, TIS58, or exact 2N2905. The onsemi 2N2905A datasheet is useful component evidence but does not establish that an A-suffix model represents the source's unsuffixed device.

## Sources and rights boundary

- Central model listing: <https://my.centralsemi.com/content/engineering/spicemodels/index.php>
- Central site-use terms: <https://www.centralsemi.com/terms-web>
- ngspice manual: <https://ngspice.sourceforge.io/docs/ngspice-manual.pdf>
- ngspice project/license: <https://sourceforge.net/projects/ngspice/>
- Week 9 local source map: `../../spec/decisions/week09-source-map.md`

ngspice licensing covers the simulator, not third-party model cards. The repository itself currently declares no license, so even project-authored model material remains project-local until that separate decision is made.
