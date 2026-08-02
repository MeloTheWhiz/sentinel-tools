from __future__ import annotations

import platform

from .base import Platform
from .linux import LinuxPlatform
from .windows import WindowsPlatform


def get_platform() -> Platform:
    system = platform.system()

    if system == "Linux":
        return LinuxPlatform()

    if system == "Windows":
        return WindowsPlatform()

    raise NotImplementedError(f"{system} is not supported yet.")
