from __future__ import annotations

import json
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

from sentinel_tools import __version__
from sentinel_tools.engine import run_all
from sentinel_tools.redaction import redact_report, redact_sections
from sentinel_tools.scoring.health import Finding, calculate


def collect_sections() -> dict[str, dict[str, str]]:
    return run_all()


def build_system_summary(system_data: dict[str, str]) -> dict[str, str]:
    summary_keys = (
        "Hostname",
        "Operating System",
        "Kernel",
        "Architecture",
        "Desktop",
        "CPU",
        "Memory",
        "Python",
        "Python executable",
        "KDE Plasma",
    )

    return {
        key: system_data[key]
        for key in summary_keys
        if key in system_data and system_data[key].strip()
    }


def filter_findings(
    findings: list[Finding],
    *,
    severity: str | None = None,
    finding_code: str | None = None,
) -> list[Finding]:
    selected = findings

    if severity is not None:
        normalized_severity = severity.strip().lower()
        selected = [
            finding
            for finding in selected
            if finding.severity.value == normalized_severity
        ]

    if finding_code is not None:
        normalized_code = finding_code.strip().upper()
        selected = [
            finding for finding in selected if finding.code.upper() == normalized_code
        ]

    return selected


def build_report(
    sections: dict[str, dict[str, str]] | None = None,
    *,
    severity: str | None = None,
    finding_code: str | None = None,
) -> dict[str, Any]:
    report_sections = sections if sections is not None else collect_sections()
    health = calculate(report_sections["system"])

    findings = filter_findings(
        health.findings,
        severity=severity,
        finding_code=finding_code,
    )

    system_summary = build_system_summary(report_sections["system"])

    return {
        "application": {
            "name": "Sentinel Tools",
            "version": __version__,
        },
        "generated_at": datetime.now().astimezone().isoformat(),
        "system_summary": system_summary,
        "health": {
            "score": health.score,
            "status": health.status,
            "findings": [
                {
                    "code": finding.code,
                    "severity": finding.severity.value,
                    "category": finding.category,
                    "title": finding.display_title,
                    "message": finding.message,
                    "explanation": finding.explanation,
                    "recommendation": finding.recommendation,
                    "repair_id": finding.repair_id,
                }
                for finding in findings
            ],
        },
        "diagnostics": report_sections,
    }


def save_text(
    path: Path,
    sections: dict[str, dict[str, str]] | None = None,
    *,
    redact: bool = False,
    severity: str | None = None,
    finding_code: str | None = None,
) -> Path:
    report_sections = sections if sections is not None else collect_sections()

    if redact:
        report_sections = redact_sections(report_sections)
    health = calculate(report_sections["system"])
    findings = filter_findings(
        health.findings,
        severity=severity,
        finding_code=finding_code,
    )

    system_summary = build_system_summary(report_sections["system"])
    lines = [
        "SENTINEL TOOLS SYSTEM REPORT",
        f"Generated: {datetime.now().astimezone().isoformat()}",
        "",
        "SYSTEM SUMMARY",
    ]

    for key, value in system_summary.items():
        lines.append(f"{key}: {value}")

    lines.extend(
        [
            "",
            f"Health score: {health.score}/100",
            f"Health status: {health.status}",
        ]
    )

    if findings:
        lines.extend(["", "HEALTH FINDINGS"])
        for finding in findings:
            lines.append(
                f"[{finding.code}][{finding.severity.value.upper()}] {finding.message}"
            )
            lines.append(f"Recommendation: {finding.recommendation}")
    elif severity is not None or finding_code is not None:
        lines.extend(
            [
                "",
                "HEALTH FINDINGS",
                "No findings matched the selected filters.",
            ]
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
    *,
    redact: bool = False,
    severity: str | None = None,
    finding_code: str | None = None,
) -> Path:
    report = build_report(
        sections,
        severity=severity,
        finding_code=finding_code,
    )

    if redact:
        report = redact_report(report)
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path


