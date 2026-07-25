import pytest

from sentinel_tools.catalog import ISSUES, IssueDefinition, definition
from sentinel_tools.models import Severity


def test_definition_returns_registered_issue() -> None:
    issue = definition("USR001")

    assert isinstance(issue, IssueDefinition)
    assert issue.code == "USR001"
    assert issue.severity is Severity.WARNING
    assert issue.category == "services"
    assert issue.title == "User service failure"


def test_networkmanager_definition_has_repair_id() -> None:
    issue = definition("SVC001")

    assert issue.repair_id == "enable-networkmanager"


def test_catalog_contains_all_current_health_codes() -> None:
    expected_codes = {
        "SYS001",
        "USR001",
        "SVC001",
        "SVC002",
        "JRN001",
        "PKG001",
        "PKG002",
        "STR001",
        "STR002",
    }

    assert set(ISSUES) == expected_codes


def test_unknown_issue_code_raises_key_error() -> None:
    with pytest.raises(KeyError):
        definition("UNKNOWN")
