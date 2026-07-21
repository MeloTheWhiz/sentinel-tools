from __future__ import annotations

from dataclasses import dataclass, field


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


@dataclass
class HealthScore:
    score: int = 100
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.score >= 90:
            return "Excellent"
        if self.score >= 75:
            return "Good"
        if self.score >= 60:
            return "Needs attention"
        return "Critical"


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


def calculate(data: dict[str, str]) -> HealthScore:
    result = HealthScore()

    failed_system = data.get("Failed system services", "None")
    if failed_system.strip().lower() != "none":
        result.score -= 20
        result.warnings.append("One or more system services have failed.")
        result.recommendations.append(
            "Inspect failed services with: systemctl --failed"
        )

    failed_user = data.get("Failed user services", "None")
    if failed_user.strip().lower() != "none":
        result.score -= 10
        result.warnings.append("One or more user services have failed.")
        result.recommendations.append(
            "Inspect failed user services with: systemctl --user --failed"
        )

    journal = data.get("High-priority errors from this boot", "None")
    errors = relevant_journal_errors(journal)
    penalty = journal_penalty(errors)

    if penalty:
        result.score -= penalty
        result.warnings.append(
            f"The current boot contains {len(errors)} relevant high-priority error(s)."
        )
        result.recommendations.append(
            "Review relevant boot errors with: journalctl -b -p err"
        )

    package_database = data.get("Package database", "")
    if "no database errors" not in package_database.lower():
        result.score -= 20
        result.warnings.append("The package database may contain errors.")
        result.recommendations.append(
            "Check the package database with: pacman -Dk"
        )

    orphan_packages = data.get("Orphan packages", "None")
    if orphan_packages.strip().lower() != "none":
        result.score -= 5
        result.warnings.append("Orphan packages are installed.")
        result.recommendations.append(
            "Review orphan packages with: pacman -Qtdq"
        )

    result.score = max(0, min(100, result.score))
    return result
