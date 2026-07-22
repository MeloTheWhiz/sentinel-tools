from sentinel_tools.scoring.health import (
    Severity,
    calculate,
    journal_recommendation,
    relevant_journal_errors,
    root_filesystem_usage,
)


def healthy_data() -> dict[str, str]:
    return {
        "Failed system services": "None",
        "Failed user services": "None",
        "High-priority errors from this boot": "None",
        "Package database": "No database errors have been found!",
        "Orphan packages": "None",
    }


def test_healthy_system_scores_100() -> None:
    result = calculate(healthy_data())

    assert result.score == 100
    assert result.status == "Excellent"
    assert result.warnings == []


def test_failed_system_service_reduces_score() -> None:
    data = healthy_data()
    data["Failed system services"] = "example.service failed"

    result = calculate(data)

    assert result.score == 80
    assert result.status == "Good"
    assert "system services" in result.warnings[0]


def test_score_never_goes_below_zero() -> None:
    data = {
        "Failed system services": "failed",
        "Failed user services": "failed",
        "High-priority errors from this boot": "errors",
        "Package database": "corrupt",
        "Orphan packages": "many packages",
    }

    result = calculate(data)

    assert result.score >= 0


def test_expected_journal_messages_are_ignored() -> None:
    data = healthy_data()
    data["High-priority errors from this boot"] = "\n".join(
        [
            "kernel: virt/tdx: TDX not supported by the host platform",
            "kernel: Watchdog hardware is disabled",
            "sudo: a password is required",
        ]
    )

    result = calculate(data)

    assert result.score == 100
    assert result.warnings == []


def test_real_journal_error_reduces_score() -> None:
    data = healthy_data()
    data["High-priority errors from this boot"] = "kernel: device reset failed with -71"

    result = calculate(data)

    assert result.score < 100
    assert "relevant high-priority" in result.warnings[0]


def test_failed_system_service_is_critical() -> None:
    data = healthy_data()
    data["Failed system services"] = "example.service failed"

    result = calculate(data)

    assert result.findings[0].severity is Severity.CRITICAL


def test_orphan_packages_are_informational() -> None:
    data = healthy_data()
    data["Orphan packages"] = "unused-package"

    result = calculate(data)

    assert result.findings[0].severity is Severity.INFO


def test_serious_journal_error_is_critical() -> None:
    data = healthy_data()
    data["High-priority errors from this boot"] = "kernel: filesystem error detected"

    result = calculate(data)

    assert result.findings[0].severity is Severity.CRITICAL


def test_duplicate_journal_messages_are_collapsed() -> None:
    journal = "\n".join(
        [
            "Jul 21 18:00:01 host kernel: device reset failed with -71",
            "Jul 21 18:00:02 host kernel: device reset failed with -71",
            "Jul 21 18:00:03 host kernel: device reset failed with -71",
        ]
    )

    errors = relevant_journal_errors(journal)

    assert len(errors) == 1


def test_process_ids_do_not_prevent_deduplication() -> None:
    journal = "\n".join(
        [
            "example[1234]: connection failed",
            "example[5678]: connection failed",
        ]
    )

    errors = relevant_journal_errors(journal)

    assert len(errors) == 1


def test_distinct_journal_errors_are_preserved() -> None:
    journal = "\n".join(
        [
            "kernel: device reset failed with -71",
            "kernel: filesystem error detected",
        ]
    )

    errors = relevant_journal_errors(journal)

    assert len(errors) == 2


def test_filesystem_error_gets_filesystem_recommendation() -> None:
    recommendation = journal_recommendation(["kernel: filesystem error detected"])

    assert "filesystem" in recommendation.lower()
    assert "storage health" in recommendation.lower()


def test_device_reset_gets_hardware_recommendation() -> None:
    recommendation = journal_recommendation(
        ["kernel: usb device reset failed with -71"]
    )

    assert "journalctl -k" in recommendation
    assert "hardware" in recommendation.lower()


def test_out_of_memory_gets_memory_recommendation() -> None:
    recommendation = journal_recommendation(
        ["kernel: out of memory: killed process 1234"]
    )

    assert "memory pressure" in recommendation.lower()
    assert "swap" in recommendation.lower()


def test_unknown_journal_error_gets_default_recommendation() -> None:
    recommendation = journal_recommendation(["example.service: unexpected error"])

    assert recommendation == ("Review relevant boot errors with: journalctl -b -p err")


def test_failed_system_service_uses_sys001() -> None:
    result = calculate(
        {
            "Failed system services": "example.service",
            "Failed user services": "None",
            "High-priority errors from this boot": "None",
            "Package database": "No database errors found",
            "Orphan packages": "None",
        }
    )

    assert result.findings[0].code == "SYS001"


