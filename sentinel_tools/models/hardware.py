from __future__ import annotations

from dataclasses import dataclass

from .system import CPUInfo, DiskInfo, MemoryInfo


@dataclass(slots=True)
class HardwareInventory:
    computer_vendor: str | None
    computer_model: str | None
    bios_vendor: str | None
    bios_version: str | None
    cpu: CPUInfo
    memory: MemoryInfo
    disks: list[DiskInfo]
