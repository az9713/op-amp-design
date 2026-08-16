"""Zero-dependency proof: one graph -> deterministic SVG + SPICE + receipt.

This is architecture evidence, not a production renderer or circuit design.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET


GRAPH = {
    "schema": "probe.circuit-graph.v1",
    "circuit": "W01.INV_TEST.PROBE",
    "ground_net": "SGND",
    "nets": ["VIN", "SUM", "OUT", "P15", "N15", "SGND"],
    "components": [
        {
            "id": "SRC.VIN",
            "kind": "voltage_source",
            "pins": {"p": "VIN", "n": "SGND"},
            "value": "AC 1",
        },
        {
            "id": "MOD.INV1.RIN",
            "kind": "resistor",
            "pins": {"1": "VIN", "2": "SUM"},
            "value": "4.7k",
        },
        {
            "id": "MOD.INV1.RFB",
            "kind": "resistor",
            "pins": {"1": "OUT", "2": "SUM"},
            "value": "4.7k",
        },
        {
            "id": "DEV.U_INV1",
            "kind": "opamp",
            "pins": {"noninv": "SGND", "inv": "SUM", "vp": "P15", "vn": "N15", "out": "OUT"},
            "model": "IDEAL_OPAMP",
        },
        {
            "id": "INF.VP",
            "kind": "dc_source",
            "pins": {"p": "P15", "n": "SGND"},
            "value": "15",
        },
        {
            "id": "INF.VN",
            "kind": "dc_source",
            "pins": {"p": "N15", "n": "SGND"},
            "value": "-15",
        },
    ],
}


LAYOUT = {
    ("SRC.VIN", "p"): (45, 100), ("SRC.VIN", "n"): (45, 145),
    ("MOD.INV1.RIN", "1"): (75, 100), ("MOD.INV1.RIN", "2"): (145, 100),
    ("MOD.INV1.RFB", "1"): (260, 45), ("MOD.INV1.RFB", "2"): (145, 45),
    ("DEV.U_INV1", "inv"): (170, 100), ("DEV.U_INV1", "noninv"): (170, 130),
    ("DEV.U_INV1", "out"): (260, 115), ("DEV.U_INV1", "vp"): (210, 75),
    ("DEV.U_INV1", "vn"): (210, 155),
    ("INF.VP", "p"): (310, 55), ("INF.VP", "n"): (310, 145),
    ("INF.VN", "p"): (350, 145), ("INF.VN", "n"): (350, 175),
}


def normalized_pinmap(graph: dict) -> dict[str, dict[str, str]]:
    return {c["id"]: dict(sorted(c["pins"].items())) for c in graph["components"]}


def validate(graph: dict) -> None:
    nets = set(graph["nets"])
    ids: set[str] = set()
    for component in graph["components"]:
        assert component["id"] not in ids, f"duplicate ID: {component['id']}"
        ids.add(component["id"])
        assert component["pins"], f"pinless component: {component['id']}"
        for pin, net in component["pins"].items():
            assert net in nets, f"unknown net {net} at {component['id']}.{pin}"
            assert (component["id"], pin) in LAYOUT, f"missing layout endpoint {component['id']}.{pin}"
    used = {net for component in graph["components"] for net in component["pins"].values()}
    assert nets == used, f"declared/used nets differ: {nets ^ used}"


def svg_projection(graph: dict) -> str:
    colors = {"wire": "#263238", "part": "#111820", "pin": "#d85a45"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 210" role="img" aria-labelledby="title">',
        '<title id="title">Canonical-graph inverter probe</title>',
        '<style>text{font-family:Arial,sans-serif;font-size:9px}.wire{fill:none;stroke:#263238;stroke-width:2}.part{fill:none;stroke:#111820;stroke-width:2}.pin{fill:#d85a45}</style>',
    ]
    for component in graph["components"]:
        cid = component["id"]
        coords = [LAYOUT[(cid, pin)] for pin in component["pins"]]
        x = sum(p[0] for p in coords) / len(coords)
        y = sum(p[1] for p in coords) / len(coords)
        parts.append(f'<g data-component-id="{html.escape(cid)}" data-kind="{component["kind"]}">')
        if component["kind"] == "opamp":
            parts.append('<path class="part" d="M170 80 L170 150 L260 115 Z"/>')
            parts.append('<text x="182" y="102">−</text><text x="182" y="135">+</text>')
        elif component["kind"] == "resistor":
            (x1, y1), (x2, y2) = coords
            parts.append(f'<path class="part" d="M{x1} {y1} L{x1+10} {y1} l8 -6 l12 12 l12 -12 l12 12 l8 -6 L{x2} {y2}"/>')
        else:
            parts.append(f'<circle class="part" cx="{x:.1f}" cy="{y:.1f}" r="11"/>')
        parts.append(f'<text x="{x-20:.1f}" y="{y-14:.1f}">{html.escape(cid)}</text>')
        for pin, net in sorted(component["pins"].items()):
            px, py = LAYOUT[(cid, pin)]
            parts.append(f'<circle class="pin" cx="{px}" cy="{py}" r="2.4" data-pin="{html.escape(pin)}" data-net="{html.escape(net)}"/>')
        parts.append('</g>')
    endpoints: dict[str, list[tuple[str, str, tuple[int, int]]]] = {net: [] for net in graph["nets"]}
    for component in graph["components"]:
        for pin, net in component["pins"].items():
            endpoints[net].append((component["id"], pin, LAYOUT[(component["id"], pin)]))
    for net in sorted(endpoints):
        pts = endpoints[net]
        root = pts[0]
        for target in pts[1:]:
            x1, y1 = root[2]
            x2, y2 = target[2]
            mid = (x1 + x2) // 2
            ep = f'{root[0]}.{root[1]}|{target[0]}.{target[1]}'
            parts.append(f'<path class="wire" data-net="{net}" data-endpoints="{html.escape(ep)}" d="M{x1} {y1} H{mid} V{y2} H{x2}"/>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def spice_projection(graph: dict) -> str:
    node = lambda n: "0" if n == graph["ground_net"] else n
    lines = ["* generated from probe.circuit-graph.v1", f"* circuit {graph['circuit']}"]
    for c in graph["components"]:
        pins = " ".join(f"{pin}={net}" for pin, net in sorted(c["pins"].items()))
        lines.append(f"* @pinmap {c['id']} {pins}")
        p = c["pins"]
        safe = re.sub(r"[^A-Za-z0-9_]", "_", c["id"])
        if c["kind"] == "resistor":
            lines.append(f"R_{safe} {node(p['1'])} {node(p['2'])} {c['value']}")
        elif c["kind"] in {"voltage_source", "dc_source"}:
            prefix = "" if c["kind"] == "voltage_source" else "DC "
            lines.append(f"V_{safe} {node(p['p'])} {node(p['n'])} {prefix}{c['value']}")
        elif c["kind"] == "opamp":
            order = ["noninv", "inv", "vp", "vn", "out"]
            lines.append(f"X_{safe} {' '.join(node(p[k]) for k in order)} {c['model']}")
    lines.extend([".subckt IDEAL_OPAMP noninv inv vp vn out", "EGAIN out 0 noninv inv 1e6", ".ends IDEAL_OPAMP", ".end", ""])
    return "\n".join(lines)


def svg_pinmap(raw: str) -> dict[str, dict[str, str]]:
    root = ET.fromstring(raw)
    result: dict[str, dict[str, str]] = {}
    for group in root.iter("{http://www.w3.org/2000/svg}g"):
        cid = group.attrib.get("data-component-id")
        if not cid:
            continue
        result[cid] = {}
        for child in group:
            pin = child.attrib.get("data-pin")
            if pin:
                result[cid][pin] = child.attrib["data-net"]
        result[cid] = dict(sorted(result[cid].items()))
    return result


def spice_pinmap(raw: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for line in raw.splitlines():
        if not line.startswith("* @pinmap "):
            continue
        _, _, cid, *pairs = line.split()
        result[cid] = dict(sorted(pair.split("=", 1) for pair in pairs))
    return result


def digest(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path(__file__).with_name("out"))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    validate(GRAPH)
    graph_raw = json.dumps(GRAPH, indent=2, sort_keys=True) + "\n"
    svg_raw = svg_projection(GRAPH)
    spice_raw = spice_projection(GRAPH)
    expected = normalized_pinmap(GRAPH)
    svg_map = svg_pinmap(svg_raw)
    spice_map = spice_pinmap(spice_raw)
    receipt = {
        "graph_equals_svg": expected == svg_map,
        "graph_equals_spice": expected == spice_map,
        "pinmap": expected,
        "sha256": {"graph.json": digest(graph_raw), "inverter.svg": digest(svg_raw), "inverter.cir": digest(spice_raw)},
    }
    assert receipt["graph_equals_svg"] and receipt["graph_equals_spice"]
    outputs = {
        "graph.json": graph_raw,
        "inverter.svg": svg_raw,
        "inverter.cir": spice_raw,
        "receipt.json": json.dumps(receipt, indent=2, sort_keys=True) + "\n",
    }
    for name, raw in outputs.items():
        (args.out / name).write_text(raw, encoding="utf-8", newline="\n")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
