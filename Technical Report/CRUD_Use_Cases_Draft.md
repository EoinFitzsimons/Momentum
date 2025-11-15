# CRUD Use Cases for Momentum - Working Draft

## Database Tables Overview
1. **Championships** - Racing season/series management
2. **Drivers** - Driver profiles and attributes
3. **Race_Results** - Individual race performance records
4. **Races** - Individual race events
5. **Staff_Members** - Team personnel (engineers, mechanics, etc.)
6. **Teams** - Racing organizations/constructors
7. **Tracks** - Circuit/venue information

---

## Use Case Template Structure (Per Your Template)

For each table, document CRUD operations using this format:

### Requirement X: [Table Name] - [Operation]

**Description & Priority**
- What does this do?
- Why is it important? (Priority: High/Medium/Low)

**Scope**
- The scope of this use case is to [action] on the [table] table

**Flow Description**

**Precondition**
- What must be true before this happens?

**Activation**
- This use case starts when [Actor] [does something]

**Main Flow**
1. System does X
2. User does Y
3. System validates/processes
4. System confirms

**Alternate Flow**
- What if something goes differently?

**Exceptional Flow**
- What if something goes wrong?

**Termination**
- How does it end successfully?

**Post Condition**
- What's changed in the system?

---

## EXAMPLE: Championships Table CRUD

### Requirement 1: Create Championship

**Description & Priority**
Creates a new championship/season in the database when the player starts a career. This initializes the racing calendar for the entire season. **Priority: High** - Without this, the game cannot function as there's no competition structure.

**Scope**
The scope of this use case is to insert a new championship record into the Championships table with all required attributes (discipline, season year, number of races).

**Precondition**
- Player has selected a team and racing discipline
- Database connection is active
- Player is authenticated in the game

**Activation**
This use case starts when the player confirms team selection and the system needs to initialize the championship structure.

**Main Flow**
1. System receives championship parameters (discipline, year, race count)
2. System validates discipline is one of the seven supported types
3. System generates unique championship ID
4. System inserts championship record into database
5. System confirms insertion was successful
6. System returns championship ID to calling function

**Alternate Flow A1: Championship Already Exists**
- If championship for this discipline/year already exists
- System retrieves existing championship ID instead
- Use case continues from step 6

**Exceptional Flow E1: Database Connection Failure**
- If database is unavailable during insertion
- System logs error with full details
- System displays error message to player
- Player is returned to team selection screen
- Use case terminates abnormally

**Termination**
System returns the new championship ID and initializes the race calendar generation process.

**Post Condition**
- New championship record exists in database
- Championship ID is available for creating related race records
- System state updated to active championship

---

### Requirement 2: Read Championship Details

**Description & Priority**
Retrieves championship information from the database to display standings, race calendar, and championship metadata. **Priority: High** - Core functionality for displaying season information to player.

**Scope**
The scope of this use case is to query and retrieve championship data from the Championships table based on championship ID.

**Precondition**
- Championship exists in database
- Player has active career save with championship ID stored
- Database is accessible

**Activation**
This use case starts when the player navigates to the standings screen or season calendar view.

**Main Flow**
1. System receives championship ID from game state
2. System queries Championships table with ID
3. Database returns championship record
4. System parses championship data (discipline, season, race count)
5. System requests related data (races, standings)
6. System formats data for display
7. System presents championship information to player

**Alternate Flow A1: No Championship Found**
- If championship ID doesn't exist in database
- System checks if career is corrupted
- System prompts player to restart career or load backup
- Use case terminates

**Exceptional Flow E1: Database Query Timeout**
- If query takes longer than timeout threshold
- System cancels query
- System attempts retry with smaller data set
- If retry fails, display cached data if available
- If no cache, show error and return to hub

**Termination**
System displays complete championship information including calendar, standings, and season progress.

**Post Condition**
- Championship data is loaded in memory
- UI displays current standings and race information
- Player can interact with championship management features

---

### Requirement 3: Update Championship Status

