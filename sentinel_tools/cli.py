from __future__ import annotations

import argparse
from pathlib import Path

from sentinel_tools import __version__
from sentinel_tools.checks import network, security, storage, system
from sentinel_tools.config.loader import load_config
from sentinel_tools.core import ensure_arch, header
from sentinel_tools.logging.setup import configure_logging
from sentinel_tools.maintenance import clean, update
from sentinel_tools.reporting import save_json, save_text
from sentinel_tools.scoring.health import calculate


def show(title: str, data: dict) -> None:
    header(title)
    for key, value in data.items():
        print(f"\n{key}:")
        print(value or "None")


def show_health_score(data: dict[str, str]) -> None:
    result = calculate(data)

    header("HEALTH SCORE")
    print(f"Score: {result.score}/100")
    print(f"Status: {result.status}")

    print("\nFindings:")
    if result.findings:
        for finding in result.findings:
            label = finding.severity.value.upper()
            print(f"[{label}] {finding.message}")
            print(f"  Recommendation: {finding.recommendation}")
    else:
        print("[OK] No health findings detected.")


def run_health_check() -> None:
    data = system.collect()
    show("SYSTEM HEALTH", data)
    show_health_score(data)


def menu() -> None:
    actions = {
        "1": ("Update system", update),
        "2": ("Clean system", clean),
        "3": ("System health", run_health_check),
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
    logger = configure_logging()
    config = load_config()

    logger.info("Sentinel Tools started")
    logger.info("Loaded configuration: %s", config)

    ensure_arch()
    parser = argparse.ArgumentParser(prog="sentinel-tools")
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")
    for command in (
        "menu",
        "health",
        "update",
        "clean",
        "security",
        "network",
        "storage",
    ):
        sub.add_parser(command)

    report_parser = sub.add_parser("report")
    report_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
    )
    report_parser.add_argument(
        "--output",
        type=Path,
    )

    args = parser.parse_args()
    command = args.command or "menu"

    if command == "menu":
        menu()
    elif command == "health":
        health_data = system.collect()
        show("SYSTEM HEALTH", health_data)
        show_health_score(health_data)
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
        if args.output:
            output = args.output.expanduser()
        elif args.format == "json":
            output = Path.home() / "sentinel-tools-report.json"
        else:
            output = Path.home() / "sentinel-tools-report.txt"

        output.parent.mkdir(parents=True, exist_ok=True)

        if args.format == "json":
            print(save_json(output))
        else:
            print(save_text(output))


if __name__ == "__main__":
    main()
