from __future__ import annotations

from unittest.mock import patch
from pathlib import Path

import pytest
import shutil
import subprocess

from sentinel_tools.platform.base import Platform
from sentinel_tools.platform.detect import get_platform
from sentinel_tools.platform.linux import (
    LinuxPlatform,
    _read_cpu_model,
    _read_memory_info,
    _read_disks,
    _read_storage_devices,
)


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
