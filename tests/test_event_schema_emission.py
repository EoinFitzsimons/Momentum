"""Validate events emitted during a short realtime run against JSON schemas."""

from __future__ import annotations

import pytest

from momentum.database.models import Driver, Track
from momentum.services.race_simulation_api import simulate_race
from tools.schema_validator import SchemaValidator


@pytest.mark.integration
def test_emitted_events_validate_against_schema():
    validator = SchemaValidator()
    if not getattr(validator, "schemas", None):
        pytest.skip("Event schemas not present; skipping event emission validation")

    events: list[dict] = []

    def capture(event: dict) -> None:
        events.append(event)

    track = Track(
        id=1,
        name="EvtTrack",
        country="UK",
        primary_discipline="SINGLE_SEATER",
        length_km=3.2,
    )
    driver = Driver(id=1, name="D1", nationality="GBR", birth_date="1990-01-01")

    simulate_race(
        drivers=[driver],
        track=track,
        laps=2,
        seed=42,
        event_callback=capture,
        verbose=False,
        player_overrides={"push": 1.0, "overtake": 1.0},
    )

    if not events:
        pytest.skip("Realtime run emitted no events; skipping schema validation")

    validated_any = False

    for ev in events:
        etype = ev.get("type") or ev.get("event_type")
        if not etype:
            continue

        schema_name = None
        if etype in {"lap_complete", "lap"}:
            schema_name = "lap_complete"
        elif etype == "overtake":
            schema_name = "overtake"
        elif etype in {"incident", "contact_during_overtake", "dnf"}:
            schema_name = "incident"

        if schema_name and schema_name in validator.schemas:
            valid, err = validator.validate_event(ev, schema_name)
            assert valid, f"Event failed schema {schema_name}: {err}"
            validated_any = True

    if not validated_any:
        pytest.skip("No schema-backed event types were produced in this run")
