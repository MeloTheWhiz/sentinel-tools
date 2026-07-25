import pytest

from sentinel_tools.repairs import (
    REPAIRS,
    RepairRisk,
    available_repairs,
    repair_definition,
)


def test_networkmanager_repair_is_registered() -> None:
    repair = repair_definition("enable-networkmanager")

    assert repair.repair_id == "enable-networkmanager"
    assert repair.title == "Enable NetworkManager"
    assert repair.requires_root is True
    assert repair.risk is RepairRisk.LOW
    assert repair.supported_platforms == ("linux",)
    assert repair.commands == (
        ("systemctl", "is-enabled", "NetworkManager"),
        ("sudo", "systemctl", "enable", "NetworkManager"),
        ("sudo", "systemctl", "start", "NetworkManager"),
        ("systemctl", "is-active", "NetworkManager"),
    )


def test_available_repairs_returns_registered_repairs() -> None:
    repairs = available_repairs()

    assert len(repairs) == len(REPAIRS)
    assert repair_definition("enable-networkmanager") in repairs


def test_repair_contains_documented_steps() -> None:
    repair = repair_definition("enable-networkmanager")

    assert len(repair.steps) == 4
    assert "Verify that NetworkManager is active." in repair.steps


def test_unknown_repair_raises_key_error() -> None:
    with pytest.raises(KeyError):
        repair_definition("unknown-repair")
