from __future__ import annotations

from sentinel_tools.repairs import (
    available_repairs,
    repair_definition,
)
from sentinel_tools.ui.console import key_value, section


def list_repairs() -> None:
    section("Available Repairs")

    for repair in available_repairs():
        print(f"• {repair.repair_id}")
        print(f"  {repair.title}")
        print()


def show_repair_info(repair_id: str) -> None:
    repair = repair_definition(repair_id)

    section(repair.title)

    key_value("Repair ID", repair.repair_id)
    key_value("Requires Root", "Yes" if repair.requires_root else "No")
    key_value("Risk", repair.risk.value.title())
    key_value(
        "Platforms",
        ", ".join(repair.supported_platforms),
    )

    print()
    print(repair.description)
    print()
    print("Steps:")

    for step in repair.steps:
        print(f"  • {step}")
