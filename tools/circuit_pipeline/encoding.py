"""Lossless SPICE-safe token encoding for canonical IDs and open terminals."""
from __future__ import annotations


def encode_id(prefix: str, value: str) -> str:
    return prefix + "Z" + value.encode("utf-8").hex().upper()


def decode_id(prefix: str, token: str) -> str:
    marker = prefix + "Z"
    if not token.startswith(marker):
        raise ValueError(f"token {token!r} does not start with {marker!r}")
    return bytes.fromhex(token[len(marker) :]).decode("utf-8")


def encode_net(net_id: str | None, component_id: str, pin_id: str) -> str:
    if net_id is None:
        return "OZ" + (component_id + "\x00" + pin_id).encode("utf-8").hex().upper()
    if net_id == "SGND":
        return "0"
    return encode_id("N", net_id)


def decode_net(token: str) -> str | None:
    if token == "0":
        return "SGND"
    if token.startswith("OZ"):
        bytes.fromhex(token[2:]).decode("utf-8")
        return None
    return decode_id("N", token)
