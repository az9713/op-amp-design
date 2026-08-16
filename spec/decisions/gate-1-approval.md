# Gate 1 approval record

- **Status:** approved
- **Approval date:** 2026-08-15
- **Authority:** user instruction in the active Codex task
- **Approved architecture:** `spec/decisions/adr-001-canonical-toolchain.md`
- **Authorized next phase:** Week 9 vertical proof
- **Dependency authority:** install and pin ngspice for this workspace
- **Still gated:** chronological weekly production and `capstone.html` integration until Gate 2

## Binding Phase 3 requirements

1. Complete independent Figure 9.1 Transcription B and adjudicate it against Transcription A before accepting the Week 9 graph.
2. Encode the Week 9 cumulative physical state and each electrically distinct configuration in the canonical schema.
3. Generate the main sheet, transistor-level detail, ideal and realistic SPICE decks, values/source tables, and verification receipts from that graph.
4. Parse actual SVG semantics and SPICE element terminals/subcircuit pin order for equivalence; generator comments are not sufficient evidence.
5. Run ngspice DC, AC, and transient checks where models permit; label unsupported historical-model behavior honestly.
6. Stop at Gate 2 for user review before chronological batch production or capstone integration.
