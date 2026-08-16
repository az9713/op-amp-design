# ADR-001: Canonical circuit graph and deterministic projection toolchain

- **Date:** 2026-08-15
- **Status:** Accepted for Phase 2 prototyping; production approval remains conditional on the Week 9 vertical proof
- **Decision owners:** project integration
- **Scope:** circuit representation, SVG/SPICE generation, equivalence evidence, simulation boundary, and renderer fallback

## Context

The release invariant is stronger than “the drawing looks connected”: every weekly SVG schematic and its ideal/realistic SPICE netlists must be projections of the same component/pin/net graph. Physical hardware accumulates by week; configurations change electrical connections without renaming physical objects; inactive installed hardware remains in the physical manifest.

The existing approaches do not enforce that invariant:

- `_gen_schematics.py` emits hand-authored SVG strings from coordinates and writes to a hard-coded WSL path. Connectivity is implicit in line placement.
- `_gen_engine.py`, `_gen_schemdraw_box.py`, and `_gen_book_and_schemdraw.py` drive Schemdraw as turtle graphics. They attach many shapes to library anchors, but there is no project-level component/pin/net graph from which a SPICE deck can be projected. `_gen_engine.py` also preserves superseded conceptual circuits—for example, its Week 2 two-inverting-block loop is labeled as `xdot = -x` even though the integrated specification identifies the sign error.
- `check_schematic_connections.py` checks geometric symptoms such as op-amp pin hits, transistor-body hits, and unmarked T-junctions. It does not know component identity or named electrical nets. On the current `schematics.html`, it reports four diagrams as `STOP` for unmarked T-junctions but exits successfully because the attempt log converts repeated failures into waivers. It is useful as a visual lint, not as connectivity proof.
- `schematic-methods.html` recommends lcapy/CircuiTikZ and then KiCad because both are net-aware. That diagnosis is correct, but neither tool is presently available, and neither should become a second independently maintained source of connectivity.

### Runtime evidence

Observed on native Windows during this decision:

| Capability | Result |
|---|---|
| Native Python | 3.13.5 |
| Bundled Python | 3.12.13 |
| Pydantic / NetworkX / svgwrite / pytest on native Python | 2.11.5 / 3.6.1 / 1.4.3 / 8.4.2 |
| Node | 22.22.0 |
| Schemdraw | unavailable |
| lcapy | unavailable |
| SKiDL | unavailable |
| ngspice | unavailable |
| KiCad CLI | unavailable |
| TeX/CircuiTikZ toolchain | unavailable |

No dependency was installed for this evaluation.

## Decision

Use a **declarative canonical JSON graph with native Python validation and two deterministic, one-way projectors**:

1. **Canonical model** — schema-versioned JSON documents for physical objects, component instances, typed pins, named nets, hierarchy, parameters, model bindings, weekly state, configuration state, source provenance, and presentation state. JSON is the authored electrical source. The project-owned Python validator enforces cross-reference and cumulative-state invariants; an immutable Pydantic facade may be added later for authoring ergonomics but may not become a second source of truth.
2. **SVG projector** — a project-owned analog schematic renderer that receives only the canonical graph plus a separate layout overlay. It emits semantic SVG with `data-component-id`, `data-pin`, `data-net`, and routed-endpoint metadata.
3. **SPICE projector** — a project-owned emitter that flattens the same graph into ideal or realistic SPICE variants. Model/subcircuit substitution is controlled by an explicit allow-list; it may not change external component pins or circuit nets.
4. **Equivalence verifier** — independently parse the emitted SVG semantic metadata and the actual SPICE statements/subcircuit pin order, normalize both pin maps, and compare each with the canonical graph. A mismatch fails the build.
5. **ngspice simulation boundary** — select ngspice as the primary batch simulator once dependency installation is separately authorized. Until it is present, only schema, connectivity, analytical, and deterministic-generation checks may pass; electrical simulation gates remain explicitly unavailable.

The SVG layout overlay may contain placement, orientation, net-label placement, routing corridors, and orthogonal waypoints. It may refer only to canonical component pins and named nets. It cannot declare a component, pin, connection, value, or model. A manual waypoint is therefore layout authorship, not electrical authorship.

### Canonical layering

```text
canonical graph.json
        |
        v
validated canonical graph --> normalized snapshot + source/value tables
        |                                   |
        +--> layout overlay --> semantic SVG+--> connectivity receipt
        |
        +--> model binding --> SPICE deck --+--> ngspice results
```

