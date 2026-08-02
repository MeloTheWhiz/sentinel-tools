from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path

from sentinel_tools.models import CPUInfo, DiskInfo, MemoryInfo

from .base import Platform


VOLUMES_PATH = Path("/Volumes")


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
    return (
        _run_sysctl("machdep.cpu.brand_string")
        or _run_sysctl("hw.model")
        or platform.processor()
        or None
    )


def _read_memory_info() -> MemoryInfo:
    raw_total = _run_sysctl("hw.memsize")

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
    mountpoints = [Path("/")]

    try:
        mountpoints.extend(path for path in VOLUMES_PATH.iterdir() if path.is_dir())
    except OSError:
        pass

    disks: list[DiskInfo] = []
    seen_mountpoints: set[str] = set()

    for mountpoint_path in mountpoints:
        mountpoint = str(mountpoint_path)

        if mountpoint in seen_mountpoints:
            continue

        try:
            usage = shutil.disk_usage(mountpoint)
        except OSError:
            continue

        seen_mountpoints.add(mountpoint)
        disks.append(
            DiskInfo(
                device=mountpoint,
                mountpoint=mountpoint,
                total_bytes=usage.total,
                used_bytes=usage.used,
                free_bytes=usage.free,
            )
        )

    return disks


class MacOSPlatform(Platform):
    @property
    def name(self) -> str:
        return "macOS"

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
        # Physical-device discovery will be implemented separately.
        return []

    def network(self) -> dict:
        return {}

    def battery(self) -> dict | None:
        return None
