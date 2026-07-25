from __future__ import annotations

from sentinel_tools.repairs.base import RepairDefinition, RepairRisk

REPAIRS: dict[str, RepairDefinition] = {
    "enable-networkmanager": RepairDefinition(
        repair_id="enable-networkmanager",
        title="Enable NetworkManager",
        description=(
            "Enable and start NetworkManager, then verify that the service "
            "entered an active state."
        ),
        supported_platforms=("linux",),
        requires_root=True,
        risk=RepairRisk.LOW,
        steps=(
            "Check whether NetworkManager is installed.",
            "Enable NetworkManager at boot.",
            "Start NetworkManager immediately.",
            "Verify that NetworkManager is active.",
        ),
    ),
}


def repair_definition(repair_id: str) -> RepairDefinition:
    return REPAIRS[repair_id]


def available_repairs() -> tuple[RepairDefinition, ...]:
    return tuple(REPAIRS.values())
