"""Project a canonical graph and write SVG, SPICE, and equivalence receipt."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import ProjectionError, build_semantic_graph, select_semantic_subgraph
from .equivalence import build_connectivity_receipt
from .spice import emit_spice, parse_spice
from .svg import emit_svg, load_layout_overlay, parse_svg


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="canonical JSON graph")
    parser.add_argument("--variant", required=True, help="configuration variant ID")
    parser.add_argument("--fidelity", choices=("ideal", "realistic"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--layout", type=Path, help="presentation-only JSON layout overlay")
    parser.add_argument("--view", choices=("main", "detail"), default="main")
    parser.add_argument("--detail-module", help="module ID required by --view detail")
    args = parser.parse_args(argv)
    try:
        document = json.loads(args.graph.read_text(encoding="utf-8"))
        semantic = build_semantic_graph(document, variant_id=args.variant, fidelity=args.fidelity)
        if args.view == "detail" and not args.detail_module:
            raise ValueError("--detail-module is required by --view detail")
        layout = load_layout_overlay(args.layout) if args.layout else None
        projection = select_semantic_subgraph(semantic, args.detail_module) if args.view == "detail" else semantic
        svg_text = emit_svg(
            projection,
            view=args.view,
            detail_module_id=args.detail_module,
            layout=layout,
        )
        spice_text = emit_spice(projection)
        receipt = build_connectivity_receipt(
            projection,
            parse_svg(svg_text),
            parse_spice(spice_text),
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ProjectionError, ValueError) as exc:
        print(f"projection failed: {exc}", file=sys.stderr)
        return 2
    stem = f"{args.variant.lower().replace('.', '-')}-{args.fidelity}"
    if args.view == "detail":
        stem += f"-{args.detail_module.lower().replace('.', '-')}-detail"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / f"{stem}.svg").write_text(svg_text, encoding="utf-8", newline="\n")
    (args.output_dir / f"{stem}.cir").write_text(spice_text, encoding="utf-8", newline="\n")
    (args.output_dir / f"{stem}.connectivity.json").write_text(
        receipt.to_json(), encoding="utf-8", newline="\n"
    )
    if not receipt.passed:
        print(receipt.to_json(), file=sys.stderr, end="")
        return 1
    print(f"PASS: wrote {stem}.svg, {stem}.cir, and {stem}.connectivity.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
