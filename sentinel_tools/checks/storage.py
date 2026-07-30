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
        lsblk = run(["lsblk", "-dno", "NAME,TYPE"])
        drives = []
        if lsblk.stdout:
            for line in lsblk.stdout.splitlines():
                parts = line.split()
                if len(parts) == 2 and parts[1] == "disk":
                    name = parts[0]
                    if name.startswith("sd") or name.startswith("nvme"):
                        drives.append(name)

        if drives:
            for drive in drives:
                result = run(["smartctl", "-H", f"/dev/{drive}"], sudo=True, sudo_prompt=False)
                data[f"Drive health /dev/{drive}"] = result.stdout or result.stderr
        else:
            data["Drive health"] = "No compatible SD or NVMe drives detected."
    else:
        data["Drive health"] = "Install smartmontools to enable SMART checks."
    return data
