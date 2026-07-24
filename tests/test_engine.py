from __future__ import annotations

import pytest

from sentinel_tools import engine


def test_available_checks() -> None:
    assert engine.available_checks() == (
        "system",
        "network",
        "storage",
        "security",
    )


def test_run_check_returns_dict() -> None:
    result = engine.run_check("system")

    assert isinstance(result, dict)


def test_run_check_is_case_insensitive() -> None:
    registry = engine.CheckRegistry()
    calls: list[str] = []

    def collector() -> dict[str, str]:
        calls.append("called")
        return {"status": "ok"}

    registry.register("system", collector)

    assert registry.run("SYSTEM") == {"status": "ok"}
    assert calls == ["called"]


def test_run_check_unknown() -> None:
    with pytest.raises(ValueError, match="Unknown diagnostic check"):
        engine.run_check("does-not-exist")


def test_run_all_runs_everything() -> None:
    result = engine.run_all()

    assert set(result) == {
        "system",
        "network",
        "storage",
        "security",
    }


def test_run_all_selected_checks() -> None:
    result = engine.run_all(["system", "network"])

    assert set(result) == {
        "system",
        "network",
    }


def test_registry_registers_and_runs_check() -> None:
    registry = engine.CheckRegistry()

    registry.register(
        "Example",
        lambda: {"status": "ok"},
    )

    assert registry.available() == ("example",)
    assert registry.run("EXAMPLE") == {"status": "ok"}


def test_registry_rejects_empty_name() -> None:
    registry = engine.CheckRegistry()

    with pytest.raises(ValueError, match="cannot be empty"):
        registry.register("   ", lambda: {})


def test_registry_replaces_existing_check() -> None:
    registry = engine.CheckRegistry()

    registry.register("example", lambda: {"value": "first"})
    registry.register("example", lambda: {"value": "second"})

    assert registry.available() == ("example",)
    assert registry.run("example") == {"value": "second"}


def test_registry_runs_selected_checks() -> None:
    registry = engine.CheckRegistry()

    registry.register("first", lambda: {"value": "1"})
    registry.register("second", lambda: {"value": "2"})

    assert registry.run_all(["SECOND"]) == {
        "second": {"value": "2"},
    }
