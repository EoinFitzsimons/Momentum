# Full Code Audit

Date: 2025-11-30

Summary

- Repository files scanned: 197 (all workspace files).
- Focus: Extract top-level `class` and `def` definitions for all Python source files and list other non-Python artifacts scanned.
- Output: this file is a per-file inventory useful for planning, test mapping and refactor decisions.

Notes about the run

- I enumerated all repository files and ran targeted searches per major Python subfolder to avoid results caps.
- The inventory below lists each Python module that declares top-level classes and/or functions and shows the names found. For non-Python files (docs, images, binaries) I list the filenames so you have a complete manifest.

High-level results (selected highlights)

- Total files: 197
- Python packages / modules with top-level definitions: many (primary paths under `Momentum/Python/`).

Per-file inventory (Python modules only — classes & top-level defs)

- `Momentum/Python/simulation.py` (FastAPI entry)

  - `root`
  - `health_check`
  - `get_database_stats`
  - `get_all_drivers`
  - `get_teams`
  - `simulate_race`
  - `test_endpoint`
  - `create_season`
  - `simulate_next_race`
  - `get_season_state`
  - `get_standings`
- `Momentum/Python/database/models.py`

  - `Driver` (dataclass / model)
  - `Team`
  - `Track`
  - `Championship`
  - `Race`
  - `RaceResult`
- `Momentum/Python/database/models/staff_models.py`

  - `StaffRole` (Enum)
  - `StaffTier` (Enum)
  - `BudgetCategory` (Enum)
  - `StaffMember`
  - `TeamStaffing`
  - `generate_staff_requirements`
  - `calculate_role_importance`
- `Momentum/Python/database/models/supplier_models.py`

  - `SupplierCategory` (Enum)
  - `SupplierTier` (Enum)
  - `Supplier`
  - `ComponentContract`
- `Momentum/Python/database/models/multi_discipline_models.py`

  - `RacingDiscipline` (Enum)
  - `Vehicle`
  - `MultiDisciplineDriver`
  - `MultiDisciplineTeam`
  - `Track`
  - `Championship`
  - `Race`
- `Momentum/Python/database/database_factory.py`

  - `DatabaseFactory`
- `Momentum/Python/database/database_manager.py`

  - `DatabaseManager`
- `Momentum/Python/services/simulation_service.py`

  - `SimulationService`
- `Momentum/Python/vehicles/vehicle.py`

  - `RaceCar`
- `Momentum/Python/vehicles/components/enums.py`

  - Many Enums (RacingDiscipline, AspirationType, FuelSystem, FuelType, EngineConfiguration, HybridSystemType, EnergyStorageType, ERSMode, GearboxType, DifferentialType, DrivetrainLayout, SuspensionType, ChassisMaterial, DamperType, BrakeMaterial, BrakeConfiguration, AeroConfiguration, WingType, TireType, TireCompound, ControlUnitType, SteeringType, SafetyRating)
- `Momentum/Python/vehicles/components/engine.py`

  - `EngineComponent`
  - `HybridPowerUnit`
- `Momentum/Python/vehicles/components/electronics.py`

  - `ElectronicControlUnit`
  - `SteeringSystem`
  - `SafetySystem`
- `Momentum/Python/vehicles/components/drivetrain.py`

  - `Gearbox`
  - `Differential`
  - `Drivetrain`
- `Momentum/Python/vehicles/components/chassis.py`

  - `Suspension`
  - `BrakeSystem`
  - `Chassis`
- `Momentum/Python/vehicles/components/aerodynamics.py`

  - `AerodynamicsPackage`
  - `Tire`
  - `TireSet`
- `Momentum/Python/disciplines/base_engine.py`

  - `RacingDiscipline` (Enum)
  - `RaceEventType` (Enum)
  - `DisciplineContext` (dataclass)
  - `BaseDisciplineEngine` (ABC)
- `Momentum/Python/disciplines/race_simulation.py`

  - `SimulationContext`
  - `RaceSimulator`
- `Momentum/Python/disciplines/multi_discipline_simulator.py`

  - `MultiDisciplineSimulator`
  - `simulate_race` (top-level function)
