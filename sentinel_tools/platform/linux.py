from __future__ import annotations

import os
import platform
import shutil
from pathlib import Path

from sentinel_tools.models import CPUInfo, DiskInfo, MemoryInfo

from .base import Platform


CPUINFO_PATH = Path("/proc/cpuinfo")
MEMINFO_PATH = Path("/proc/meminfo")
MOUNTS_PATH = Path("/proc/mounts")


def _read_cpu_model() -> str | None:
    try:
        cpuinfo = CPUINFO_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None

    for line in cpuinfo.splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() in {"model name", "Hardware", "Processor"}:
            model = value.strip()
            if model:
                return model


def _read_memory_info() -> MemoryInfo:
    try:
        meminfo = MEMINFO_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return MemoryInfo(
            total_bytes=None,
            available_bytes=None,
        )

    values: dict[str, int] = {}

    for line in meminfo.splitlines():
        key, separator, raw_value = line.partition(":")
        if not separator:
            continue

        parts = raw_value.strip().split()
        if not parts:
            continue

        try:
            value = int(parts[0])
        except ValueError:
            continue

        unit = parts[1].lower() if len(parts) > 1 else ""

        if unit == "kb":
            value *= 1024

        values[key.strip()] = value

    return MemoryInfo(
        total_bytes=values.get("MemTotal"),
        available_bytes=values.get("MemAvailable"),
    )


def _read_disks() -> list[DiskInfo]:
    try:
        mounts = MOUNTS_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return []

    ignored_filesystems = {
        "autofs",
        "binfmt_misc",
        "bpf",
        "cgroup",
        "cgroup2",
        "configfs",
        "debugfs",
        "devpts",
        "devtmpfs",
        "efivarfs",
        "fusectl",
        "hugetlbfs",
        "mqueue",
        "proc",
        "pstore",
        "rpc_pipefs",
        "securityfs",
        "sysfs",
        "tmpfs",
        "tracefs",
    }

    disks: list[DiskInfo] = []
    seen_devices: set[str] = set()

    for line in mounts.splitlines():
        parts = line.split()

        if len(parts) < 3:
            continue

        device, mountpoint, filesystem = parts[:3]

        if filesystem in ignored_filesystems:
            continue

        if not device.startswith("/dev/"):
            continue

        if device in seen_devices:
            continue

        try:
            usage = shutil.disk_usage(mountpoint)
        except OSError:
            continue

        seen_devices.add(device)
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


class LinuxPlatform(Platform):
    @property
    def name(self) -> str:
        return "Linux"

    def cpu(self) -> CPUInfo:
        return CPUInfo(
            model=_read_cpu_model() or platform.processor() or None,
            architecture=platform.machine() or None,
            logical_cores=os.cpu_count(),
        )

    def memory(self) -> MemoryInfo:
        return _read_memory_info()

    def disks(self) -> list[DiskInfo]:
        return _read_disks()

    def network(self) -> dict:
        return {}

    def battery(self) -> dict | None:
        return None
