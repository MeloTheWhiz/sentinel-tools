from __future__ import annotations

import tomllib
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
"""


def config_path() -> Path:
    return Path.home() / ".config" / "sentinel-tools" / "config.toml"


def ensure_config() -> Path:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(DEFAULT_CONFIG, encoding="utf-8")

    return path


def load_config() -> dict[str, object]:
    path = ensure_config()

    with path.open("rb") as file:
        return tomllib.load(file)
