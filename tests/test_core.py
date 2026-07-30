from __future__ import annotations

import subprocess

from sentinel_tools.core import run


def test_run_success() -> None:
    result = run(["printf", "sentinel"])

    assert result.ok
    assert result.stdout == "sentinel"
    assert result.stderr == ""


def test_run_missing_command() -> None:
    result = run(["sentinel-command-that-does-not-exist"])

    assert not result.ok
    assert result.returncode == 127
    assert "Command not found" in result.stderr


def test_noninteractive_sudo_uses_dash_n(monkeypatch) -> None:
    captured_command: list[str] = []

    def fake_run(command, **kwargs):
        captured_command.extend(command)
        return subprocess.CompletedProcess(
            command,
            returncode=1,
            stdout="",
            stderr="sudo: a password is required",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = run(["smartctl", "-H", "/dev/nvme0n1"], sudo=True, sudo_prompt=False)

    assert captured_command[:2] == ["sudo", "-n"]
    assert result.stderr == "Administrator access required."
