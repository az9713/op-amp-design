# Requirements audit — Phase 0/1 weekly specification drafts

**Status:** REVIEW REPORT ONLY. This file does not authorize or perform circuit encoding, schematic rendering, SPICE authoring, simulation, dependency installation, toolchain selection, or modification of `capstone.html`.

**Date:** 2026-08-15  
**Scope:** `project-controls.html`, `drafts/spec-weeks-00-04.md`, `drafts/spec-weeks-05-09.md`, and `drafts/spec-weeks-10-13.md`, checked against `preflight-decisions.html` (DEC-001 through DEC-016 and D-01 through D-04) and `implementation-plan.html`.  
**Verdict:** **REQUEST CHANGES BEFORE GATE 0 APPROVAL.** The drafts are unusually strong as source-aware engineering notes, but they are not yet one integrated fourteen-state specification. No decision is wholly absent; the blockers are cross-range identity, incomplete build definitions, inconsistent acceptance/provenance fields, and several unresolved circuit adaptations.

## Executive findings

### Blockers

1. **The three ranges do not share stable identities or rail/net names.** Weeks 0–4 use `AC.*`, `INF.*`, `P15_*`, `N15_*`, `SGND`, and `PGND`; Weeks 5–9 provisionally use `CORE.*`, `INFRA.VP15`, `INFRA.VN15`, and `INFRA.AGND`; Weeks 10–13 use `CMP-*`, `PLANT-*`, `SRC-*`, `VCC_15`, `VEE_15`, and `AGND` (`spec-weeks-00-04.md:17-30`, `spec-weeks-05-09.md:13-16`, `spec-weeks-10-13.md:19-37`). Until these are reconciled, DEC-002 and DEC-009 cannot be audited mechanically and the phrase “same physical chassis” is not a provable identity claim.
2. **Gate 0 electrical blockers remain unresolved.** The regulator implementation and protection, Week 6 oscillator allocation/limiter, Week 7 diagnostic fixture, Week 8 topology, Week 8→9 preservation map, Week 9 double transcription/models, Week 10 current-repeater insertion, Week 11 rectifier interface, Week 12 four-quadrant multiplier and regulator twin, and Week 13 compensation values all remain open (`spec-weeks-00-04.md:430-438`, `spec-weeks-05-09.md:596-610`, `spec-weeks-10-13.md:472-480`). That is appropriate for a draft, but it means the present package cannot close Gate 0.
3. **Week 12's claimed physical superset is incomplete.** `CMP-SUM1` is reconfigured as the first integrating summer, but the Week 12 physical delta only names `CMP-INT3`, two multipliers, and `TWIN-REG1`; it does not identify the integrating feedback capacitor, selection hardware, or previously installed physical element that makes the summer an integrator (`spec-weeks-10-13.md:224-232`). Configuration wiring alone cannot supply a component that did not previously exist.
4. **Week 12 is not yet build-ready.** The two required multiplier modules have only abstract interfaces and an explicitly TBD physical implementation (`spec-weeks-10-13.md:268-313`). The regulator twin also lacks its frozen state equation, signs, scale, and component graph (`spec-weeks-10-13.md:315-337`). These are correctly disclosed, but DEC-004/005 cannot pass until they are resolved or the user explicitly approves them as pre-implementation design tasks with acceptance criteria.

### Major issues

