from __future__ import annotations

from pathlib import Path

from sentinel_tools.reporting import save_html, save_json, save_text


def default_report_path(report_format: str) -> Path:
    if report_format == "json":
        return Path.home() / "sentinel-tools-report.json"

    if report_format == "html":
        return Path.home() / "sentinel-tools-report.html"

    return Path.home() / "sentinel-tools-report.txt"


def save_report(
    *,
    report_format: str,
    output: Path | None = None,
    redact: bool = False,
    severity: str | None = None,
    finding_code: str | None = None,
) -> Path:
    destination = (
        output.expanduser()
        if output is not None
        else default_report_path(report_format)
    )

    destination.parent.mkdir(parents=True, exist_ok=True)

    save_options = {
        "redact": redact,
        "severity": severity,
        "finding_code": finding_code,
    }

    if report_format == "json":
        return save_json(destination, **save_options)

    if report_format == "html":
        return save_html(destination, **save_options)

    return save_text(destination, **save_options)
