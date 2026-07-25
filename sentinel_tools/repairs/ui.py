from __future__ import annotations

import shlex

from sentinel_tools.repairs import available_repairs, repair_definition
from sentinel_tools.ui.console import key_value, section, status


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
    key_value("Platforms", ", ".join(repair.supported_platforms))

    print()
    print(repair.description)
    print()
    print("Steps:")

    for step in repair.steps:
        print(f"  • {step}")


def show_repair_dry_run(repair_id: str) -> None:
    repair = repair_definition(repair_id)

    section(f"Dry Run: {repair.title}")
    status("INFO", "No commands will be executed.")

    key_value("Repair ID", repair.repair_id)
    key_value("Requires Root", "Yes" if repair.requires_root else "No")
    key_value("Risk", repair.risk.value.title())

    print()
    print("Planned commands:")

    for command in repair.commands:
        print(f"  $ {shlex.join(command)}")