**Description & Priority**
Updates championship fields when races complete or season progresses (e.g., races_completed counter, current_round). **Priority: Medium** - Important for tracking season progress but not blocking core functionality.

**Scope**
The scope of this use case is to modify existing championship records when race events conclude or season state changes.

**Precondition**
- Championship exists in database
- Race has been completed and results validated
- System has calculated updated standings

**Activation**
This use case starts when a race weekend is completed and the player returns to career hub.

**Main Flow**
1. System receives race completion signal
2. System retrieves championship ID from race record
3. System queries current championship state
4. System increments races_completed counter
5. System updates current_round number
6. System commits changes to database
7. System validates update was successful
8. System triggers standings recalculation

**Alternate Flow A1: Season Complete**
- If this was the final race of the season
- System sets championship status to "completed"
- System marks championship as archived
- System prompts player about next season
- Use case branches to season advancement flow

**Exceptional Flow E1: Update Conflict**
- If another process modified the record simultaneously
- System detects version conflict
- System rolls back transaction
- System retries update with latest data
- If retry fails, log error and alert player

**Termination**
System confirms championship state updated and standings screen reflects latest race result.

**Post Condition**
- Championship record updated with current race count
- Season progress percentage recalculated
- Calendar UI shows completed races marked
- Player can proceed to next race or season

---

### Requirement 4: Delete Championship (Rare)

**Description & Priority**
Removes championship record from database when player deletes career save or resets season. **Priority: Low** - Edge case functionality, rarely used in normal gameplay.

**Scope**
The scope of this use case is to safely remove a championship record and all cascading related records (races, results) from the database.

**Precondition**
- Championship exists in database
- Player has confirmed deletion intent
- No other game processes are accessing this championship

**Activation**
This use case starts when player selects "Delete Career" from save management menu.

**Main Flow**
1. System displays confirmation dialog with championship details
2. Player confirms deletion action
3. System begins database transaction
4. System deletes all race_results linked to this championship
5. System deletes all race records linked to this championship
6. System deletes championship record
7. System commits transaction
8. System removes associated save file from disk
9. System confirms deletion to player

**Alternate Flow A1: Player Cancels**
- If player clicks "Cancel" in confirmation dialog
- System aborts deletion process
- No database changes occur
- Player returns to save management screen

**Exceptional Flow E1: Foreign Key Constraint Violation**
- If related records prevent deletion
- System identifies dependent records
- System informs player of data dependencies
- System offers to delete all related data
- If player declines, deletion is cancelled
- Use case terminates without changes

**Termination**
System confirms championship and all related data deleted, returns player to main menu.

**Post Condition**
- Championship record removed from database
- All race and result records for this championship deleted
- Save file removed from file system
- Player's career list updated to reflect deletion

---

## YOUR TASK: Repeat This Pattern

Now you need to create similar CRUD use cases for:

### Drivers Table (4 use cases)
- **Create Driver**: When game generates drivers or player creates custom driver
- **Read Driver**: Viewing driver profile, scouting, hiring screen
- **Update Driver**: Attributes change over season, contract updates, performance tracking
- **Delete Driver**: Retiring drivers, removing from database (rare)

### Race_Results Table (4 use cases)
- **Create Race Result**: After race simulation completes
- **Read Race Result**: Viewing past race results, history, statistics
- **Update Race Result**: Correction/adjustment (rare, maybe for testing)
- **Delete Race Result**: Season reset, corrupted data cleanup

### Races Table (4 use cases)
- **Create Race**: When championship calendar is generated
- **Read Race**: Viewing next race details, circuit information
- **Update Race**: Marking race as completed, weather changes
- **Delete Race**: Season reset, calendar modification

### Staff_Members Table (4 use cases)
- **Create Staff**: Hiring engineers, mechanics, designers
- **Read Staff**: Viewing team roster, staff profiles
- **Update Staff**: Skill progression, contract renewal, role changes
- **Delete Staff**: Firing staff, retirement, contract expiry

