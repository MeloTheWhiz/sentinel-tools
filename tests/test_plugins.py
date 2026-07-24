from __future__ import annotations

from types import ModuleType

import pytest

from sentinel_tools.engine import CheckRegistry
from sentinel_tools.plugins import loader


def test_load_plugin_registers_checks(monkeypatch) -> None:
    registry = CheckRegistry()
    plugin = ModuleType("example_plugin")

    def register(received_registry: CheckRegistry) -> None:
        received_registry.register(
            "example",
            lambda: {"status": "ok"},
        )

    plugin.register = register

    monkeypatch.setattr(
        loader,
        "import_module",
        lambda module_name: plugin,
    )

    loaded = loader.load_plugin(
        "example_plugin",
        registry,
    )

    assert loaded is plugin
    assert registry.available() == ("example",)
    assert registry.run("example") == {"status": "ok"}


def test_load_plugin_rejects_empty_module_name() -> None:
    registry = CheckRegistry()

    with pytest.raises(
        ValueError,
        match="Plugin module name cannot be empty",
    ):
        loader.load_plugin("   ", registry)


def test_load_plugin_requires_register_function(monkeypatch) -> None:
    registry = CheckRegistry()
    plugin = ModuleType("invalid_plugin")

    monkeypatch.setattr(
        loader,
        "import_module",
        lambda module_name: plugin,
    )

    with pytest.raises(
        ValueError,
        match="must define a callable register",
    ):
        loader.load_plugin("invalid_plugin", registry)


def test_load_plugins_loads_multiple_modules(monkeypatch) -> None:
    registry = CheckRegistry()
    imported: list[str] = []

    def fake_import_module(module_name: str) -> ModuleType:
        imported.append(module_name)

        plugin = ModuleType(module_name)

        def register(received_registry: CheckRegistry) -> None:
            received_registry.register(
                module_name,
                lambda name=module_name: {"plugin": name},
            )

        plugin.register = register
        return plugin

    monkeypatch.setattr(
        loader,
        "import_module",
        fake_import_module,
    )

    loaded = loader.load_plugins(
        ["plugin_one", "plugin_two"],
        registry,
    )

    assert imported == [
        "plugin_one",
        "plugin_two",
    ]
    assert tuple(module.__name__ for module in loaded) == (
        "plugin_one",
        "plugin_two",
    )
    assert registry.available() == (
        "plugin_one",
        "plugin_two",
    )
    assert registry.run("plugin_two") == {
        "plugin": "plugin_two",
    }
