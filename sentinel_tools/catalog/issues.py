from __future__ import annotations

from dataclasses import dataclass

from sentinel_tools.models import Severity


@dataclass(frozen=True)
class IssueDefinition:
    code: str
    severity: Severity
    category: str
    title: str
    explanation: str
    recommendation: str
    repair_id: str | None = None


ISSUES: dict[str, IssueDefinition] = {
    "SYS001": IssueDefinition(
        code="SYS001",
        severity=Severity.CRITICAL,
        category="services",
        title="System service failure",
        explanation=(
            "One or more system-level services entered a failed state. "
            "This can affect networking, hardware support, login services, "
            "background tasks, or other core system functions."
        ),
        recommendation="Inspect failed services with: systemctl --failed",
    ),
    "USR001": IssueDefinition(
        code="USR001",
        severity=Severity.WARNING,
        category="services",
        title="User service failure",
        explanation=(
            "One or more services running under the current user account "
            "failed to start or stopped unexpectedly."
        ),
        recommendation=("Inspect failed user services with: systemctl --user --failed"),
    ),
    "SVC001": IssueDefinition(
        code="SVC001",
        severity=Severity.CRITICAL,
        category="network",
        title="Network service inactive",
        explanation=(
            "NetworkManager is not currently active, so managed wired, "
            "wireless, VPN, and mobile network connections may be unavailable."
        ),
        recommendation=(
            "Inspect NetworkManager with: systemctl status NetworkManager; "
            "then enable it with: "
            "sudo systemctl enable --now NetworkManager"
        ),
        repair_id="enable-networkmanager",
    ),
    "SVC002": IssueDefinition(
        code="SVC002",
        severity=Severity.WARNING,
        category="services",
        title="Time synchronization inactive",
        explanation=(
            "Neither chronyd nor systemd-timesyncd appears to be active. "
            "An inaccurate clock can affect logs, certificates, "
            "authentication, software updates, and scheduled tasks."
        ),
        recommendation=(
            "Enable chronyd or systemd-timesyncd to keep the system clock accurate."
        ),
    ),
    "JRN001": IssueDefinition(
        code="JRN001",
        severity=Severity.WARNING,
        category="journal",
        title="High-priority boot errors",
        explanation=(
            "The system journal contains one or more high-priority events "
            "from the current boot after known harmless messages and "
            "duplicate events were removed."
        ),
        recommendation=("Review relevant boot errors with: journalctl -b -p err"),
    ),
    "PKG001": IssueDefinition(
        code="PKG001",
        severity=Severity.CRITICAL,
        category="packages",
        title="Package database problem",
        explanation=(
            "Pacman did not report a clean package database. Missing files, "
            "broken dependencies, or inconsistent package metadata may be "
            "present."
        ),
        recommendation="Check the package database with: pacman -Dk",
    ),
    "PKG002": IssueDefinition(
        code="PKG002",
        severity=Severity.INFO,
        category="packages",
        title="Orphan packages detected",
        explanation=(
            "Packages that were installed as dependencies are no longer "
            "required by any installed package."
        ),
        recommendation="Review orphan packages with: pacman -Qtdq",
    ),
    "STR001": IssueDefinition(
        code="STR001",
        severity=Severity.CRITICAL,
        category="storage",
        title="Root filesystem critically full",
        explanation=(
            "The root filesystem has reached a critically high usage level. "
            "The system may fail to write logs, install updates, create "
            "temporary files, or start services."
        ),
        recommendation=(
            "Free disk space immediately. Review usage with: "
            "sudo du -xhd1 / | sort -h; and inspect package caches, logs, "
            "downloads, and old snapshots."
        ),
    ),
    "STR002": IssueDefinition(
        code="STR002",
        severity=Severity.WARNING,
        category="storage",
        title="Root filesystem usage high",
        explanation=(
            "The root filesystem is approaching a critical usage level and "
            "should be cleaned before free space becomes insufficient."
        ),
        recommendation=(
            "Review root filesystem usage with: "
            "sudo du -xhd1 / | sort -h; then remove unnecessary files before "
            "space becomes critical."
        ),
    ),
}


def definition(code: str) -> IssueDefinition:
    return ISSUES[code]
