from __future__ import annotations

from argparse import Namespace

from sentinel_tools.cli import (
    DIAGNOSTIC_TITLES,
    menu,
    run_diagnostic,
    run_health_check,
)
from sentinel_tools.maintenance import clean, update
from sentinel_tools.reports.service import save_report


class SentinelApp:
    def run(self, args: Namespace) -> None:
        command = args.command or "menu"

        if command == "menu":
            menu()
        elif command == "health":
            run_health_check()
        elif command == "update":
            raise SystemExit(update())
        elif command == "clean":
            raise SystemExit(clean())
        elif command in DIAGNOSTIC_TITLES:
            run_diagnostic(command)
        elif command == "report":
            print(
                save_report(
                    report_format=args.format,
                    output=args.output,
                    redact=args.redact,
                    severity=args.severity,
                    finding_code=args.finding_code,
                )
            )
