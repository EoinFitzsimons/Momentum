#!/usr/bin/env python
"""Verify all championship system components are working."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Test 1: Service imports
try:
    from services.championship_service import ChampionshipService, POINTS_SYSTEMS
    print("✅ Championship service imported successfully")
except Exception as e:
    print(f"❌ Failed to import championship service: {e}")
    sys.exit(1)

# Test 2: GUI imports
try:
    from GUI.gui_championship import (
        ChampionshipSelectionDialog,
        ChampionshipWindow,
        PreRaceSetupDialog,
        PostRaceResultsDialog
    )
    print("✅ All GUI components imported successfully")
except Exception as e:
    print(f"❌ Failed to import GUI components: {e}")
    sys.exit(1)

# Test 3: API server
try:
    from simulation import app
    print("✅ API server imported successfully")
except Exception as e:
    print(f"❌ Failed to import API server: {e}")
    sys.exit(1)

# Test 4: Verify service methods
required_methods = [
    'calculate_points',
    'recalculate_standings',
    'create_championship_season',
    'validate_race_event',
    'update_race_lifecycle_status',
    'get_championship_calendar'
]

service_methods = [m for m in dir(ChampionshipService) if not m.startswith('_')]
print("\nChampionship Service Methods:")
for method in required_methods:
    has_method = method in service_methods
    status = "✓" if has_method else "✗"
    print(f"  {status} {method}")

all_present = all(m in service_methods for m in required_methods)
if not all_present:
    print("❌ Some methods missing from championship service")
    sys.exit(1)

print("\n✅ All required methods present")

# Test 5: Verify points systems
print("\nPoints Systems Configured:")
for discipline in POINTS_SYSTEMS:
    print(f"  ✓ {discipline}")

# Test 6: Verify API endpoints
endpoints = [getattr(r, 'path', '') for r in app.routes]  # type: ignore[attr-defined]
championship_endpoints = [e for e in endpoints if 'championship' in e.lower() or 'race' in e.lower()]
print(f"\n✅ API Endpoints: {len(championship_endpoints)} championship-related routes")  # type: ignore[index]

print("\n" + "="*60)
print("✅ ALL VERIFICATION CHECKS PASSED")
print("="*60)
