from __future__ import annotations

from sentinel_tools.core import have, run, system_identity

IGNORED_DISPLAY_JOURNAL_PATTERNS = (
    "a password is required",
    "no password was provided",
    "a terminal is required",
)


def service_state(service: str) -> str:
    """Return the current systemd state for a service."""
    result = run(["systemctl", "is-active", service])

    if result.stdout:
        return result.stdout

    if result.stderr:
        return result.stderr

    return "unknown"


def filter_journal_output(output: str) -> str:
    """Remove expected probe noise from displayed journal errors."""
    if not output.strip():
        return "None"

    visible_lines = []

    for line in output.splitlines():
        lowered = line.lower()

        if any(pattern in lowered for pattern in IGNORED_DISPLAY_JOURNAL_PATTERNS):
            continue

        visible_lines.append(line)

    return "\n".join(visible_lines) if visible_lines else "None"


def collect() -> dict[str, str]:
    """Collect system identity, service, package, and journal information."""
    data = system_identity()

    commands = {
        "Uptime and load": ["uptime"],
        "Memory": ["free", "-h"],
        "Filesystems": [
            "df",
            "-hT",
            "-x",
            "tmpfs",
            "-x",
            "devtmpfs",
        ],
        "Failed system services": [
            "systemctl",
            "--failed",
            "--no-legend",
            "--plain",
        ],
        "Failed user services": [
            "systemctl",
            "--user",
            "--failed",
            "--no-legend",
            "--plain",
        ],
        "Orphan packages": ["pacman", "-Qtdq"],
    }

    for label, command in commands.items():
        result = run(command)
        data[label] = result.stdout or result.stderr or "None"

    journal = run(
        [
            "journalctl",
            "-b",
            "-p",
            "err",
            "--no-pager",
            "-n",
            "30",
        ]
    )
    journal_output = journal.stdout or journal.stderr
    data["High-priority errors from this boot"] = filter_journal_output(journal_output)

    services = {
        "NetworkManager": "NetworkManager.service",
        "Bluetooth": "bluetooth.service",
        "Chrony": "chronyd.service",
        "Systemd timesync": "systemd-timesyncd.service",
    }

    for label, service in services.items():
        data[f"Service {label}"] = service_state(service)

    if have("plasmashell"):
        plasma = run(["plasmashell", "--version"])
        data["KDE Plasma"] = plasma.stdout or plasma.stderr or "Unknown"

    database = run(["pacman", "-Dk"])
    data["Package database"] = database.stdout or database.stderr or "Unknown"

    return data
