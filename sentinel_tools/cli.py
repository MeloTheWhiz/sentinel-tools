from __future__ import annotations

import argparse
from pathlib import Path

from sentinel_tools import __version__
from sentinel_tools.checks import network, security, storage, system
from sentinel_tools.core import ensure_arch, header
from sentinel_tools.maintenance import clean, update
from sentinel_tools.reporting import save_text


def show(title: str, data: dict) -> None:
    header(title)
    for key, value in data.items():
        print(f"\n{key}:")
        print(value or "None")


def menu() -> None:
    actions = {
        "1": ("Update system", update),
        "2": ("Clean system", clean),
        "3": ("System health", lambda: show("SYSTEM HEALTH", system.collect())),
        "4": ("Security audit", lambda: show("SECURITY AUDIT", security.collect())),
        "5": ("Network diagnostics", lambda: show("NETWORK DIAGNOSTICS", network.collect())),
        "6": ("Storage diagnostics", lambda: show("STORAGE DIAGNOSTICS", storage.collect())),
        "7": ("Save report", lambda: print(save_text(Path.home() / "sentinel-tools-report.txt"))),
    }

    while True:
        header(f"SENTINEL TOOLS v{__version__}")
        for key, (label, _) in actions.items():
            print(f"[{key}] {label}")
        print("[0] Exit")
        choice = input("\nChoose an option: ").strip()
        if choice == "0":
            return
        action = actions.get(choice)
        if action:
            action[1]()
            input("\nPress Enter to continue...")
        else:
            print("Invalid selection.")


def main() -> None:
    ensure_arch()
    parser = argparse.ArgumentParser(prog="sentinel-tools")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")
    for command in ("menu", "health", "update", "clean", "security", "network", "storage", "report"):
        sub.add_parser(command)

    args = parser.parse_args()
    command = args.command or "menu"

    if command == "menu":
        menu()
    elif command == "health":
        show("SYSTEM HEALTH", system.collect())
    elif command == "update":
        raise SystemExit(update())
    elif command == "clean":
        raise SystemExit(clean())
    elif command == "security":
        show("SECURITY AUDIT", security.collect())
    elif command == "network":
        show("NETWORK DIAGNOSTICS", network.collect())
    elif command == "storage":
        show("STORAGE DIAGNOSTICS", storage.collect())
    elif command == "report":
        print(save_text(Path.home() / "sentinel-tools-report.txt"))


if __name__ == "__main__":
    main()
