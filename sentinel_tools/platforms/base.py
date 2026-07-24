from __future__ import annotations

from abc import ABC, abstractmethod


class PlatformBackend(ABC):
    """Define the interface implemented by operating-system backends."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the human-readable platform name."""

    @abstractmethod
    def collect_system(self) -> dict[str, str]:
        """Collect system health and identity information."""
