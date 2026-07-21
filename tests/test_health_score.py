from sentinel_tools.scoring.health import calculate


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
    data["High-priority errors from this boot"] = (
        "kernel: device reset failed with -71"
    )

    result = calculate(data)

    assert result.score < 100
    assert "relevant high-priority" in result.warnings[0]
