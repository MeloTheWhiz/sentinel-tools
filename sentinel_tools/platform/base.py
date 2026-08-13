from __future__ import annotations

from abc import ABC, abstractmethod

from sentinel_tools.models import (
    CPUInfo,
    DiskInfo,
    HardwareInventory,
    MemoryInfo,
    SystemInfo,
)


class Platform(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def cpu(self) -> CPUInfo: ...

    @abstractmethod
    def memory(self) -> MemoryInfo: ...

    @abstractmethod
    def disks(self) -> list[DiskInfo]: ...

    @abstractmethod
    def storage_devices(self) -> list[str]: ...

    def computer_vendor(self) -> str | None:
        return None

    def computer_model(self) -> str | None:
        return None

    def bios_vendor(self) -> str | None:
        return None

    def bios_version(self) -> str | None:
        return None

    def inventory(self) -> HardwareInventory:
        return HardwareInventory(
            computer_vendor=self.computer_vendor(),
            computer_model=self.computer_model(),
            bios_vendor=self.bios_vendor(),
            bios_version=self.bios_version(),
            cpu=self.cpu(),
            memory=self.memory(),
            disks=self.disks(),
        )

    def system_info(self) -> SystemInfo:
        return SystemInfo(
            operating_system=self.name,
            cpu=self.cpu(),
            memory=self.memory(),
            disks=self.disks(),
        )

    @abstractmethod
    def network(self) -> dict: ...

    @abstractmethod
    def battery(self) -> dict | None: ...