5. **`project-controls.html` contains stale/incompatible naming examples.** It declares `W12-BUTTERWORTH`, `W12-VDP`, `W13-FIXED-A`, and `W13-CHANGE-A` (`project-controls.html:110-115`), while the drafts use `W12-BW`, `W13-FIXED-AS`, `W13-VARY-AS`, and several child configurations (`spec-weeks-10-13.md:234`, `359-404`). Either the controls or the integrated specification must become the single naming register before graph work.
6. **The required schema is not applied uniformly.** `project-controls.html:81-90` requires identity/purpose (including learning objective), cumulative state, evidence, electrical boundary, values, additions, verification, presentation, historical/modern treatment, and issues. Weeks 0–9 have consistent headings but no explicit learning-objective field. Weeks 10–13 also omit explicit learning objectives; Weeks 12–13 fold inheritance/delta and components/pins into prose rather than providing complete, auditable fields for each configuration.
7. **Recommended-value provenance does not consistently satisfy the controls.** The controls require a derived claim to expose formula, inputs, units, and dependencies (`project-controls.html:98-101`). Examples needing reclassification or derivation include the Week 1 `100 ohm` output isolator (`spec-weeks-00-04.md:168`) and Week 5 `470 ohm/1 kohm/2.2 kohm` load and `10/47/100 uF` capacitor sets (`spec-weeks-05-09.md:91-92`). These are useful proposals, but they are not derived results as currently documented. Use **Proposed** until a load/current/pole/thermal calculation is shown.
8. **Evidence vocabulary is inconsistent with project controls.** All three drafts define only Verified/Derived/TBD (`spec-weeks-00-04.md:7-12`, `spec-weeks-05-09.md:7-16`, `spec-weeks-10-13.md:11-17`), omitting the controls' distinct **Proposed** and **Deferred** classes. Consequently, engineering recommendations are sometimes labeled Derived without a derivation, and deferred work is described textually instead of using the shared evidence class.
9. **The three validation gates are not specified consistently for every week/configuration.** Week 9 explicitly lists connectivity, electrical, and visual/source acceptance (`spec-weeks-05-09.md:567-576`), and Weeks 10–13 have a strong range-level matched-graph contract (`spec-weeks-10-13.md:450-459`). Weeks 0–8 generally state SPICE targets and sheet recommendations, but they do not all state mechanical connectivity equivalence and source/visual acceptance criteria. Add a common three-gate acceptance block to every configuration or a binding global block that enumerates all configuration IDs.
10. **Source locators are uneven.** Weeks 5–9 cite exact `capstone.html` line ranges and PDF pages. Weeks 10–13 refer to “capstone Chapter N step” or “Capstone Week 12” without line/anchor locators (`spec-weeks-10-13.md:65`, `148`, `325`). Weeks 0–4 cite Roberge precisely but do not locate the corresponding capstone narrative. Add stable line/anchor locators or quote a short source statement plus the baseline hash. External datasheet evidence in Weeks 0–4 should also have a durable local snapshot or version/hash if it will remain a release authority.
11. **741-class alternatives are not carried through the whole range.** Weeks 0–4 do this well (`spec-weeks-00-04.md:180-185`, `248`, `321`, `403`), and Week 5 mentions the alternative (`spec-weeks-05-09.md:105-109`). Weeks 6–13 do not carry a 741-class note even where LM301A stock channels remain active. A single inherited device-variant contract could avoid repetitive prose while satisfying DEC-016.
12. **A temporary Week 4 fixture is ambiguously inherited in Week 5.** Weeks 0–4 define `MEAS.LOOP_INJ1` as temporary, not permanent chassis circuitry (`spec-weeks-00-04.md:17-28`), while Week 5 says it inherits Week 4 loop-injection/test points subject to reconciliation (`spec-weeks-05-09.md:41-45`). The integrated state must say which physical test points persist and which stimulus fixture is configuration-only.
13. **Week 1 socket identity needs normalization.** The range register reserves `AC.INT3.SOCKET` but not `AC.INT2.SOCKET`, while the Week 1 end state installs both empty socket positions and Week 4 later populates `AC.INT2` (`spec-weeks-00-04.md:17-30`, `120-122`, `342-360`). Give each physical socket a stable identity distinct from the removable amplifier module inserted into it.
14. **Week 10's “add” operation may actually be a replacement.** The current-repeater insertion point and removed/replaced Week 9 load parts are unresolved (`spec-weeks-10-13.md:57-61`, `113-117`). DEC-002 requires the final delta to enumerate those retained, removed, and replaced component IDs, not merely state that a load was added.

### Boundary and tool-selection check

**PASS.** No draft generates an SVG, netlist, simulation, or circuit manifest, selects a renderer/simulator stack, or installs a dependency. Tool/model references are framed as future requirements or open choices. `project-controls.html:67-73` correctly limits work to source reading and specification drafting; its baseline environment inventory is descriptive rather than a toolchain choice. The SHA-256 values recorded at `project-controls.html:135-140` match the current six baseline files.

## DEC-001 through DEC-016 compliance matrix

