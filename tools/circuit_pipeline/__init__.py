"""Deterministic semantic SVG/SPICE projection and connectivity checking."""

from .core import ProjectionError, SemanticGraph, build_semantic_graph, select_semantic_subgraph
from .equivalence import ConnectivityReceipt, build_connectivity_receipt
from .spice import emit_spice, parse_spice
from .svg import emit_svg, emit_svg_detail, load_layout_overlay, parse_svg
from .simulation import (
    ACAnalysis,
    NgspiceError,
    NgspiceRunner,
    OperatingPointAnalysis,
    Probe,
    SimulationCase,
    SimulationPlan,
    TransientAnalysis,
    emit_ngspice_deck,
    parse_wrdata,
)

__all__ = [
    "ConnectivityReceipt",
    "ProjectionError",
    "SemanticGraph",
    "build_connectivity_receipt",
    "build_semantic_graph",
    "select_semantic_subgraph",
    "emit_spice",
    "emit_svg",
    "emit_svg_detail",
    "load_layout_overlay",
    "parse_spice",
    "parse_svg",
    "ACAnalysis",
    "NgspiceError",
    "NgspiceRunner",
    "OperatingPointAnalysis",
    "Probe",
    "SimulationCase",
    "SimulationPlan",
    "TransientAnalysis",
    "emit_ngspice_deck",
    "parse_wrdata",
]
