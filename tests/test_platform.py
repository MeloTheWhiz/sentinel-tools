from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from sentinel_tools.models import CPUInfo, DiskInfo, MemoryInfo, SystemInfo
from sentinel_tools.platform.base import Platform
from sentinel_tools.platform.detect import get_platform
from sentinel_tools.platform.freebsd import (
    FreeBSDPlatform,
)
from sentinel_tools.platform.freebsd import (
    _read_cpu_model as _read_freebsd_cpu_model,
)
from sentinel_tools.platform.freebsd import (
    _read_disks as _read_freebsd_disks,
)
from sentinel_tools.platform.freebsd import (
    _read_memory_info as _read_freebsd_memory_info,
)
from sentinel_tools.platform.linux import (
    LinuxPlatform,
    _read_cpu_model,
    _read_disks,
    _read_dmi_value,
    _read_memory_info,
    _read_storage_devices,
)
from sentinel_tools.platform.macos import (
    MacOSPlatform,
)
from sentinel_tools.platform.macos import (
    _read_cpu_model as _read_macos_cpu_model,
)
from sentinel_tools.platform.macos import (
    _read_disks as _read_macos_disks,
)
from sentinel_tools.platform.macos import (
    _read_memory_info as _read_macos_memory_info,
)
from sentinel_tools.platform.windows import WindowsPlatform


def test_linux_platform_implements_base_interface() -> None:
    platform_instance = LinuxPlatform()

    assert isinstance(platform_instance, Platform)
    assert platform_instance.name == "Linux"


def test_linux_cpu_returns_expected_fields() -> None:
    cpu_info = LinuxPlatform().cpu()

    assert cpu_info.architecture is not None
    assert cpu_info.model is not None
    assert cpu_info.logical_cores is not None


@patch("sentinel_tools.platform.detect.platform.system", return_value="Linux")
def test_get_platform_returns_linux_platform(mock_system) -> None:
    platform_instance = get_platform()

    assert isinstance(platform_instance, LinuxPlatform)
    mock_system.assert_called_once_with()


@patch("sentinel_tools.platform.detect.platform.system", return_value="UnsupportedOS")
def test_get_platform_rejects_unsupported_system(mock_system) -> None:
    with pytest.raises(
        NotImplementedError,
        match="UnsupportedOS is not supported yet",
    ):
        get_platform()

    mock_system.assert_called_once_with()


def test_read_cpu_model_from_proc_cpuinfo(tmp_path: Path) -> None:
    cpuinfo = tmp_path / "cpuinfo"
    cpuinfo.write_text(
        "processor : 0\n"
        "vendor_id : AuthenticAMD\n"
        "model name : AMD Ryzen 5 PRO 2400GE\n",
        encoding="utf-8",
    )

    with patch("sentinel_tools.platform.linux.CPUINFO_PATH", cpuinfo):
        assert _read_cpu_model() == "AMD Ryzen 5 PRO 2400GE"


