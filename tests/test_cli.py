from __future__ import annotations

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
