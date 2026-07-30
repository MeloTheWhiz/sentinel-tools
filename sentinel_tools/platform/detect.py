from __future__ import annotations

import platform

from .linux import LinuxPlatform


def get_platform():
    system = platform.system()

    if system == "Linux":
        return LinuxPlatform()

    raise NotImplementedError(f"{system} is not supported yet.")
