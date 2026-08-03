from __future__ import annotations

import platform

from .base import Platform
from .linux import LinuxPlatform
from .macos import MacOSPlatform
from .windows import WindowsPlatform
from .freebsd import FreeBSDPlatform


def get_platform() -> Platform:
    system = platform.system()

    if system == "Linux":
        return LinuxPlatform()

    if system == "Windows":
        return WindowsPlatform()

    if system == "Darwin":
        return MacOSPlatform()

    if system == "FreeBSD":
        return FreeBSDPlatform()

    raise NotImplementedError(f"{system} is not supported yet.")
