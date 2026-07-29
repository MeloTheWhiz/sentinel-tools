from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ForeignPackage:
    """A package not currently available from enabled official repositories."""

    name: str
    version: str


@dataclass(frozen=True)
class AurAuditResult:
    """Read-only summary of the system's foreign and AUR packages."""

    foreign_packages: tuple[ForeignPackage, ...]
    available_updates: tuple[str, ...]
    warnings: tuple[str, ...]


def _run_command(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    """Run a read-only system command without invoking a shell."""

    return subprocess.run(
        list(command),
        check=False,
        capture_output=True,
        text=True,
    )


def parse_foreign_packages(output: str) -> tuple[ForeignPackage, ...]:
    """Parse output produced by `pacman -Qm`."""

    packages: list[ForeignPackage] = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            continue

        packages.append(
            ForeignPackage(
                name=parts[0],
                version=parts[1],
            )
        )

    return tuple(packages)


def parse_aur_updates(output: str) -> tuple[str, ...]:
    """Parse package names from output produced by `yay -Qua`."""

    updates: list[str] = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        package_name = line.split(maxsplit=1)[0]
        updates.append(package_name)

    return tuple(updates)


def get_foreign_packages() -> tuple[ForeignPackage, ...]:
    """Return packages not supplied by enabled official repositories."""

    result = _run_command(("pacman", "-Qm"))

    if result.returncode != 0:
        message = result.stderr.strip() or "pacman -Qm failed"
        raise RuntimeError(message)

    return parse_foreign_packages(result.stdout)


def get_available_aur_updates() -> tuple[str, ...]:
    """Return available AUR updates without installing anything."""

    if shutil.which("yay") is None:
        return ()

    result = _run_command(("yay", "-Qua"))

    # yay may return 1 when there are no updates, depending on version/config.
    if result.returncode not in (0, 1):
        message = result.stderr.strip() or "yay -Qua failed"
        raise RuntimeError(message)

    return parse_aur_updates(result.stdout)


def audit_aur() -> AurAuditResult:
    """Perform a non-destructive audit of installed foreign packages."""

    foreign_packages = get_foreign_packages()
    available_updates = get_available_aur_updates()

    warnings: list[str] = []

    foreign_names = {package.name for package in foreign_packages}

    if not foreign_packages:
        warnings.append("No foreign packages are installed.")

    if "yay-debug" in foreign_names:
        warnings.append(
            "yay-debug is installed. Debug symbol packages are usually "
            "unnecessary unless you are actively debugging yay."
        )

    for package in foreign_packages:
        if package.name.endswith("-bin"):
            warnings.append(
                f"{package.name} is a binary AUR package. Its upstream "
                "binary should be reviewed because it is not compiled "
                "locally from source."
            )

    return AurAuditResult(
        foreign_packages=foreign_packages,
        available_updates=available_updates,
        warnings=tuple(warnings),
    )


def show_aur_audit() -> int:
    """Print a terminal-friendly AUR audit report."""

    try:
        result = audit_aur()
    except RuntimeError as error:
        print(f"[ERROR] AUR audit failed: {error}")
        return 1

    print()
    print("========================================")
    print("       SENTINEL AUR AUDIT")
    print("========================================")
    print()
    print("Mode: read-only")
    print("No packages will be built, installed, or removed.")

    print()
    print("Foreign packages:")

    if result.foreign_packages:
        for package in result.foreign_packages:
            print(f"  - {package.name} {package.version}")
    else:
        print("  None")

    print()
    print("Available AUR updates:")

    if result.available_updates:
        for package_name in result.available_updates:
            print(f"  - {package_name}")
    else:
        print("  None")

    print()
    print("Warnings:")

    if result.warnings:
        for warning in result.warnings:
            print(f"  [WARNING] {warning}")
    else:
        print("  None")

    print()
    print("========================================")
    print("       AUR audit complete")
    print("========================================")
    print()

    return 0
