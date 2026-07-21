from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


IGNORED_JOURNAL_PATTERNS = (
    "tdx not supported by the host platform",
    "watchdog hardware is disabled",
    "a password is required",
    "conversation failed",
    "auth could not identify password",
)

SERIOUS_JOURNAL_PATTERNS = (
    "i/o error",
    "filesystem error",
    "corruption",
    "segmentation fault",
    "kernel panic",
    "out of memory",
    "failed with",
    "device reset",
)


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass(frozen=True)
class Finding:
    severity: Severity
    message: str
    recommendation: str


@dataclass
class HealthScore:
    score: int = 100
    findings: list[Finding] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.score >= 90:
            return "Excellent"
        if self.score >= 75:
            return "Good"
        if self.score >= 60:
            return "Needs attention"
        return "Critical"

    @property
    def warnings(self) -> list[str]:
        return [finding.message for finding in self.findings]

    @property
    def recommendations(self) -> list[str]:
        return [finding.recommendation for finding in self.findings]

    def add_finding(
        self,
        *,
        severity: Severity,
        message: str,
        recommendation: str,
        penalty: int,
    ) -> None:
        self.findings.append(
            Finding(
                severity=severity,
                message=message,
                recommendation=recommendation,
            )
        )
        self.score -= penalty


def relevant_journal_errors(journal: str) -> list[str]:
    if journal.strip().lower() == "none":
        return []

    relevant: list[str] = []

    for line in journal.splitlines():
        lowered = line.lower()

        if any(pattern in lowered for pattern in IGNORED_JOURNAL_PATTERNS):
            continue

        if line.strip():
            relevant.append(line)

    return relevant


def journal_penalty(errors: list[str]) -> int:
    if not errors:
        return 0

    serious_count = sum(
        any(pattern in line.lower() for pattern in SERIOUS_JOURNAL_PATTERNS)
        for line in errors
    )

    if serious_count:
        return min(20, 10 + serious_count * 2)

    return 5


def journal_severity(errors: list[str]) -> Severity:
    serious = any(
        any(pattern in line.lower() for pattern in SERIOUS_JOURNAL_PATTERNS)
        for line in errors
    )
    return Severity.CRITICAL if serious else Severity.WARNING


def calculate(data: dict[str, str]) -> HealthScore:
    result = HealthScore()

    failed_system = data.get("Failed system services", "None")
    if failed_system.strip().lower() != "none":
        result.add_finding(
            severity=Severity.CRITICAL,
            message="One or more system services have failed.",
            recommendation="Inspect failed services with: systemctl --failed",
            penalty=20,
        )

    failed_user = data.get("Failed user services", "None")
    if failed_user.strip().lower() != "none":
        result.add_finding(
            severity=Severity.WARNING,
            message="One or more user services have failed.",
            recommendation=(
                "Inspect failed user services with: systemctl --user --failed"
            ),
            penalty=10,
        )

    journal = data.get("High-priority errors from this boot", "None")
    errors = relevant_journal_errors(journal)
    penalty = journal_penalty(errors)

    if penalty:
        result.add_finding(
            severity=journal_severity(errors),
            message=(
                f"The current boot contains {len(errors)} "
                "relevant high-priority error(s)."
            ),
            recommendation=(
                "Review relevant boot errors with: journalctl -b -p err"
            ),
            penalty=penalty,
        )

    package_database = data.get("Package database", "")
    if "no database errors" not in package_database.lower():
        result.add_finding(
            severity=Severity.CRITICAL,
            message="The package database may contain errors.",
            recommendation="Check the package database with: pacman -Dk",
            penalty=20,
        )

    orphan_packages = data.get("Orphan packages", "None")
    if orphan_packages.strip().lower() != "none":
        result.add_finding(
            severity=Severity.INFO,
            message="Orphan packages are installed.",
            recommendation="Review orphan packages with: pacman -Qtdq",
            penalty=5,
        )

    result.score = max(0, min(100, result.score))
    return result
