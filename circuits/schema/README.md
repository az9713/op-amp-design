# Canonical circuit-graph schema prototype

`circuit-graph.schema.json` is the renderer-neutral interchange contract for the
project's electrical source of truth. It uses JSON Schema 2020-12 vocabulary so
future tools can consume it, while `tools/validate_circuit_graph.py` enforces
cross-reference and cumulative-state rules that are awkward to express in JSON
Schema alone.

The graph separates:

- physical objects (`components`) and their stable pins;
- electrical identity (`nets`), including an explicit `null` for a deliberately
  unconnected pin;
- hierarchy (`modules` and pin-for-pin ports);
- ideal and realistic simulation bindings (`models` and `model_bindings`);
- electrically distinct configurations (`variants`);
- cumulative Week 0–13 inventory changes (`weekly_states` and `delta`);
- evidence status and source locators (`source_evidence`);
- non-electrical layout metadata (`render`).

Render hints cannot create connectivity. A future SVG renderer and SPICE
projector must consume the same component/pin/net relations, apply the same
variant, and emit a normalized equivalence receipt.

## Validation

```powershell
python tools/validate_circuit_graph.py path\to\graph.json
python tools/validate_circuit_graph.py --check-canonical path\to\graph.json
python -m unittest discover -s tests/schema -v
```

Canonical serialization is UTF-8 JSON with sorted object keys, compact
separators, Unicode preserved, and exactly one trailing newline. Arrays retain
their declared order because pin and hierarchy order may be meaningful to
downstream presentation and model binding.

## Prototype boundary

This package defines and validates the representation. It does not select a
schematic renderer, SPICE engine, or device library, and it contains no Week 9
or other project circuit graph.
