"""Objective mapping boundary for FR-OBJ-001."""

from typing import Any


def anchor_public_interfaces(interfaces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return placeholder objective anchors for externally-facing interfaces only."""
    return [
        {
            "interface": interface["name"],
            "objective": "Expose repository analysis capability to end users",
        }
        for interface in interfaces
        if interface.get("public") is True
    ]
