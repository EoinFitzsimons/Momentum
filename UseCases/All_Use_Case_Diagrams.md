````markdown
# Use Case Diagrams

This file contains the mermaid diagrams for each use case. Diagrams were moved from `All_Use_Cases_Detailed.md` to keep the primary document focused on textual use-case descriptions.

---

## UC-1: Read Driver Details

```mermaid
 flowchart TB
   %% Actors
   actorSim([Simulation Service])
   actorDB([Drivers DB])

   %% System boundary
   subgraph "Game Backend System"
     UC1((Read Driver Details))
   end

   actorSim --- UC1
   UC1 --- actorDB
```

---

## UC-2: Read Race Configuration

```mermaid
graph TB
  Sim([Simulation Service])
  UI([Client UI])
  subgraph "Game Backend System"
    UC((Read Race Configuration))
  end
  Sim --- UC
  UI --- UC
```

---

## UC-3: Create Race Result

```mermaid
graph TB
  Sim([Simulation Service])
  subgraph "Game Backend System"
    UC((Create Race Result))
  end
  Sim --- UC
```

---

## UC-4: Read Race Results

```mermaid
graph TB
  UI([User])
  subgraph "Game Backend System"
    UC((Read Race Results))
  end
  UI --- UC
```

---

## UC-5: Read Championship Details

```mermaid
graph TB
  UI([Client])
  subgraph "Game Backend System"
    UC((Read Championship Details))
  end
  UI --- UC
```

---

## UC-6: Update Championship Standings

```mermaid
graph TB
  Standings([Standings Service])
  subgraph "Game Backend System"
    UC((Update Championship Standings))
  end
  Standings --- UC
```

---

## UC-7: Create Race Event

```mermaid
graph TB
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Create Race Event))
  end
  Admin --- UC
```

---

## UC-8: Read Race Schedule

```mermaid
graph TB
  UI([User / UI])
  subgraph "Game Backend System"
    UC((Read Race Schedule))
  end
  UI --- UC
```

---

## UC-9: Update Race Status

```mermaid
graph TB
  Service([Simulation/Service])
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Update Race Status))
  end
  Service --- UC
  Admin --- UC
```

---

## UC-10: Create Championship

```mermaid
graph TB
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Create Championship))
  end
  Admin --- UC
```

---

## UC-11: Read Team Details

```mermaid
graph TB
  UI([Player / UI])
  subgraph "Game Backend System"
    UC((Read Team Details))
  end
  UI --- UC
```

---

## UC-12: Create New Team

```mermaid
graph TB
  Actor([Player/Admin])
  subgraph "Game Backend System"
    UC((Create New Team))
  end
  Actor --- UC
```

---

## UC-13: Read Team Details (player team)

```mermaid
graph TB
  Player([Player])
  subgraph "Game Backend System"
    UC((Read Player Team Details))
  end
  Player --- UC
```

---

## UC-14: Update Team Attributes

```mermaid
graph TB
  Actor([Player/Admin])
  subgraph "Game Backend System"
    UC((Update Team Attributes))
  end
  Actor --- UC
```

---

## UC-15: Read Available Drivers

```mermaid
graph TB
  Player([Player])
  AI([Team AI])
  subgraph "Game Backend System"
    UC((Read Available Drivers))
  end
  Player --- UC
  AI --- UC
```

---

## UC-16: Update Driver Contract

```mermaid
graph TB
  TM([Team Manager])
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Update Driver Contract))
  end
  TM --- UC
  Admin --- UC
```

---

## UC-17: Read Available Staff

```mermaid
graph TB
  Player([Player])
  subgraph "Game Backend System"
    UC((Read Available Staff))
  end
  Player --- UC
```

---

## UC-18: Update Staff Contract

```mermaid
graph TB
  Player([Player])
  TM([Team Manager])
  subgraph "Game Backend System"
    UC((Update Staff Contract))
  end
  Player --- UC
  TM --- UC
```

---

## UC-19: Update Driver Skills/Age

```mermaid
graph TB
  Scheduler([Game Loop / Scheduler])
  subgraph "Game Backend System"
    UC((Update Driver Skills/Age))
  end
  Scheduler --- UC
```

---

## UC-20: Update Team Budget

```mermaid
graph TB
  Finance([Finance System])
  Game([Game Loop])
  subgraph "Game Backend System"
    UC((Update Team Budget))
  end
  Finance --- UC
  Game --- UC
```

---

## UC-21: Create New Driver (rookie generation)

```mermaid
graph TB
  Admin([Admin/System])
  subgraph "Game Backend System"
    UC((Create New Driver))
  end
  Admin --- UC
```

---

## UC-22: Create New Staff Member (staff generation)

```mermaid
graph TB
  Admin([Admin/System])
  subgraph "Game Backend System"
    UC((Create New Staff Member))
  end
  Admin --- UC
```

---

## UC-23: Delete Championship

```mermaid
graph TB
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Delete Championship))
  end
  Admin --- UC
```

---

## UC-24: Create Custom Track

```mermaid
graph TB
  Designer([Designer/Admin])
  subgraph "Game Backend System"
    UC((Create Custom Track))
  end
  Designer --- UC
```

---

## UC-25: Update Track Characteristics

```mermaid
graph TB
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Update Track Characteristics))
  end
  Admin --- UC
```

---

## UC-26: Delete Track

```mermaid
graph TB
  Admin([Admin])
  subgraph "Game Backend System"
    UC((Delete Track))
  end
  Admin --- UC
```

---

## UC-27: Read Staff Performance Modifiers

```mermaid
graph TB
  Sim([Simulation Service])
  subgraph "Game Backend System"
    UC((Read Staff Performance Modifiers))
  end
  Sim --- UC
```

---

## UC-28: Update Driver Appearance

```mermaid
graph TB
  Player([Player])
  subgraph "Game Backend System"
    UC((Update Driver Appearance))
  end
  Player --- UC
```

---

## UC-29: Update Team Branding

```mermaid
graph TB
  Player([Player/Admin])
  subgraph "Game Backend System"
    UC((Update Team Branding))
  end
  Player --- UC
```

---

````
