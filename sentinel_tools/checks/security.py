from sentinel_tools.core import have, run


def collect() -> dict:
    data = {}
    if have("ufw"):
        result = run(["ufw", "status", "verbose"], sudo=True, sudo_prompt=False)
        data["Firewall"] = result.stdout or result.stderr
    elif have("nft"):
        result = run(["nft", "list", "ruleset"], sudo=True, sudo_prompt=False)
        data["Firewall"] = result.stdout or result.stderr
    else:
        data["Firewall"] = "No supported firewall command found."

    ports = run(["ss", "-lntup"])
    data["Listening ports"] = ports.stdout or ports.stderr

    boot = run(["findmnt", "-no", "SOURCE,FSTYPE,OPTIONS", "/boot"])
    data["Boot mount"] = boot.stdout or boot.stderr
    return data
