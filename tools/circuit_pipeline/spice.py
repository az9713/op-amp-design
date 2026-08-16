"""Hierarchical semantic SPICE projection and connectivity parser.

Connectivity is recovered from element terminals, `.subckt` formal pins, and
subcircuit instance terminals. Comments are ignored and carry no authority.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .core import ComponentSemantics, SemanticGraph
from .encoding import decode_id, decode_net, encode_id, encode_net


PRIMITIVE_DESIGNATORS = {
    "resistor": ("R", 2),
    "capacitor": ("C", 2),
    "inductor": ("L", 2),
    "diode": ("D", 2),
    "bjt": ("Q", 3),
    "npn_bjt": ("Q", 3),
    "pnp_bjt": ("Q", 3),
    "jfet": ("J", 3),
    "n_jfet": ("J", 3),
    "mosfet": ("M", 4),
    "switch": ("S", 4),
    "voltage_source": ("V", 2),
    "current_source": ("I", 2),
}
DESIGNATOR_PINS = {
    "R": ("P", "N"),
    "C": ("P", "N"),
    "L": ("P", "N"),
    "D": ("A", "K"),
    "Q": ("C", "B", "E"),
    "J": ("D", "G", "S"),
    "M": ("D", "G", "S", "B"),
    "S": ("P", "N", "CTRL_P", "CTRL_N"),
    "V": ("P", "N"),
    "I": ("P", "N"),
}
TOKEN = re.compile(r"^[A-Za-z0-9_+.-]+$")


def _safe_reference(reference: str) -> str:
    if not TOKEN.fullmatch(reference):
        raise ValueError(f"SPICE model reference contains unsupported characters: {reference!r}")
    return reference


def _element_designator(component: ComponentSemantics) -> tuple[str, int | None]:
    if component.model_kind == "subcircuit":
        return "X", None
    try:
        return PRIMITIVE_DESIGNATORS[component.kind]
    except KeyError as exc:
        raise ValueError(f"{component.id}: unsupported primitive kind {component.kind!r}") from exc


def _instance_token(designator: str, component_id: str) -> str:
    return designator + encode_id("I", component_id)


def _module_name(module_id: str) -> str:
    return encode_id("M", module_id)


def _port_name(port_id: str) -> str:
    return encode_id("P", port_id)


def _node_for(module: Any, net_id: str | None, component_id: str, pin_id: str) -> str:
    if net_id is not None:
        for port_id, port_net in module.ports:
            if port_net == net_id:
                return _port_name(port_id)
    return encode_net(net_id, component_id, pin_id)


def _emit_component(component: ComponentSemantics, module: Any) -> str:
    designator, count = _element_designator(component)
    if count is not None and len(component.pins) != count:
        raise ValueError(f"{component.id}: {component.kind} requires {count} terminals, got {len(component.pins)}")
    nodes = [_node_for(module, net, component.id, pin) for pin, net in component.pins]
    tail: list[str]
    if designator in {"R", "C", "L", "V", "I"}:
        if component.value is None:
            raise ValueError(f"{component.id}: {component.kind} requires a value")
        rendered_value = str(component.value)
        tail = [rendered_value if designator in {"V", "I"} else rendered_value.replace(" ", "")]
        if designator == "C" and component.parameters.get("simulation_initial_condition") is not None:
            initial = _safe_reference(str(component.parameters["simulation_initial_condition"]))
            tail.append(f"IC={initial}")
    else:
        tail = [_safe_reference(component.model_reference)]
    return " ".join([_instance_token(designator, component.id), *nodes, *tail])


def emit_spice(graph: SemanticGraph, *, include_model_interfaces: bool = True) -> str:
    modules = {module.id: module for module in graph.modules}
    components_by_module: dict[str, list[ComponentSemantics]] = {module_id: [] for module_id in modules}
    for component in graph.components:
        components_by_module[component.module_id].append(component)

    lines = [f".title {graph.project_id} semantic connectivity"]
    model_interfaces: dict[str, tuple[str, ...]] = {}
    for component in graph.components:
        if component.model_kind == "subcircuit":
            pins = tuple(pin for pin, _ in component.pins)
            previous = model_interfaces.get(component.model_reference)
            if previous is not None and previous != pins:
                raise ValueError(f"model {component.model_reference!r} is used with inconsistent pin order")
            model_interfaces[component.model_reference] = pins
    if include_model_interfaces:
        for reference in sorted(model_interfaces):
            safe = _safe_reference(reference)
            lines.append(".subckt " + " ".join([safe, *model_interfaces[reference]]))
            lines.append(f".ends {safe}")

    for module_id in sorted(modules, key=lambda item: (item.count("."), item), reverse=True):
        module = modules[module_id]
        formal_ports = [_port_name(port_id) for port_id, _ in module.ports]
        lines.append(".subckt " + " ".join([_module_name(module_id), *formal_ports]))
        for component in sorted(components_by_module[module_id], key=lambda item: item.id):
            lines.append(_emit_component(component, module))
        for child in sorted((item for item in modules.values() if item.parent_id == module_id), key=lambda item: item.id):
            child_nodes = [_node_for(module, net_id, child.id, port_id) for port_id, net_id in child.ports]
            lines.append(" ".join([_instance_token("X", child.id), *child_nodes, _module_name(child.id)]))
        lines.append(f".ends {_module_name(module_id)}")

    for module in sorted((item for item in modules.values() if item.parent_id is None), key=lambda item: item.id):
        nodes = [encode_net(net_id, module.id, port_id) for port_id, net_id in module.ports]
        lines.append(" ".join([_instance_token("X", module.id), *nodes, _module_name(module.id)]))
    lines.append(".end")
    return "\n".join(lines) + "\n"


@dataclass
class SpiceElement:
    token: str
    designator: str
    nodes: list[str]
    reference: str


@dataclass
class Subcircuit:
    name: str
    formal_pins: list[str]
    elements: list[SpiceElement] = field(default_factory=list)


def _logical_lines(text: str) -> list[str]:
    result: list[str] = []
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("*"):
            continue
        if stripped.startswith("+"):
            if not result:
                raise ValueError("SPICE continuation without preceding line")
            result[-1] += " " + stripped[1:].strip()
        else:
            result.append(stripped)
    return result


def _parse_element(tokens: list[str], model_interfaces: dict[str, list[str]]) -> SpiceElement:
    instance = tokens[0]
    designator = instance[0].upper()
    if designator == "X":
        if len(tokens) < 3:
            raise ValueError(f"invalid subcircuit instance: {' '.join(tokens)}")
        reference = tokens[-1]
        nodes = tokens[1:-1]
        expected = model_interfaces.get(reference)
        if expected is not None and len(nodes) != len(expected):
            raise ValueError(f"{instance}: subcircuit {reference!r} expects {len(expected)} pins, got {len(nodes)}")
        return SpiceElement(instance, designator, nodes, reference)
    pins = DESIGNATOR_PINS.get(designator)
    if pins is None:
        raise ValueError(f"unsupported SPICE element designator {designator!r}")
    if len(tokens) < 1 + len(pins) + 1:
        raise ValueError(f"{instance}: too few terminals")
    return SpiceElement(instance, designator, tokens[1 : 1 + len(pins)], tokens[1 + len(pins)])


def parse_spice(text: str) -> dict[str, Any]:
    lines = _logical_lines(text)
    definitions: dict[str, Subcircuit] = {}
    top_elements: list[list[str]] = []
    current: Subcircuit | None = None
    raw_elements: dict[str, list[list[str]]] = {}
    for line in lines:
        tokens = line.split()
        directive = tokens[0].lower()
        if directive == ".subckt":
            if current is not None or len(tokens) < 2:
                raise ValueError("nested or malformed .subckt")
            current = Subcircuit(tokens[1], tokens[2:])
            if current.name in definitions:
                raise ValueError(f"duplicate .subckt {current.name!r}")
            definitions[current.name] = current
            raw_elements[current.name] = []
        elif directive == ".ends":
            if current is None:
                raise ValueError(".ends without .subckt")
            if len(tokens) > 1 and tokens[1] != current.name:
                raise ValueError(f".ends name {tokens[1]!r} does not match {current.name!r}")
            current = None
        elif directive.startswith("."):
            continue
        elif current is None:
            top_elements.append(tokens)
        else:
            raw_elements[current.name].append(tokens)
    if current is not None:
        raise ValueError(f"unterminated .subckt {current.name!r}")

    interfaces = {name: definition.formal_pins for name, definition in definitions.items()}
    for name, groups in raw_elements.items():
        definitions[name].elements = [_parse_element(tokens, interfaces) for tokens in groups]
    parsed_top = [_parse_element(tokens, interfaces) for tokens in top_elements]

    module_defs = {name: definition for name, definition in definitions.items() if name.startswith("MZ")}
    model_defs = {name: definition for name, definition in definitions.items() if not name.startswith("MZ")}
    module_instances: dict[str, SpiceElement] = {}
    for element in parsed_top:
        if element.designator == "X" and element.reference in module_defs:
            module_instances[decode_id("I", element.token[1:])] = element
    for definition in module_defs.values():
        for element in definition.elements:
            if element.designator == "X" and element.reference in module_defs:
                module_instances[decode_id("I", element.token[1:])] = element

    module_net_maps: dict[str, dict[str, str | None]] = {}
    unresolved = set(module_instances)
    while unresolved:
        progressed = False
        for module_id in sorted(unresolved):
            instance = module_instances[module_id]
            definition = module_defs[instance.reference]
            parent_definition = next(
                (candidate for candidate in module_defs.values() if instance in candidate.elements),
                None,
            )
            if parent_definition is None:
                actual_nets = [decode_net(node) for node in instance.nodes]
                parent_id = None
            else:
                parent_id = decode_id("M", parent_definition.name)
                if parent_id not in module_net_maps:
                    continue
                parent_ports = {
                    formal: module_net_maps[parent_id][decode_id("P", formal)]
                    for formal in parent_definition.formal_pins
                }
                actual_nets = [parent_ports[node] if node in parent_ports else decode_net(node) for node in instance.nodes]
            port_ids = [decode_id("P", token) for token in definition.formal_pins]
            module_net_maps[module_id] = dict(zip(port_ids, actual_nets))
            unresolved.remove(module_id)
            progressed = True
            break
        if not progressed:
            raise ValueError(f"cannot resolve module instance hierarchy: {sorted(unresolved)}")

    result: dict[str, Any] = {
        "project_id": "",
        "variant_id": None,
        "fidelity": "",
        "components": {},
        "modules": {},
    }
    for module_id, instance in sorted(module_instances.items()):
        definition = module_defs[instance.reference]
        parent_definition = next((item for item in module_defs.values() if instance in item.elements), None)
        parent_id = decode_id("M", parent_definition.name) if parent_definition else None
        result["modules"][module_id] = {
            "id": module_id,
            "parent_id": parent_id,
            "ports": module_net_maps[module_id],
        }
        formal_to_net = {
            formal: module_net_maps[module_id][decode_id("P", formal)]
            for formal in definition.formal_pins
        }
        for element in definition.elements:
            if element.designator == "X" and element.reference in module_defs:
                continue
            component_id = decode_id("I", element.token[1:])
            if element.designator == "X":
                pin_names = model_defs[element.reference].formal_pins
                model_kind = "subcircuit"
            else:
                pin_names = list(DESIGNATOR_PINS[element.designator])
                model_kind = "primitive"
            nets = [formal_to_net[node] if node in formal_to_net else decode_net(node) for node in element.nodes]
            result["components"][component_id] = {
                "id": component_id,
                "module_id": module_id,
                "kind": _kind_from_designator(element.designator),
                "state_class": "",
                "model_id": "",
                "model_reference": element.reference,
                "model_kind": model_kind,
                "pins": dict(zip(pin_names, nets)),
            }
    return result


def _kind_from_designator(designator: str) -> str:
    reverse = {value[0]: key for key, value in PRIMITIVE_DESIGNATORS.items()}
    return "subcircuit" if designator == "X" else reverse[designator]