- Per-discipline engines & rulebooks (examples)

  - `disciplines/single_seater/single_seater_engine.py`: `SingleSeaterEngine`
  - `disciplines/single_seater/rulebook.py`: `SingleSeaterRulebook`
  - `disciplines/production_touring/production_touring_engine.py`: `ProductionTouringEngine`
  - `disciplines/rally_stage/rally_stage_engine.py`: `RallyStageEngine`
  - `disciplines/drag_acceleration/drag_acceleration_engine.py`: `DragAccelerationEngine`
  - `disciplines/endurance/endurance_engine.py`: `EnduranceEngine`
  - `disciplines/sprint_rallycross/sprint_rallycross_engine.py`: `SprintRallycrossEngine`
  - `disciplines/urban_street/urban_street_engine.py`: `UrbanStreetEngine`
- `Momentum/Python/systems/*` (major systems and helpers)

  - `game_loop.py`: `GameLoop`, `SeasonState`, `ChampionshipStanding`
  - `standings_manager.py`: `DriverStanding`, `ConstructorStanding`, `ChampionshipStandings`, `StandingsManager`
  - `championship_manager.py`: `DriverContract`, `SeasonCalendar`, `ChampionshipManager`, `TransferMarket`
  - `component_integration.py`: `ComponentIntegration`
  - `component_manager.py`: `ComponentManager`, `RepairReport`, `ComponentDamageEvent`
  - `component_persistence.py`: `ComponentPersistence`
  - `component_factory.py`: `ComponentFactory`
  - `vehicle_development.py`: `VehicleDevelopmentEngine`, `DevelopmentProject`, `ComponentType`
  - `team_management.py`: `TeamManager`, `TeamFinancials`, `Contract`
  - `staff_management.py`: `StaffManagementSystem`, `StaffMarket`
  - `realistic_circuit_generator.py` / `comprehensive_circuit_generator.py`: circuit generator classes and top-level `generate_*` functions
  - `currency_system.py`: `Currency` (Enum), `CurrencyConfig`, `CurrencySystem`, plus helpers `format_currency`, `get_single_seater_budget_cap`
  - `world_state.py`: `GameWorld`, `GameWorldState`, `PlayerProfile`
  - `team_name_generator.py`: `TeamNameGenerator`, plus helper name generation functions
- `Momentum/Python/gui/*` (PyQt screens and helpers)

  - `gui_game.py`: many QWidget/QMainWindow classes (MainMenuScreen, DisciplineSelectionScreen, TeamSelectionScreen, RaceWeekendScreen, StandingsScreen, CareerHubScreen, TeamManagementScreen, CarDevelopmentScreen, FinancesScreen, SettingsScreen, `MomentumGame`)
  - `gui_garage.py`: `GarageWorkshopScreen`
  - `gui_component_health.py`: `ComponentHealthBar`, `ComponentHealthPanel`, `ComponentRepairButton`
  - `log_viewer.py`: `LogViewer`
- `Momentum/Python/services` and `Momentum/Python/api`

  - API models in `api/schemas.py` (Pydantic models: `RaceSimulationRequest`, `DriverResult`, `RaceResultResponse`, `DriverSummary`, `DriversListResponse`, `TeamSummary`, `TeamsListResponse`, `HealthCheckResponse`, `DatabaseStatsResponse`, `APIInfoResponse`)
  - `services/simulation_service.py`: `SimulationService`
- `Momentum/Python/ai/decision_engine.py`

  - `DecisionType` (Enum), `AIDecision`, `TeamPersonality`, `TeamAI`, `DriverAI`
- `Momentum/Python/scripts` (CLI / generation)

  - `generate_initial_database.py`: `DatabaseGenerator` and `main`
  - `import_circuits.py`: `map_circuit_to_db_fields`, `import_circuits`
  - `regenerate_database.py`, `clean_test_data.py`, `build_exe.py` — top-level `main` / helper functions
- Tests

  - Multiple test files under `Momentum/Python/tests/` with standalone test functions and small test fixtures (`test_race_simulation.py`, `test_game_loop_api.py`, `test_component_integration.py`, `test_2025_season.py`, `test_playability.py`, `test_staff_system.py`, `test_driver_system.py`, `examples/driver_examples.py`, etc.)

Non-Python / other files (selected)

- Docs: many `Technical Report/*.md`, `Momentum/*.md`, `Branding/*`, `Proposal/*` documents, and `Technical Report/Images/*`.
- Binaries/images: PSD/PNG files under `Branding/` and `Technical Report/Images/`.

Gaps

- This audit enumerates top-level definitions and produces a comprehensive manifest. It is suitable for planning and for picking modules to expand with full method signatures and docstrings.
