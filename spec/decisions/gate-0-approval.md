# Gate 0 approval record

- **Status:** approved
- **Approval date:** 2026-08-15
- **Authority:** user instruction in the active Codex task
- **Scope:** `G0-01` through `G0-15`, accepted exactly as recommended in `weekly-electrical-specification.html`
- **Authorized next phase:** Phase 2 canonical-model and toolchain selection
- **Not yet authorized by this record:** chronological circuit production, `capstone.html` integration, or release beyond the later gates

## Binding consequences

1. Phase 2 may create the canonical schema, validator, renderer/SPICE prototypes, architecture decision record, and throwaway evaluation circuits.
2. Phase 2 must preserve the cumulative physical-state model, distinct configuration graphs, ±15 V historical baseline, and all deferred-project boundaries.
3. SVG and SPICE must be generated from, or mechanically proven equivalent to, the same canonical component/pin/net graph.
4. Gate 1 remains the architecture exit: the selected stack must expose and compare rendered and simulated connectivity.
5. Week 9 implementation begins only after the Phase 2 architecture is selected and recorded; its release remains subject to Gate 2.

## Approved recommendation set

The full recommendation text remains authoritative in `weekly-electrical-specification.html`. This receipt deliberately references, rather than duplicates, that text so later amendments cannot silently diverge.
