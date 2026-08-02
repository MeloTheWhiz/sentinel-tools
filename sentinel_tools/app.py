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
from sentinel_tools.core import ensure_arch
from sentinel_tools.config.loader import load_config, plugin_modules
from sentinel_tools.engine import registry
from sentinel_tools.maintenance import clean, update
from sentinel_tools.plugins import load_plugins
from sentinel_tools.reports.service import save_report
from sentinel_tools.aur import show_aur_audit
from sentinel_tools.ui.console import status
from sentinel_tools.platform import get_platform


def _format_bytes(value: int | None) -> str:
    if value is None:
        return "Unknown"

    gibibytes = value / (1024**3)
    return f"{gibibytes:.2f} GiB"


def show_system_info() -> None:
    system_info = get_platform().system_info()
    cpu_info = system_info.cpu
    memory_info = system_info.memory
    disks = system_info.disks

    used_memory = None
    if memory_info.total_bytes is not None and memory_info.available_bytes is not None:
        used_memory = memory_info.total_bytes - memory_info.available_bytes

    print()
    print("========================================")
    print("       SENTINEL SYSTEM INFORMATION")
    print("========================================")
    print()
    print(f"Operating system: {system_info.operating_system}")
    print(f"Architecture:     {cpu_info.architecture or 'Unknown'}")
    print(f"Processor:        {cpu_info.model or 'Unknown'}")
    print(f"Logical cores:    {cpu_info.logical_cores or 'Unknown'}")
    print()
    print(f"Memory total:     {_format_bytes(memory_info.total_bytes)}")
    print(f"Memory available: {_format_bytes(memory_info.available_bytes)}")
    print(f"Memory used:      {_format_bytes(used_memory)}")
    print()
    print("Storage:")

    if not disks:
        print("  No mounted storage detected.")
    else:
        for disk in disks:
            print(
                f"  {disk.mountpoint}: "
                f"{_format_bytes(disk.used_bytes)} used / "
                f"{_format_bytes(disk.total_bytes)} total "
                f"({_format_bytes(disk.free_bytes)} free)"
            )

    print()
    print("========================================")


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
            ensure_arch()
            run_health_check()
        elif command == "checks":
            show_available_checks()
        elif command == "system-info":
            show_system_info()
        elif command == "update":
            ensure_arch()
            raise SystemExit(update())
        elif command == "clean":
            ensure_arch()
            raise SystemExit(clean())
        elif command in DIAGNOSTIC_TITLES:
            ensure_arch()
            run_diagnostic(command)
        elif command == "aur":
            ensure_arch()
            raise SystemExit(show_aur_audit())
        elif command == "report":
            destination = save_report(
                report_format=args.format,
                output=args.output,
                redact=args.redact,
                severity=args.severity,
                finding_code=args.finding_code,
            )
            status("OK", f"Report saved to {destination}")
