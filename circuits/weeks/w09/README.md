# Week 9 canonical circuit content

`graph.json` is the sole electrical source of truth for the Week 9 Figure 9.1
amplifier, its three configurations, and the cumulative chassis objects needed
on the main sheet. Generated SVG and SPICE files must come from the shared
pipeline; none are maintained here by hand.

`case-manifest.json` is the proposed machine-readable substitution contract for
the six source-defined compensation cases. It cannot change connectivity by
itself and is not yet consumed by the pipeline. Every referenced component ID
exists in `graph.json`; a future case loader must validate and apply its value
and state overrides before deck generation.

## Explicit representation decisions

- Historical part identity lives in component `parameters`; the only active
  device bindings currently admitted are topology-only ideal bindings. Missing
  realistic bindings are intentionally absent.
- The physical 50 kohm balance potentiometer is represented electrically by
  `AMP1.R_BAL_L` and `AMP1.R_BAL_R`, both carrying
  `physical_identity=AMP1.R_BAL`. Their 25 kohm midpoint is proposed solely as
  a deterministic topology default, not a source-selected trim setting.
- `AMP1.CC`, `W09.RIN`, `W09.RFB`, `W09.RALPHA`, `W09.RSOURCE`, and `W09.VSRC` retain symbolic
  values. Source-defined sweep cases are stored on `AMP1.CC.parameters.cases`.
  The current schema and projector cannot substitute a case-specific value or
  remove `W09.RALPHA` for an open-circuit case. Therefore emitted decks prove
  connectivity only until case-parameter support is added.
- `MOD.INT1.RIN` and `MOD.INT1.CFB` retain symbolic values because the cited
  Week 9 sources do not specify them. The restored configuration is a complete
  electrical graph but not yet a numerically runnable deck.
- Retained modules are module-level placeholders for the Week 9 main sheet.
  Their permanent electrical details remain on separate sheets as decided in
  pre-flight; the empty topology-tier subcircuit is not a functional model.
- The Week 7 and Week 8 deltas map the capstone's stated stage-level additions
  onto the final Figure 9.1 object identities. Those subsets are explicit
  project interpretations (`proposed`), because Chapters 7 and 8 describe
  precursor topologies rather than a pin-for-pin Figure 9.1 assembly ledger.
- `INF.PWR_ENTRY.VP15` and `INF.PWR_ENTRY.VN15` are ideal simulation boundary
  sources, not a replacement for the separate physical supply sheet.

## Source omissions preserved as TBD

- 5.6 kohm precision-dot/tolerance status;
- all four diode part numbers and realistic models;
- 1.0 uF technology/polarity and other capacitor construction details;
- historical package pin numbers;
- numeric `R1`, generator impedance, output load, probe loading, parasitics,
  and the retained end-state `Cc`.

The output load, output probe capacitance, and three critical-node parasitics are explicit deferred
components (`W09.LOAD`, `W09.CPAR_HIGHZ`, `W09.CPAR_COMPA`, and
`W09.CPAR_COMPB`, plus `W09.CPROBE_OUT`), rather than invisible simulator assumptions.

The graph defers physical patch-cord routing only. Its logical nets remain
explicit in every configuration.
