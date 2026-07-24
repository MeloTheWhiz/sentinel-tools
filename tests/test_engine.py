import pytest

from sentinel_tools.engine import CHECKS, available_checks, run_all, run_check


def test_available_checks_contains_builtin_checks() -> None:
    assert available_checks() == (
        "system",
        "network",
        "storage",
        "security",
    )


def test_run_check_uses_registered_collector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        CHECKS,
        "example",
        lambda: {"Status": "OK"},
    )

    result = run_check("example")

    assert result == {"Status": "OK"}


def test_run_check_normalizes_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        CHECKS,
        "example",
        lambda: {"Status": "OK"},
    )

    result = run_check("  EXAMPLE  ")

    assert result == {"Status": "OK"}


def test_run_check_rejects_unknown_check() -> None:
    with pytest.raises(ValueError, match="Unknown diagnostic check"):
        run_check("missing")


def test_run_all_runs_selected_checks(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(
        CHECKS,
        "first",
        lambda: {"Result": "One"},
    )
    monkeypatch.setitem(
        CHECKS,
        "second",
        lambda: {"Result": "Two"},
    )

    result = run_all(("first", "second"))

    assert result == {
        "first": {"Result": "One"},
        "second": {"Result": "Two"},
    }
