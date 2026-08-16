"""Publication-oriented semantic SVG projection and parser.

Geometry and styling are deterministic presentation data. Electrical identity
remains the component/model-pin/net relation carried by terminal and wire SVG
elements, so rotating or restyling a symbol cannot change connectivity.
"""
from __future__ import annotations

import math
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from .core import ComponentSemantics, SemanticGraph
from .encoding import encode_id


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def _tag(name: str) -> str:
    return f"{{{SVG_NS}}}{name}"


@dataclass(frozen=True)
class PlacedComponent:
    component: ComponentSemantics
    x: float
    y: float
    rotation: int
    mirror: bool
    render: dict[str, Any]
    pins: tuple[tuple[str, str | None, float, float, float, float], ...]


def _element(parent: ET.Element, name: str, attrs: dict[str, Any]) -> ET.Element:
    return ET.SubElement(parent, _tag(name), {key: str(value) for key, value in attrs.items()})


def _line(parent: ET.Element, x1: float, y1: float, x2: float, y2: float, cls: str = "symbol-line") -> None:
    _element(parent, "line", {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "class": cls})


def _text(parent: ET.Element, x: float, y: float, value: str, cls: str) -> None:
    item = _element(parent, "text", {"x": x, "y": y, "class": cls})
    item.text = value


def _pin_layout(component: ComponentSemantics) -> dict[str, tuple[float, float]]:
    pin_ids = [pin for pin, _ in component.pins]
    kind = component.kind.lower()
    if kind in {"resistor", "capacitor", "inductor", "diode"}:
        positions = [(-45, 0), (45, 0)]
    elif kind in {"bjt", "npn_bjt", "pnp_bjt"}:
        known = {"C": (30, -35), "B": (-45, 0), "E": (30, 35)}
        return {pin: known.get(pin, (0, 0)) for pin in pin_ids}
    elif kind in {"jfet", "n_jfet"}:
        known = {"D": (28, -36), "G": (-45, 0), "S": (28, 36)}
        return {pin: known.get(pin, (0, 0)) for pin in pin_ids}
    elif kind in {"voltage_source", "current_source"}:
        positions = [(0, -45), (0, 45)]
    elif kind == "switch":
        known = {"P": (-45, 0), "N": (45, 0), "CTRL_P": (0, 38), "CTRL_N": (18, 38)}
        return {pin: known.get(pin, (0, 0)) for pin in pin_ids}
    elif kind == "opamp" or component.model_kind == "subcircuit" and len(pin_ids) == 5:
        known = {
            "INP": (-50, 18),
            "INM": (-50, -18),
            "OUT": (55, 0),
            "VP": (0, -52),
            "VN": (0, 52),
            # Externally compensated amplifiers such as LM301A need distinct
            # semantic terminals; placing both at the symbol origin makes a
            # visually ambiguous short even when the graph is correct.
            "COMPA": (24, -52),
            "COMPB": (24, 52),
        }
        return {pin: known.get(pin, (0, 0)) for pin in pin_ids}
    else:
        left_count = (len(pin_ids) + 1) // 2
        positions = []
        for index in range(left_count):
            positions.append((-50, (index - (left_count - 1) / 2) * 18))
        for index in range(len(pin_ids) - left_count):
            count = len(pin_ids) - left_count
            positions.append((50, (index - (count - 1) / 2) * 18))
    return {pin: positions[index] for index, pin in enumerate(pin_ids)}


def _transform_point(x: float, y: float, rotation: int, mirror: bool) -> tuple[float, float]:
    if mirror:
        x = -x
    radians = math.radians(rotation)
    return (
        round(x * math.cos(radians) - y * math.sin(radians), 6),
        round(x * math.sin(radians) + y * math.cos(radians), 6),
    )


def load_layout_overlay(path: str | Path) -> dict[str, Any]:
    """Load a presentation-only JSON overlay without mutating graph semantics."""
    overlay = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(overlay, dict):
        raise ValueError("layout overlay root must be an object")
    viewport = overlay.get("viewport", {})
    if not isinstance(viewport, dict) or not all(isinstance(viewport.get(key), (int, float)) for key in ("width", "height")):
        raise ValueError("layout overlay requires numeric viewport.width and viewport.height")
    for field in ("components", "module_positions", "net_routes"):
        if field in overlay and not isinstance(overlay[field], dict):
            raise ValueError(f"layout overlay {field} must be an object")
    return overlay