Generated SVG, SPICE, JSON snapshots, tables, and receipts are outputs. Direct edits to them are prohibited.

## Required canonical schema

The production schema must include at least:

- stable physical object and occupant IDs from the Gate 0 integration register;
- component kind, reference, physical state, source citation, and implementation-addition flag;
- named, typed pins with package pin mapping kept separate from logical pin names;
- named nets with `SGND` mapped to SPICE node `0`, while `PGND` remains distinct until `INF.GND_STAR`;
- module ports and hierarchy boundary mappings;
- installed, inactive, removed-off-circuit, reserved-unpopulated, and configuration-only-fixture state classes;
- parameter expressions, recommended values, units, tolerances, ratings, and evidence status;
- mutually exclusive configuration selections and explicit open/disconnected states;
- ideal and realistic model bindings with provenance/licensing fields;
- layout references that cannot create electrical objects;
- deterministic ordering rules and schema version.

Validation must reject duplicate IDs, unknown pins/nets, orphan nets, undeclared opens, multiple drivers where disallowed, incompatible selector states, missing hidden power endpoints, collapsed `SGND`/`PGND`, and configuration references to absent hardware.

## Projection and equivalence policy

### SVG

- Symbol terminals are named anchors owned by the component definition.
- Every wire is created from a named net and canonical endpoint list, never from two anonymous coordinates.
- Junction dots are derived from graph degree and route topology.
- Crossings without a junction remain distinct route layers/segments.
- Hierarchical main/detail sheets share the same boundary pin map.
- Coral/grey/black are presentation attributes from state deltas; color never changes connectivity.
- Text and symbol metrics must be pinned for reproducible render review. A project-bundled font or an approved deterministic font policy is required before publication.

### SPICE

- Each component kind owns a declared logical-pin-to-SPICE-terminal order.
- `SGND` alone maps to node `0`; a real net-tie implementation preserves `PGND` as a separate named node before the tie.
- Ideal and realistic decks share the external graph. Differences inside model subcircuits and analysis fixtures require declared, reviewed exceptions.
- Measurement sources, loop injection, probes, and simulator-only initial conditions are configuration fixtures and must be present in the corresponding configuration manifest.
- Production equivalence parses actual emitted element terminals. Generator-authored comments alone are not sufficient evidence.

### Reproducibility

- Pin Python and every non-standard dependency in a lock file after installation is authorized.
- Use stable sorting, explicit numeric/unit formatting, UTF-8, LF newlines, and no timestamps or absolute workspace paths in generated artifacts.
- Record schema version, generator version, input hashes, dependency versions, output hashes, and model hashes.
- Run generation twice in clean directories and require byte-identical canonical JSON, SVG, SPICE, and receipts.
- Treat simulator numeric output separately: record ngspice version/platform and compare declared tolerances rather than requiring cross-platform byte identity.

## Probe evidence

`spec/decisions/probes/adr-001/probe.py` is a zero-dependency architecture probe, not a production circuit or renderer. It defines one inverter graph and projects it to canonical JSON, semantic SVG, and SPICE. It then reconstructs component/pin/net maps from both projections and compares them with the graph.

Two independent output directories produced byte-identical files:

| Artifact | SHA-256 |
|---|---|
| `graph.json` | `491bd5b2f6cc14e1de95aea7072f7685bf03db544e2a2973fa8b257b95bda705` |
| `inverter.svg` | `604b7424dbf9d6f62cbb8d3840806b8559f81374947fbef050d2bacd71265995` |
| `inverter.cir` | `4bee7d5d94c6e1a58221db709754928c3c771c63da1b4c54176f89a34603ffb8` |

Both `graph_equals_svg` and `graph_equals_spice` are true in the generated receipts. This proves the architectural seam and deterministic emission for a small graph. It does **not** prove publication layout, SPICE validity in ngspice, or Week 9 scalability.

Run the probe with:

```powershell
python .\spec\decisions\probes\adr-001\probe.py --out .\spec\decisions\probes\adr-001\out
```

## Alternatives considered

