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

    sentinel = app.SentinelApp(config={})
    sentinel.run(Namespace(command="health"))

    assert calls == ["health"]


def test_app_runs_diagnostic_command(monkeypatch) -> None:
    calls: list[str] = []

    monkeypatch.setattr(
        app,
        "run_diagnostic",
        lambda command: calls.append(command),
    )

    sentinel = app.SentinelApp(config={})
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

    sentinel = app.SentinelApp(config={})
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

    sentinel = app.SentinelApp(config={})

    with pytest.raises(SystemExit) as error:
        sentinel.run(Namespace(command=command))

    assert error.value.code == 0


def test_app_loads_configured_plugins_once(monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], object]] = []

    def fake_load_plugins(module_names, registry) -> tuple[object, ...]:
        calls.append((tuple(module_names), registry))
        return ()

    monkeypatch.setattr(app, "load_plugins", fake_load_plugins)

    sentinel = app.SentinelApp(
        config={
            "plugins": {
                "modules": [
                    "sentinel_example",
                    "sentinel_extra",
                ]
            }
        }
    )

    sentinel.initialize_plugins()
    sentinel.initialize_plugins()

    assert calls == [
        (
            (
                "sentinel_example",
                "sentinel_extra",
            ),
            app.registry,
        )
    ]


def test_app_runs_aur_command(monkeypatch) -> None:
    from argparse import Namespace

    import pytest

    import sentinel_tools.app as app_module
    from sentinel_tools.app import SentinelApp

    called = False

    def fake_show_aur_audit() -> int:
        nonlocal called
        called = True
        return 0

    monkeypatch.setattr(
        app_module,
        "show_aur_audit",
        fake_show_aur_audit,
    )

    app = SentinelApp(config={})

    with pytest.raises(SystemExit) as error:
        app.run(Namespace(command="aur"))

    assert error.value.code == 0
    assert called
