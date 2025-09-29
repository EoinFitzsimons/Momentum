# Momentum API Documentation

## Overview

The Momentum Motorsport Simulation API provides comprehensive endpoints for managing and simulating multi-discipline racing events. Built with FastAPI, it offers interactive documentation, request validation, and high-performance race simulation capabilities.

## Base URL

```
http://localhost:8000
```

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

### System Information

#### GET /

Returns basic API information and available endpoints.

**Response:**
```json
{
  "message": "Momentum Simulation API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "database_stats": "/stats",
    "drivers": "/drivers",
    "teams": "/teams",
    "simulate_race": "/simulate/race"
  }
}
```

### Health Check

#### GET /health

Performs comprehensive system health check including database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "stats": {
    "drivers": 50,
    "teams": 20,
    "tracks": 15,
    "championships": 4,
    "races": 200,
    "race_results": 1500
  }
}
```

**Error Response (500):**
```json
{
  "detail": "Health check failed: Database connection error"
}
```

### Database Statistics

#### GET /stats

Returns detailed database statistics for system monitoring.

**Response:**
```json
{
  "database_stats": {
    "drivers": 50,
    "teams": 20,
    "tracks": 15,
    "championships": 4,
    "races": 200,
    "race_results": 1500
  }
}
```

### Driver Management

#### GET /drivers

Retrieves all drivers with comprehensive attributes and career statistics.

**Response:**
```json
{
  "drivers": [
    {
      "id": 1,
      "name": "Lewis Hamilton",
      "nationality": "GBR",
      "birth_date": "1985-01-07",
      "skill": 0.95,
      "consistency": 0.90,
      "aggression": 0.75,
      "racecraft": 0.98,
      "adaptability": 0.92,
      "career_wins": 103,
      "career_podiums": 182,
      "career_points": 4405,
      "biography": "Seven-time Formula 1 World Champion...",
      "current_team_id": 1
    }
  ],
  "count": 50
}
```

**Driver Attributes:**
- `skill`: Raw driving talent (0.0-1.0)
- `consistency`: Performance reliability (0.0-1.0) 
- `aggression`: Risk-taking tendency (0.0-1.0)
- `racecraft`: Strategic intelligence (0.0-1.0)
- `adaptability`: Environmental adaptation (0.0-1.0)

### Team Management

#### GET /teams

Retrieves teams with optional filtering by racing discipline.

**Parameters:**
- `discipline` (optional): Filter by racing discipline
  - Valid values: `formula`, `rally`, `endurance`, `street`

**Example Requests:**
```bash
# Get all teams
GET /teams

# Get Formula racing teams only
GET /teams?discipline=formula

# Get Rally teams only  
GET /teams?discipline=rally
```

**Response:**
```json
{
  "teams": [
    {
      "id": 1,
      "name": "Mercedes AMG F1 Team",
      "nationality": "GER",
      "founded_year": 2010,
      "discipline": "formula",
      "tier": "tier1",
      "budget": 400.0,
      "headquarters": "Brackley, UK",
      "team_principal": "Toto Wolff",
      "biography": "The most successful Formula 1 team...",
      "total_wins": 125,
      "total_podiums": 250,
      "championships": 8
    }
  ],
  "count": 12,
  "discipline": "formula"
}
```

**Team Tiers:**
- `tier1`: Elite teams (budget: 300-500M)
- `tier2`: Midfield teams (budget: 100-200M)  
- `tier3`: Smaller teams (budget: 50-100M)

### Race Simulation

#### POST /simulate/race

Executes Monte Carlo-based race simulation with specified parameters.

**Request Body:**
```json
{
  "race_id": 1,
  "weather_conditions": "dry",
  "participants": [
    {
      "driver_id": 1,
      "team_id": 1
    },
    {
      "driver_id": 2,
      "team_id": 1
    },
    {
      "driver_id": 3,
      "team_id": 2
    }
  ]
}
```

**Request Parameters:**
- `race_id` (optional): Race event identifier (default: 1)
- `weather_conditions` (optional): Weather during race
  - Valid values: `dry`, `wet`, `mixed` (default: `dry`)
- `participants`: Array of race participants
  - `driver_id`: Driver identifier (required)
  - `team_id`: Team identifier (required)

**Response:**
```json
{
  "race_id": 1,
  "weather": "dry",
  "results": [
    {
      "driver_id": 1,
      "team_id": 1,
      "position": 1,
      "points": 25,
      "fastest_lap": true
    },
    {
      "driver_id": 2,
      "team_id": 1,
      "position": 2,
      "points": 18,
      "fastest_lap": false
    }
  ],
  "simulation_status": "completed"
}
```

**Points System (Formula 1 Standard):**
- 1st: 25 points
- 2nd: 18 points
- 3rd: 15 points
- 4th: 12 points
- 5th: 10 points
- 6th: 8 points
- 7th: 6 points
- 8th: 4 points
- 9th: 2 points
- 10th: 1 point
- Fastest lap: +1 point (if in top 10)

**Error Response (500):**
```json
{
  "detail": "Simulation failed: Invalid participant data"
}
```

### Legacy Test Endpoint

#### GET /test

Simple connectivity test endpoint for debugging.

**Response:**
```json
{
  "message": "Simulation test successful."
}
```

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `400`: Bad Request - Invalid parameters
- `404`: Not Found - Resource doesn't exist
- `422`: Validation Error - Request body validation failed
- `500`: Internal Server Error - System error

**Standard Error Response:**
```json
{
  "detail": "Error description"
}
```

**Validation Error Response:**
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production deployment, consider:
- Request rate limits per IP
- Authentication and authorization
- Input validation and sanitization

## Example Usage

### Python Client
```python
import requests

# Get all drivers
response = requests.get("http://localhost:8000/drivers")
drivers = response.json()

# Run race simulation
simulation_request = {
    "race_id": 1,
    "weather_conditions": "wet",
    "participants": [
        {"driver_id": 1, "team_id": 1},
        {"driver_id": 2, "team_id": 2}
    ]
}

response = requests.post(
    "http://localhost:8000/simulate/race",
    json=simulation_request
)
results = response.json()
```

### JavaScript Client
```javascript
// Get Formula teams
const response = await fetch('http://localhost:8000/teams?discipline=formula');
const teams = await response.json();

// Run simulation
const simulation = await fetch('http://localhost:8000/simulate/race', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        race_id: 1,
        weather_conditions: 'dry',
        participants: [
            { driver_id: 1, team_id: 1 },
            { driver_id: 2, team_id: 2 }
        ]
    })
});

const results = await simulation.json();
```

### cURL Examples
```bash
# Health check
curl http://localhost:8000/health

# Get drivers
curl http://localhost:8000/drivers

# Get Formula teams
curl "http://localhost:8000/teams?discipline=formula"

# Run race simulation
curl -X POST http://localhost:8000/simulate/race \
  -H "Content-Type: application/json" \
  -d '{
    "race_id": 1,
    "weather_conditions": "wet",
    "participants": [
      {"driver_id": 1, "team_id": 1},
      {"driver_id": 2, "team_id": 2}
    ]
  }'
```

## Development Notes

- The API uses FastAPI's automatic validation and serialization
- All endpoints return JSON responses
- Database operations use SQLite with connection pooling
- Monte Carlo simulation runs 1000 iterations by default
- Results are deterministic when using the same random seed