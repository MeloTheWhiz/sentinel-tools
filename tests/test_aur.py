from __future__ import annotations

from sentinel_tools.aur import (
    ForeignPackage,
    parse_aur_updates,
    parse_foreign_packages,
)


def test_parse_foreign_packages() -> None:
    output = """
claude-desktop-bin 1.24012.9-1
yay 13.0.1-1
yay-debug 13.0.1-1
"""

    assert parse_foreign_packages(output) == (
        ForeignPackage(
            name="claude-desktop-bin",
            version="1.24012.9-1",
        ),
        ForeignPackage(
            name="yay",
            version="13.0.1-1",
        ),
        ForeignPackage(
            name="yay-debug",
            version="13.0.1-1",
        ),
    )


def test_parse_foreign_packages_ignores_blank_lines() -> None:
    output = "\n\n yay 13.0.1-1 \n\n"

    assert parse_foreign_packages(output) == (
        ForeignPackage(
            name="yay",
            version="13.0.1-1",
        ),
    )


def test_parse_foreign_packages_ignores_invalid_lines() -> None:
    output = """
invalid
yay 13.0.1-1
"""

    assert parse_foreign_packages(output) == (
        ForeignPackage(
            name="yay",
            version="13.0.1-1",
        ),
    )


def test_parse_aur_updates() -> None:
    output = """
claude-desktop-bin 1.24012.9-1 -> 1.24013.1-1
yay 13.0.1-1 -> 13.0.2-1
"""

    assert parse_aur_updates(output) == (
        "claude-desktop-bin",
        "yay",
    )


def test_parse_aur_updates_with_empty_output() -> None:
    assert parse_aur_updates("") == ()
