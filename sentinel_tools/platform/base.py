from __future__ import annotations

from abc import ABC, abstractmethod

from sentinel_tools.models import CPUInfo, DiskInfo, MemoryInfo


class Platform(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def cpu(self) -> CPUInfo:
        ...

    @abstractmethod
    def memory(self) -> MemoryInfo:
        ...

    @abstractmethod
    def disks(self) -> list[DiskInfo]:
        ...

    @abstractmethod
    def network(self) -> dict:
        ...

    @abstractmethod
    def battery(self) -> dict | None:
        ...