The ratings below measure whether the *draft specification package* faithfully and sufficiently captures each locked decision; they do not claim that later implementation outputs already exist.

| Decision | Rating | Evidence and gap |
|---|---|---|
| **DEC-001 — complete end-of-week state with active emphasis** | **PASS** | Every week identifies a cumulative state and active configuration; retained inactive modules are grey in the planned view. |
| **DEC-002 — cumulative state plus explicit delta** | **PARTIAL** | Each range uses the rule, but incompatible IDs prevent a single Week 0→13 inheritance proof. Week 10 replacement details and Week 12 integrating-summer hardware are unresolved. |
| **DEC-003 — large sheet, pin-for-pin details as needed** | **PASS** | Main/detail recommendations are present throughout, including large W12 sheets and detailed W13 campaign sheets. |
| **DEC-004 — symbolic but build-ready values table** | **PARTIAL** | Tables exist, but several values are unsupported proposals and material subsystems remain TBD, especially W5, W8, W10, W12, and W13. |
| **DEC-005 — Roberge topology plus identified practical additions** | **PARTIAL** | Additions and deviations are generally called out, often very well. Some exact topologies and the effect of additions remain unresolved, so build readiness is not achieved yet. |
| **DEC-006 — honest incomplete/nonfunctional states** | **PASS** | Week 7 explicitly rejects the false claim that an input pair is a functioning integrator; Week 8 is labeled transitional rather than Figure 9.1. |
| **DEC-007 — historical ±15 V primary, modern notes separate** | **PASS** | ±15 V is consistently primary; same-voltage substitutions and the separate low-voltage project remain distinct. |
| **DEC-008 — SVG plus matched ideal/realistic SPICE outputs** | **PASS** | Every range specifies these as future projections/targets without falsely claiming they exist. |
| **DEC-009 — one canonical graph; reject mismatches** | **PARTIAL** | The identity rule is explicit, but cross-range module/net namespaces are incompatible and several pin graphs are still TBD. |
| **DEC-010 — conventional notation, coral delta, grey inactive** | **PASS** | The presentation contract is explicit across the drafts; black carried-forward active circuitry should be stated once in the integrated style contract because only coral/grey recur in the drafts. |
| **DEC-011 — hidden power pins only via infrastructure** | **PASS** | All ranges bind hidden pins to the Week 0 infrastructure contract. Rail names must still be normalized. |
| **DEC-012 — permanent Week 0 infrastructure sheet** | **PASS** | Week 0 has a substantive infrastructure specification and later sheets reference it. Protection/earth/connector choices remain Gate 0 blockers. |
| **DEC-013 — separate W12 Butterworth and Van der Pol** | **PASS** | `W12-BW` and `W12-VDP` are distinct complete-sheet/graph/netlist targets sharing one cumulative physical state. Their build definitions remain incomplete, but they are not conflated. |
| **DEC-014 — separate W13 compensation campaigns** | **PASS** | `W13-FIXED-AS` and `W13-VARY-AS` are separated, and mutually exclusive networks/configurations require separate graphs/netlists. Naming must be reconciled with controls. |
| **DEC-015 — defer physical cords, not electrical nets/wires** | **PASS** | This boundary is explicit in all three ranges and is particularly clear in W12 and the matched-graph contract. |
| **DEC-016 — LM301A primary; 741-class alternative** | **PARTIAL** | LM301A is consistently the baseline. The 741 comparison contract is strong in W0–4 but largely disappears after W5; it needs an inherited global variant note or relevant weekly notes. |

**Decision totals:** PASS 11, PARTIAL 5, FAIL 0.

## Required weekly-field coverage

Legend: **P** = present and usable; **△** = present but incomplete/inconsistent; **—** = absent as a distinct required field.

| Week(s) | Identity/purpose | Cumulative + delta | Source locator | Components/pins/nets | Values/provenance | Additions/assumptions | Ideal + realistic | Three gates | Main/detail | Historical/modern | Issues |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W0–W4 | △ | P | △ | P | △ | P | P | △ | P | P | P |
| W5–W6 | △ | P | P | △ | △ | P | P | △ | P | △ | P |
| W7 | △ | P | P | P | △ | P | P | △ | P | △ | P |
| W8 | △ | P | P | △ | △ | P | P | △ | P | △ | P |
| W9 | △ | P | P | △ | △ | P | P | P | P | △ | P |
| W10–W11 | △ | △ | △ | △ | △ | P | P | P* | P | △ | P |
| W12 | △ | △ | △ | △ | △ | P | P | P* | P | △ | P |
| W13 | △ | △ | △ | △ | △ | P | P | P* | P | △ | P |

