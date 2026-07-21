from sentinel_tools.core import confirm, have, header, run


def update() -> int:
    header("SENTINEL TOOLS — SYSTEM UPDATE")
    pacman = run(["pacman", "-Syu"], sudo=True)
    print(pacman.stdout or pacman.stderr)
    if not pacman.ok:
        return pacman.returncode

    if have("flatpak"):
        flatpak = run(["flatpak", "update", "-y"])
        print(flatpak.stdout or flatpak.stderr)
    return 0


def clean() -> int:
    header("SENTINEL TOOLS — SAFE CLEANUP")

    if have("paccache"):
        for command in (["paccache", "-rk2"], ["paccache", "-ruk0"]):
            result = run(command, sudo=True)
            print(result.stdout or result.stderr)
    else:
        print("Install pacman-contrib to enable package-cache cleanup.")

    if have("flatpak"):
        result = run(["flatpak", "uninstall", "--unused", "-y"])
        print(result.stdout or result.stderr)

    result = run(["pacman", "-Qtdq"])
    orphans = result.stdout.splitlines() if result.stdout else []
    if orphans:
        print("\nOrphan packages:")
        print("\n".join(orphans))
        if confirm("Remove these orphan packages?"):
            removal = run(["pacman", "-Rns", "--", *orphans], sudo=True)
            print(removal.stdout or removal.stderr)
    else:
        print("No orphan packages found.")

    if confirm("Remove archived journal logs older than 14 days?"):
        journal = run(["journalctl", "--vacuum-time=14d"], sudo=True)
        print(journal.stdout or journal.stderr)

    if have("fstrim"):
        trim = run(["fstrim", "-av"], sudo=True)
        print(trim.stdout or trim.stderr)
    return 0
