from __future__ import annotations

import getpass
import re
import socket
from copy import deepcopy
from pathlib import Path
from typing import Any

PRIVATE_IPV4_PATTERN = re.compile(
    r"\b(?:"
    r"10(?:\.\d{1,3}){3}|"
    r"192\.168(?:\.\d{1,3}){2}|"
    r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}"
    r")\b"
)

MAC_ADDRESS_PATTERN = re.compile(
    r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"
)


def redact_text(value: str) -> str:
    result = value

    username = getpass.getuser()
    hostname = socket.gethostname()
    home = str(Path.home())

    replacements = (
        (home, "[HOME]"),
        (hostname, "[HOSTNAME]"),
        (username, "[USER]"),
    )

    for sensitive, replacement in replacements:
        if sensitive:
            result = result.replace(sensitive, replacement)

    result = PRIVATE_IPV4_PATTERN.sub("[PRIVATE-IP]", result)
    result = MAC_ADDRESS_PATTERN.sub("[MAC-ADDRESS]", result)

    return result


def redact_wifi_table(value: str) -> str:
    lines = value.splitlines()

    if not lines:
        return value

    redacted_lines = [lines[0]]

    for line in lines[1:]:
        if not line.strip():
            redacted_lines.append(line)
            continue

        in_use = "*" if line.lstrip().startswith("*") else " "
        redacted_lines.append(f"{in_use}       [REDACTED-SSID]")

    return "\n".join(redacted_lines)


def redact_network_devices(value: str) -> str:
    redacted_lines: list[str] = []

    for line in value.splitlines():
        parts = line.split(":", 3)

        if (
            len(parts) == 4
            and parts[1] == "wifi"
            and parts[2].startswith("connected")
        ):
            parts[3] = "[REDACTED-SSID]"
            line = ":".join(parts)

        redacted_lines.append(line)

    return "\n".join(redacted_lines)


def redact_sections(
    sections: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    redacted = deepcopy(sections)

    for section_name, values in redacted.items():
        for key, value in values.items():
            text = str(value)

            if section_name == "network" and key == "Wi-Fi":
                values[key] = redact_wifi_table(text)
            elif section_name == "network" and key == "Devices":
                values[key] = redact_network_devices(text)
            elif key == "Hostname":
                values[key] = "[HOSTNAME]"
            else:
                values[key] = redact_text(text)

    return redacted


def redact_report(report: dict[str, Any]) -> dict[str, Any]:
    redacted = deepcopy(report)

    diagnostics = redacted.get("diagnostics")
    if isinstance(diagnostics, dict):
        redacted["diagnostics"] = redact_sections(diagnostics)

    redacted["redacted"] = True
    return redacted
