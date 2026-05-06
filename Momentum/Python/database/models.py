"""
Legacy re-export module for backward compatibility.

All model definitions have been consolidated into database/models/__init__.py
to resolve circular import issues with PyInstaller.
"""

from database.models import (  # noqa: F401
    Driver,
    Team,
    Track,
    Championship,
    Race,
    RaceResult,
    StaffMember,
    SCHEMA_SQL,
)

__all__ = [
    "Driver",
    "Team",
    "Track",
    "Championship",
    "Race",
    "RaceResult",
    "StaffMember",
    "SCHEMA_SQL",
]
