from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path


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


def operating_system_name() -> str:
    os_release = Path("/etc/os-release")

    if os_release.exists():
        values: dict[str, str] = {}

        for line in os_release.read_text(encoding="utf-8").splitlines():
            if "=" not in line:
                continue

            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')

        return values.get("PRETTY_NAME") or values.get("NAME") or platform.system()

    return platform.system()


def desktop_environment() -> str:
    return (
        os.environ.get("XDG_CURRENT_DESKTOP")
        or os.environ.get("DESKTOP_SESSION")
        or os.environ.get("XDG_SESSION_DESKTOP")
        or "Unknown"
    )


def cpu_model() -> str:
    cpuinfo = Path("/proc/cpuinfo")

    if cpuinfo.exists():
        for line in cpuinfo.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.lower().startswith("model name"):
                _, value = line.split(":", 1)
                return value.strip()

    processor = platform.processor().strip()
    return processor or "Unknown"


def total_memory() -> str:
    meminfo = Path("/proc/meminfo")

    if meminfo.exists():
        for line in meminfo.read_text(encoding="utf-8").splitlines():
            if line.startswith("MemTotal:"):
                kibibytes = int(line.split()[1])
                gibibytes = kibibytes / 1024 / 1024
                return f"{gibibytes:.1f} GiB"

    return "Unknown"


def system_identity() -> dict[str, str]:
    return {
        "Hostname": platform.node(),
        "Operating System": operating_system_name(),
        "Kernel": platform.release(),
        "Architecture": platform.machine(),
        "Desktop": desktop_environment(),
        "CPU": cpu_model(),
        "Memory": total_memory(),
        "Python": platform.python_version(),
        "Python executable": sys.executable,
    }
