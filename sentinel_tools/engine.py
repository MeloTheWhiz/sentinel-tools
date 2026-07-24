from __future__ import annotations

from collections.abc import Callable, Iterable

from sentinel_tools.checks import network, security, storage, system

Collector = Callable[[], dict[str, str]]

CHECKS: dict[str, Collector] = {
    "system": system.collect,
    "network": network.collect,
    "storage": storage.collect,
    "security": security.collect,
}


def available_checks() -> tuple[str, ...]:
    """Return all registered checks."""
    return tuple(CHECKS)


def run_check(name: str) -> dict[str, str]:
    """Run a single diagnostic check."""
    normalized = name.strip().lower()

    try:
        collector = CHECKS[normalized]
    except KeyError as error:
        available = ", ".join(available_checks())
        raise ValueError(
            f"Unknown diagnostic check '{name}'. Available checks: {available}"
        ) from error

    return collector()


def run_all(
    names: Iterable[str] | None = None,
) -> dict[str, dict[str, str]]:
    """Run multiple checks."""
    selected = available_checks() if names is None else tuple(names)

    return {name.lower(): run_check(name) for name in selected}
