"""
Database Models Package

This package contains all database model definitions for the Momentum
motorsport simulation system.

Note: The main models (Driver, Team, Track, Championship, Race, RaceResult, SCHEMA_SQL)
are in the parent models.py file.
"""

import importlib.util
import sys
from pathlib import Path as _Path

# Add parent directory to path to import from models.py
parent_dir = _Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Now we can import from the models.py file in the parent database directory
# We need to be careful here - we're in database/models/__init__.py
# and we want to import from database/models.py
models_file = _Path(__file__).parent.parent / "models.py"
spec = importlib.util.spec_from_file_location("database_models_main", models_file)
assert (
    spec is not None and spec.loader is not None
), f"Failed to load spec for {models_file}"
models_main = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models_main)

# Export main models from models.py
Driver = models_main.Driver
Team = models_main.Team
Track = models_main.Track
Championship = models_main.Championship
Race = models_main.Race
RaceResult = models_main.RaceResult
StaffMember = models_main.StaffMember
SCHEMA_SQL = models_main.SCHEMA_SQL

# Import specialized models from submodules

__all__ = [
    # Main models (from models.py)
    "Driver",
    "Team",
    "Track",
    "Championship",
    "Race",
    "RaceResult",
    "StaffMember",
    "SCHEMA_SQL",
]
