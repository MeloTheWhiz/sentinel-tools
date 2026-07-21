from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass
class Result:
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run(
    command: Iterable[str],
    *,
    sudo: bool = False,
    sudo_prompt: bool = True,
) -> Result:
    cmd = list(command)

    if sudo:
        sudo_command = ["sudo"]

        if not sudo_prompt:
            sudo_command.append("-n")

        cmd = [*sudo_command, *cmd]

    try:
        process = subprocess.run(
            cmd,
            text=True,
            capture_output=True,
            check=False,
        )
    except FileNotFoundError as error:
        return Result(
            returncode=127,
            stdout="",
            stderr=f"Command not found: {error.filename}",
        )

    stderr = process.stderr.strip()

    if sudo and not sudo_prompt and process.returncode != 0:
        sudo_messages = (
            "a password is required",
            "no password was provided",
            "a terminal is required",
        )
        if any(message in stderr.lower() for message in sudo_messages):
            stderr = "Administrator access required."

    return Result(
        returncode=process.returncode,
        stdout=process.stdout.strip(),
        stderr=stderr,
    )


def have(command: str) -> bool:
    return shutil.which(command) is not None


def header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def confirm(prompt: str) -> bool:
    return input(f"{prompt} [y/N]: ").strip().lower() in {"y", "yes"}


def ensure_arch() -> None:
    if not Path("/etc/arch-release").exists():
        raise SystemExit("Sentinel Tools v0.1.1 currently supports Arch Linux only.")


def system_identity() -> dict[str, str]:
    return {
        "Hostname": platform.node(),
        "Kernel": platform.release(),
        "Architecture": platform.machine(),
    }