def test_failed_user_service_uses_usr001() -> None:
    result = calculate(
        {
            "Failed system services": "None",
            "Failed user services": "example-user.service",
            "High-priority errors from this boot": "None",
            "Package database": "No database errors found",
            "Orphan packages": "None",
        }
    )

    assert result.findings[0].code == "USR001"


def test_journal_error_uses_jrn001() -> None:
    result = calculate(
        {
            "Failed system services": "None",
            "Failed user services": "None",
            "High-priority errors from this boot": "kernel: device reset",
            "Package database": "No database errors found",
            "Orphan packages": "None",
        }
    )

    assert result.findings[0].code == "JRN001"


def test_package_database_error_uses_pkg001() -> None:
    result = calculate(
        {
            "Failed system services": "None",
            "Failed user services": "None",
            "High-priority errors from this boot": "None",
            "Package database": "Database validation failed",
            "Orphan packages": "None",
        }
    )

    assert result.findings[0].code == "PKG001"


def test_orphan_packages_use_pkg002() -> None:
    result = calculate(
        {
            "Failed system services": "None",
            "Failed user services": "None",
            "High-priority errors from this boot": "None",
            "Package database": "No database errors found",
            "Orphan packages": "unused-package",
        }
    )

    assert result.findings[0].code == "PKG002"


def test_inactive_networkmanager_uses_svc001() -> None:
    data = healthy_data()
    data["Service NetworkManager"] = "inactive"

    result = calculate(data)

    assert result.findings[0].code == "SVC001"
    assert result.findings[0].severity is Severity.CRITICAL
    assert result.score == 85


def test_active_networkmanager_creates_no_finding() -> None:
    data = healthy_data()
    data["Service NetworkManager"] = "active"

    result = calculate(data)

    assert result.findings == []


def test_inactive_time_services_use_svc002() -> None:
    data = healthy_data()
    data["Service Chrony"] = "inactive"
    data["Service Systemd timesync"] = "inactive"

    result = calculate(data)

    assert result.findings[0].code == "SVC002"
    assert result.findings[0].severity is Severity.WARNING
    assert result.score == 95


def test_active_chrony_satisfies_time_sync_check() -> None:
    data = healthy_data()
    data["Service Chrony"] = "active"
    data["Service Systemd timesync"] = "inactive"

    result = calculate(data)

    assert result.findings == []


def test_missing_service_data_does_not_create_findings() -> None:
    result = calculate(healthy_data())

    assert all(not finding.code.startswith("SVC") for finding in result.findings)


def test_root_filesystem_usage_is_parsed() -> None:
    filesystem_data = """\
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda2      ext4  100G   91G  9.0G  91% /
/dev/sda1      vfat  1.0G  100M  924M  10% /boot
"""

    assert root_filesystem_usage(filesystem_data) == 91


def test_root_filesystem_parser_ignores_other_mounts() -> None:
    filesystem_data = """\
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda2      ext4  100G   40G   60G  40% /
/dev/sdb1      ext4  500G  490G   10G  98% /mnt/storage
"""

    assert root_filesystem_usage(filesystem_data) == 40


def test_root_filesystem_parser_returns_none_for_invalid_data() -> None:
    assert root_filesystem_usage("Filesystem information unavailable") is None


def test_critical_root_usage_uses_str001() -> None:
    data = healthy_data()
    data["Filesystem usage"] = """\
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda2      ext4  100G   96G  4.0G  96% /
"""

    result = calculate(data)

    finding = next(finding for finding in result.findings if finding.code == "STR001")

    assert finding.severity is Severity.CRITICAL
    assert "96%" in finding.message
    assert result.score == 80


def test_high_root_usage_uses_str002() -> None:
    data = healthy_data()
    data["Filesystem usage"] = """\
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda2      ext4  100G   89G   11G  89% /
"""

    result = calculate(data)

    finding = next(finding for finding in result.findings if finding.code == "STR002")

    assert finding.severity is Severity.WARNING
    assert "89%" in finding.message
    assert result.score == 90


def test_healthy_root_usage_creates_no_storage_finding() -> None:
    data = healthy_data()
    data["Filesystem usage"] = """\
Filesystem     Type  Size  Used Avail Use% Mounted on
/dev/sda2      ext4  100G   50G   50G  50% /
"""

    result = calculate(data)

    assert all(not finding.code.startswith("STR") for finding in result.findings)


def test_missing_filesystem_data_creates_no_storage_finding() -> None:
    result = calculate(healthy_data())

    assert all(not finding.code.startswith("STR") for finding in result.findings)
