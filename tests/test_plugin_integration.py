from __future__ import annotations

from sentinel_tools import app, engine
from sentinel_tools.engine import CheckRegistry


def test_configured_plugin_loads_and_runs(monkeypatch) -> None:
    registry = CheckRegistry()

    monkeypatch.setattr(app, "registry", registry)
    monkeypatch.setattr(engine, "registry", registry)

    sentinel = app.SentinelApp(
        config={
            "plugins": {
                "modules": [
                    "sentinel_tools.plugins.example",
                ]
            }
        }
    )

    sentinel.initialize_plugins()

    assert registry.available() == ("example",)
    assert engine.run_check("example") == {
        "Plugin": "Sentinel Tools example plugin",
        "Status": "Loaded successfully",
    }
