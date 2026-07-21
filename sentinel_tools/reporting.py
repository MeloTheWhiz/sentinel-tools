from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from sentinel_tools import __version__
from sentinel_tools.checks import network, security, storage, system
from sentinel_tools.scoring.health import calculate


def collect_sections() -> dict[str, dict[str, str]]:
    return {
        "system": system.collect(),
        "network": network.collect(),
        "storage": storage.collect(),
        "security": security.collect(),
    }


def build_report(
    sections: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    report_sections = sections if sections is not None else collect_sections()
    health = calculate(report_sections["system"])

    return {
        "application": {
            "name": "Sentinel Tools",
            "version": __version__,
        },
        "generated_at": datetime.now().astimezone().isoformat(),
        "health": {
            "score": health.score,
            "status": health.status,
            "findings": [
                {
                    "severity": finding.severity.value,
                    "message": finding.message,
                    "recommendation": finding.recommendation,
                }
                for finding in health.findings
            ],
        },
        "diagnostics": report_sections,
    }


def save_text(
    path: Path,
    sections: dict[str, dict[str, str]] | None = None,
) -> Path:
    report_sections = sections if sections is not None else collect_sections()
    health = calculate(report_sections["system"])

    lines = [
        "SENTINEL TOOLS SYSTEM REPORT",
        f"Generated: {datetime.now().astimezone().isoformat()}",
        f"Health score: {health.score}/100",
        f"Health status: {health.status}",
    ]

    if health.findings:
        lines.extend(["", "HEALTH FINDINGS"])
        for finding in health.findings:
            lines.append(
                f"[{finding.severity.value.upper()}] {finding.message}"
            )
            lines.append(
                f"Recommendation: {finding.recommendation}"
            )

    for title, values in report_sections.items():
        lines.extend(["", "=" * 72, title.upper(), "=" * 72])
        for key, value in values.items():
            lines.extend(["", f"{key}:", str(value)])

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def save_json(
    path: Path,
    sections: dict[str, dict[str, str]] | None = None,
) -> Path:
    report = build_report(sections)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