def _place_components(
    components: Iterable[ComponentSemantics],
    layout_components: dict[str, Any] | None = None,
) -> tuple[PlacedComponent, ...]:
    layout_components = layout_components or {}
    placed: list[PlacedComponent] = []
    for index, component in enumerate(sorted(components, key=lambda item: item.id)):
        render = {**component.render, **layout_components.get(component.id, {})}
        x = float(render.get("x", 180 + 220 * (index % 3)))
        y = float(render.get("y", 150 + 150 * (index // 3)))
        rotation = int(render.get("rotation", 0))
        mirror = bool(render.get("mirror", False))
        local_positions = _pin_layout(component)
        pins = []
        for pin_id, net_id in component.pins:
            local_x, local_y = local_positions[pin_id]
            delta_x, delta_y = _transform_point(local_x, local_y, rotation, mirror)
            pins.append((pin_id, net_id, local_x, local_y, x + delta_x, y + delta_y))
        placed.append(PlacedComponent(component, x, y, rotation, mirror, render, tuple(pins)))
    return tuple(placed)


def _draw_resistor(group: ET.Element) -> None:
    points = [(-45, 0), (-30, 0), (-24, -10), (-12, 10), (0, -10), (12, 10), (24, -10), (30, 0), (45, 0)]
    _element(group, "polyline", {"points": " ".join(f"{x},{y}" for x, y in points), "class": "symbol-line resistor-body"})


def _draw_capacitor(group: ET.Element) -> None:
    _line(group, -45, 0, -7, 0)
    _line(group, -7, -22, -7, 22, "symbol-line capacitor-plate")
    _line(group, 7, -22, 7, 22, "symbol-line capacitor-plate")
    _line(group, 7, 0, 45, 0)


def _draw_diode(group: ET.Element) -> None:
    _line(group, -45, 0, -16, 0)
    _element(group, "polygon", {"points": "-16,-18 -16,18 13,0", "class": "symbol-fill diode-body"})
    _line(group, 15, -21, 15, 21, "symbol-line diode-bar")
    _line(group, 15, 0, 45, 0)


def _draw_bjt(group: ET.Element, pnp: bool) -> None:
    _line(group, -45, 0, -12, 0)
    _line(group, -12, -25, -12, 25)
    _line(group, -12, -12, 30, -35)
    _line(group, -12, 12, 30, 35)
    points = "-5,12 8,14 1,24" if pnp else "27,33 14,31 21,21"
    _element(group, "polygon", {"points": points, "class": "symbol-fill transistor-arrow", "data-polarity": "pnp" if pnp else "npn"})


def _draw_jfet(group: ET.Element) -> None:
    _line(group, 12, -25, 12, 25)
    _line(group, 12, -25, 28, -36)
    _line(group, 12, 25, 28, 36)
    _line(group, -45, 0, 4, 0)
    _element(group, "polygon", {"points": "2,-5 12,0 2,5", "class": "symbol-fill jfet-arrow"})


def _draw_source(group: ET.Element, current: bool) -> None:
    _line(group, 0, -45, 0, -28)
    _line(group, 0, 28, 0, 45)
    _element(group, "circle", {"cx": 0, "cy": 0, "r": 28, "class": "symbol-line symbol-paper source-body"})
    if current:
        _line(group, 0, 15, 0, -13)
        _element(group, "polygon", {"points": "0,-18 -6,-7 6,-7", "class": "symbol-fill source-arrow"})
    else:
        _line(group, -7, -10, 7, -10, "symbol-line voltage-polarity")
        _line(group, 0, -17, 0, -3, "symbol-line voltage-polarity")
        _line(group, -7, 12, 7, 12, "symbol-line voltage-polarity")


def _draw_opamp(group: ET.Element) -> None:
    _element(group, "polygon", {"points": "-34,-34 -34,34 40,0", "class": "symbol-line symbol-paper opamp-body"})
    _line(group, -50, -18, -34, -18)
    _line(group, -50, 18, -34, 18)
    _line(group, 40, 0, 55, 0)
    _line(group, 0, -42, 0, -19)
    _line(group, 0, 19, 0, 42)
    _text(group, -29, -13, "−", "polarity")
    _text(group, -29, 23, "+", "polarity")


def _draw_switch(group: ET.Element) -> None:
    _line(group, -45, 0, -18, 0)
    _line(group, 18, 0, 45, 0)
    _element(group, "circle", {"cx": -18, "cy": 0, "r": 3, "class": "symbol-fill switch-contact"})
    _element(group, "circle", {"cx": 18, "cy": 0, "r": 3, "class": "symbol-fill switch-contact"})
    _line(group, -16, -2, 13, -18)
    _line(group, 0, 38, 0, 22, "control-line")


def _draw_generic_subcircuit(group: ET.Element) -> None:
    _element(group, "rect", {"x": -38, "y": -30, "width": 76, "height": 60, "rx": 3, "class": "symbol-line symbol-paper subcircuit-body"})


def _draw_symbol(group: ET.Element, component: ComponentSemantics) -> None:
    kind = component.kind.lower()
    if kind == "resistor":
        _draw_resistor(group)
    elif kind == "capacitor":
        _draw_capacitor(group)
    elif kind == "diode":
        _draw_diode(group)
    elif kind in {"bjt", "npn_bjt", "pnp_bjt"}:
        polarity = str(component.parameters.get("polarity", "pnp" if kind == "pnp_bjt" else "npn")).lower()
        _draw_bjt(group, pnp=polarity == "pnp")
    elif kind in {"jfet", "n_jfet"}:
        _draw_jfet(group)
    elif kind == "voltage_source":
        _draw_source(group, current=False)
    elif kind == "current_source":
        _draw_source(group, current=True)
    elif kind == "switch":
        _draw_switch(group)
    elif kind == "opamp" or component.model_kind == "subcircuit" and len(component.pins) == 5:
        _draw_opamp(group)
    else:
        _draw_generic_subcircuit(group)


def _segment_intersection(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> tuple[float, float] | None:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    a_horizontal = ay1 == ay2
    b_horizontal = by1 == by2
    if a_horizontal == b_horizontal:
        return None
    horizontal, vertical = (a, b) if a_horizontal else (b, a)
    hx1, hy, hx2, _ = horizontal
    vx, vy1, _, vy2 = vertical
    if min(hx1, hx2) < vx < max(hx1, hx2) and min(vy1, vy2) < hy < max(vy1, vy2):
        return vx, hy
    return None


def _point_on_segment_interior(x: float, y: float, segment: tuple[float, float, float, float], clearance: float = 5.0) -> bool:
    x1, y1, x2, y2 = segment
    if y1 == y2 and abs(y - y1) <= clearance:
        return min(x1, x2) + clearance < x < max(x1, x2) - clearance
    if x1 == x2 and abs(x - x1) <= clearance:
        return min(y1, y2) + clearance < y < max(y1, y2) - clearance
    return False


def _segment_enters_rectangle(
    segment: tuple[float, float, float, float],
    rectangle: tuple[float, float, float, float],
    clearance: float = 8.0,
) -> bool:
    x1, y1, x2, y2 = segment
    left, top, right, bottom = rectangle
    if y1 == y2 and top - clearance < y1 < bottom + clearance:
        return max(min(x1, x2), left - clearance) < min(max(x1, x2), right + clearance)
    if x1 == x2 and left - clearance < x1 < right + clearance:
        return max(min(y1, y2), top - clearance) < min(max(y1, y2), bottom + clearance)
    return False


def _draw_ground(parent: ET.Element, x: float, y: float) -> None:
    _line(parent, x, y, x, y + 9, "port-line ground-symbol")
    _line(parent, x - 10, y + 9, x + 10, y + 9, "port-line ground-symbol")
    _line(parent, x - 7, y + 13, x + 7, y + 13, "port-line ground-symbol")
    _line(parent, x - 3, y + 17, x + 3, y + 17, "port-line ground-symbol")


def _draw_power(parent: ET.Element, x: float, y: float, up: bool) -> None:
    direction = -1 if up else 1
    _line(parent, x, y, x, y + direction * 14, "port-line")
    _element(parent, "polygon", {"points": f"{x},{y + direction * 20} {x - 6},{y + direction * 11} {x + 6},{y + direction * 11}", "class": "symbol-fill power-arrow", "data-rail-polarity": "positive" if up else "negative"})


def emit_svg(
    graph: SemanticGraph,
    *,
    view: str = "main",
    detail_module_id: str | None = None,
    layout: dict[str, Any] | None = None,
) -> str:
    if view not in {"main", "detail"}:
        raise ValueError("view must be 'main' or 'detail'")
    modules = {module.id: module for module in graph.modules}
    if view == "detail":
        if detail_module_id not in modules:
            raise ValueError(f"unknown detail module {detail_module_id!r}")
        included_modules = {module_id for module_id in modules if module_id == detail_module_id or module_id.startswith(detail_module_id + ".")}
    else:
        included_modules = set(modules)
    layout = layout or {}
    collapsed_modules = set(layout.get("collapsed_modules", []))
    if view == "main":
        collapsed_modules.update(
            module_id
            for module_id, hint in layout.get("module_positions", {}).items()
            if isinstance(hint, dict) and hint.get("detail_ref")
        )
    unknown_collapsed = collapsed_modules - included_modules
    if unknown_collapsed:
        raise ValueError(f"layout collapses unknown modules: {sorted(unknown_collapsed)}")
    collapsed_descendants: set[str] = set()
    for module_id in included_modules:
        parent_id = modules[module_id].parent_id
        while parent_id in modules:
            if parent_id in collapsed_modules:
                collapsed_descendants.add(module_id)
                break
            parent_id = modules[parent_id].parent_id
    components = tuple(component for component in graph.components if component.module_id in included_modules)
    hidden_module_ids = collapsed_modules | collapsed_descendants
    visible_components = tuple(component for component in components if component.module_id not in hidden_module_ids)
    hidden_components = tuple(component for component in components if component.module_id in hidden_module_ids)
    if layout.get("strict_components"):
        missing_layout = sorted({component.id for component in visible_components} - set(layout.get("components", {})))
        if missing_layout:
            raise ValueError(f"strict layout omits visible components: {missing_layout}")
    placed = _place_components(visible_components, layout.get("components"))
    viewport = layout.get("viewport", {})
    width = int(viewport.get("width", 1000))
    height = int(viewport.get("height", max(320, int(max((item.y for item in placed), default=180) + 140))))
    root = ET.Element(_tag("svg"), {"viewBox": f"0 0 {width} {height}", "role": "img", "data-project-id": graph.project_id, "data-variant-id": graph.variant_id or "", "data-fidelity": graph.fidelity, "data-view": view, "data-detail-module-id": detail_module_id or "", "data-layout-id": layout.get("sheet_id", "")})
    title = ET.SubElement(root, _tag("title"))
    title.text = f"{view.title()} circuit projection: {graph.project_id}"
    style = ET.SubElement(root, _tag("style"))
    style.text = (
        ".symbol-line,.port-line,.wire,.port-wire,.net-trunk,.control-line{fill:none;stroke:#171717;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;vector-effect:non-scaling-stroke}"
        ".symbol-fill{fill:#171717;stroke:#171717;stroke-width:1}.symbol-paper{fill:#fff}.component.inactive{opacity:.34}"
        ".component.changed .symbol-line,.component.changed .symbol-fill{stroke:#d85c41}.component.changed .symbol-fill{fill:#d85c41}.designator.inactive,.value.inactive{opacity:.34}"
        ".module-boundary{fill:none;stroke:#8b9299;stroke-width:1;stroke-dasharray:6 4}.junction{fill:#171717}.crossing{fill:#fff;stroke:#171717;stroke-width:1}"
        ".designator{font:600 11px system-ui;fill:#171717}.value{font:10px system-ui;fill:#555}.pin-label,.port-label{font:9px ui-monospace;fill:#555}"
        ".module-label{font:600 12px system-ui;fill:#555}.collapsed-title{font:700 22px system-ui;fill:#171717}.collapsed-subtitle,.net-label{font:11px system-ui;fill:#555}.polarity{font:16px system-ui;fill:#171717}.collapsed-module.inactive{opacity:.38}"
        ".zone{fill:#f8fafb;stroke:#c5cbd1;stroke-width:1}.zone-label{font:600 11px system-ui;fill:#737b83}.semantic-ledger{display:none}"
    )
    zone_layer = _element(root, "g", {"class": "zone-layer"})
    boundary_layer = _element(root, "g", {"class": "boundary-layer"})
    wire_layer = _element(root, "g", {"class": "wire-layer"})
    symbol_layer = _element(root, "g", {"class": "symbol-layer"})
    annotation_layer = _element(root, "g", {"class": "annotation-layer"})

    for zone in layout.get("zones", []):
        if not isinstance(zone, dict):
            continue
        _element(zone_layer, "rect", {"x": zone["x"], "y": zone["y"], "width": zone["width"], "height": zone["height"], "rx": 8, "class": "zone", "data-zone-id": zone.get("id", "")})
        _text(zone_layer, float(zone["x"]) + 10, float(zone["y"]) + 18, str(zone.get("id", "")).replace("_", " "), "zone-label")

    placed_by_module: dict[str, list[PlacedComponent]] = {module_id: [] for module_id in included_modules}
    for item in placed:
        placed_by_module[item.component.module_id].append(item)
    visible_connected_nets = {
        net_id
        for item in placed
        for _, net_id, _, _, _, _ in item.pins
        if net_id is not None
    }
    port_endpoints: dict[str, list[tuple[str, float, float]]] = {}
    port_markers: dict[str, list[tuple[float, float]]] = {}
    collapsed_obstacles: list[tuple[tuple[float, float, float, float], set[str]]] = []
    module_hints = layout.get("module_positions", {})
    for module_index, module_id in enumerate(sorted(included_modules)):
        items = placed_by_module[module_id]
        hint = module_hints.get(module_id, {})
        if hint:
            left = float(hint["x"])
            top = float(hint["y"])
            right = left + float(hint["width"])
            bottom = top + float(hint["height"])
        elif items:
            left = min(item.x for item in items) - 85
            right = max(item.x for item in items) + 85
            top = min(item.y for item in items) - 85
            bottom = max(item.y for item in items) + 75
        elif module_id in collapsed_modules:
            left, right, top, bottom = 40, 280, 50 + 90 * module_index, 120 + 90 * module_index
        else:
            left, right, top, bottom = 0, 1, 0, 1
        module = modules[module_id]
        visible_module = module_id not in collapsed_descendants and bool(hint or items or module_id in collapsed_modules)
        group = _element(boundary_layer, "g", {"id": encode_id("module-", module_id), "class": "module" + ("" if visible_module else " semantic-ledger"), "data-module-id": module_id, "data-parent-id": module.parent_id or ""})
        if visible_module:
            _element(group, "rect", {"x": left, "y": top, "width": right - left, "height": bottom - top, "rx": 8, "class": "module-boundary"})
            _text(group, left + 10, top + 18, str(hint.get("title", module_id)), "module-label")
        if module_id in collapsed_modules:
            collapsed_obstacles.append(((left, top, right, bottom), {net_id for _, net_id in module.ports}))
            block_title = str(hint.get("title", module_id))
            block_subtitle = str(hint.get("subtitle", "collapsed module; see detail sheet"))
            _text(group, (left + right) / 2 - 35, (top + bottom) / 2, block_title, "collapsed-title")
            _text(group, (left + right) / 2 - 75, (top + bottom) / 2 + 24, block_subtitle, "collapsed-subtitle")
            group.set("class", group.attrib["class"] + " collapsed-module")
            if hint.get("style"):
                group.set("class", group.attrib["class"] + " " + str(hint["style"]))
            group.set("data-detail-ref", str(hint.get("detail_ref", "")))
        for port_index, (port_id, net_id) in enumerate(module.ports):
            short_id = port_id.rsplit(".", 1)[-1]
            port_hint = hint.get("ports", {}).get(port_id, hint.get("ports", {}).get(short_id, {}))
            show_port = bool(port_hint.get("visible", net_id in visible_connected_nets if module_id in collapsed_modules else True))
            if "x" in port_hint and "y" in port_hint:
                port_x, port_y = float(port_hint["x"]), float(port_hint["y"])
            elif module_id in collapsed_modules and short_id in {"OUT"}:
                port_x, port_y = right, top + 70
            elif module_id in collapsed_modules and short_id in {"VP15"}:
                port_x, port_y = left + (right - left) * .4, top
            elif module_id in collapsed_modules and short_id in {"VN15", "AGND"}:
                port_x, port_y = left + (right - left) * (.6 if short_id == "VN15" else .5), bottom
            elif module_id in collapsed_modules and short_id in {"COMP_A", "COMP_B"}:
                port_x, port_y = right, top + (130 if short_id == "COMP_A" else 190)
            else:
                port_x = left
                port_y = top + 45 + 34 * port_index
            _element(group, "circle", {"class": "module-port" + ("" if show_port else " semantic-ledger"), "cx": port_x if show_port else 0, "cy": port_y if show_port else 0, "r": 3 if show_port else 0, "data-port-id": port_id, "data-net-id": net_id})
            if show_port:
                port_markers.setdefault(net_id, []).append((port_x, port_y))
            if visible_module and show_port:
                label_dx = float(port_hint.get("label_dx", 6 if port_x == left else -45))
                label_dy = float(port_hint.get("label_dy", -6))
                _text(group, port_x + label_dx, port_y + label_dy, short_id, "port-label")
            if show_port and (module_id in collapsed_modules or view == "detail") and hint.get("connect_ports", True):
                port_endpoints.setdefault(net_id, []).append((f"{module_id}::{port_id}", port_x, port_y))
            if visible_module and show_port and net_id == "SGND":
                _draw_ground(group, port_x, port_y + 2)
            elif visible_module and show_port and net_id in {"P15", "VCC"}:
                _draw_power(group, port_x, port_y + 2, up=True)
            elif visible_module and show_port and net_id in {"N15", "VEE"}:
                _draw_power(group, port_x, port_y + 2, up=False)

    net_terminals: dict[str, list[tuple[str, str, float, float]]] = {}
    for item in placed:
        for pin_id, net_id, _, _, global_x, global_y in item.pins:
            if net_id is not None:
                net_terminals.setdefault(net_id, []).append((item.component.id, pin_id, global_x, global_y))
    visual_nets = set(net_terminals) | set(port_endpoints)
    all_anchors: dict[str, list[tuple[float, float]]] = {
        net_id: [(item[2], item[3]) for item in terminals] + port_markers.get(net_id, [])
        for net_id, terminals in net_terminals.items()
    }
    for net_id, markers in port_markers.items():
        all_anchors.setdefault(net_id, []).extend(point for point in markers if point not in all_anchors.get(net_id, []))
    routed_segments: list[tuple[str, tuple[float, float, float, float]]] = []
    net_routes = layout.get("net_routes", {})
    for net_index, net_id in enumerate(sorted(visual_nets)):
        net_group = _element(wire_layer, "g", {"class": "net", "data-net-id": net_id})
        terminals = [(f"{component_id}::{pin_id}", pin_x, pin_y, True) for component_id, pin_id, pin_x, pin_y in sorted(net_terminals.get(net_id, []))]
        terminals += [(port_ref, x, y, False) for port_ref, x, y in sorted(port_endpoints.get(net_id, []))]
        if not terminals:
            continue
        xs, ys = [item[1] for item in terminals], [item[2] for item in terminals]
        route_hint = net_routes.get(net_id, {})
        rail = route_hint.get("rail") if isinstance(route_hint, dict) else None
        if rail:
            trunk_horizontal = True
            trunk_coordinate = float(route_hint.get("coordinate", {"top": 38.0, "middle": height / 2, "bottom": height - 38.0}[rail]))
        elif route_hint.get("orientation") in {"horizontal", "vertical"}:
            trunk_horizontal = route_hint["orientation"] == "horizontal"
            ordered = sorted(ys if trunk_horizontal else xs)
            trunk_coordinate = float(route_hint.get("coordinate", ordered[len(ordered) // 2]))
        else:
            trunk_horizontal = max(xs) - min(xs) >= max(ys) - min(ys)
            ordered = sorted(ys if trunk_horizontal else xs)
            trunk_coordinate = ordered[len(ordered) // 2]
            # A distinct-net terminal dot must never sit on a through wire. Move
            # the presentation-only trunk locally; electrical membership is
            # still carried exclusively by data-terminal-ref/data-net-id.
            span_min, span_max = (min(xs), max(xs)) if trunk_horizontal else (min(ys), max(ys))
            obstacle_channels = []
            for (left, top, right, bottom), port_nets in collapsed_obstacles:
                if net_id not in port_nets:
                    obstacle_channels.extend((top - 18, bottom + 18) if trunk_horizontal else (left - 18, right + 18))
            candidates = [trunk_coordinate + offset for offset in (0, 18, -18, 36, -36, 54, -54)]
            candidates.extend(sorted(set(obstacle_channels), key=lambda item: (abs(item - trunk_coordinate), item)))
            for candidate in candidates:
                candidate_segment = (span_min, candidate, span_max, candidate) if trunk_horizontal else (candidate, span_min, candidate, span_max)
                collision = any(
                    _point_on_segment_interior(anchor_x, anchor_y, candidate_segment)
                    for other_net, anchors in all_anchors.items()
                    if other_net != net_id
                    for anchor_x, anchor_y in anchors
                )
                collision = collision or any(
                    net_id not in port_nets and _segment_enters_rectangle(candidate_segment, rectangle)
                    for rectangle, port_nets in collapsed_obstacles
                )
                if not collision:
                    trunk_coordinate = candidate
                    break
        if trunk_horizontal:
            trunk = (min(xs), trunk_coordinate, max(xs), trunk_coordinate)
        else:
            trunk = (trunk_coordinate, min(ys), trunk_coordinate, max(ys))
        if len(terminals) > 1 and (trunk[0], trunk[1]) != (trunk[2], trunk[3]):
            _element(net_group, "line", {"class": "net-trunk", "x1": trunk[0], "y1": trunk[1], "x2": trunk[2], "y2": trunk[3], "data-net-id": net_id})
            routed_segments.append((net_id, trunk))
        for terminal_ref, pin_x, pin_y, electrical in terminals:
            end_x, end_y = (pin_x, trunk_coordinate) if trunk_horizontal else (trunk_coordinate, pin_y)
            points: tuple[tuple[float, float], ...] = ((pin_x, pin_y), (end_x, end_y))
            direct = (pin_x, pin_y, end_x, end_y)
            foreign = [point for other_net, anchors in all_anchors.items() if other_net != net_id for point in anchors]
            if any(_point_on_segment_interior(x, y, direct) for x, y in foreign):
                for offset in (14, -14, 28, -28, 42, -42):
                    if pin_x == end_x:
                        candidate = ((pin_x, pin_y), (pin_x + offset, pin_y), (pin_x + offset, end_y), (end_x, end_y))
                    else:
                        candidate = ((pin_x, pin_y), (pin_x, pin_y + offset), (end_x, pin_y + offset), (end_x, end_y))
                    segments = [(a[0], a[1], b[0], b[1]) for a, b in zip(candidate, candidate[1:])]
                    if not any(_point_on_segment_interior(x, y, segment) for segment in segments for x, y in foreign):
                        points = candidate
                        break
            if electrical:
                attrs = {"class": "wire", "points": " ".join(f"{x},{y}" for x, y in points), "data-terminal-ref": terminal_ref, "data-net-id": net_id, "fill": "none"}
            else:
                attrs = {"class": "port-wire", "points": " ".join(f"{x},{y}" for x, y in points), "data-port-ref": terminal_ref, "data-net-id": net_id, "fill": "none"}
            _element(net_group, "polyline", attrs)
            routed_segments.extend((net_id, (a[0], a[1], b[0], b[1])) for a, b in zip(points, points[1:]))
            if len(terminals) >= 3:
                _element(net_group, "circle", {"cx": end_x, "cy": end_y, "r": 3.5, "class": "junction", "data-net-id": net_id})
        if route_hint and (rail or route_hint.get("priority") == "critical"):
            label_x = float(route_hint.get("label_x", trunk[0] + 4))
            label_y = float(route_hint.get("label_y", trunk[1] - 6))
            _text(net_group, label_x, label_y, str(route_hint.get("label", net_id)), "net-label")

    ledger = _element(root, "g", {"class": "semantic-ledger"})
    for component in hidden_components:
        group = _element(ledger, "g", {"class": "component collapsed-member", "data-component-id": component.id, "data-module-id": component.module_id, "data-state-class": component.state_class, "data-kind": component.kind, "data-model-id": component.model_id, "data-model-reference": component.model_reference})
        for pin_id, net_id in component.pins:
            _element(group, "circle", {"class": "terminal", "cx": 0, "cy": 0, "r": 0, "data-pin-id": pin_id, "data-net-id": net_id or "", "data-open": "true" if net_id is None else "false"})
            if net_id is not None:
                _element(ledger, "polyline", {"class": "wire", "points": "0,0 1,0", "data-terminal-ref": f"{component.id}::{pin_id}", "data-net-id": net_id})

    crossings: set[tuple[float, float]] = set()
    for index, (net_a, segment_a) in enumerate(routed_segments):
        for net_b, segment_b in routed_segments[index + 1 :]:
            if net_a != net_b:
                crossing = _segment_intersection(segment_a, segment_b)
                if crossing is not None:
                    crossings.add(crossing)
    for crossing_x, crossing_y in sorted(crossings):
        _element(annotation_layer, "circle", {"cx": crossing_x, "cy": crossing_y, "r": 4, "class": "crossing", "data-connected": "false"})

    for item in placed:
        component = item.component
        style_name = item.render.get("style")
        if not style_name or style_name == "active" and component.state_class == "persistent-inactive":
            style_name = "inactive" if component.state_class == "persistent-inactive" else "active"
        transform = f"translate({item.x} {item.y}) rotate({item.rotation})"
        if item.mirror:
            transform += " scale(-1 1)"
        group = _element(symbol_layer, "g", {"id": encode_id("component-", component.id), "class": f"component {style_name}", "transform": transform, "data-component-id": component.id, "data-module-id": component.module_id, "data-state-class": component.state_class, "data-kind": component.kind, "data-model-id": component.model_id, "data-model-reference": component.model_reference, "data-rotation": item.rotation, "data-mirror": str(item.mirror).lower()})
        component_title = ET.SubElement(group, _tag("title"))
        component_title.text = component.id
        _draw_symbol(group, component)
        for pin_id, net_id, local_x, local_y, global_x, global_y in item.pins:
            _element(group, "circle", {"class": "terminal", "cx": local_x, "cy": local_y, "r": 3, "data-pin-id": pin_id, "data-net-id": net_id or "", "data-open": "true" if net_id is None else "false", "data-global-x": global_x, "data-global-y": global_y})
            if component.kind.lower() in {"bjt", "npn_bjt", "pnp_bjt", "jfet", "n_jfet", "opamp"}:
                _text(annotation_layer, global_x + 4, global_y - 5, pin_id, "pin-label")
        visible_id = str(item.render.get("label", component.id.rsplit(".", 1)[-1] if layout else component.id))
        if item.render.get("show_designator", True):
            _text(annotation_layer, item.x + float(item.render.get("label_dx", -32)), item.y + float(item.render.get("label_dy", -48)), visible_id, "designator " + style_name)
        if component.value is not None and item.render.get("show_value", True):
            _text(annotation_layer, item.x + float(item.render.get("value_dx", -25)), item.y + float(item.render.get("value_dy", 58)), str(component.value), "value " + style_name)

    ET.indent(root, space="  ")
    return ET.tostring(root, encoding="unicode", xml_declaration=False) + "\n"


def emit_svg_detail(graph: SemanticGraph, module_id: str, *, layout: dict[str, Any] | None = None) -> str:
    return emit_svg(graph, view="detail", detail_module_id=module_id, layout=layout)


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_svg(text: str) -> dict[str, Any]:
    root = ET.fromstring(text)
    if _local(root.tag) != "svg":
        raise ValueError("document root is not SVG")
    result: dict[str, Any] = {"project_id": root.attrib.get("data-project-id", ""), "variant_id": root.attrib.get("data-variant-id") or None, "fidelity": root.attrib.get("data-fidelity", ""), "components": {}, "modules": {}}
    wire_membership: dict[str, str] = {}
    for element in root.iter():
        if "wire" not in set(element.attrib.get("class", "").split()):
            continue
        terminal_ref = element.attrib.get("data-terminal-ref")
        net_id = element.attrib.get("data-net-id")
        points = element.attrib.get("points", "").split()
        if not terminal_ref or not net_id or len(points) < 2:
            raise ValueError("semantic SVG wire lacks terminal, net, or geometry")
        if terminal_ref in wire_membership:
            raise ValueError(f"terminal {terminal_ref!r} has multiple semantic wires")
        wire_membership[terminal_ref] = net_id
    for element in root.iter():
        classes = set(element.attrib.get("class", "").split())
        if "module" in classes:
            module_id = element.attrib["data-module-id"]
            ports: dict[str, str] = {}
            for child in element:
                if "module-port" in set(child.attrib.get("class", "").split()):
                    ports[child.attrib["data-port-id"]] = child.attrib["data-net-id"]
            result["modules"][module_id] = {"id": module_id, "parent_id": element.attrib.get("data-parent-id") or None, "ports": ports}
        if "component" in classes:
            component_id = element.attrib["data-component-id"]
            pins: dict[str, str | None] = {}
            for child in element:
                if "terminal" in set(child.attrib.get("class", "").split()):
                    pin_id = child.attrib["data-pin-id"]
                    pins[pin_id] = None if child.attrib.get("data-open") == "true" else child.attrib["data-net-id"]
            result["components"][component_id] = {"id": component_id, "module_id": element.attrib["data-module-id"], "kind": element.attrib["data-kind"], "state_class": element.attrib["data-state-class"], "model_id": element.attrib["data-model-id"], "model_reference": element.attrib["data-model-reference"], "model_kind": "", "pins": pins}
    for component_id, component in result["components"].items():
        for pin_id, net_id in component["pins"].items():
            terminal_ref = f"{component_id}::{pin_id}"
            if net_id is None:
                if terminal_ref in wire_membership:
                    raise ValueError(f"open terminal {terminal_ref!r} has a semantic wire")
            elif wire_membership.get(terminal_ref) != net_id:
                raise ValueError(f"terminal {terminal_ref!r} declares net {net_id!r} but wire membership is {wire_membership.get(terminal_ref)!r}")
    return result
