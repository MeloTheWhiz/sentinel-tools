from datetime import datetime
from pathlib import Path

from sentinel_tools.checks import network, security, storage, system


def save_text(path: Path) -> Path:
    sections = {
        "SYSTEM": system.collect(),
        "NETWORK": network.collect(),
        "STORAGE": storage.collect(),
        "SECURITY": security.collect(),
    }

    lines = [
        "SENTINEL TOOLS SYSTEM REPORT",
        f"Generated: {datetime.now().astimezone().isoformat()}",
    ]

    for title, values in sections.items():
        lines.extend(["", "=" * 72, title, "=" * 72])
        for key, value in values.items():
            lines.extend(["", f"{key}:", str(value)])

    path.write_text("\n".join(lines))
    return path
