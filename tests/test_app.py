from __future__ import annotations

from argparse import Namespace

import pytest

from sentinel_tools import app


def test_app_runs_health_command(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        app,
        "run_health_check",
        lambda: calls.append("health"),
    )

    sentinel = app.SentinelApp()
    sentinel.run(Namespace(command="health"))

    assert calls == ["health"]


def test_app_runs_diagnostic_command(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        app,
        "run_diagnostic",
        lambda command: calls.append(command),
    )

    sentinel = app.SentinelApp()
    sentinel.run(Namespace(command="network"))

    assert calls == ["network"]


def test_app_runs_report_command(monkeypatch, capsys) -> None:
    calls: list[dict[str, object]] = []

    def fake_save_report(**kwargs):
        calls.append(kwargs)
        return "/tmp/report.json"

    monkeypatch.setattr(app, "save_report", fake_save_report)

    args = Namespace(
        command="report",
        format="json",
        output=None,
        redact=True,
        severity="warning",
        finding_code="NET001",
    )

    sentinel = app.SentinelApp()
    sentinel.run(args)

    output = capsys.readouterr().out

    assert calls == [
        {
            "report_format": "json",
            "output": None,
            "redact": True,
            "severity": "warning",
            "finding_code": "NET001",
        }
    ]
    assert "/tmp/report.json" in output


@pytest.mark.parametrize(
    ("command", "function_name"),
    [
        ("update", "update"),
        ("clean", "clean"),
    ],
)
def test_app_raises_exit_for_maintenance(
    monkeypatch,
    command: str,
    function_name: str,
) -> None:
    monkeypatch.setattr(app, function_name, lambda: 0)

    sentinel = app.SentinelApp()

    with pytest.raises(SystemExit) as error:
        sentinel.run(Namespace(command=command))

    assert error.value.code == 0
