from __future__ import annotations

from sentinel_tools.platforms import get_platform
from sentinel_tools.platforms.linux import filter_journal_output, service_state

__all__ = [
    "collect",
    "filter_journal_output",
    "service_state",
]


def collect() -> dict[str, str]:
    """Collect system information through the detected platform backend."""
    return get_platform().collect_system()