`*` Weeks 10–13 rely on one binding range-level three-gate contract at `spec-weeks-10-13.md:450-459`; that is acceptable if the integrated specification explicitly maps every configuration ID to it.

The recurring identity/purpose gap is the missing explicit **learning objective** required by `project-controls.html:81`. Titles and experiments imply intent, but the schema asked for a discrete field.

## Deferred-ledger audit

| Deferred item | Rating | Evidence and gap |
|---|---|---|
| **D-01 — physical patch-cord drawings** | **PASS** | Carried by all ranges; physical paths/labels are deferred while electrical connections stay explicit. The final range includes a trigger. |
| **D-02 — low-voltage redesign** | **PASS** | Preserved throughout as a separate future project and never allowed to modify the ±15 V baseline. |
| **D-03 — full modern alternatives** | **PASS** | Same-voltage substitutions may be noted; full parallel drawings are triggered by material topology/operation changes. |
| **D-04 — physical construction documentation** | **PARTIAL** | Preserved in all ranges, but the integrated ledger must distinguish deferred mechanical layout from in-scope electrical/thermal requirements. Transistor matching, SOA, heatsinking constraints, grounding requirements, and parasitic budgets cannot be deferred merely because board placement and photographs are. |

The abbreviated W0–4 and W5–9 carry-forwards do not state triggers/prerequisites; the W10–13 ledger does. The integrated specification should include one authoritative D-01…D-04 table with trigger, prerequisite, owner, and no-silent-drop rule.

## Compact remediation list

1. Create one integration-owned identity registry for every chassis module, physical socket, component, port, rail, ground, and configuration; map and retire all `AC/CORE/CMP`, `INF/INFRA`, and rail-name aliases.
2. Normalize configuration IDs in `project-controls.html` and the integrated specification; keep separate graph IDs for every electrically distinct configuration.
3. Add the missing schema fields to every week: explicit learning objective, inherited/retained/removed/replaced sets, full delta, source statement/locator, and three-gate acceptance mapping.
4. Resolve or explicitly submit for user approval every blocker ledger item before calling Gate 0 closed. Do not convert a TBD topology into an implementation task without its expected graph boundary and acceptance criteria.
5. Repair Week 12's physical delta: identify the integrating-summer capacitor/selection hardware, exact fourth integrator module/socket relation, multiplier implementations, and regulator-twin state equation/components.
6. Reclassify unsupported “Derived candidates” as **Proposed**, or supply calculation, inputs, units, dependencies, rating/thermal checks, and source provenance.
7. Add precise capstone locators to W0–4 and W10–13 and preserve any external datasheet authority by version plus local snapshot/hash or another reproducible source record.
8. Add one inherited device-variant contract: LM301A primary with compensation-pin behavior; 741-class separate model/pin/dynamics alternative; modern ±15 V substitutions; D-02 low-voltage exclusion.
9. Make temporary fixtures configuration-owned rather than silently cumulative, especially `MEAS.LOOP_INJ1`; distinguish permanent test points from external injection equipment.
10. Publish one authoritative deferred ledger with D-01…D-04 triggers/prerequisites and a clear line between deferred mechanics and required electrical safety/thermal/parasitic specifications.

## What is done well

- The drafts consistently refuse to invent missing connectivity and expose ambiguities as blockers.
- Week 7's nonfunctional state is handled honestly, exactly as DEC-006 requires.
- The W12 Butterworth and Van der Pol paths and the two W13 compensation campaigns are separated rather than overlaid into electrically impossible drawings.
- Patch-cord deferral is correctly limited to physical routing; electrical nets remain mandatory.
- Week 9 has a credible three-gate proof contract, and Weeks 10–13 provide a strong reusable matched-graph acceptance section.
- The source discussions distinguish Roberge's conceptual figures from build-ready adaptations and identify several errors in earlier simplified interpretations.

