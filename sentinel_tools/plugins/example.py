from __future__ import annotations

from sentinel_tools.engine import CheckRegistry


def collect() -> dict[str, str]:
    """Return example diagnostic information."""
    return {
        "Plugin": "Sentinel Tools example plugin",
        "Status": "Loaded successfully",
    }


def register(registry: CheckRegistry) -> None:
    """Register the example diagnostic check."""
    registry.register("example", collect)
