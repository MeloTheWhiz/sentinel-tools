from sentinel_tools.core import have, run


def collect() -> dict:
    data = {}
    usage = run(["df", "-hT", "-x", "tmpfs", "-x", "devtmpfs"])
    data["Filesystem usage"] = usage.stdout or usage.stderr

    mounts = run(["findmnt", "-D"])
    data["Mounts"] = mounts.stdout or mounts.stderr

    if have("btrfs"):
        usage = run(["btrfs", "filesystem", "usage", "/"], sudo=True, sudo_prompt=False)
        data["Btrfs root usage"] = usage.stdout or usage.stderr
        scrub = run(["btrfs", "scrub", "status", "/"], sudo=True, sudo_prompt=False)
        data["Btrfs scrub"] = scrub.stdout or scrub.stderr

    if have("smartctl"):
        result = run(["smartctl", "-H", "/dev/sda"], sudo=True, sudo_prompt=False)
        data["Drive health /dev/sda"] = result.stdout or result.stderr
    else:
        data["Drive health"] = "Install smartmontools to enable SMART checks."
    return data
