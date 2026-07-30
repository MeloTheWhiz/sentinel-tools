from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CPUInfo:
    model: str | None
    architecture: str | None
    logical_cores: int | None


@dataclass(slots=True)
class MemoryInfo:
    total_bytes: int | None
    available_bytes: int | None


@dataclass(slots=True)
class DiskInfo:
    device: str
    mountpoint: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
