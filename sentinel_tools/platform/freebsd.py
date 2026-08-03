from __future__ import annotations

import os
import platform
import shutil
import subprocess

from sentinel_tools.models import CPUInfo, DiskInfo, MemoryInfo

from .base import Platform


def _run_sysctl(name: str) -> str | None:
    if shutil.which("sysctl") is None:
        return None

    try:
        result = subprocess.run(
            ["sysctl", "-n", name],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return None

    if result.returncode != 0:
        return None

    value = result.stdout.strip()
    return value or None


def _read_cpu_model() -> str | None:
    return _run_sysctl("hw.model") or platform.processor() or None


def _read_memory_info() -> MemoryInfo:
    raw_total = _run_sysctl("hw.physmem")

    if raw_total is None:
        return MemoryInfo(
            total_bytes=None,
            available_bytes=None,
        )

    try:
        total_bytes = int(raw_total)
    except ValueError:
        total_bytes = None

    return MemoryInfo(
        total_bytes=total_bytes,
        available_bytes=None,
    )


def _read_disks() -> list[DiskInfo]:
    try:
        result = subprocess.run(
            ["df", "-kP"],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return []

    if result.returncode != 0:
        return []

    disks: list[DiskInfo] = []
    seen_mountpoints: set[str] = set()

    for line in result.stdout.splitlines()[1:]:
        parts = line.split()

        if len(parts) < 6:
            continue

        device = parts[0]
        mountpoint = parts[-1]

        if not device.startswith("/dev/"):
            continue

        if mountpoint in seen_mountpoints:
            continue

        try:
            usage = shutil.disk_usage(mountpoint)
        except OSError:
            continue

        seen_mountpoints.add(mountpoint)
        disks.append(
            DiskInfo(
                device=device,
                mountpoint=mountpoint,
                total_bytes=usage.total,
                used_bytes=usage.used,
                free_bytes=usage.free,
            )
        )

    return disks


class FreeBSDPlatform(Platform):
    @property
    def name(self) -> str:
        return "FreeBSD"

    def cpu(self) -> CPUInfo:
        return CPUInfo(
            model=_read_cpu_model(),
            architecture=platform.machine() or None,
            logical_cores=os.cpu_count(),
        )

    def memory(self) -> MemoryInfo:
        return _read_memory_info()

    def disks(self) -> list[DiskInfo]:
        return _read_disks()

    def storage_devices(self) -> list[str]:
        # Physical-device discovery will be added separately.
        return []

    def network(self) -> dict:
        return {}

    def battery(self) -> dict | None:
        return None
