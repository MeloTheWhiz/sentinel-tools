from __future__ import annotations

import argparse
from argparse import Namespace

import pytest

from sentinel_tools import cli


def test_run_diagnostic_uses_engine(monkeypatch, capsys) -> None:
    calls: list[str] = []

    def fake_run_check(name: str) -> dict[str, str]:
        calls.append(name)
        return {"Firewall": "Active"}

    monkeypatch.setattr(cli, "run_check", fake_run_check)
    cli.run_diagnostic("security")
    output = capsys.readouterr().out

    assert calls == ["security"]
    assert "SECURITY AUDIT" in output
    assert "Firewall:" in output
    assert "Active" in output


def test_run_health_check_uses_engine(monkeypatch, capsys) -> None:
    system_data = {"Operating System": "Arch Linux", "Kernel": "Linux test"}
    monkeypatch.setattr(
        cli,
        "run_check",
        lambda name: system_data if name == "system" else {},
    )
    monkeypatch.setattr(cli, "show_health_score", lambda data: None)

    cli.run_health_check()
    output = capsys.readouterr().out

    assert "SYSTEM HEALTH" in output
    assert "Operating System:" in output
    assert "Arch Linux" in output


@pytest.mark.parametrize(
    ("command", "title", "payload"),
    [
        ("security", "SECURITY AUDIT", {"Firewall": "Active"}),
        ("network", "NETWORK DIAGNOSTICS", {"Connectivity": "Online"}),
        ("storage", "STORAGE DIAGNOSTICS", {"Filesystem": "Healthy"}),
    ],
)
def test_diagnostic_commands_use_engine(
    command, title, payload, monkeypatch, capsys
) -> None:
    calls: list[str] = []

    def fake_run_check(name: str) -> dict[str, str]:
        calls.append(name)
        return payload

    monkeypatch.setattr(cli, "run_check", fake_run_check)
    monkeypatch.setattr(cli, "ensure_arch", lambda: None)
    monkeypatch.setattr(
        cli.argparse.ArgumentParser,
        "parse_args",
        lambda self: cli.argparse.Namespace(command=command),
    )

    cli.main()
    output = capsys.readouterr().out

    assert calls == [command]
    assert title in output


def test_build_parser_contains_expected_commands() -> None:
    parser = cli.build_parser()
    choices = parser._subparsers._group_actions[0].choices

    assert {
        "menu",
        "health",
        "update",
        "clean",
        "security",
        "network",
        "storage",
        "checks",
        "report",
    } <= set(choices)


def test_report_parser_accepts_options() -> None:
    parser = cli.build_parser()
    args = parser.parse_args(
        [
            "report",
            "--format",
            "json",
            "--redact",
            "--severity",
            "warning",
            "--finding-code",
            "NET001",
        ]
    )

    assert args.command == "report"
    assert args.format == "json"
    assert args.redact is True
    assert args.severity == "warning"
    assert args.finding_code == "NET001"


def test_help_is_available_without_platform_check(monkeypatch) -> None:
    def fail_platform_check() -> None:
        raise AssertionError("ensure_arch should not run for --help")

    monkeypatch.setattr(cli, "ensure_arch", fail_platform_check)
    monkeypatch.setattr("sys.argv", ["sentinel-tools", "--help"])

    with pytest.raises(SystemExit) as error:
        cli.main()

    assert error.value.code == 0


def test_parser_accepts_aur_command() -> None:
    args = cli.build_parser().parse_args(["aur"])

    assert args.command == "aur"


def test_main_delegates_to_sentinel_app(monkeypatch) -> None:
    calls: list[object] = []
    args = Namespace(command="health")

    class FakeSentinelApp:
        def run(self, received_args) -> None:
            calls.append(received_args)

    monkeypatch.setattr(cli, "ensure_arch", lambda: None)
    monkeypatch.setattr(
        argparse.ArgumentParser,
        "parse_args",
        lambda self: args,
    )

    import sentinel_tools.app

    monkeypatch.setattr(sentinel_tools.app, "SentinelApp", FakeSentinelApp)
    cli.main()

    assert calls == [args]
