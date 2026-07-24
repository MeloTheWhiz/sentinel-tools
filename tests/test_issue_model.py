from __future__ import annotations

from sentinel_tools.models import Issue, Severity
from sentinel_tools.scoring.health import Finding


def test_issue_stores_structured_metadata() -> None:
    issue = Issue(
        code="SVC001",
        severity=Severity.CRITICAL,
        message="NetworkManager is not active.",
        recommendation="Enable NetworkManager.",
        category="network",
        title="Network service inactive",
        explanation="The primary Linux network service is not running.",
        repair_id="enable-networkmanager",
    )

    assert issue.code == "SVC001"
    assert issue.category == "network"
    assert issue.title == "Network service inactive"
    assert issue.display_title == "Network service inactive"
    assert issue.repair_id == "enable-networkmanager"


def test_issue_uses_message_as_fallback_title() -> None:
    issue = Issue(
        code="SYS001",
        severity=Severity.WARNING,
        message="A system service failed.",
        recommendation="Inspect failed services.",
    )

    assert issue.display_title == "A system service failed."


def test_finding_remains_a_compatibility_alias() -> None:
    finding = Finding(
        "SYS001",
        Severity.CRITICAL,
        "A system service failed.",
        "Inspect failed services.",
    )

    assert isinstance(finding, Issue)
    assert finding.code == "SYS001"
