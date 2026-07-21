from sentinel_tools.scoring.health import (
    Severity,
    calculate,
    journal_recommendation,
    relevant_journal_errors,
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
