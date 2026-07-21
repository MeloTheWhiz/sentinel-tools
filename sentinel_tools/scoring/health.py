from __future__ import annotations

from dataclasses import dataclass, field


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

    journal_errors = data.get("High-priority errors from this boot", "None")
    if journal_errors.strip().lower() != "none":
        result.score -= 10
        result.warnings.append("The current boot contains high-priority errors.")
        result.recommendations.append(
            "Review boot errors with: journalctl -b -p err"
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
