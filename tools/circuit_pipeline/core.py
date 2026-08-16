"""Apply one graph variant and normalize its electrical semantics."""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from tools.validate_circuit_graph import canonical_json, validate_document


CONNECTED_STATES = {
    "persistent-installed",
    "persistent-inactive",
    "configuration-only-fixture",
}


class ProjectionError(ValueError):
    """The canonical graph cannot be projected without losing semantics."""


@dataclass(frozen=True)
class ComponentSemantics:
    id: str
    module_id: str
    kind: str
    state_class: str
    model_id: str
    model_reference: str
    model_kind: str
    pins: tuple[tuple[str, str | None], ...]
    value: str | float | int | None
    parameters: dict[str, Any]
    render: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "module_id": self.module_id,
            "kind": self.kind,
            "state_class": self.state_class,
            "model_id": self.model_id,
            "model_reference": self.model_reference,
            "model_kind": self.model_kind,
            "pins": {pin: net for pin, net in self.pins},
        }


@dataclass(frozen=True)
class ModuleSemantics:
    id: str
    parent_id: str | None
    ports: tuple[tuple[str, str], ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "ports": {port: net for port, net in self.ports},
        }


@dataclass(frozen=True)
class SemanticGraph:
    project_id: str
    variant_id: str | None
    fidelity: str
    components: tuple[ComponentSemantics, ...]
    modules: tuple[ModuleSemantics, ...]
    canonical_json: str

    def normalized(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
            "variant_id": self.variant_id,
            "fidelity": self.fidelity,
            "components": {item.id: item.as_dict() for item in self.components},
            "modules": {item.id: item.as_dict() for item in self.modules},
        }


def _by_id(items: list[dict[str, Any]], kind: str) -> dict[str, dict[str, Any]]:
    indexed = {item["id"]: item for item in items}
    if len(indexed) != len(items):
        raise ProjectionError(f"duplicate {kind} IDs")
    return indexed


def build_semantic_graph(
    document: dict[str, Any],
    *,
    variant_id: str | None,
    fidelity: str,
) -> SemanticGraph:
    """Validate, apply a variant, and bind component pins to model pin order."""
    if fidelity not in {"ideal", "realistic"}:
        raise ProjectionError("fidelity must be 'ideal' or 'realistic'")
    issues = validate_document(document)
    if issues:
        raise ProjectionError("canonical graph is invalid:\n" + "\n".join(map(str, issues)))

    graph = copy.deepcopy(document)
    components = _by_id(graph["components"], "component")
    models = _by_id(graph["models"], "model")
    modules = _by_id(graph["modules"], "module")
    variants = _by_id(graph["variants"], "variant")

    model_overrides: dict[str, str] = {}
    if variant_id is not None:
        variant = variants.get(variant_id)
        if variant is None:
            raise ProjectionError(f"unknown variant {variant_id!r}")
        for override in variant["connection_overrides"]:
            component = components[override["component_id"]]
            pin = next(pin for pin in component["pins"] if pin["id"] == override["pin_id"])
            pin["net"] = override["net"]
        for override in variant["state_overrides"]:
            components[override["component_id"]]["state_class"] = override["state_class"]
        for override in variant["model_overrides"]:
            if override["fidelity"] == fidelity:
                model_overrides[override["component_id"]] = override["model_id"]

    semantic_components: list[ComponentSemantics] = []
    for component_id in sorted(components):
        component = components[component_id]
        if component["state_class"] not in CONNECTED_STATES:
            continue
        model_id = model_overrides.get(component_id, component["model_bindings"].get(fidelity))
        if model_id is None:
            raise ProjectionError(f"{component_id}: no {fidelity} model binding")
        model = models[model_id]
        canonical_pins = {pin["id"]: pin["net"] for pin in component["pins"]}
        pin_map = component.get("model_pin_map") or {pin: pin for pin in canonical_pins}
        reverse_map: dict[str, str] = {}
        for canonical_pin, model_pin in pin_map.items():
            if model_pin in reverse_map:
                raise ProjectionError(f"{component_id}: multiple canonical pins map to model pin {model_pin!r}")
            reverse_map[model_pin] = canonical_pin
        missing = [pin for pin in model["pin_names"] if pin not in reverse_map]
        extra = sorted(set(reverse_map) - set(model["pin_names"]))
        if missing or extra:
            raise ProjectionError(f"{component_id}: incomplete model pin map; missing={missing}, extra={extra}")
        ordered_pins = tuple(
            (model_pin, canonical_pins[reverse_map[model_pin]])
            for model_pin in model["pin_names"]
        )
        semantic_components.append(
            ComponentSemantics(
                id=component_id,
                module_id=component["module_id"],
                kind=component["kind"],
                state_class=component["state_class"],
                model_id=model_id,
                model_reference=model["reference"],
                model_kind=model["kind"],
                pins=ordered_pins,
                value=component.get("value"),
                parameters=component.get("parameters", {}),
                render=component.get("render", {}),
            )
        )

    active_module_ids = {component.module_id for component in semantic_components}
    pending = list(active_module_ids)
    while pending:
        module_id = pending.pop()
        parent = modules[module_id].get("parent_id")
        if parent is not None and parent not in active_module_ids:
            active_module_ids.add(parent)
            pending.append(parent)
    semantic_modules = tuple(
        ModuleSemantics(
            id=module_id,
            parent_id=modules[module_id].get("parent_id"),
            ports=tuple((port["id"], port["net"]) for port in modules[module_id]["ports"]),
        )
        for module_id in sorted(active_module_ids)
    )
    return SemanticGraph(
        project_id=graph["project_id"],
        variant_id=variant_id,
        fidelity=fidelity,
        components=tuple(semantic_components),
        modules=semantic_modules,
        canonical_json=canonical_json(document),
    )


def select_semantic_subgraph(graph: SemanticGraph, module_id: str) -> SemanticGraph:
    """Select one module subtree as a standalone sheet/netlist projection."""
    module_ids = {module.id for module in graph.modules}
    if module_id not in module_ids:
        raise ProjectionError(f"unknown module {module_id!r}")
    included = {item for item in module_ids if item == module_id or item.startswith(module_id + ".")}
    modules = tuple(
        ModuleSemantics(
            id=module.id,
            parent_id=None if module.id == module_id else module.parent_id,
            ports=module.ports,
        )
        for module in graph.modules
        if module.id in included
    )
    return SemanticGraph(
        project_id=graph.project_id,
        variant_id=graph.variant_id,
        fidelity=graph.fidelity,
        components=tuple(component for component in graph.components if component.module_id in included),
        modules=modules,
        canonical_json=graph.canonical_json,
    )
