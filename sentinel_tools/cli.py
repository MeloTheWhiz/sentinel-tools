from __future__ import annotations

import argparse
from pathlib import Path

from sentinel_tools import __version__
from sentinel_tools.aur import show_aur_audit
from sentinel_tools.engine import available_checks, run_check
from sentinel_tools.logging.setup import configure_logging
from sentinel_tools.reports.service import save_report
from sentinel_tools.scoring.health import calculate
from sentinel_tools.ui.console import (
    banner,
    command_hint,
    key_value,
    section,
    status,
)

DIAGNOSTIC_TITLES = {
    "security": "Security Audit",
    "network": "Network Diagnostics",
    "storage": "Storage Diagnostics",
}


def show(title: str, data: dict[str, str]) -> None:
    section(title)
    if not data:
        status("INFO", "No diagnostic data was returned.")
        return
    for key, value in data.items():
        key_value(key, value)


def show_health_score(data: dict[str, str]) -> None:
    result = calculate(data)
    section("Health Score")
    key_value("Score", f"{result.score}/100")
    key_value("Status", result.status)
    section("Health Findings")

    if not result.findings:
        status("OK", "No health findings detected.")
        return

    for finding in result.findings:
        severity = finding.severity.value.upper()
        status("ERROR" if severity == "CRITICAL" else severity, finding.message)
        print(f"  Code: {finding.code}")
        print(f"  Recommendation: {finding.recommendation}")


def run_health_check() -> None:
    data = run_check("system")
    show("System Health", data)
    show_health_score(data)


def run_diagnostic(command: str) -> None:
    show(DIAGNOSTIC_TITLES[command], run_check(command))


def show_available_checks() -> None:
    """Display all registered diagnostic checks."""
    section("Available Checks")

    commands = {
        "system": ("health", "System Health"),
        "network": ("network", "Network Diagnostics"),
        "storage": ("storage", "Storage Diagnostics"),
        "security": ("security", "Security Audit"),
    }

    for name in available_checks():
        command, title = commands.get(
            name,
            (name, name.replace("_", " ").title()),
        )
        command_hint(f"sentinel-tools {command}", title)


def menu() -> None:
    from sentinel_tools.maintenance import clean, update

    actions = {
        "1": ("Update system", update),
        "2": ("Clean system", clean),
        "3": ("System health", run_health_check),
        "4": ("Security audit", lambda: run_diagnostic("security")),
        "5": ("Network diagnostics", lambda: run_diagnostic("network")),
        "6": ("Storage diagnostics", lambda: run_diagnostic("storage")),
        "7": ("AUR security audit", show_aur_audit),
        "8": (
            "Save text report",
            lambda: status(
                "OK", f"Report saved to {save_report(report_format='text')}"
            ),
        ),
    }
    while True:
        banner(__version__)
        section("Interactive Menu")
        for key, (label, _) in actions.items():
            print(f"  [{key}] {label}")
        print("  [0] Exit")

        try:
            choice = input("\nChoose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            status("INFO", "Exiting Sentinel Tools.")
            return

        if choice == "0":
            status("INFO", "Exiting Sentinel Tools.")
            return

        action = actions.get(choice)
        if action is None:
            status("WARN", "Invalid selection. Choose a listed menu number.")
            continue

        action[1]()
        try:
            input("\nPress Enter to continue...")
        except (EOFError, KeyboardInterrupt):
            print()
            return


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sentinel-tools",
        description=(
            "Run Arch Linux diagnostics, create shareable reports, "
            "and perform safe maintenance tasks."
        ),
        epilog=(
            "Examples:\n"
            "  sentinel-tools health\n"
            "  sentinel-tools security\n"
            "  sentinel-tools report --format html --redact\n"
            "  sentinel-tools menu"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    subparsers = parser.add_subparsers(
        dest="command", metavar="COMMAND", title="commands"
    )
    subparsers.add_parser("menu", help="Open the interactive menu.")
    subparsers.add_parser(
        "health", help="Run the system health check and calculate a score."
    )
    subparsers.add_parser(
        "security", help="Inspect firewall and security-related system state."
    )
    subparsers.add_parser(
        "network", help="Inspect connectivity and network configuration."
    )
    subparsers.add_parser(
        "storage", help="Inspect filesystems, disks, and storage usage."
    )
    subparsers.add_parser("checks", help="List registered diagnostic checks.")
    subparsers.add_parser(
        "update", help="Safely update Arch Linux and Flatpak packages."
    )
    subparsers.add_parser(
        "system-info",
        help="Display platform-neutral operating system and hardware information.",
    )
    subparsers.add_parser(
        "inventory",
        help="Display detailed hardware inventory information.",
    )
    subparsers.add_parser(
        "clean", help="Perform guided package and filesystem cleanup."
    )
    subparsers.add_parser(
        "aur", help="Audit installed AUR and foreign packages without modifying them."
    )
    report_parser = subparsers.add_parser(
        "report", help="Create a text, JSON, or HTML system report."
    )
    report_parser.add_argument(
        "--format",
        choices=("text", "json", "html"),
        default="text",
        help="Output format. Default: text.",
    )
    report_parser.add_argument(
        "--output", type=Path, help="Destination path for the report."
    )
    report_parser.add_argument(
        "--redact", action="store_true", help="Mask sensitive report data."
    )
    report_parser.add_argument(
        "--severity",
        choices=("info", "warning", "critical"),
        help="Include only findings with this severity.",
    )
    report_parser.add_argument(
        "--finding-code",
        type=str.upper,
        help="Include only one finding code, such as JRN001.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    logger = configure_logging()
    logger.info("Sentinel Tools started")

    from sentinel_tools.app import SentinelApp

    try:
        SentinelApp().run(args)
    except KeyboardInterrupt:
        print()
        status("INFO", "Operation cancelled.")
        raise SystemExit(130) from None


if __name__ == "__main__":
    main()
