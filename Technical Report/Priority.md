Feature Priority List - Momentum

HIGH PRIORITY - Must Have for Basic Playability

P1: Single Race Execution

Required CRUD Operations:

READ Drivers - Load driver attributes (skill, consistency, speed)

READ Teams - Load team capabilities (budget, performance level)

READ Races - Load race details (circuit, distance, conditions)

CREATE Race_Results - Save race outcomes (positions, points, times)

Use Cases Needed:

UC-1: Read Driver Details

UC-2: Read Team Details

UC-3: Read Race Configuration

UC-4: Create Race Result

Database Tables: Drivers (read), Teams (read), Races (read), Race_Results (create)

P2: View Race Results

Required CRUD Operations:

READ Race_Results - Display finishing positions, points, lap times

Use Cases Needed:

UC-5: Read Race Results

Database Tables: Race_Results (read)

P3: Championship Standings

Required CRUD Operations:

READ Championships - Load championship configuration (name, discipline, points system)

READ Race_Results - Aggregate points across multiple races

UPDATE Championships - Update standings after each race

Use Cases Needed:

UC-6: Read Championship Details

UC-7: Update Championship Standings

Database Tables: Championships (read, update), Race_Results (read)

P4: Multi-Race Season

Required CRUD Operations:

CREATE Races - Add races to championship calendar

READ Races - Display calendar/schedule

UPDATE Races - Mark races as completed

CREATE Race_Results - Save results for each race in season

Use Cases Needed:

UC-8: Create Race Event

UC-9: Read Race Schedule

UC-10: Update Race Status (scheduled → completed)

Database Tables: Races (create, read, update), Race_Results (create), Championships (read)

P5: Championship Creation

Required CRUD Operations:

CREATE Championships - Start new championship/season

Use Cases Needed:

UC-11: Create Championship (start new season)

Database Tables: Championships (create)

MEDIUM PRIORITY - Essential for Career Mode

P6: Team Management (Basic)

Required CRUD Operations:

CREATE Teams - Initialize player's team at career start

READ Teams - View team stats, budget, performance

UPDATE Teams - Modify budget, development level, reputation

Use Cases Needed:

UC-12: Create New Team (career start)

UC-13: Read Team Details (team screen)

UC-14: Update Team Attributes (budget changes, development)

Database Tables: Teams (create, read, update)

P7: Driver Hiring/Management

Required CRUD Operations:

READ Drivers - Browse available drivers

UPDATE Drivers - Assign driver to team (change team_id)

Use Cases Needed:

UC-15: Read Available Drivers (driver market)

UC-16: Update Driver Contract (hire/sign)

Database Tables: Drivers (read, update)
Note: No CREATE needed - 1,781 drivers already in database can be recycled

P8: Basic Staff Management

Required CRUD Operations:

READ Staff_Members - View available staff

UPDATE Staff_Members - Assign staff to team (change team_id)

Use Cases Needed:

UC-17: Read Available Staff

UC-18: Update Staff Contract (hire)

Database Tables: Staff_Members (read, update)
Note: No CREATE needed - 57,936 staff already in database can be recycled

P9: Driver Progression/Aging

Required CRUD Operations:

UPDATE Drivers - Modify skill attributes based on performance/age (or reset for retired drivers)

READ Race_Results - Analyze performance to determine progression

Use Cases Needed:

UC-19: Update Driver Skills/Age (end of season, or recycle retired drivers)

Database Tables: Drivers (update), Race_Results (read)

P10: Financial Management

Required CRUD Operations:

UPDATE Teams - Modify budget (income from sponsors, costs from salaries)

READ Teams - Display financial status

Use Cases Needed:

UC-20: Update Team Budget (end of race/season)

Database Tables: Teams (read, update)

LOW PRIORITY - Nice to Have / Polish

P11: Create New Drivers/Staff

Database has 1,781 drivers and 57,936 staff already. Can recycle existing entities by updating ages/attributes instead of creating new ones when people retire.

Required CRUD Operations:

CREATE Drivers - Generate new rookie drivers (optional enhancement)

CREATE Staff_Members - Generate new staff entering job market (optional enhancement)

Use Cases Needed:

UC-21: Create New Driver (rookie generation)

UC-22: Create New Staff Member (staff generation)

Database Tables: Drivers (create), Staff_Members (create)
Note: Not needed for basic gameplay - existing entities can be recycled

P12: Championship Cleanup

Required CRUD Operations:

DELETE Championships - Remove old/completed championships

Use Cases Needed:

UC-23: Delete Championship (cleanup old saves)

Database Tables: Championships (delete)

P13: Track Management

175 tracks already in circuits_database.json can be pre-populated.

Required CRUD Operations:

CREATE Tracks - Add custom tracks (nice to have, not essential)

UPDATE Tracks - Modify track characteristics (not essential)

DELETE Tracks - Remove unused tracks (not essential)

Use Cases Needed:

UC-24: Create Custom Track (advanced feature)

UC-25: Update Track Characteristics (advanced feature)

UC-26: Delete Track (cleanup)

Database Tables: Tracks (create, update, delete)
Note: READ Tracks is already covered in P1 (high priority)

P14: Staff Performance Impact

Required CRUD Operations:

READ Staff_Members - Get staff attributes (engineer skill, mechanic skill)

READ Teams - Apply staff bonuses to team performance in races

Use Cases Needed:

UC-27: Read Staff Performance Modifiers (during race simulation)

Database Tables: Staff_Members (read), Teams (read)

P15: Advanced Customization

Required CRUD Operations:

UPDATE Drivers - Change driver name/appearance (cosmetic)

UPDATE Teams - Change team name/colours (cosmetic)

Use Cases Needed:

UC-28: Update Driver Appearance (cosmetic)

UC-29: Update Team Branding (cosmetic)

Database Tables: Drivers (update), Teams (update)
Note: Already covered by existing UPDATE operations - just different use cases

Summary

 HIGH Priority (Must Have - Core Gameplay):

UC-1: Read Driver Details

UC-2: Read Race Configuration

UC-3: Create Race Result

MEDIUM Priority (Career Mode Depth):

UC-4: Read Race Results

UC-5: Read Championship Details

UC-6: Update Championship Standings

UC-7: Create Race Event

UC-8: Read Race Schedule

UC-9 Update Race Status

UC-10: Create Championship

UC-11: Read Team Details

UC-12: Create New Team

UC-13: Read Team Details (team screen)

UC-14: Update Team Attributes

UC-15: Read Available Drivers

UC-16: Update Driver Contract

UC-17: Read Available Staff

UC-18: Update Staff Contract

UC-19: Update Driver Skills/Age (includes recycling retired drivers)

UC-20: Update Team Budget

LOW Priority (Polish & Advanced Features):

UC-21: Create New Driver (not needed - recycle existing 1,781 drivers)

UC-22: Create New Staff Member (not needed - recycle existing 57,936 staff)

UC-23: Delete Championship

UC-24: Create Custom Track

UC-25: Update Track Characteristics

UC-26: Delete Track

UC-27: Read Staff Performance Modifiers

UC-28: Update Driver Appearance

UC-29: Update Team Branding
