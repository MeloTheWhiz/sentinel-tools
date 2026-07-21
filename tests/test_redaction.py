from __future__ import annotations

import json
from pathlib import Path

from sentinel_tools.redaction import redact_sections, redact_text
from sentinel_tools.reporting import save_json, save_text


def sensitive_sections() -> dict[str, dict[str, str]]:
    return {
        "system": {
            "Hostname": "Lenovo-Arch",
            "Paths": "/home/melo/Projects/sentinel-tools",
            "Failed system services": "None",
            "Failed user services": "None",
            "High-priority errors from this boot": "None",
            "Package database": "No database errors have been found!",
            "Orphan packages": "None",
        },
        "network": {
            "Wi-Fi": (
                "IN-USE  SSID          SIGNAL  RATE       SECURITY\n"
                "*       Yum Yum Yum   70      540 Mbit/s WPA2\n"
                "        NeighborNet   40      195 Mbit/s WPA2"
            ),
            "Routes": (
                "default via 192.168.1.1 "
                "src 192.168.1.47 "
                "aa:bb:cc:dd:ee:ff"
            ),
        },
        "storage": {"Mount": "/home/melo"},
        "security": {"Listening": "192.168.1.47:8080"},
    }


def test_redact_text_masks_private_network_data() -> None:
    result = redact_text(
        "Gateway 192.168.1.1 device aa:bb:cc:dd:ee:ff"
    )

    assert "192.168.1.1" not in result
    assert "aa:bb:cc:dd:ee:ff" not in result
    assert "[PRIVATE-IP]" in result
    assert "[MAC-ADDRESS]" in result


def test_redact_sections_masks_hostname_and_wifi() -> None:
    redacted = redact_sections(sensitive_sections())

    assert redacted["system"]["Hostname"] == "[HOSTNAME]"
    assert "Yum Yum Yum" not in redacted["network"]["Wi-Fi"]
    assert "NeighborNet" not in redacted["network"]["Wi-Fi"]
    assert "[REDACTED-SSID]" in redacted["network"]["Wi-Fi"]
    assert "192.168.1.47" not in redacted["network"]["Routes"]


def test_save_redacted_json(tmp_path: Path) -> None:
    path = tmp_path / "redacted.json"

    save_json(path, sensitive_sections(), redact=True)
    report = json.loads(path.read_text(encoding="utf-8"))

    assert report["redacted"] is True
    assert report["diagnostics"]["system"]["Hostname"] == "[HOSTNAME]"
    assert "Yum Yum Yum" not in json.dumps(report)
    assert "192.168.1.47" not in json.dumps(report)


def test_save_redacted_text(tmp_path: Path) -> None:
    path = tmp_path / "redacted.txt"

    save_text(path, sensitive_sections(), redact=True)
    text = path.read_text(encoding="utf-8")

    assert "Yum Yum Yum" not in text
    assert "NeighborNet" not in text
    assert "192.168.1.47" not in text
    assert "[HOSTNAME]" in text
    assert "[REDACTED-SSID]" in text
