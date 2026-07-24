from __future__ import annotations

from collections.abc import Callable, Iterable

from sentinel_tools.checks import network, security, storage, system

Collector = Callable[[], dict[str, str]]


class CheckRegistry:
    """Store and run diagnostic check collectors."""

    def __init__(self) -> None:
        self._checks: dict[str, Collector] = {}

    def register(self, name: str, collector: Collector) -> None:
        normalized = name.strip().lower()

        if not normalized:
            raise ValueError("Check name cannot be empty.")

        self._checks[normalized] = collector

    def available(self) -> tuple[str, ...]:
        return tuple(self._checks)

    def run(self, name: str) -> dict[str, str]:
        normalized = name.strip().lower()

        try:
            collector = self._checks[normalized]
        except KeyError as error:
            available = ", ".join(self.available())
            raise ValueError(
                f"Unknown diagnostic check '{name}'. Available checks: {available}"
            ) from error

        return collector()

    def run_all(
        self,
        names: Iterable[str] | None = None,
    ) -> dict[str, dict[str, str]]:
        selected = self.available() if names is None else tuple(names)

        return {name.strip().lower(): self.run(name) for name in selected}


registry = CheckRegistry()
registry.register("system", system.collect)
registry.register("network", network.collect)
registry.register("storage", storage.collect)
registry.register("security", security.collect)


def available_checks() -> tuple[str, ...]:
    """Return all registered checks."""
    return registry.available()


def run_check(name: str) -> dict[str, str]:
    """Run a single diagnostic check."""
    return registry.run(name)


def run_all(
    names: Iterable[str] | None = None,
) -> dict[str, dict[str, str]]:
    """Run multiple checks."""
    return registry.run_all(names)