def test_read_cpu_model_returns_none_when_file_missing(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing-cpuinfo"

    with patch("sentinel_tools.platform.linux.CPUINFO_PATH", missing_file):
        assert _read_cpu_model() is None


def test_read_memory_info_from_proc_meminfo(tmp_path: Path) -> None:
    meminfo = tmp_path / "meminfo"
    meminfo.write_text(
        "MemTotal:        16384000 kB\n"
        "MemFree:          1024000 kB\n"
        "MemAvailable:     8192000 kB\n",
        encoding="utf-8",
    )

    with patch("sentinel_tools.platform.linux.MEMINFO_PATH", meminfo):
        memory_info = _read_memory_info()

    assert memory_info.total_bytes == 16384000 * 1024
    assert memory_info.available_bytes == 8192000 * 1024


def test_read_memory_info_returns_none_when_file_missing(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing-meminfo"

    with patch("sentinel_tools.platform.linux.MEMINFO_PATH", missing_file):
        memory_info = _read_memory_info()

    assert memory_info.total_bytes is None
    assert memory_info.available_bytes is None


def test_read_disks_from_proc_mounts(tmp_path: Path) -> None:
    mounts = tmp_path / "mounts"
    mounts.write_text(
        "/dev/sda2 / ext4 rw,relatime 0 0\n"
        "proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0\n"
        "/dev/sda1 /boot vfat rw,relatime 0 0\n",
        encoding="utf-8",
    )

    def fake_disk_usage(mountpoint: str) -> object:
        usage_by_mountpoint = {
            "/": shutil._ntuple_diskusage(
                total=1000,
                used=600,
                free=400,
            ),
            "/boot": shutil._ntuple_diskusage(
                total=500,
                used=100,
                free=400,
            ),
        }
        return usage_by_mountpoint[mountpoint]

    with (
        patch("sentinel_tools.platform.linux.MOUNTS_PATH", mounts),
        patch(
            "sentinel_tools.platform.linux.shutil.disk_usage",
            side_effect=fake_disk_usage,
        ),
    ):
        disks = _read_disks()

    assert len(disks) == 2
    assert disks[0].device == "/dev/sda2"
    assert disks[0].mountpoint == "/"
    assert disks[0].total_bytes == 1000
    assert disks[1].device == "/dev/sda1"
    assert disks[1].mountpoint == "/boot"


def test_read_disks_returns_empty_when_mounts_file_missing(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing-mounts"

    with patch("sentinel_tools.platform.linux.MOUNTS_PATH", missing_file):
        assert _read_disks() == []


def test_read_storage_devices_discovers_physical_drives() -> None:
    completed = subprocess.CompletedProcess(
        args=["lsblk"],
        returncode=0,
        stdout=(
            "/dev/zram0 disk\n"
            "/dev/sda disk\n"
            "/dev/sda1 part\n"
            "/dev/nvme0n1 disk\n"
            "/dev/nvme0n1p1 part\n"
            "/dev/mmcblk0 disk\n"
        ),
        stderr="",
    )

    with (
        patch(
            "sentinel_tools.platform.linux.shutil.which",
            return_value="/usr/bin/lsblk",
        ),
        patch(
            "sentinel_tools.platform.linux.subprocess.run",
            return_value=completed,
        ),
    ):
        devices = _read_storage_devices()

    assert devices == [
        "/dev/sda",
        "/dev/nvme0n1",
        "/dev/mmcblk0",
    ]


def test_read_storage_devices_returns_empty_without_lsblk() -> None:
    with patch(
        "sentinel_tools.platform.linux.shutil.which",
        return_value=None,
    ):
        assert _read_storage_devices() == []


def test_read_storage_devices_returns_empty_when_lsblk_fails() -> None:
    completed = subprocess.CompletedProcess(
        args=["lsblk"],
        returncode=1,
        stdout="",
        stderr="lsblk failed",
    )

    with (
        patch(
            "sentinel_tools.platform.linux.shutil.which",
            return_value="/usr/bin/lsblk",
        ),
        patch(
            "sentinel_tools.platform.linux.subprocess.run",
            return_value=completed,
        ),
    ):
        assert _read_storage_devices() == []


def test_system_info_aggregates_platform_data(monkeypatch) -> None:
    platform_instance = LinuxPlatform()

    cpu = CPUInfo(
        model="Test CPU",
        architecture="x86_64",
        logical_cores=8,
    )
    memory = MemoryInfo(
        total_bytes=16 * 1024**3,
        available_bytes=8 * 1024**3,
    )
    disks = [
        DiskInfo(
            device="/dev/test",
            mountpoint="/",
            total_bytes=1000,
            used_bytes=400,
            free_bytes=600,
        )
    ]

    monkeypatch.setattr(platform_instance, "cpu", lambda: cpu)
    monkeypatch.setattr(platform_instance, "memory", lambda: memory)
    monkeypatch.setattr(platform_instance, "disks", lambda: disks)

    result = platform_instance.system_info()

    assert isinstance(result, SystemInfo)
    assert result.operating_system == "Linux"
    assert result.cpu == cpu
    assert result.memory == memory
    assert result.disks == disks


@patch(
    "sentinel_tools.platform.detect.platform.system",
    return_value="Windows",
)
def test_get_platform_returns_windows_platform(mock_system) -> None:
    platform_instance = get_platform()

    assert isinstance(platform_instance, WindowsPlatform)
    mock_system.assert_called_once_with()


def test_windows_platform_implements_base_interface() -> None:
    platform_instance = WindowsPlatform()

    assert isinstance(platform_instance, Platform)
    assert platform_instance.name == "Windows"


def test_windows_cpu_returns_shared_model() -> None:
    with (
        patch(
            "sentinel_tools.platform.windows.platform.processor",
            return_value="Test Windows CPU",
        ),
        patch(
            "sentinel_tools.platform.windows.platform.machine",
            return_value="AMD64",
        ),
        patch(
            "sentinel_tools.platform.windows.os.cpu_count",
            return_value=8,
        ),
    ):
        cpu_info = WindowsPlatform().cpu()

    assert cpu_info.model == "Test Windows CPU"
    assert cpu_info.architecture == "AMD64"
    assert cpu_info.logical_cores == 8


def test_windows_disks_detect_drive_letters() -> None:
    def fake_exists(path: str) -> bool:
        return path in {"C:\\", "D:\\"}

    def fake_disk_usage(path: str) -> object:
        usage_by_path = {
            "C:\\": shutil._ntuple_diskusage(
                total=1000,
                used=600,
                free=400,
            ),
            "D:\\": shutil._ntuple_diskusage(
                total=2000,
                used=500,
                free=1500,
            ),
        }
        return usage_by_path[path]

    with (
        patch(
            "sentinel_tools.platform.windows.os.path.exists",
            side_effect=fake_exists,
        ),
        patch(
            "sentinel_tools.platform.windows.shutil.disk_usage",
            side_effect=fake_disk_usage,
        ),
    ):
        disks = WindowsPlatform().disks()

    assert len(disks) == 2

    assert disks[0].device == "C:\\"
    assert disks[0].mountpoint == "C:\\"
    assert disks[0].total_bytes == 1000

    assert disks[1].device == "D:\\"
    assert disks[1].mountpoint == "D:\\"
    assert disks[1].total_bytes == 2000


def test_windows_memory_returns_unknown_off_windows() -> None:
    memory_info = WindowsPlatform().memory()

    assert memory_info.total_bytes is None
    assert memory_info.available_bytes is None


@patch(
    "sentinel_tools.platform.detect.platform.system",
    return_value="Darwin",
)
def test_get_platform_returns_macos_platform(mock_system) -> None:
    platform_instance = get_platform()

    assert isinstance(platform_instance, MacOSPlatform)
    mock_system.assert_called_once_with()


def test_macos_platform_implements_base_interface() -> None:
    platform_instance = MacOSPlatform()

    assert isinstance(platform_instance, Platform)
    assert platform_instance.name == "macOS"


def test_macos_cpu_uses_sysctl_model() -> None:
    with (
        patch(
            "sentinel_tools.platform.macos._run_sysctl",
            side_effect=lambda name: {
                "machdep.cpu.brand_string": "Apple M2",
                "hw.model": "Mac14,5",
            }.get(name),
        ),
        patch(
            "sentinel_tools.platform.macos.platform.machine",
            return_value="arm64",
        ),
        patch(
            "sentinel_tools.platform.macos.os.cpu_count",
            return_value=8,
        ),
    ):
        cpu_info = MacOSPlatform().cpu()

    assert cpu_info.model == "Apple M2"
    assert cpu_info.architecture == "arm64"
    assert cpu_info.logical_cores == 8


def test_macos_memory_reads_total_bytes() -> None:
    with patch(
        "sentinel_tools.platform.macos._run_sysctl",
        return_value=str(16 * 1024**3),
    ):
        memory_info = _read_macos_memory_info()

    assert memory_info.total_bytes == 16 * 1024**3
    assert memory_info.available_bytes is None


def test_macos_memory_returns_unknown_for_invalid_value() -> None:
    with patch(
        "sentinel_tools.platform.macos._run_sysctl",
        return_value="invalid",
    ):
        memory_info = _read_macos_memory_info()

    assert memory_info.total_bytes is None
    assert memory_info.available_bytes is None


def test_macos_cpu_falls_back_to_hw_model() -> None:
    with patch(
        "sentinel_tools.platform.macos._run_sysctl",
        side_effect=lambda name: "MacBookAir7,1" if name == "hw.model" else None,
    ):
        assert _read_macos_cpu_model() == "MacBookAir7,1"


def test_macos_disks_include_root_and_volumes(tmp_path: Path) -> None:
    volumes = tmp_path / "Volumes"
    external = volumes / "External"
    volumes.mkdir()
    external.mkdir()

    def fake_disk_usage(mountpoint: str) -> object:
        usage_by_mountpoint = {
            "/": shutil._ntuple_diskusage(
                total=1000,
                used=400,
                free=600,
            ),
            str(external): shutil._ntuple_diskusage(
                total=2000,
                used=500,
                free=1500,
            ),
        }
        return usage_by_mountpoint[mountpoint]

    with (
        patch(
            "sentinel_tools.platform.macos.VOLUMES_PATH",
            volumes,
        ),
        patch(
            "sentinel_tools.platform.macos.shutil.disk_usage",
            side_effect=fake_disk_usage,
        ),
    ):
        disks = _read_macos_disks()

    assert len(disks) == 2
    assert disks[0].mountpoint == "/"
    assert disks[1].mountpoint == str(external)


@patch(
    "sentinel_tools.platform.detect.platform.system",
    return_value="FreeBSD",
)
def test_get_platform_returns_freebsd_platform(mock_system) -> None:
    platform_instance = get_platform()

    assert isinstance(platform_instance, FreeBSDPlatform)
    mock_system.assert_called_once_with()


def test_freebsd_platform_implements_base_interface() -> None:
    platform_instance = FreeBSDPlatform()

    assert isinstance(platform_instance, Platform)
    assert platform_instance.name == "FreeBSD"


def test_freebsd_cpu_uses_sysctl_model() -> None:
    with (
        patch(
            "sentinel_tools.platform.freebsd._run_sysctl",
            return_value="AMD Ryzen 7 5700G",
        ),
        patch(
            "sentinel_tools.platform.freebsd.platform.machine",
            return_value="amd64",
        ),
        patch(
            "sentinel_tools.platform.freebsd.os.cpu_count",
            return_value=16,
        ),
    ):
        cpu_info = FreeBSDPlatform().cpu()

    assert cpu_info.model == "AMD Ryzen 7 5700G"
    assert cpu_info.architecture == "amd64"
    assert cpu_info.logical_cores == 16


def test_freebsd_memory_reads_total_bytes() -> None:
    with patch(
        "sentinel_tools.platform.freebsd._run_sysctl",
        return_value=str(32 * 1024**3),
    ):
        memory_info = _read_freebsd_memory_info()

    assert memory_info.total_bytes == 32 * 1024**3
    assert memory_info.available_bytes is None


def test_freebsd_memory_returns_unknown_for_invalid_value() -> None:
    with patch(
        "sentinel_tools.platform.freebsd._run_sysctl",
        return_value="invalid",
    ):
        memory_info = _read_freebsd_memory_info()

    assert memory_info.total_bytes is None
    assert memory_info.available_bytes is None


def test_freebsd_cpu_falls_back_to_platform_processor() -> None:
    with (
        patch(
            "sentinel_tools.platform.freebsd._run_sysctl",
            return_value=None,
        ),
        patch(
            "sentinel_tools.platform.freebsd.platform.processor",
            return_value="Fallback CPU",
        ),
    ):
        assert _read_freebsd_cpu_model() == "Fallback CPU"


def test_freebsd_disks_parse_df_output() -> None:
    completed = subprocess.CompletedProcess(
        args=["df", "-kP"],
        returncode=0,
        stdout=(
            "Filesystem 1024-blocks Used Available Capacity Mounted on\n"
            "/dev/ada0p2 1000000 400000 600000 40% /\n"
            "tmpfs 100000 1000 99000 1% /tmp\n"
            "/dev/ada0p1 500000 100000 400000 20% /boot\n"
        ),
        stderr="",
    )

    def fake_disk_usage(mountpoint: str) -> object:
        usage_by_mountpoint = {
            "/": shutil._ntuple_diskusage(
                total=1000,
                used=400,
                free=600,
            ),
            "/boot": shutil._ntuple_diskusage(
                total=500,
                used=100,
                free=400,
            ),
        }
        return usage_by_mountpoint[mountpoint]

    with (
        patch(
            "sentinel_tools.platform.freebsd.subprocess.run",
            return_value=completed,
        ),
        patch(
            "sentinel_tools.platform.freebsd.shutil.disk_usage",
            side_effect=fake_disk_usage,
        ),
    ):
        disks = _read_freebsd_disks()

    assert len(disks) == 2
    assert disks[0].device == "/dev/ada0p2"
    assert disks[0].mountpoint == "/"
    assert disks[1].device == "/dev/ada0p1"
    assert disks[1].mountpoint == "/boot"


def test_freebsd_disks_return_empty_when_df_fails() -> None:
    completed = subprocess.CompletedProcess(
        args=["df", "-kP"],
        returncode=1,
        stdout="",
        stderr="df failed",
    )

    with patch(
        "sentinel_tools.platform.freebsd.subprocess.run",
        return_value=completed,
    ):
        assert _read_freebsd_disks() == []


def test_read_dmi_value_returns_trimmed_value(tmp_path: Path) -> None:
    dmi_path = tmp_path / "dmi"
    dmi_path.mkdir()

    vendor_file = dmi_path / "sys_vendor"
    vendor_file.write_text("Lenovo\n", encoding="utf-8")

    with patch("sentinel_tools.platform.linux.DMI_PATH", dmi_path):
        assert _read_dmi_value("sys_vendor") == "Lenovo"


def test_read_dmi_value_returns_none_when_missing(tmp_path: Path) -> None:
    dmi_path = tmp_path / "dmi"
    dmi_path.mkdir()

    with patch("sentinel_tools.platform.linux.DMI_PATH", dmi_path):
        assert _read_dmi_value("product_name") is None


def test_linux_inventory_reads_dmi_metadata(tmp_path: Path) -> None:
    dmi_path = tmp_path / "dmi"
    dmi_path.mkdir()

    values = {
        "sys_vendor": "Lenovo",
        "product_name": "ThinkCentre M715q",
        "bios_vendor": "LENOVO",
        "bios_version": "M11KT39A",
    }

    for filename, value in values.items():
        (dmi_path / filename).write_text(value, encoding="utf-8")

    with patch("sentinel_tools.platform.linux.DMI_PATH", dmi_path):
        platform_instance = LinuxPlatform()

        assert platform_instance.computer_vendor() == "Lenovo"
        assert platform_instance.computer_model() == "ThinkCentre M715q"
        assert platform_instance.bios_vendor() == "LENOVO"
        assert platform_instance.bios_version() == "M11KT39A"
