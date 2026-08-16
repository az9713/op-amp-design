"""Normalized connectivity comparison and deterministic receipt generation."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from .core import SemanticGraph


IGNORED_COMPONENT_FIELDS = {
    "kind",
    "state_class",
    "model_id",
    "model_reference",
    "model_kind",
}
IGNORED_ROOT_FIELDS = {"project_id", "variant_id", "fidelity"}


def _connectivity_view(graph: dict[str, Any]) -> dict[str, Any]:
    components = {}
    for component_id, component in graph.get("components", {}).items():
        components[component_id] = {
            key: value
            for key, value in component.items()
            if key not in IGNORED_COMPONENT_FIELDS
        }
    return {
        "components": components,
        "modules": graph.get("modules", {}),
    }


def _diff(expected: Any, actual: Any, path: str = "$") -> list[str]:
    if type(expected) is not type(actual):
        return [f"{path}: type {type(expected).__name__} != {type(actual).__name__}"]
    if isinstance(expected, dict):
        differences: list[str] = []
        for key in sorted(set(expected) | set(actual)):
            child = f"{path}.{key}"
            if key not in expected:
                differences.append(f"{child}: unexpected")
            elif key not in actual:
                differences.append(f"{child}: missing")
            else:
                differences.extend(_diff(expected[key], actual[key], child))
        return differences
    if isinstance(expected, list):
        if expected != actual:
            return [f"{path}: {expected!r} != {actual!r}"]
        return []
    return [] if expected == actual else [f"{path}: {expected!r} != {actual!r}"]


@dataclass(frozen=True)
class ConnectivityReceipt:
    passed: bool
    canonical_sha256: str
    variant_id: str | None
    fidelity: str
    svg_differences: tuple[str, ...]
    spice_differences: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "canonical_sha256": self.canonical_sha256,
            "variant_id": self.variant_id,
            "fidelity": self.fidelity,
            "svg_differences": list(self.svg_differences),
            "spice_differences": list(self.spice_differences),
        }

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), sort_keys=True, separators=(",", ":")) + "\n"


def build_connectivity_receipt(
    canonical: SemanticGraph,
    svg_graph: dict[str, Any],
    spice_graph: dict[str, Any],
) -> ConnectivityReceipt:
    expected = _connectivity_view(canonical.normalized())
    svg_differences = tuple(_diff(expected, _connectivity_view(svg_graph)))
    spice_differences = tuple(_diff(expected, _connectivity_view(spice_graph)))
    return ConnectivityReceipt(
        passed=not svg_differences and not spice_differences,
        canonical_sha256=hashlib.sha256(canonical.canonical_json.encode("utf-8")).hexdigest(),
        variant_id=canonical.variant_id,
        fidelity=canonical.fidelity,
        svg_differences=svg_differences,
        spice_differences=spice_differences,
    )
