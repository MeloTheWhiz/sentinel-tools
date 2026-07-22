from sentinel_tools.core import have, run, system_identity


def service_state(service: str) -> str:
    result = run(["systemctl", "is-active", service])

    if result.stdout:
        return result.stdout

    if result.stderr:
        return result.stderr

    return "unknown"


def collect() -> dict[str, str]:
    data = system_identity()

    commands = {
        "Uptime and load": ["uptime"],
        "Memory": ["free", "-h"],
        "Filesystems": ["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"],
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
        "High-priority errors from this boot": [
            "journalctl",
            "-b",
            "-p",
            "err",
            "--no-pager",
            "-n",
            "30",
        ],
        "Orphan packages": ["pacman", "-Qtdq"],
    }

    for label, command in commands.items():
        result = run(command)
        data[label] = result.stdout or result.stderr or "None"

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
        data["KDE Plasma"] = plasma.stdout or plasma.stderr

    database = run(["pacman", "-Dk"])
    data["Package database"] = database.stdout or database.stderr

    return data
