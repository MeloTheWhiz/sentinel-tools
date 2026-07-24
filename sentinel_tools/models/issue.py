from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Severity(StrEnum):
    """Represent the importance of a diagnostic issue."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Issue:
    """Represent a structured diagnostic issue."""

    code: str
    severity: Severity
    message: str
    recommendation: str
    category: str = "system"
    title: str = ""
    explanation: str = ""
    repair_id: str | None = None

    @property
    def display_title(self) -> str:
        """Return a useful title for CLI and report displays."""
        return self.title or self.message