| Approach | Connectivity authority | Analog layout control | SVG/SPICE identity | Native reproducibility now | Decision |
|---|---|---|---|---|---|
| Canonical JSON graph + native validator + owned SVG/SPICE projectors | One project graph | High through constrained layouts | Direct and mechanically checkable | Yes | **Selected** |
| lcapy -> CircuiTikZ | lcapy netlist | High for textbook analog circuits | Requires a separate SPICE projector or normalization layer | No; lcapy and TeX absent | Renderer fallback candidate |
| KiCad schematic/ERC/export | KiCad schematic | High, manual | SPICE and canonical-state synchronization need import/export proof | No; CLI absent | Difficult-sheet fallback |
| Schemdraw generators | Drawing command sequence | Medium | No project graph; SPICE would be separate | No; package absent | Rejected as authority |
| Hand SVG | Coordinates | High | No electrical model | Yes, but electrically unverifiable | Rejected |
| SKiDL/KiCad generation | Python net graph | Medium; PCB-oriented autorouting | Possible but adds KiCad representation boundary | No; tools absent | Rejected for primary teaching renderer |
| netlistsvg/ELK/tscircuit | Net graph | Low for publication analog topology | Possible | Node present, packages not established | Rejected for primary analog renderer |

## Fallback policy

The canonical graph remains the authority under every fallback.

1. **First renderer fallback: lcapy/CircuiTikZ adapter.** If the owned renderer cannot achieve a publication-quality sheet without excessive layout code, export the selected graph/configuration to lcapy syntax, render it, and attach semantic IDs during post-processing. Re-import/extract its node mapping and compare with the canonical graph. This fallback requires separately approved, pinned lcapy and TeX installations.
2. **Difficult transistor-sheet fallback: KiCad.** For a Week 9 detail that remains unreadable, generate or transcribe a KiCad schematic from the canonical manifest, export SVG, extract KiCad connectivity, and compare it back to the canonical graph. Hand-edited KiCad layout is allowed only if connectivity round-trips cleanly; SPICE is still emitted from the canonical graph.
3. **No fallback to hand SVG or coordinate-first Schemdraw.** Existing pages remain visual references and regression inputs, not generation authorities.

## Consequences

### Benefits

- The SVG and SPICE deck cannot drift through independent authorship.
- Weekly physical inheritance and separate active configurations become data, not drawing conventions.
- The renderer can be replaced without changing electrical identity.
- Exact component/pin/net receipts are machine-comparable.
- Windows regeneration works before heavyweight EDA/TeX dependencies are available.

### Costs

- The project must build and maintain an analog symbol library, constrained orthogonal router, layout overlay schema, SPICE emitter, and independent parsers.
- Publication layout remains partly curated; deterministic does not mean automatic.
- Any optional authoring/test dependency and later ngspice must be pinned and documented; the validation core remains standard-library executable.
- Model provenance and licensing remain separate release work.

### Known limitations and required proof

- The current probe is one simple inverter and uses SPICE pin-map comments as its extraction aid. Production verification must parse actual SPICE element terminals and subcircuit declarations.
- No installed simulator has parsed or run the probe deck.
- The custom SVG path has not rendered the Figure 9.1 transistor-level amplifier, switches, selectors, or multi-sheet hierarchy.
- Layout collision, net-label reuse, page breaking, print typography, and responsive embedding remain unproven.
- ngspice compatibility of historical LM301A and transistor models is unproven.
- The decision must be revisited if the Week 9 proof cannot meet all three gates without unsafe renderer-specific exceptions.

## Gate 1 / Week 9 acceptance criteria

Before this ADR advances from provisional to production-approved, the Week 9 proof must demonstrate:

1. exact Figure 9.1 component, logical-pin, package-pin, and named-net representation;
2. cumulative main sheet plus pin-for-pin detail from one graph;
3. separate inverter, slew, compensation-sweep, and restored-integrator configurations;
4. ideal and realistic SPICE projections with actual parser-based pin/net equivalence;
5. successful ngspice syntax, operating-point, AC, and transient runs or an explicitly recorded simulator blocker;
6. no ambiguous crossing, missing junction, overlap, clipping, or hidden signal connection;
7. byte-identical clean regeneration on the pinned Windows environment;
8. a renderer-effort assessment against the lcapy and KiCad fallbacks before batch production.

## Files produced by this evaluation

- `spec/decisions/adr-001-canonical-toolchain.md`
- `spec/decisions/probes/adr-001/probe.py`
- `spec/decisions/probes/adr-001/out-a/*`
- `spec/decisions/probes/adr-001/out-b/*` (second clean generation used for byte comparison)
