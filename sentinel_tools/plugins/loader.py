from __future__ import annotations

from collections.abc import Iterable
from importlib import import_module
from types import ModuleType
from typing import Protocol

from sentinel_tools.engine import CheckRegistry


class PluginModule(Protocol):
    """Interface expected from a Sentinel Tools plugin."""

    def register(self, registry: CheckRegistry) -> None:
        """Register plugin checks with the supplied registry."""


def load_plugin(
    module_name: str,
    registry: CheckRegistry,
) -> ModuleType:
    """Import one plugin module and register its checks."""
    normalized = module_name.strip()

    if not normalized:
        raise ValueError("Plugin module name cannot be empty.")

    module = import_module(normalized)
    register = getattr(module, "register", None)

    if not callable(register):
        raise TypeError(
            f"Plugin '{normalized}' must define a callable register(registry) function."
        )

    register(registry)

    return module


def load_plugins(
    module_names: Iterable[str],
    registry: CheckRegistry,
) -> tuple[ModuleType, ...]:
    """Import and register multiple plugin modules."""
    return tuple(load_plugin(module_name, registry) for module_name in module_names)
