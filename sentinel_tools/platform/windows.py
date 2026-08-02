from __future__ import annotations

import ctypes
import os
import platform
import shutil
import string
from ctypes import wintypes

from sentinel_tools.models import CPUInfo, DiskInfo, MemoryInfo

from .base import Platform


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", wintypes.DWORD),
        ("dwMemoryLoad", wintypes.DWORD),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def _read_memory_info() -> MemoryInfo:
    try:
        kernel32 = ctypes.WinDLL(
            "kernel32",
            use_last_error=True,
        )
    except (AttributeError, OSError):
        return MemoryInfo(
            total_bytes=None,
            available_bytes=None,
        )

    status = MEMORYSTATUSEX()
    status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)

    global_memory_status = kernel32.GlobalMemoryStatusEx
    global_memory_status.argtypes = [ctypes.POINTER(MEMORYSTATUSEX)]
    global_memory_status.restype = wintypes.BOOL

    if not global_memory_status(ctypes.byref(status)):
        return MemoryInfo(
            total_bytes=None,
            available_bytes=None,
        )

    return MemoryInfo(
        total_bytes=status.ullTotalPhys,
        available_bytes=status.ullAvailPhys,
    )


def _read_disks() -> list[DiskInfo]:
    disks: list[DiskInfo] = []

    for letter in string.ascii_uppercase:
        root = f"{letter}:\\"

        if not os.path.exists(root):
            continue

        try:
            usage = shutil.disk_usage(root)
        except OSError:
            continue

        disks.append(
            DiskInfo(
                device=root,
                mountpoint=root,
                total_bytes=usage.total,
                used_bytes=usage.used,
                free_bytes=usage.free,
            )
        )

    return disks


class WindowsPlatform(Platform):
    @property
    def name(self) -> str:
        return "Windows"

    def cpu(self) -> CPUInfo:
        processor = (
            platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER") or None
        )

        return CPUInfo(
            model=processor,
            architecture=platform.machine() or None,
            logical_cores=os.cpu_count(),
        )

    def memory(self) -> MemoryInfo:
        return _read_memory_info()

    def disks(self) -> list[DiskInfo]:
        return _read_disks()

    def storage_devices(self) -> list[str]:
        # Physical-drive discovery will be implemented separately.
        return []

    def network(self) -> dict:
        return {}

    def battery(self) -> dict | None:
        return None
