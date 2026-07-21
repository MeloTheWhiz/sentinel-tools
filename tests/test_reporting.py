import json
from pathlib import Path

from sentinel_tools.reporting import build_report, save_json, save_text


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


def test_save_json_writes_valid_json(tmp_path: Path) -> None:
    path = tmp_path / "report.json"

    result = save_json(path, sample_sections())
    data = json.loads(path.read_text(encoding="utf-8"))

    assert result == path
    assert data["application"]["name"] == "Sentinel Tools"
    assert data["health"]["score"] == 100
    assert data["diagnostics"]["network"]["Connectivity"] == "Online"


def test_save_text_includes_health_score(tmp_path: Path) -> None:
    path = tmp_path / "report.txt"

    result = save_text(path, sample_sections())
    text = path.read_text(encoding="utf-8")

    assert result == path
    assert "Health score: 100/100" in text
    assert "Health status: Excellent" in text
    assert "test-host" in text
