from __future__ import annotations

import pytest

from sentinel_tools.config.loader import plugin_modules


def test_plugin_modules_returns_configured_modules() -> None:
    config = {
        "plugins": {
            "modules": [
                "sentinel_example",
                " sentinel_extra ",
            ]
        }
    }

    assert plugin_modules(config) == (
        "sentinel_example",
        "sentinel_extra",
    )


def test_plugin_modules_returns_empty_tuple_when_missing() -> None:
    assert plugin_modules({}) == ()


def test_plugin_modules_requires_list() -> None:
    config = {
        "plugins": {
            "modules": "sentinel_example",
        }
    }

    with pytest.raises(
        TypeError,
        match="must be a list",
    ):
        plugin_modules(config)


def test_plugin_modules_rejects_empty_names() -> None:
    config = {
        "plugins": {
            "modules": ["   "],
        }
    }

    with pytest.raises(
        ValueError,
        match="cannot be empty",
    ):
        plugin_modules(config)
