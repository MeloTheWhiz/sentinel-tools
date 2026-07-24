import json
from pathlib import Path

from sentinel_tools.reporting import (
    build_report,
    filter_findings,
    save_html,
    save_json,
    save_text,
)
from sentinel_tools.scoring.health import Finding, Severity


def sample_sections() -> dict[str, dict[str, str]]:
    return {
        "system": {
            "Hostname": "test-host",
            "Failed system services": "None",
            "Failed user services": "None",
            "High-priority errors from this boot": "None",
            "Package database": "No database errors have been found!",
            "Orphan packages": "None",
        },
        "network": {"Connectivity": "Online"},
        "storage": {"Filesystem": "Healthy"},
        "security": {"Firewall": "Active"},
    }


def test_build_report_contains_health_data() -> None:
    report = build_report(sample_sections())

    assert report["health"]["score"] == 100
    assert report["health"]["status"] == "Excellent"
    assert report["health"]["findings"] == []
    assert report["diagnostics"]["system"]["Hostname"] == "test-host"
    assert report["system_summary"]["Hostname"] == "test-host"


def test_save_json_writes_valid_json(tmp_path: Path) -> None:
    path = tmp_path / "report.json"

    result = save_json(path, sample_sections())
    data = json.loads(path.read_text(encoding="utf-8"))

    assert result == path
    assert data["application"]["name"] == "Sentinel Tools"
    assert data["health"]["score"] == 100
    assert data["diagnostics"]["network"]["Connectivity"] == "Online"
    assert data["system_summary"]["Hostname"] == "test-host"


def test_save_text_includes_health_score(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"

    result = save_text(path, sample_sections())
    text = path.read_text(encoding="utf-8")

    assert result == path
    assert "Health score: 100/100" in text
    assert "Health status: Excellent" in text
    assert "test-host" in text
    assert "SYSTEM SUMMARY" in text
    assert "Hostname: test-host" in text


def test_save_html_contains_report_data(tmp_path: Path) -> None:
    path = tmp_path / "report.html"

    result = save_html(path, sample_sections())
    html = path.read_text(encoding="utf-8")

    assert result == path
    assert "<!DOCTYPE html>" in html
    assert "Sentinel Tools System Report" in html
    assert "100/100" in html
    assert "Excellent" in html
    assert "System Summary" in html
    assert "test-host" in html


def test_save_html_escapes_values(tmp_path: Path) -> None:
    path = tmp_path / "report.html"
    sections = sample_sections()
    sections["network"]["Unsafe"] = "<script>alert(1)</script>"

    save_html(path, sections)
    html = path.read_text(encoding="utf-8")

    assert "<script>" not in html
    assert "&lt;script&gt;" in html


def test_save_html_supports_redaction(tmp_path: Path) -> None:
    path = tmp_path / "report.html"
    sections = sample_sections()
    sections["network"]["Address"] = "192.168.1.25"

    save_html(path, sections, redact=True)
    html = path.read_text(encoding="utf-8")

    assert "192.168.1.25" not in html
    assert "[PRIVATE-IP]" in html
    assert "Redacted" in html


def problem_sections() -> dict[str, dict[str, str]]:
    sections = sample_sections()
    sections["system"]["Failed system services"] = "example.service"
    sections["system"]["Failed user services"] = "example-user.service"
    sections["system"]["Orphan packages"] = "unused-package"
    return sections


def test_filter_findings_by_severity() -> None:
    findings = [
        Finding("SYS001", Severity.CRITICAL, "System failure", "Fix system"),
        Finding("USR001", Severity.WARNING, "User failure", "Fix user service"),
    ]

    filtered = filter_findings(findings, severity="critical")

    assert [finding.code for finding in filtered] == ["SYS001"]


def test_filter_findings_by_code_is_case_insensitive() -> None:
    findings = [
        Finding("SYS001", Severity.CRITICAL, "System failure", "Fix system"),
        Finding("USR001", Severity.WARNING, "User failure", "Fix user service"),
    ]

    filtered = filter_findings(findings, finding_code="usr001")

    assert [finding.code for finding in filtered] == ["USR001"]


def test_build_report_filters_findings_by_severity() -> None:
    report = build_report(problem_sections(), severity="warning")

    assert [finding["code"] for finding in report["health"]["findings"]] == ["USR001"]


def test_build_report_combines_finding_filters() -> None:
    report = build_report(
        problem_sections(),
        severity="critical",
        finding_code="SYS001",
    )

    assert [finding["code"] for finding in report["health"]["findings"]] == ["SYS001"]


def test_build_report_returns_no_findings_when_filters_do_not_match() -> None:
    report = build_report(
        problem_sections(),
        severity="warning",
        finding_code="SYS001",
    )

    assert report["health"]["findings"] == []


def test_save_json_filters_findings(tmp_path: Path) -> None:
    path = tmp_path / "filtered.json"

    save_json(path, problem_sections(), finding_code="PKG002")
    data = json.loads(path.read_text(encoding="utf-8"))

    assert [finding["code"] for finding in data["health"]["findings"]] == ["PKG002"]
