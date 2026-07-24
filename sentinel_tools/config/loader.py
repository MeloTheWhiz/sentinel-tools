from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path


DEFAULT_CONFIG = """[general]
theme = "dark"
health_threshold = 90

[checks]
smart = true
network = true
wifi_speed_test = false

[reports]
default_format = "text"

[plugins]
modules = []
"""


def config_path() -> Path:
    """Return the Sentinel Tools configuration path."""
    return Path.home() / ".config" / "sentinel-tools" / "config.toml"


def ensure_config() -> Path:
    """Create the default configuration file when it does not exist."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(DEFAULT_CONFIG, encoding="utf-8")

    return path


def load_config() -> dict[str, object]:
    """Load the Sentinel Tools configuration."""
    path = ensure_config()

    with path.open("rb") as file:
        return tomllib.load(file)


def plugin_modules(config: Mapping[str, object]) -> tuple[str, ...]:
    """Return configured plugin module names."""
    plugins = config.get("plugins")

    if plugins is None:
        return ()

    if not isinstance(plugins, Mapping):
        raise ValueError("The 'plugins' configuration must be a table.")

    modules = plugins.get("modules", [])

    if not isinstance(modules, list):
        raise ValueError("The 'plugins.modules' setting must be a list.")

    normalized: list[str] = []

    for module_name in modules:
        if not isinstance(module_name, str):
            raise ValueError("Every entry in 'plugins.modules' must be a string.")

        module_name = module_name.strip()

        if not module_name:
            raise ValueError("Plugin module names cannot be empty.")

        normalized.append(module_name)

    return tuple(normalized)