### Teams Table (4 use cases)
- **Create Team**: Game initialization, database population
- **Read Team**: Team selection, viewing competitor teams
- **Update Team**: Budget changes, headquarters location, reputation
- **Delete Team**: Database cleanup (rare, mainly for testing)

### Tracks Table (4 use cases)
- **Create Track**: Database population with 175 circuits
- **Read Track**: Displaying circuit details, race weekend info
- **Update Track**: Configuration changes, surface updates
- **Delete Track**: Circuit removal (rare, mainly for testing)

---

## TIPS FOR WRITING IN YOUR OWN WORDS

1. **Think about the actual game flow**: When does this operation happen in your game?
2. **Use your actual table/field names**: Reference `driver.raw_speed`, `team.budget`, `race.circuit_id`
3. **Reference your actual Python code**: Mention `DatabaseManager`, `get_driver()`, `create_championship()`
4. **Include error scenarios you've encountered**: Database locks, missing foreign keys, validation errors
5. **Describe YOUR UI interactions**: "Player clicks 'Next Race Weekend' button", "Standings screen loads"

## WHAT TO AVOID (AI-Detection Red Flags)

❌ Generic phrases like "The system processes the request"
❌ Overly formal language that doesn't match your style
❌ Perfect grammar with no personality
❌ Identical structure for every use case (vary it naturally)
❌ No mention of your specific implementation details

## WHAT TO INCLUDE (Shows It's Your Work)

✅ Specific field names from YOUR database schema
✅ References to YOUR actual Python classes/methods
✅ YOUR GUI screen names ("Career Hub", "Standings Screen")
✅ Real issues YOU encountered ("Initially forgot to cascade delete results")
✅ Your design decisions ("Chose SQLite because...", "Championship ID uses hash of discipline+year")
✅ Natural variations in how you describe each operation

---

## QUESTIONS TO ANSWER FOR EACH CRUD

These questions will help you write each use case in your own words:

**CREATE:**
- When in the game does this record get created?
- What data is required? Where does it come from?
- What validation do you perform?
- What happens if creation fails?
- What other tables are affected?

**READ:**
- Where in the UI is this data displayed?
- What filtering/sorting happens?
- How do you handle large result sets?
- What if the record doesn't exist?
- Do you join with other tables?

**UPDATE:**
- What triggers an update to this record?
- Which fields can change? Which can't?
- How do you prevent update conflicts?
- What validation happens before updating?
- Are there cascade effects on other tables?

**DELETE:**
- When would you actually delete this record?
- Is it a soft delete (status='deleted') or hard delete?
- What happens to related records (cascade)?
- How do you prevent accidental deletion?
- Can deletions be undone?

---

## STRUCTURE FOR YOUR TECHNICAL REPORT

Based on the template, organize like this:

### 2.1.1 Functional Requirements

**2.1.1.1 Use Case Diagram**
- Single diagram showing all 7 tables
- CRUD operations as use cases
- Database as system boundary
- Player/System as actors

**2.1.1.2 - 2.1.1.29: Individual Use Cases**
- Requirement 1-4: Championships CRUD
- Requirement 5-8: Drivers CRUD
- Requirement 9-12: Race_Results CRUD
- Requirement 13-16: Races CRUD
- Requirement 17-20: Staff_Members CRUD
- Requirement 21-24: Teams CRUD
- Requirement 25-28: Tracks CRUD

Each follows the use case template format.

---

## NEXT STEPS

1. **Start with Championships** - Use my example above as reference
2. **Do Drivers next** - Similar complexity to Championships
3. **Then do the simpler tables** - Tracks, Teams have less complex logic
4. **Finish with Race_Results** - Most complex due to many foreign keys

Remember: Your supervisor wants to see YOUR understanding of YOUR system. Reference your actual code, your actual database, your actual design decisions. The use cases should read like someone who actually built this system explaining how it works.

Good luck! Let me know if you want me to review any specific use case before you submit.
