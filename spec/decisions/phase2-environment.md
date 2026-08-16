# Phase 2 environment receipt

Captured 2026-08-15 in `C:\Users\simon\Downloads\op_amps_roberge`.

## Confirmed native runtime

- Python 3.13.5 at `C:\Users\simon\AppData\Local\Programs\Python\Python313\python.exe`
- Available Python packages relevant to evaluation: `networkx`, `jsonschema`, `numpy`, `scipy`, `matplotlib`
- Not importable in the active Python: `schemdraw`, `lcapy`
- Not found on the active command path: `ngspice`, `kicad-cli`, Graphviz `dot`
- No dependency was installed during this inventory.

## Existing evidence

- Existing Schemdraw/hand-SVG generators and HTML outputs remain non-authoritative presentation experiments.
- `schematic-methods.html` correctly identifies representation/connectivity as the primary problem, but its preferred lcapy/CircuiTikZ route is not presently reproducible in the native environment.
- The legacy SVG geometry checker is presentation-specific; it does not establish component/pin/net equivalence with SPICE.

## Baseline test result

`python -m unittest discover -s tests -v` passes all four existing legacy SVG checks. This proves the old checker still runs; it does not approve the old circuit content or select the Phase 2 architecture.

## Architecture implication

The first candidate must work without relying on an unavailable EDA stack: a declarative canonical graph, standard-library validation/projection core, deterministic SVG output, and deterministic SPICE output. Optional external renderers/simulators may be adapters or later validation layers, not the only source of truth.

## Phase 3 update

After Gate 1 approval, the user explicitly authorized ngspice installation. Ngspice 47 was installed through Scoop's `extras` manifest on 2026-08-15; 7-Zip 26.02 was installed as Scoop's extraction dependency. Exact source, manifest, binary hashes, and paths are recorded in `dependency-lock.json`.
