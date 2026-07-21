from __future__ import annotations

import os
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


def run(command: Iterable[str], *, sudo: bool = False) -> Result:
    cmd = list(command)
    if sudo:
        cmd = ["sudo", *cmd]
    process = subprocess.run(cmd, text=True, capture_output=True, check=False)
    return Result(process.returncode, process.stdout.strip(), process.stderr.strip())


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
