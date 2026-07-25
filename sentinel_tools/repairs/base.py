from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RepairRisk(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class RepairDefinition:
    repair_id: str
    title: str
    description: str
    supported_platforms: tuple[str, ...]
    requires_root: bool
    risk: RepairRisk
    steps: tuple[str, ...]
    commands: tuple[tuple[str, ...], ...]
