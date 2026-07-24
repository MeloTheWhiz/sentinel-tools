from __future__ import annotations

import platform

from sentinel_tools.platforms.base import PlatformBackend
from sentinel_tools.platforms.linux import LinuxPlatform


def get_platform(system_name: str | None = None) -> PlatformBackend:
    """Return the backend for the current operating system."""
    detected_name = system_name or platform.system()
    normalized_name = detected_name.strip().lower()

    if normalized_name == "linux":
        return LinuxPlatform()

    raise NotImplementedError(
        f"Sentinel Tools does not yet support the {detected_name} platform."
    )
