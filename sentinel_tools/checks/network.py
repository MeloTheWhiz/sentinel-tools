from sentinel_tools.core import run, have


def collect() -> dict:
    data = {}
    if have("nmcli"):
        result = run(
            ["nmcli", "-t", "-f", "DEVICE,TYPE,STATE,CONNECTION", "device", "status"]
        )
        data["Devices"] = result.stdout or result.stderr
        wifi = run(
            [
                "nmcli",
                "-f",
                "IN-USE,SSID,SIGNAL,RATE,SECURITY",
                "device",
                "wifi",
                "list",
            ]
        )
        data["Wi-Fi"] = wifi.stdout or wifi.stderr
    else:
        result = run(["ip", "-brief", "address"])
        data["Devices"] = result.stdout or result.stderr

    for label, command in {
        "Routes": ["ip", "route"],
        "Internet reachability": ["ping", "-c", "3", "-W", "2", "1.1.1.1"],
    }.items():
        result = run(command)
        data[label] = result.stdout or result.stderr
    return data
