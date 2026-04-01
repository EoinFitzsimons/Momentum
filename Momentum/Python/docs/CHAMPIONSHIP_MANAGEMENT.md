# Championship Management System (UC-4 to UC-10)

## Overview

Complete implementation of the Championship Management System covering Use Cases 4 through 10. This system provides comprehensive championship lifecycle management, race scheduling, results tracking, and standings calculation with discipline-specific points systems.

## Issue Reference

- **GitHub Issue**: [#7 - Championship Management System](https://github.com/EoinFitzsimons/FinalProject/issues/7)
- **Priority**: MEDIUM (Career Mode - Final Submission)
- **Due Date**: March 15, 2026

## Implemented Use Cases

### UC-4: Read Race Results
- **Endpoint**: `GET /races/{id}/results`
- **Features**:
  - Complete race classification with lap data
  - Provisional/final status handling
  - Fastest lap tracking
  - DNF reason tracking
  - Gap to winner calculation

### UC-5: Read Championship Details
- **Endpoint**: `GET /championships/{id}`
- **Features**:
  - Championship metadata aggregation
  - Current season standings
  - Full race calendar
  - Archived championship support
  - Season-specific queries

### UC-6: Update Championship Standings
- **Endpoint**: `POST /championships/{id}/standings/recalculate`
- **Features**:
  - Discipline-specific points systems (7 different systems)
  - Tie-breaking rules (wins → podiums → fastest laps → consistency)
  - Automatic recalculation trigger
  - Historical standings preservation

### UC-7: Create Race Event
- **Endpoint**: `POST /championships/{id}/events`
- **Features**:
  - Date/track conflict validation
  - Track availability checks
  - Automatic round number assignment
  - Weather condition configuration

### UC-8: Read Race Schedule
- **Endpoint**: `GET /championships/{id}/schedule`
- **Features**:
  - Chronological race ordering
  - Status flag display (scheduled/in-progress/completed/cancelled)
  - Track information integration
  - Multi-season support

### UC-9: Update Race Status
- **Endpoint**: `PATCH /races/{id}/status`
- **Features**:
  - Lifecycle validation
  - Valid transitions: scheduled→in-progress→completed
  - Cancellation support
  - Event notification hooks (ready for future implementation)

### UC-10: Create Championship
- **Endpoint**: `POST /championships`
- **Features**:
  - Season rollover automation
  - Calendar generation
  - Rules validation
  - Multi-discipline support
  - Tier-based configuration

## Points Systems

Each racing discipline has a unique points allocation system:

| Discipline | System | Winner Points | Point-Scoring Positions |
|------------|--------|---------------|------------------------|
| SINGLE_SEATER | F1-style | 25 | Top 10 + FL bonus |
| ENDURANCE | Endurance-style | 25 | Top 15 |
| PRODUCTION_TOURING | Touring-style | 32 | Top 15 |
| URBAN_STREET | Drift-style | 25 | Top 10 + FL bonus |
| DRAG_ACCELERATION | Elimination-style | 20 | Top 8 |
| SPRINT_RALLYCROSS | Rallycross-style | 30 | Top 13 |

**Fastest Lap Bonus**: SINGLE_SEATER and URBAN_STREET disciplines award +1 point for fastest lap if finishing in top 10.

## Architecture

### File Structure

```
Momentum/Python/
├── simulation.py                          # Main API server (NEW)
├── services/
│   └── championship_service.py            # Business logic (NEW)
├── api/
│   └── schemas.py                         # Updated with championship schemas
├── database/
│   ├── models.py                          # Updated Championship/Race models
│   └── database_manager.py                # Existing (compatible)
└── tests/
    └── test_championship_management.py    # Comprehensive test suite (NEW)
```

### Service Layer

**championship_service.py** provides:
- Points calculation engine
- Standings recalculation with tie-breaking
- Season calendar management
- Race event validation
- Status lifecycle management

### Database Schema Updates

**Championships Table**:
```sql
CREATE TABLE championships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    discipline TEXT NOT NULL,
    season_length INTEGER NOT NULL,
    points_system TEXT NOT NULL,
    current_season INTEGER NOT NULL,
    tier TEXT DEFAULT 'TOP_TIER',
    founded_year INTEGER DEFAULT 2025,
    description TEXT DEFAULT '',
    archived INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Races Table**:
```sql
CREATE TABLE races (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    championship_id INTEGER NOT NULL,
    track_id INTEGER NOT NULL,
    season INTEGER NOT NULL,
    round_number INTEGER NOT NULL,
    race_date TEXT NOT NULL,
    weather_conditions TEXT DEFAULT '',
    laps INTEGER NOT NULL DEFAULT 0,
    race_duration_minutes INTEGER DEFAULT 90,
    status TEXT DEFAULT 'scheduled',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (championship_id) REFERENCES championships(id),
    FOREIGN KEY (track_id) REFERENCES tracks(id)
);
```

## API Usage Examples

### Create a Championship

```bash
POST /championships
Content-Type: application/json

{
  "name": "2025 Formula Championship",
  "discipline": "SINGLE_SEATER",
  "season_length": 20,
  "points_system": "standard",
  "tier": "TOP_TIER",
  "founded_year": 2025,
  "description": "Premier single-seater championship",
  "track_ids": [1, 2, 3, 4, 5],
  "start_date": "2025-03-15"
}
```

### Get Championship Details

```bash
GET /championships/1?season=1
```

Response includes:
- Championship metadata
- Current standings
- Full race calendar

### Update Race Status

```bash
PATCH /races/1/status
Content-Type: application/json

{
  "status": "in-progress"
}
```

### Recalculate Standings

```bash
POST /championships/1/standings/recalculate?season=1
```

Returns updated standings with all tie-breaking applied.

## Testing

### Run Integration Tests

```bash
cd Momentum/Python
python tests/test_championship_management.py
```

**Test Coverage**:
- ✓ Championship creation with calendar
- ✓ Race event scheduling and validation
- ✓ Race status lifecycle transitions
- ✓ Results tracking and retrieval
- ✓ Standings calculation with tie-breaking
- ✓ All 7 discipline points systems
- ✓ Championship details aggregation

### Test Results

```
============================================================
✓ ALL TESTS PASSED
============================================================

Features Verified:
  ✓ Championship creation with season rollover
  ✓ Race event scheduling with validation
  ✓ Race schedule retrieval
  ✓ Race status lifecycle management
  ✓ Race results tracking
  ✓ Championship standings calculation
  ✓ Discipline-specific points systems
  ✓ Tie-breaking rules
  ✓ Championship details aggregation
```

## Starting the API Server

```bash
cd Momentum/Python
python simulation.py
```

Or with uvicorn:

```bash
uvicorn simulation:app --reload --host 127.0.0.1 --port 8000
```

**API Documentation**: http://127.0.0.1:8000/docs

## Tie-Breaking Rules

When drivers are tied on points, the following rules apply in order:

1. **Total Wins** - Driver with more race victories
2. **Total Podiums** - Driver with more podium finishes
3. **Fastest Laps** - Driver with more fastest laps
4. **Races Started** - Driver with more race starts (consistency)

## Future Enhancements

The system is designed to support:

- [ ] Async job queue for large recalculations
- [ ] Real-time standings updates via WebSocket
- [ ] Event notification system (race status changes)
- [ ] Season archival and historical queries
- [ ] Team championship standings
- [ ] Constructor points calculations
- [ ] Multi-class championships (endurance)
- [ ] Sprint race support
- [ ] Reverse grid configurations

## Dependencies

All required dependencies are in `requirements.txt`:
- fastapi
- uvicorn
- pydantic
- sqlite3 (built-in)

## Technical Report Reference

This implementation addresses:
- **Section 2.1.1**: Championship Management Architecture
- **Section 3.2**: Use Case Implementation (UC-4 to UC-10)
- **Section 4.1**: Integration Testing

## Contributing

When extending this system:
1. Add new points systems to `POINTS_SYSTEMS` dict in `championship_service.py`
2. Update tie-breaking logic in `recalculate_standings()` if needed
3. Add new status transitions to `valid_transitions` dict in `update_race_lifecycle_status()`
4. Update API schemas in `api/schemas.py`
5. Add tests to `tests/test_championship_management.py`

## Licence

Part of Momentum Motorsport Simulation - Final Year Project
