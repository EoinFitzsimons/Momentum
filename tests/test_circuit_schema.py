import json

import pytest
from pathlib import Path

from momentum.data.circuit_schema import (
    FILES,
    CircuitError,
    load_circuits,
    parse_circuit,
    read_sources,
    validate_records,
)


def _shipped(discipline):
    return next(raw for _, raw in read_sources() if raw["primary_discipline"] == discipline)


def test_every_shipped_circuit_meets_its_schema_and_profile():
    circuits = load_circuits()
    assert len(circuits) == 150
    assert {c.discipline_key for c in circuits} == set(FILES)


def test_total_turns_are_derived_not_stored():
    raw = dict(_shipped("SINGLE_SEATER"))
    circuit = parse_circuit(raw)
    assert circuit.turns == raw["left_turns"] + raw["right_turns"]
    raw["turns"] = circuit.turns
    with pytest.raises(ValueError):
        parse_circuit(raw)


def test_a_field_from_another_discipline_is_refused():
    raw = dict(_shipped("SINGLE_SEATER"))
    raw["joker"] = {"extra_length_m": 60.0, "branch_at_fraction": 0.5}
    with pytest.raises(ValueError):
        parse_circuit(raw)


def test_rallycross_is_refused_a_long_straight():
    raw = dict(_shipped("SPRINT_RALLYCROSS"))
    raw["longest_straight_m"] = raw["length_km"] * 1000 * 0.4
    with pytest.raises(ValueError, match="longest straight"):
        parse_circuit(raw)


def test_drag_strip_has_no_lap_geometry():
    raw = _shipped("DRAG_ACCELERATION")
    record = parse_circuit(raw).to_record()
    assert record["is_point_to_point"] and record["turns"] == 0
    assert record["length_km"] == pytest.approx((402.34 + raw["shutdown_m"]) / 1000, abs=1e-3)
    with pytest.raises(ValueError):
        parse_circuit({**raw, "left_turns": 2})


def test_every_problem_is_reported_together(tmp_path):
    bad = dict(_shipped("PRODUCTION_TOURING"))
    bad["track_width_min_m"] = bad["track_width_max_m"] + 1
    good = _shipped("PRODUCTION_TOURING")
    _, errors = validate_records([("a.json", bad), ("b.json", good), ("c.json", dict(good))])
    assert any("track width" in e for e in errors)
    assert any("duplicate circuit id" in e for e in errors)
    for discipline, filename in FILES.items():
        records = [raw for _, raw in read_sources() if raw["primary_discipline"] == discipline]
        (tmp_path / filename).write_text(json.dumps(records), encoding="utf-8")
    (tmp_path / FILES["PRODUCTION_TOURING"]).write_text(json.dumps([bad]), encoding="utf-8")
    with pytest.raises(CircuitError, match="track width"):
        load_circuits(tmp_path)


@pytest.mark.unit
def test_every_source_file_ships_in_installed_builds():
    """pyproject's package-data must cover each per-discipline circuit file."""
    import tomllib
    from fnmatch import fnmatch

    root = Path(__file__).resolve().parents[1]
    with open(root / "pyproject.toml", "rb") as fh:
        patterns = tomllib.load(fh)["tool"]["setuptools"]["package-data"]["momentum.data"]
    data_dir = root / "momentum" / "data"
    for source in sorted((data_dir / "circuits").glob("*.json")):
        relative = source.relative_to(data_dir).as_posix()
        assert any(fnmatch(relative, pattern) for pattern in patterns), relative
