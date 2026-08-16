# Circuit projection and equivalence pipeline

This package projects one validated canonical graph/configuration into two
deterministic connectivity representations:

- semantic SVG, where every rendered terminal and module port carries explicit
  component/pin/net identity;
- hierarchical SPICE, where module boundaries are real `.subckt` declarations,
  module instances carry actual boundary nets, and device connectivity is read
  from element terminals.

The SPICE parser ignores comments. Primitive terminal counts come from SPICE
element classes (`R`, `C`, `Q`, `M`, `S`, and so on); `X` instance terminal
counts and pin names come from parsed `.subckt` declarations. Stable IDs and net
IDs are losslessly encoded into legal instance/node tokens.

The connectivity emitter uses model-interface `.subckt` declarations so the
parser can verify actual terminal order without depending on comments. The
separate runnable simulation emitter binds those same interfaces to sourced
model bodies or model cards while preserving identical pins and nets.

## Publication SVG projection

The semantic SVG renderer uses conventional analog symbols for resistors,
capacitors, diodes, NPN/PNP BJTs, N-channel JFETs, voltage/current sources,
op-amps, switches, and generic subcircuits. Ground and positive/negative power
ports receive conventional glyphs. `render.x`, `render.y`, `render.rotation`,
`render.mirror`, and `render.style` control presentation only; every terminal
and orthogonal wire still carries canonical component, pin, and net identity.

Multi-terminal nets receive explicit junction dots. Intersections between
different nets receive insulated crossing marks with `data-connected="false"`.
Module boundaries and ports appear on the main sheet; `emit_svg_detail()` emits
a selected module and its descendants using the same stable electrical IDs.
`load_layout_overlay()` accepts a deterministic JSON presentation overlay with
viewport, component positions, module boxes/collapse directives, visual zones,
and net rail preferences. An overlay cannot add or remove electrical objects.
Collapsed main-sheet internals remain in a hidden semantic ledger so reparsing
and SVG/SPICE equivalence still cover every canonical component and terminal.

## Command

```powershell
python -m tools.circuit_pipeline graph.json `
  --variant CFG.NAME `
  --fidelity ideal `
  --output-dir generated\proof
```

Add `--layout layout.json --view main` for a composed main sheet, or
`--layout detail.json --view detail --detail-module AMP1` for a module sheet.

The command reparses both outputs before writing them. It emits a deterministic
SVG, `.cir` netlist, and `.connectivity.json` receipt, and exits nonzero if
either parsed representation differs from the canonical connectivity.

## Runnable ngspice projection

`simulation.py` adds a deliberately narrower, runnable projection. A
`SimulationPlan` supplies approved `.include` files or inline `.model`/real
`.subckt` bodies, named probes, `.op`, `.ac`, and `.tran` analyses, and one or
more parameter cases. Empty interface stubs are prohibited in runnable decks.

`NgspiceRunner` accepts an explicit executable path (the pinned mode) or locates
`ngspice` on `PATH`. Before running it repeats SVG/SPICE connectivity
equivalence. Each receipt records the canonical connectivity hash, executable
hash, normalized version and version hash, include hashes, per-case deck and
normalized-command hashes, parameters, and parsed result tables. Operating
point tables expose checked scalar lookup through `TableResult.scalar()`.

Supported current probes are voltage/current-source branch vectors. Voltage
probes target canonical nets. Other device-current expressions, noise,
distortion, pole-zero, and Monte Carlo analyses remain outside this iteration
and must be added as explicit typed operations rather than raw command strings.
