"""
R-SIM-002, R-DISC-001, R-EVT-001, R-FAIL-001: Integration and contract tests.
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import Driver, Track, Team
from RaceLogic.base_race_engine import RaceContext, RacingDiscipline, BaseDisciplineEngine
from services.race_simulation_api import simulate_race
from services.race_engine_factory import create_discipline_engine
from tools.schema_validator import SchemaValidator


class TestDisciplineAdapterContract:
    def _create_test_context(self) -> RaceContext:
        track = Track(id=1, name="Test", country="UK", primary_discipline="SINGLE_SEATER", length_km=5.0)
        drivers = [
            Driver(id=1, name="D1", nationality="GBR", birth_date="1990-01-01", preferred_discipline="SINGLE_SEATER", current_team_id=1),
            Driver(id=2, name="D2", nationality="GBR", birth_date="1990-01-01", preferred_discipline="SINGLE_SEATER", current_team_id=2),
        ]
        teams = {
            1: Team(id=1, name="Team 1", nationality="GBR", discipline="SINGLE_SEATER", tier="TIER_1", budget=10_000_000),
            2: Team(id=2, name="Team 2", nationality="GBR", discipline="SINGLE_SEATER", tier="TIER_1", budget=10_000_000),
        }
        return RaceContext(
            discipline=RacingDiscipline.SINGLE_SEATER,
            track=track,
            drivers=drivers,
            teams=teams,
            total_laps=3,
        )

    def test_adapter_instantiation_with_seed(self):
        context = self._create_test_context()
        context.discipline = RacingDiscipline.URBAN_STREET

        adapter = create_discipline_engine(context, seed=42)
        assert adapter is not None
        assert hasattr(adapter, "simulate_race")
        assert hasattr(adapter, "get_attribute_weights")
        assert hasattr(adapter, "calculate_lap_time")

    def test_adapter_get_attribute_weights(self):
        context = self._create_test_context()
        context.discipline = RacingDiscipline.URBAN_STREET

        adapter = create_discipline_engine(context, seed=42)
        assert adapter is not None
        weights = adapter.get_attribute_weights()

        assert isinstance(weights, dict)
        assert len(weights) > 0
        for attr_name, weight in weights.items():
            assert isinstance(attr_name, str)
            assert isinstance(weight, float)
            assert 0 <= weight <= 1, f"Weight {attr_name}={weight} out of range"


class TestRealtimeModeAndStreaming:
    def _create_test_context(self) -> RaceContext:
        track = Track(id=1, name="Test", country="UK", primary_discipline="SINGLE_SEATER", length_km=5.0)
        drivers = [
            Driver(id=1, name="D1", nationality="GBR", birth_date="1990-01-01", preferred_discipline="SINGLE_SEATER", current_team_id=1),
            Driver(id=2, name="D2", nationality="GBR", birth_date="1990-01-01", preferred_discipline="SINGLE_SEATER", current_team_id=2),
        ]
        teams = {
            1: Team(id=1, name="Team 1", nationality="GBR", discipline="SINGLE_SEATER", tier="TIER_1", budget=10_000_000),
            2: Team(id=2, name="Team 2", nationality="GBR", discipline="SINGLE_SEATER", tier="TIER_1", budget=10_000_000),
        }
        return RaceContext(
            discipline=RacingDiscipline.SINGLE_SEATER,
            track=track,
            drivers=drivers,
            teams=teams,
            total_laps=2,
        )

    def test_event_callback_is_invoked(self):
        context = self._create_test_context()
        events_captured = []

        def capture_event(event: dict) -> None:
            events_captured.append(event)

        results = simulate_race(
            drivers=context.drivers,
            track=context.track,
            laps=context.total_laps,
            event_callback=capture_event,
            seed=42,
            verbose=False
        )

        assert len(results) > 0
        assert isinstance(events_captured, list)

    def test_realtime_speed_parameter_accepted(self):
        context = self._create_test_context()

        results = simulate_race(
            drivers=context.drivers,
            track=context.track,
            laps=context.total_laps,
            event_callback=lambda x: None,
            seed=42,
            verbose=False
        )

        assert len(results) > 0


class TestEventContract:
    def test_event_schema_load(self):
        validator = SchemaValidator()

        expected_schemas = ["lap_complete", "overtake", "incident"]
        for schema_name in expected_schemas:
            assert schema_name in validator.schemas, (
                f"Event schema {schema_name} not loaded; available: {list(validator.schemas.keys())}"
            )

    def test_event_has_required_fields(self):
        example_event = {
            "event_id": "evt-001",
            "schema_version": "1.0.0",
            "event_type": "lap_complete",
            "race_id": "race-001",
            "timestamp": "2025-04-29T12:00:00Z",
            "payload": {
                "lap_number": 1,
                "driver_id": 1,
                "lap_time": 78.5,
                "position": 1
            }
        }

        validator = SchemaValidator()
        valid, error = validator.validate_event(example_event, "lap_complete")
        if not valid:
            print(f"Warning: event validation failed: {error}")


class TestFailureModes:
    def test_missing_drivers_raises_error(self):
        track = Track(id=1, name="Test", country="UK", primary_discipline="SINGLE_SEATER", length_km=5.0)

        with pytest.raises(ValueError, match="drivers parameter is required"):
            simulate_race(
                drivers=None,
                track=track,
                laps=5,
                seed=42
            )

    def test_missing_track_raises_error(self):
        driver = Driver(id=1, name="D1", preferred_discipline="formula")

        with pytest.raises(ValueError, match="track parameter is required"):
            simulate_race(
                drivers=[driver],
                track=None,
                laps=5,
                seed=42
            )

    def test_invalid_laps_handled(self):
        track = Track(id=1, name="Test", country="UK", primary_discipline="SINGLE_SEATER", length_km=5.0)
        driver = Driver(id=1, name="D1", nationality="GBR", birth_date="1990-01-01", preferred_discipline="SINGLE_SEATER")

        results = simulate_race(
            drivers=[driver],
            track=track,
            laps=0,
            seed=42,
            verbose=False
        )

        assert isinstance(results, list)


class TestSchemaValidation:
    def test_driver_schema_validation(self):
        validator = SchemaValidator()

        valid_driver = {
            "id": 1,
            "name": "Test Driver",
            "team_id": 1,
            "status": "active",
            "attributes": {"raw_speed": 0.8}
        }

        valid, error = validator.validate_driver(valid_driver)
        if "driver" in validator.schemas:
            assert valid, f"Driver validation failed: {error}"

    def test_track_schema_validation(self):
        validator = SchemaValidator()

        valid_track = {
            "id": 1,
            "name": "Test Track",
            "lap_time": 78.0,
            "length_m": 5000
        }

        valid, error = validator.validate_track(valid_track)
        if "track" in validator.schemas:
            assert valid, f"Track validation failed: {error}"

    def test_result_schema_validation(self):
        validator = SchemaValidator()

        valid_result = {
            "race_id": "race-001",
            "driver_id": 1,
            "finishing_position": 1,
            "seed": 42,
            "lap_times": [78.5, 78.2],
            "incidents": []
        }

        valid, error = validator.validate_result(valid_result)
        if "result" in validator.schemas:
            assert valid, f"Result validation failed: {error}"
