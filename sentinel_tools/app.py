from __future__ import annotations

from argparse import Namespace
from collections.abc import Mapping

from sentinel_tools.cli import (
    DIAGNOSTIC_TITLES,
    menu,
    run_diagnostic,
    run_health_check,
    show_available_checks,
)
from sentinel_tools.config.loader import load_config, plugin_modules
from sentinel_tools.engine import registry
from sentinel_tools.maintenance import clean, update
from sentinel_tools.plugins import load_plugins
from sentinel_tools.repairs.ui import (
    list_repairs,
    show_repair_dry_run,
    show_repair_info,
)
from sentinel_tools.reports.service import save_report
from sentinel_tools.ui.console import status


class SentinelApp:
    """Coordinate Sentinel Tools startup and command execution."""

    def __init__(self, config: Mapping[str, object] | None = None) -> None:
        self.config = dict(load_config() if config is None else config)
        self._plugins_loaded = False

    def initialize_plugins(self) -> None:
        if self._plugins_loaded:
            return
        load_plugins(plugin_modules(self.config), registry)
        self._plugins_loaded = True

    def run(self, args: Namespace) -> None:
        self.initialize_plugins()
        command = args.command or "menu"

        if command == "menu":
            menu()
        elif command == "health":
            run_health_check()
        elif command == "checks":
            show_available_checks()
        elif command == "update":
            raise SystemExit(update())
        elif command == "clean":
            raise SystemExit(clean())
        elif command in DIAGNOSTIC_TITLES:
            run_diagnostic(command)
        elif command == "report":
            destination = save_report(
                report_format=args.format,
                output=args.output,
                redact=args.redact,
                severity=args.severity,
                finding_code=args.finding_code,
            )
            status("OK", f"Report saved to {destination}")
        elif command == "repair":
            if args.repair_command == "list":
                list_repairs()
            elif args.repair_command == "info":
                show_repair_info(args.repair_id)
            elif args.repair_command == "run":
                show_repair_dry_run(args.repair_id)
