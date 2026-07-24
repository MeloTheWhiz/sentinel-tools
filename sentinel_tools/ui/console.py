from __future__ import annotations

import os
import sys


def color_enabled() -> bool:
    return (
        sys.stdout.isatty()
        and os.environ.get("NO_COLOR") is None
        and os.environ.get("TERM", "").lower() != "dumb"
    )


def style(text: str, code: str) -> str:
    if not color_enabled():
        return text
    return f"\033[{code}m{text}\033[0m"


def banner(version: str) -> None:
    print()
    print("+" + "-" * 70 + "+")
    print(f"| {style('SENTINEL TOOLS', '1;36'):<79}|")
    subtitle = f"System diagnostics and safe maintenance | v{version}"
    print(f"| {subtitle:<69} |")
    print("+" + "-" * 70 + "+")


def section(title: str) -> None:
    normalized = title.strip().upper()
    print()
    print(style(normalized, "1;36"))
    print("-" * min(max(len(normalized), 24), 72))


def status(label: str, message: str) -> None:
    codes = {"OK": "32", "INFO": "36", "WARN": "33", "ERROR": "31"}
    normalized = label.strip().upper()
    marker = style(f"[{normalized}]", codes.get(normalized, "1"))
    print(f"{marker} {message}")


def key_value(key: str, value: object) -> None:
    text = str(value).strip() or "None"
    label = style(f"{key}:", "1")
    if "\n" not in text:
        print(f"{label} {text}")
        return
    print(label)
    for line in text.splitlines():
        print(f"  {line}")


def command_hint(command: str, description: str) -> None:
    """Display a command with a short description."""
    print(f"  {command:<28} {description}")
