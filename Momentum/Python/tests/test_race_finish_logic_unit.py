"""Unit tests for simplified race finish helper logic."""


def race_finished(driver_laps, total_laps):
    """Return True when the leader reached total laps or all active drivers are DNF."""
    active_drivers = [lap for lap in driver_laps if lap is not None]

    if not active_drivers:
        return True

    return max(active_drivers) >= total_laps


def test_race_finished_leader_completed():
    assert race_finished([3.0, 2.8, 2.5], total_laps=3)


def test_race_finished_leader_not_completed():
    assert not race_finished([2.9, 2.8, 2.5], total_laps=3)


def test_race_finished_all_completed():
    assert race_finished([3.0, 3.0, 3.0], total_laps=3)


def test_race_finished_with_dnf_entries():
    assert race_finished([3.0, None, 2.5], total_laps=3)


def test_race_finished_all_dnf():
    assert race_finished([None, None, None], total_laps=3)
