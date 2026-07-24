from __future__ import annotations

import pytest

from sentinel_tools.checks import system
from sentinel_tools.platforms import LinuxPlatform, PlatformBackend, get_platform


class FakePlatform(PlatformBackend):
    """Small test backend used to verify collector delegation."""

    @property
    def name(self) -> str:
        return "Fake"

    def collect_system(self) -> dict[str, str]:
        return {"Platform": self.name}


def test_linux_platform_is_detected() -> None:
    backend = get_platform("Linux")

    assert isinstance(backend, LinuxPlatform)
    assert backend.name == "Linux"


def test_platform_detection_is_case_insensitive() -> None:
    backend = get_platform("lInUx")

    assert isinstance(backend, LinuxPlatform)


def test_unsupported_platform_raises_clear_error() -> None:
    with pytest.raises(NotImplementedError, match="Windows"):
        get_platform("Windows")


def test_system_collector_delegates_to_platform(monkeypatch) -> None:
    fake_platform = FakePlatform()

    monkeypatch.setattr(system, "get_platform", lambda: fake_platform)

    assert system.collect() == {"Platform": "Fake"}
