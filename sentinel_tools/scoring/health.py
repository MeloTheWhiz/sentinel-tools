from __future__ import annotations

import re
from dataclasses import dataclass, field

from sentinel_tools.catalog import definition
from sentinel_tools.models import Issue, Severity

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

JOURNAL_PREFIX_PATTERN = re.compile(
    r"^(?:"
    r"(?:[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}"
    r"|\d{4}-\d{2}-\d{2}T\S+)"
    r"\s+\S+\s+"
    r")?"
    r"[^:\s]+(?:\[\d+\])?:\s*"
)

PROCESS_ID_PATTERN = re.compile(r"\[\d+\]")

Finding = Issue


@dataclass
class HealthScore:
    score: int = 100
    findings: list[Issue] = field(default_factory=list)

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
        code: str,
        message: str,
        penalty: int,
        severity: Severity | None = None,
        recommendation: str | None = None,
    ) -> None:
        issue_definition = definition(code)

        self.findings.append(
            Issue(
                code=issue_definition.code,
                severity=severity or issue_definition.severity,
                message=message,
                recommendation=(recommendation or issue_definition.recommendation),
                category=issue_definition.category,
                title=issue_definition.title,
                explanation=issue_definition.explanation,
                repair_id=issue_definition.repair_id,
            )
        )
        self.score -= penalty


def normalize_journal_line(line: str) -> str:
    normalized = line.strip()
    normalized = JOURNAL_PREFIX_PATTERN.sub("", normalized)
    normalized = PROCESS_ID_PATTERN.sub("[]", normalized)
    return " ".join(normalized.split())


def relevant_journal_errors(journal: str) -> list[str]:
    """Return unique journal events after removing expected noise."""
    if not journal.strip() or journal.strip().lower() == "none":
        return []

    relevant: list[str] = []
    seen: set[str] = set()
    current_event: list[str] = []

    def save_current_event() -> None:
        if not current_event:
            return

        first_line = current_event[0].strip()
        lowered = first_line.lower()

        if any(pattern in lowered for pattern in IGNORED_JOURNAL_PATTERNS):
            current_event.clear()
            return

        normalized = normalize_journal_line(first_line)
        key = normalized.lower()

        if key and key not in seen:
            seen.add(key)
            relevant.append(first_line)

        current_event.clear()

    for line in journal.splitlines():
        if not line.strip():
            continue

        is_continuation = line[:1].isspace()

        if is_continuation and current_event:
            current_event.append(line)
            continue

        save_current_event()
        current_event.append(line)

    save_current_event()

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


def journal_recommendation(errors: list[str]) -> str:
    combined = "\n".join(errors).lower()

    if "filesystem error" in combined or "corruption" in combined:
        return (
            "Review filesystem errors with: journalctl -b -p err; "
            "then inspect storage health and run the appropriate filesystem check "
            "from a safe environment."
        )

    if "i/o error" in combined or "device reset" in combined:
        return (
            "Inspect kernel device errors with: journalctl -k -b -p err; "
            "then check cables, USB devices, storage health, and hardware logs."
        )

    if "out of memory" in combined:
        return (
            "Inspect memory pressure with: journalctl -b | grep -i 'out of memory'; "
            "then review RAM, swap, and high-memory processes."
        )

    if "segmentation fault" in combined:
        return (
            "Identify the crashing process with: "
            "journalctl -b | grep -i 'segmentation fault'; "
            "then update, reinstall, or debug the affected application."
        )

    if "kernel panic" in combined:
        return (
            "Review the previous boot with: journalctl -k -b -1; "
            "then check recent kernel, driver, firmware, and hardware changes."
        )

    return "Review relevant boot errors with: journalctl -b -p err"


def root_filesystem_usage(filesystem_data: str) -> int | None:
    for line in filesystem_data.splitlines():
        stripped = line.strip()

        if not stripped or stripped.lower().startswith("filesystem"):
            continue

        match = re.search(r"\s(\d+)%\s+/\s*$", stripped)

        if match:
            return int(match.group(1))

    return None


def calculate(data: dict[str, str]) -> HealthScore:
    result = HealthScore()

    failed_system = data.get("Failed system services", "None")
    if failed_system.strip().lower() != "none":
        result.add_finding(
            code="SYS001",
            message="One or more system services have failed.",
            penalty=20,
        )

    failed_user = data.get("Failed user services", "None")
    if failed_user.strip().lower() != "none":
        result.add_finding(
            code="USR001",
            message="One or more user services have failed.",
            penalty=10,
        )

    network_manager = data.get("Service NetworkManager", "unknown").strip().lower()
    if network_manager not in {"active", "unknown"}:
        result.add_finding(
            code="SVC001",
            message="NetworkManager is not active.",
            penalty=15,
        )

    chrony = data.get("Service Chrony", "unknown").strip().lower()
    timesyncd = data.get("Service Systemd timesync", "unknown").strip().lower()

    known_time_services = {
        service for service in (chrony, timesyncd) if service != "unknown"
    }

    if known_time_services and "active" not in known_time_services:
        result.add_finding(
            code="SVC002",
            message="No supported time-synchronization service is active.",
            penalty=5,
        )

    journal = data.get("High-priority errors from this boot", "None")
    errors = relevant_journal_errors(journal)
    penalty = journal_penalty(errors)

    if penalty:
        result.add_finding(
            code="JRN001",
            message=(
                f"The current boot contains {len(errors)} "
                "relevant high-priority error(s)."
            ),
            penalty=penalty,
            severity=journal_severity(errors),
            recommendation=journal_recommendation(errors),
        )

    package_database = data.get("Package database", "")
    if "no database errors" not in package_database.lower():
        result.add_finding(
            code="PKG001",
            message="The package database may contain errors.",
            penalty=20,
        )

    orphan_packages = data.get("Orphan packages", "None")
    if orphan_packages.strip().lower() != "none":
        result.add_finding(
            code="PKG002",
            message="Orphan packages are installed.",
            penalty=5,
        )

    filesystem_data = data.get("Filesystem usage", "")
    root_usage = root_filesystem_usage(filesystem_data)

    if root_usage is not None and root_usage >= 95:
        result.add_finding(
            code="STR001",
            message=(f"The root filesystem is critically full at {root_usage}%."),
            penalty=20,
        )
    elif root_usage is not None and root_usage >= 85:
        result.add_finding(
            code="STR002",
            message=f"The root filesystem usage is high at {root_usage}%.",
            penalty=10,
        )

    result.score = max(0, min(100, result.score))
    return result
