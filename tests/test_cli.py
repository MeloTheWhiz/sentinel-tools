from __future__ import annotations

import argparse
from argparse import Namespace

from sentinel_tools import cli


def test_run_diagnostic_uses_engine(
    monkeypatch,
    capsys,
) -> None:
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


def test_run_health_check_uses_engine(
    monkeypatch,
    capsys,
) -> None:
    system_data = {
        "Operating System": "Arch Linux",
        "Kernel": "Linux test",
    }

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


def test_security_command_uses_engine(
    monkeypatch,
    capsys,
) -> None:
    calls: list[str] = []

    def fake_run_check(name: str) -> dict[str, str]:
        calls.append(name)
        return {"Firewall": "Active"}

    monkeypatch.setattr(cli, "run_check", fake_run_check)
    monkeypatch.setattr(cli, "ensure_arch", lambda: None)
    monkeypatch.setattr(
        cli.argparse.ArgumentParser,
        "parse_args",
        lambda self: cli.argparse.Namespace(command="security"),
    )

    cli.main()

    output = capsys.readouterr().out

    assert calls == ["security"]
    assert "SECURITY AUDIT" in output
    assert "Firewall:" in output
    assert "Active" in output


def test_network_command_uses_engine(
    monkeypatch,
    capsys,
) -> None:
    calls: list[str] = []

    def fake_run_check(name: str) -> dict[str, str]:
        calls.append(name)
        return {"Connectivity": "Online"}

    monkeypatch.setattr(cli, "run_check", fake_run_check)
    monkeypatch.setattr(cli, "ensure_arch", lambda: None)
    monkeypatch.setattr(
        cli.argparse.ArgumentParser,
        "parse_args",
        lambda self: cli.argparse.Namespace(command="network"),
    )

    cli.main()

    output = capsys.readouterr().out

    assert calls == ["network"]
    assert "NETWORK DIAGNOSTICS" in output
    assert "Connectivity:" in output
    assert "Online" in output


def test_storage_command_uses_engine(
    monkeypatch,
    capsys,
) -> None:
    calls: list[str] = []

    def fake_run_check(name: str) -> dict[str, str]:
        calls.append(name)
        return {"Filesystem": "Healthy"}

    monkeypatch.setattr(cli, "run_check", fake_run_check)
    monkeypatch.setattr(cli, "ensure_arch", lambda: None)
    monkeypatch.setattr(
        cli.argparse.ArgumentParser,
        "parse_args",
        lambda self: cli.argparse.Namespace(command="storage"),
    )

    cli.main()

    output = capsys.readouterr().out

    assert calls == ["storage"]
    assert "STORAGE DIAGNOSTICS" in output
    assert "Filesystem:" in output
    assert "Healthy" in output


def test_build_parser_contains_expected_commands() -> None:
    parser = cli.build_parser()

    choices = parser._subparsers._group_actions[0].choices

    assert "menu" in choices
    assert "health" in choices
    assert "update" in choices
    assert "clean" in choices
    assert "security" in choices
    assert "network" in choices
    assert "storage" in choices
    assert "report" in choices


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

    monkeypatch.setattr(
        sentinel_tools.app,
        "SentinelApp",
        FakeSentinelApp,
    )

    cli.main()

    assert calls == [args]
