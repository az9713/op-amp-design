"""Validate the canonical JSON circuit graph without third-party packages.

The JSON Schema file documents the interchange format.  This module enforces
the invariants that ordinary JSON Schema cannot express conveniently: unique
stable identities, valid cross-references, pin/model compatibility, legal
weekly inheritance, and deterministic serialization.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "1.0.0"
STABLE_ID = re.compile(r"^[A-Z][A-Z0-9_]*(?:\.[A-Z][A-Z0-9_]*)*$")
WEEK_ID = re.compile(r"^W(?:0[0-9]|1[0-3])$")
STATE_CLASSES = {
    "persistent-installed",
    "persistent-inactive",
    "configuration-only-fixture",
    "removed-off-circuit",
    "reserved-unpopulated",
    "deferred",
}
EVIDENCE_LABELS = {"verified", "derived", "proposed", "tbd", "deferred"}
ROOT_KEYS = {
    "schema_version",
    "project_id",
    "title",
    "sources",
    "nets",
    "modules",
    "models",
    "components",
    "variants",
    "weekly_states",
}


@dataclass(frozen=True, order=True)
class ValidationIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path}: {self.message}"


class GraphValidator:
    """Collect all structural and graph-reference errors in one pass."""

    def __init__(self, document: Any):
        self.document = document
        self.issues: list[ValidationIssue] = []
        self.sources: dict[str, dict[str, Any]] = {}
        self.nets: dict[str, dict[str, Any]] = {}
        self.modules: dict[str, dict[str, Any]] = {}
        self.models: dict[str, dict[str, Any]] = {}
        self.components: dict[str, dict[str, Any]] = {}
        self.variants: dict[str, dict[str, Any]] = {}
        self.weeks: dict[str, dict[str, Any]] = {}

    def error(self, path: str, message: str) -> None:
        self.issues.append(ValidationIssue(path, message))

    def require_keys(self, value: Any, path: str, required: Iterable[str]) -> bool:
        if not isinstance(value, dict):
            self.error(path, "must be an object")
            return False
        for key in required:
            if key not in value:
                self.error(path, f"missing required key {key!r}")
        return True

    def stable_id(self, value: Any, path: str) -> bool:
        if not isinstance(value, str) or not STABLE_ID.fullmatch(value):
            self.error(path, "must be a canonical uppercase dotted stable ID")
            return False
        return True

    def index(self, collection: Any, name: str) -> dict[str, dict[str, Any]]:
        path = f"$.{name}"
        result: dict[str, dict[str, Any]] = {}
        if not isinstance(collection, list):
            self.error(path, "must be an array")
            return result
        for index, item in enumerate(collection):
            item_path = f"{path}[{index}]"
            if not isinstance(item, dict):
                self.error(item_path, "must be an object")
                continue
            item_id = item.get("id")
            if not self.stable_id(item_id, f"{item_path}.id"):
                continue
            if item_id in result:
                self.error(f"{item_path}.id", f"duplicate ID {item_id!r}")
            else:
                result[item_id] = item
        return result

    def evidence(self, refs: Any, path: str) -> None:
        if not isinstance(refs, list):
            self.error(path, "must be an array")
            return
        for index, ref in enumerate(refs):
            ref_path = f"{path}[{index}]"
            if not self.require_keys(ref, ref_path, ("source_id", "claim", "label")):
                continue
            source_id = ref.get("source_id")
            if source_id not in self.sources:
                self.error(f"{ref_path}.source_id", f"unknown source {source_id!r}")
            if not isinstance(ref.get("claim"), str) or not ref["claim"].strip():
                self.error(f"{ref_path}.claim", "must be a non-empty string")
            label = ref.get("label")
            if label not in EVIDENCE_LABELS:
                self.error(f"{ref_path}.label", f"must be one of {sorted(EVIDENCE_LABELS)}")
            derivation = ref.get("derivation")
            if label == "derived" and not isinstance(derivation, dict):
                self.error(ref_path, "derived evidence requires a derivation object")
            if isinstance(derivation, dict):
                for key in ("formula", "inputs", "units"):
                    if key not in derivation:
                        self.error(f"{ref_path}.derivation", f"missing required key {key!r}")

    def validate(self) -> list[ValidationIssue]:
        if not isinstance(self.document, dict):
            return [ValidationIssue("$", "document must be a JSON object")]

        unknown = sorted(set(self.document) - ROOT_KEYS)
        for key in unknown:
            self.error(f"$.{key}", "unknown root key")
        for key in ROOT_KEYS - {"title"}:
            if key not in self.document:
                self.error("$", f"missing required key {key!r}")
        if self.document.get("schema_version") != SCHEMA_VERSION:
            self.error("$.schema_version", f"must equal {SCHEMA_VERSION!r}")
        self.stable_id(self.document.get("project_id"), "$.project_id")

        self.sources = self.index(self.document.get("sources"), "sources")
        self.nets = self.index(self.document.get("nets"), "nets")
        self.modules = self.index(self.document.get("modules"), "modules")
        self.models = self.index(self.document.get("models"), "models")
        self.components = self.index(self.document.get("components"), "components")
        self.variants = self.index(self.document.get("variants"), "variants")
        self.weeks = self.index_weeks(self.document.get("weekly_states"))

        self.validate_sources()
        self.validate_global_ids()
        self.validate_nets()
        self.validate_models()
        self.validate_components()
        self.validate_modules()
        self.validate_variants()
        self.validate_weeks()
        return sorted(set(self.issues))

    def validate_global_ids(self) -> None:
        namespaces = {
            "source": self.sources,
            "net": self.nets,
            "module": self.modules,
            "model": self.models,
            "component": self.components,
            "variant": self.variants,
        }
        owners: dict[str, str] = {}
        for kind, values in namespaces.items():
            for item_id in values:
                previous = owners.get(item_id)
                if previous is not None:
                    self.error("$", f"stable ID {item_id!r} is shared by {previous} and {kind}")
                else:
                    owners[item_id] = kind

    def index_weeks(self, collection: Any) -> dict[str, dict[str, Any]]:
        path = "$.weekly_states"
        result: dict[str, dict[str, Any]] = {}
        if not isinstance(collection, list):
            self.error(path, "must be an array")
            return result
        for index, item in enumerate(collection):
            item_path = f"{path}[{index}]"
            if not isinstance(item, dict):
                self.error(item_path, "must be an object")
                continue
            item_id = item.get("id")
            if not isinstance(item_id, str) or not WEEK_ID.fullmatch(item_id):
                self.error(f"{item_path}.id", "must be W00 through W13")
                continue
            if item_id in result:
                self.error(f"{item_path}.id", f"duplicate ID {item_id!r}")
            else:
                result[item_id] = item
        return result

    def validate_sources(self) -> None:
        for source_id, source in self.sources.items():
            path = f"$.sources[{source_id}]"
            self.require_keys(source, path, ("id", "kind", "title", "locator"))
            if not isinstance(source.get("locator"), str) or not source["locator"].strip():
                self.error(f"{path}.locator", "must be a non-empty reproducible locator")
            digest = source.get("sha256")
            if digest is not None and (not isinstance(digest, str) or not re.fullmatch(r"[A-Fa-f0-9]{64}", digest)):
                self.error(f"{path}.sha256", "must be a 64-character hexadecimal SHA-256")

    def validate_nets(self) -> None:
        allowed = {"signal", "power", "ground", "control", "measurement"}
        spice_zero = []
        for net_id, net in self.nets.items():
            path = f"$.nets[{net_id}]"
            if net.get("class") not in allowed:
                self.error(f"{path}.class", f"must be one of {sorted(allowed)}")
            if net.get("spice_node") in (0, "0"):
                spice_zero.append(net_id)
            self.evidence(net.get("source_evidence", []), f"{path}.source_evidence")
        if len(spice_zero) > 1:
            self.error("$.nets", f"SPICE node 0 is assigned to multiple nets: {spice_zero}")

    def validate_models(self) -> None:
        for model_id, model in self.models.items():
            path = f"$.models[{model_id}]"
            self.require_keys(model, path, ("id", "fidelity", "kind", "reference", "pin_names"))
            pins = model.get("pin_names")
            if not isinstance(pins, list) or not pins:
                self.error(f"{path}.pin_names", "must be a non-empty array")
            elif len(pins) != len(set(pins)):
                self.error(f"{path}.pin_names", "contains duplicate model pins")
            self.evidence(model.get("source_evidence", []), f"{path}.source_evidence")

    def validate_components(self) -> None:
        for component_id, component in self.components.items():
            path = f"$.components[{component_id}]"
            self.require_keys(component, path, ("id", "kind", "module_id", "state_class", "pins", "model_bindings", "source_evidence"))
            if component.get("module_id") not in self.modules:
                self.error(f"{path}.module_id", f"unknown module {component.get('module_id')!r}")
            if component.get("state_class") not in STATE_CLASSES:
                self.error(f"{path}.state_class", f"must be one of {sorted(STATE_CLASSES)}")
            pins = component.get("pins")
            pin_ids: set[str] = set()
            if not isinstance(pins, list) or not pins:
                self.error(f"{path}.pins", "must be a non-empty array")
                pins = []
            for index, pin in enumerate(pins):
                pin_path = f"{path}.pins[{index}]"
                if not self.require_keys(pin, pin_path, ("id", "net")):
                    continue
                pin_id = pin.get("id")
                if not isinstance(pin_id, str) or not pin_id:
                    self.error(f"{pin_path}.id", "must be a non-empty string")
                elif pin_id in pin_ids:
                    self.error(f"{pin_path}.id", f"duplicate component pin {pin_id!r}")
                else:
                    pin_ids.add(pin_id)
                net_id = pin.get("net")
                if net_id is not None and net_id not in self.nets:
                    self.error(f"{pin_path}.net", f"unknown net {net_id!r}")

            bindings = component.get("model_bindings")
            if not isinstance(bindings, dict):
                self.error(f"{path}.model_bindings", "must be an object")
                bindings = {}
            for fidelity, model_id in bindings.items():
                if fidelity not in {"ideal", "realistic"}:
                    self.error(f"{path}.model_bindings.{fidelity}", "unknown fidelity")
                    continue
                model = self.models.get(model_id)
                if model is None:
                    self.error(f"{path}.model_bindings.{fidelity}", f"unknown model {model_id!r}")
                elif model.get("fidelity") != fidelity:
                    self.error(f"{path}.model_bindings.{fidelity}", f"model {model_id!r} has fidelity {model.get('fidelity')!r}")

            pin_map = component.get("model_pin_map", {})
            if not isinstance(pin_map, dict):
                self.error(f"{path}.model_pin_map", "must be an object")
            else:
                for canonical_pin in pin_map:
                    if canonical_pin not in pin_ids:
                        self.error(f"{path}.model_pin_map.{canonical_pin}", "does not name a component pin")
                for fidelity, model_id in bindings.items():
                    model = self.models.get(model_id)
                    if model:
                        valid_model_pins = set(model.get("pin_names", []))
                        for canonical_pin, model_pin in pin_map.items():
                            if model_pin not in valid_model_pins:
                                self.error(
                                    f"{path}.model_pin_map.{canonical_pin}",
                                    f"model pin {model_pin!r} is absent from {model_id!r}",
                                )
            self.evidence(component.get("source_evidence"), f"{path}.source_evidence")

    def validate_modules(self) -> None:
        claimed_components: dict[str, str] = {}
        for module_id, module in self.modules.items():
            path = f"$.modules[{module_id}]"
            parent = module.get("parent_id")
            if parent is not None:
                if parent == module_id:
                    self.error(f"{path}.parent_id", "module cannot parent itself")
                elif parent not in self.modules:
                    self.error(f"{path}.parent_id", f"unknown module {parent!r}")
            ports = module.get("ports", [])
            port_ids: set[str] = set()
            if not isinstance(ports, list):
                self.error(f"{path}.ports", "must be an array")
                ports = []
            for index, port in enumerate(ports):
                port_path = f"{path}.ports[{index}]"
                if not self.require_keys(port, port_path, ("id", "direction", "net")):
                    continue
                port_id = port.get("id")
                if port_id in port_ids:
                    self.error(f"{port_path}.id", f"duplicate port {port_id!r}")
                port_ids.add(port_id)
                if port.get("net") not in self.nets:
                    self.error(f"{port_path}.net", f"unknown net {port.get('net')!r}")
            component_ids = module.get("component_ids", [])
            if not isinstance(component_ids, list):
                self.error(f"{path}.component_ids", "must be an array")
                continue
            for component_id in component_ids:
                if component_id not in self.components:
                    self.error(f"{path}.component_ids", f"unknown component {component_id!r}")
                elif self.components[component_id].get("module_id") != module_id:
                    self.error(f"{path}.component_ids", f"component {component_id!r} points to another module")
                if component_id in claimed_components:
                    self.error(f"{path}.component_ids", f"component {component_id!r} is also claimed by {claimed_components[component_id]!r}")
                claimed_components[component_id] = module_id
        for component_id, component in self.components.items():
            if component_id not in claimed_components:
                self.error(f"$.components[{component_id}]", "is not listed by its owning module")
        self.validate_module_cycles()

    def validate_module_cycles(self) -> None:
        for module_id in self.modules:
            seen: set[str] = set()
            current: str | None = module_id
            while current is not None and current in self.modules:
                if current in seen:
                    self.error(f"$.modules[{module_id}].parent_id", "module hierarchy contains a cycle")
                    break
                seen.add(current)
                current = self.modules[current].get("parent_id")

    def validate_pin_connection(self, change: Any, path: str) -> None:
        if not self.require_keys(change, path, ("component_id", "pin_id", "net")):
            return
        component_id = change.get("component_id")
        component = self.components.get(component_id)
        if component is None:
            self.error(f"{path}.component_id", f"unknown component {component_id!r}")
        else:
            valid_pins = {pin.get("id") for pin in component.get("pins", []) if isinstance(pin, dict)}
            if change.get("pin_id") not in valid_pins:
                self.error(f"{path}.pin_id", f"unknown pin on component {component_id!r}")
        net_id = change.get("net")
        if net_id is not None and net_id not in self.nets:
            self.error(f"{path}.net", f"unknown net {net_id!r}")

    def validate_variants(self) -> None:
        for variant_id, variant in self.variants.items():
            path = f"$.variants[{variant_id}]"
            self.require_keys(variant, path, ("id", "description", "connection_overrides", "state_overrides", "model_overrides"))
            for index, change in enumerate(variant.get("connection_overrides", [])):
                self.validate_pin_connection(change, f"{path}.connection_overrides[{index}]")
            for index, change in enumerate(variant.get("state_overrides", [])):
                change_path = f"{path}.state_overrides[{index}]"
                if not self.require_keys(change, change_path, ("component_id", "state_class")):
                    continue
                if change.get("component_id") not in self.components:
                    self.error(f"{change_path}.component_id", "unknown component")
                if change.get("state_class") not in STATE_CLASSES:
                    self.error(f"{change_path}.state_class", "unknown state class")
            for index, override in enumerate(variant.get("model_overrides", [])):
                override_path = f"{path}.model_overrides[{index}]"
                if not self.require_keys(override, override_path, ("component_id", "fidelity", "model_id")):
                    continue
                if override.get("component_id") not in self.components:
                    self.error(f"{override_path}.component_id", "unknown component")
                model = self.models.get(override.get("model_id"))
                if model is None:
                    self.error(f"{override_path}.model_id", "unknown model")
                elif model.get("fidelity") != override.get("fidelity"):
                    self.error(f"{override_path}.model_id", "model fidelity does not match override")

    def validate_weeks(self) -> None:
        for week_id, week in self.weeks.items():
            path = f"$.weekly_states[{week_id}]"
            self.require_keys(week, path, ("id", "title", "learning_objective", "inherits", "configuration_ids", "delta", "source_evidence"))
            number = int(week_id[1:])
            inherits = week.get("inherits")
            expected = None if number == 0 else f"W{number - 1:02d}"
            if inherits != expected:
                self.error(f"{path}.inherits", f"must be {expected!r} for strict weekly inheritance")
            if inherits is not None and inherits not in self.weeks:
                self.error(f"{path}.inherits", f"inherited state {inherits!r} is not present")
            for variant_id in week.get("configuration_ids", []):
                if variant_id not in self.variants:
                    self.error(f"{path}.configuration_ids", f"unknown variant {variant_id!r}")
            self.evidence(week.get("source_evidence"), f"{path}.source_evidence")
            self.validate_delta(week.get("delta"), f"{path}.delta")
        self.validate_delta_timeline()

    def validate_delta_timeline(self) -> None:
        installed: set[str] = set()
        for week_id in sorted(self.weeks, key=lambda value: int(value[1:])):
            delta = self.weeks[week_id].get("delta")
            if not isinstance(delta, dict):
                continue
            path = f"$.weekly_states[{week_id}].delta"
            add = delta.get("add", []) if isinstance(delta.get("add"), list) else []
            remove = delta.get("remove", []) if isinstance(delta.get("remove"), list) else []
            for component_id in add:
                if component_id in installed:
                    self.error(f"{path}.add", f"component {component_id!r} is already in the cumulative inventory")
                installed.add(component_id)
            for component_id in remove:
                if component_id not in installed:
                    self.error(f"{path}.remove", f"component {component_id!r} is not in the cumulative inventory")
                installed.discard(component_id)
            replacements = delta.get("replace", [])
            if not isinstance(replacements, list):
                continue
            for replacement in replacements:
                if not isinstance(replacement, dict):
                    continue
                old_id = replacement.get("old_component_id")
                new_id = replacement.get("new_component_id")
                if old_id not in installed:
                    self.error(f"{path}.replace", f"old component {old_id!r} is not in the cumulative inventory")
                if new_id in installed:
                    self.error(f"{path}.replace", f"new component {new_id!r} is already in the cumulative inventory")
                installed.discard(old_id)
                if new_id in self.components:
                    installed.add(new_id)

    def validate_delta(self, delta: Any, path: str) -> None:
        required = ("add", "remove", "replace", "state_changes", "connection_changes")
        if not self.require_keys(delta, path, required):
            return
        add = delta.get("add", [])
        remove = delta.get("remove", [])
        if not isinstance(add, list) or not isinstance(remove, list):
            self.error(path, "add and remove must be arrays")
            return
        for name, ids in (("add", add), ("remove", remove)):
            if len(ids) != len(set(ids)):
                self.error(f"{path}.{name}", "contains duplicate component IDs")
            for component_id in ids:
                if component_id not in self.components:
                    self.error(f"{path}.{name}", f"unknown component {component_id!r}")
        overlap = sorted(set(add) & set(remove))
        if overlap:
            self.error(path, f"components cannot be both added and removed: {overlap}")
        for index, replacement in enumerate(delta.get("replace", [])):
            replacement_path = f"{path}.replace[{index}]"
            if not self.require_keys(replacement, replacement_path, ("old_component_id", "new_component_id")):
                continue
            old_id = replacement.get("old_component_id")
            new_id = replacement.get("new_component_id")
            if old_id == new_id:
                self.error(replacement_path, "replacement IDs must differ")
            for key, component_id in (("old_component_id", old_id), ("new_component_id", new_id)):
                if component_id not in self.components:
                    self.error(f"{replacement_path}.{key}", f"unknown component {component_id!r}")
        for index, change in enumerate(delta.get("state_changes", [])):
            change_path = f"{path}.state_changes[{index}]"
            if not self.require_keys(change, change_path, ("component_id", "from", "to")):
                continue
            if change.get("component_id") not in self.components:
                self.error(f"{change_path}.component_id", "unknown component")
            if change.get("from") not in STATE_CLASSES or change.get("to") not in STATE_CLASSES:
                self.error(change_path, "from/to must be valid state classes")
            if change.get("from") == change.get("to"):
                self.error(change_path, "state change must change the class")
        for index, change in enumerate(delta.get("connection_changes", [])):
            self.validate_pin_connection(change, f"{path}.connection_changes[{index}]")


def validate_document(document: Any) -> list[ValidationIssue]:
    """Return a deterministic, sorted list of validation issues."""
    return GraphValidator(document).validate()


def canonical_json(document: Any) -> str:
    """Return the deterministic UTF-8 JSON representation used for hashing."""
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def load_document(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="JSON graph to validate")
    parser.add_argument(
        "--check-canonical",
        action="store_true",
        help="also require byte-for-byte canonical JSON serialization",
    )
    args = parser.parse_args(argv)
    try:
        document = load_document(args.graph)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"{args.graph}: unable to load JSON: {exc}", file=sys.stderr)
        return 2
    issues = validate_document(document)
    if args.check_canonical:
        try:
            actual = args.graph.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            print(f"{args.graph}: unable to read JSON: {exc}", file=sys.stderr)
            return 2
        if actual != canonical_json(document):
            issues.append(ValidationIssue("$", "file is valid JSON but is not canonical serialization"))
    if issues:
        for issue in sorted(set(issues)):
            print(issue, file=sys.stderr)
        print(f"FAIL: {len(set(issues))} issue(s)", file=sys.stderr)
        return 1
    print(f"PASS: {args.graph}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
