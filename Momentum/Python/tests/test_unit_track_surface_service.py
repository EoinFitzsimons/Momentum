"""Unit tests for discipline/surface mapping logic."""

import pytest

from database.models import Track
from services.track_surface_service import TrackSurfaceService


@pytest.mark.unit
@pytest.mark.parametrize(
    "discipline,expected_surface",
    [
        ("SINGLE_SEATER", "asphalt"),
        ("PRODUCTION_TOURING", "asphalt"),
        ("URBAN_STREET", "concrete"),
        ("DRAG_ACCELERATION", "asphalt"),
        ("SPRINT_RALLYCROSS", "mixed"),
        ("ENDURANCE", "asphalt"),
    ],
)
def test_get_surface_for_discipline_returns_expected_primary(discipline, expected_surface):
    assert TrackSurfaceService.get_surface_for_discipline(discipline) == expected_surface


@pytest.mark.unit
def test_get_surface_for_unknown_discipline_defaults_to_asphalt():
    assert TrackSurfaceService.get_surface_for_discipline("UNKNOWN") == "asphalt"


@pytest.mark.unit
def test_get_grip_level_maps_known_and_unknown_surfaces():
    assert TrackSurfaceService.get_grip_level("asphalt") == 1.0
    assert TrackSurfaceService.get_grip_level("gravel") == 0.6
    assert TrackSurfaceService.get_grip_level("does_not_exist") == 0.9


@pytest.mark.unit
def test_assign_surface_to_track_sets_discipline_surface_when_track_is_default_asphalt():
    track = Track(
        id=0,
        name="Surface Test",
        country="UK",
        primary_discipline="SPRINT_RALLYCROSS",
        surface="asphalt",
    )

    updated = TrackSurfaceService.assign_surface_to_track(track, "SPRINT_RALLYCROSS")
    assert updated.surface == "mixed"


@pytest.mark.unit
def test_assign_surface_to_track_keeps_existing_non_default_surface():
    track = Track(
        id=0,
        name="Custom Surface",
        country="UK",
        primary_discipline="SINGLE_SEATER",
        surface="gravel",
    )

    updated = TrackSurfaceService.assign_surface_to_track(track, "SINGLE_SEATER")
    assert updated.surface == "gravel"