def save_html(
    path: Path,
    sections: dict[str, dict[str, str]] | None = None,
    *,
    redact: bool = False,
    severity: str | None = None,
    finding_code: str | None = None,
) -> Path:
    report = build_report(
        sections,
        severity=severity,
        finding_code=finding_code,
    )
    if redact:
        report = redact_report(report)

    application = report["application"]
    system_summary = report["system_summary"]
    health = report["health"]
    diagnostics = report["diagnostics"]
    summary_rows = []

    for key, value in system_summary.items():
        summary_rows.append(
            f"<tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>"
        )

    findings = []

    for finding in health["findings"]:
        findings.append(
            '<article class="finding">'
            f"<strong>{escape(str(finding['severity'])).upper()}</strong>"
            f"<h3>{escape(str(finding['title']))}</h3>"
            f"<p>{escape(str(finding['message']))}</p>"
            f"<p>{escape(str(finding['explanation']))}</p>"
            "<p><b>Category:</b> "
            f"{escape(str(finding['category']))}</p>"
            "<p><b>Recommendation:</b> "
            f"{escape(str(finding['recommendation']))}</p>"
            "</article>"
        )

    if not findings:
        findings.append(
            '<article class="finding">'
            "<strong>OK</strong>"
            "<p>No health findings detected.</p>"
            "</article>"
        )

    diagnostic_sections = []

    for section_name, values in diagnostics.items():
        rows = []

        for key, value in values.items():
            rows.append(
                "<tr>"
                f"<th>{escape(str(key))}</th>"
                f"<td><pre>{escape(str(value))}</pre></td>"
                "</tr>"
            )

        diagnostic_sections.append(
            "<section>"
            f"<h2>{escape(str(section_name)).title()}</h2>"
            "<table><tbody>" + "".join(rows) + "</tbody></table>"
            "</section>"
        )

    badge = '<span class="badge">Redacted</span>' if report.get("redacted") else ""

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sentinel Tools System Report</title>
<style>
:root {{
    color-scheme: dark;
    --background: #111217;
    --surface: #1a1c23;
    --border: #363a47;
    --text: #f4f4f5;
    --muted: #a5a7b1;
    --purple: #9b5de5;
    --green: #39ff88;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    background: var(--background);
    color: var(--text);
    font-family: system-ui, sans-serif;
    line-height: 1.5;
}}
main {{
    width: min(1100px, calc(100% - 2rem));
    margin: 2rem auto;
}}
header, section {{
    margin-bottom: 1.5rem;
    padding: 1.5rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
}}
header {{ border-top: 4px solid var(--purple); }}
h2 {{ color: var(--green); }}
.summary {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
}}
.card {{
    padding: 1rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
}}
.card strong {{
    display: block;
    font-size: 2rem;
    color: var(--green);
}}
.badge {{
    display: inline-block;
    padding: .25rem .65rem;
    border: 1px solid var(--purple);
    border-radius: 999px;
    color: var(--purple);
}}
.finding {{
    margin-top: .75rem;
    padding: 1rem;
    border: 1px solid var(--border);
    border-radius: 8px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
}}
th, td {{
    padding: .75rem;
    border-bottom: 1px solid var(--border);
    text-align: left;
    vertical-align: top;
}}
th {{
    width: 28%;
    color: var(--purple);
}}
pre {{
    margin: 0;
    white-space: pre-wrap;
    overflow-wrap: anywhere;
    font: inherit;
}}
.muted {{ color: var(--muted); }}
</style>
</head>
<body>
<main>
<header>
<h1>{escape(str(application["name"]))} System Report</h1>
<p class="muted">
Version {escape(str(application["version"]))}<br>
Generated: {escape(str(report["generated_at"]))}
</p>
{badge}
</header>

<div class="summary">
<div class="card">
<strong>{escape(str(health["score"]))}/100</strong>
<span>Health score</span>
</div>
<div class="card">
<strong>{escape(str(health["status"]))}</strong>
<span>Health status</span>
</div>
</div>

<section>
<h2>System Summary</h2>
<table><tbody>
{"".join(summary_rows)}
</tbody></table>
</section>

<section>
<h2>Health Findings</h2>
{"".join(findings)}
</section>

{"".join(diagnostic_sections)}
</main>
</body>
</html>
"""

    path.write_text(document, encoding="utf-8")
    return path
