from sentinel_tools.core import have, run
from sentinel_tools.platform import get_platform


def collect() -> dict:
    data = {}

    usage = run(["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"])
    data["Filesystem usage"] = usage.stdout or usage.stderr

    mounts = run(["findmnt", "-D"])
    data["Mounts"] = mounts.stdout or mounts.stderr

    if have("btrfs"):
        usage = run(
            ["btrfs", "filesystem", "usage", "/"],
            sudo=True,
            sudo_prompt=False,
        )
        data["Btrfs root usage"] = usage.stdout or usage.stderr

        scrub = run(
            ["btrfs", "scrub", "status", "/"],
            sudo=True,
            sudo_prompt=False,
        )
        data["Btrfs scrub"] = scrub.stdout or scrub.stderr

    if not have("smartctl"):
        data["Drive health"] = "Install smartmontools to enable SMART checks."
        return data

    devices = get_platform().storage_devices()

    if not devices:
        data["Drive health"] = "No physical storage devices detected."
        return data

    for device in devices:
        result = run(
            ["smartctl", "-H", device],
            sudo=True,
            sudo_prompt=False,
        )
        data[f"Drive health {device}"] = result.stdout or result.stderr

    return data
