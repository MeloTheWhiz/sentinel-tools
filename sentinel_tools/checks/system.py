from sentinel_tools.core import run, have, system_identity


def collect() -> dict:
    data = system_identity()
    commands = {
        "Uptime and load": ["uptime"],
        "Memory": ["free", "-h"],
        "Filesystems": ["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"],
        "Failed system services": ["systemctl", "--failed", "--no-legend", "--plain"],
        "Failed user services": ["systemctl", "--user", "--failed", "--no-legend", "--plain"],
        "High-priority errors from this boot": ["journalctl", "-b", "-p", "err", "--no-pager", "-n", "30"],
        "Orphan packages": ["pacman", "-Qtdq"],
    }
    for label, command in commands.items():
        result = run(command)
        data[label] = result.stdout or result.stderr or "None"

    if have("plasmashell"):
        plasma = run(["plasmashell", "--version"])
        data["KDE Plasma"] = plasma.stdout or plasma.stderr

    database = run(["pacman", "-Dk"], sudo=True)
    data["Package database"] = database.stdout or database.stderr
    return data
