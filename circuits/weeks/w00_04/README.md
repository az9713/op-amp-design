# Weeks 0–4 canonical circuit package

`graph.json` is the sole electrical authority for this batch. It contains W00–W04 cumulative states, twelve mutually explicit experiment configurations, ideal topology-tier model bindings, component evidence, and build-state classifications.

Generated SVG, SPICE, and connectivity receipts are under `generated/weeks00_04/`. Every receipt compares terminal/net identity parsed independently from the SVG and SPICE output with the selected canonical graph variant.

The SPICE decks in the review batch are matched structural netlists. The op-amp binding is deliberately labeled topology-tier; it is not a validated LM301A performance macromodel. No realistic-performance claim is made.

Presentation overlays live under `layout/weeks/w00_04/`. They may move symbols or collapse a device core, but cannot add or alter nets.
