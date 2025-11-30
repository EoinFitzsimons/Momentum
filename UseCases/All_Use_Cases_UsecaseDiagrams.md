# Use Case Diagrams — All Use Cases (UC-1 .. UC-29)

This file contains mermaid `flowchart TB` diagrams that emulate UML use-case diagrams (actors + system boundary + use cases). Paste into a Markdown viewer that supports mermaid or render with `mmdc`.

%% Styling init: set a consistent font and size for Word/print
%%{init: {"theme":"base","themeVariables":{"fontFamily":"Segoe UI, Arial, sans-serif","fontSize":"13px"}}}%%

### UC-1: Read Driver Details
```mermaid
flowchart TB
    %% actors
    U[User]

    %% system boundary
    subgraph System
        R([Read Driver Details])
    end

    %% associations
    U --- R
```

---

### UC-2: Read Team Details
```mermaid
flowchart TB
    %% actors
    U[User]

    subgraph System
        R([Read Team Details])
    end

    U --- R
```

---

### UC-3: Read Race Configuration
```mermaid
flowchart TB
    %% actors
    C[Client]
    S[Simulation Service]

    %% system boundary using subgraph
    subgraph System
        R([Read Race Configuration])
    end

    %% associations
    C --- R
    S --- R
```

---

### UC-4: Create Race Result
```mermaid
flowchart TB
    S[Simulation Service]
    A[Admin]

    subgraph System
        R([Create Race Result])
    end

    S --- R
    A --- R
```

---

### UC-5: Read Race Results
```mermaid
flowchart TB
    U[User]
    SS[Standings Service]

    subgraph System
        R([Read Race Results])
    end

    U --- R
    SS --- R
```

---

### UC-6: Read Championship Details
```mermaid
flowchart TB
    U[User]
    EC[External Client]

    subgraph System
        R([Read Championship Details])
    end

    U --- R
    EC --- R
```

---

### UC-7: Update Championship Standings
```mermaid
flowchart TB
    SS[Standings Service]

    subgraph System
        R([Update Championship Standings])
    end

    SS --- R
```

---

### UC-8: Create Race Event
```mermaid
flowchart TB
    GM[Game Manager]
    SCH[Scheduler]

    subgraph System
        R([Create Race Event])
    end

    GM --- R
    SCH --- R
```

---

### UC-9: Read Race Schedule
```mermaid
flowchart TB
    U[User]

    subgraph System
        R([Read Race Schedule])
    end

    U --- R
```

---

### UC-10: Update Race Status
```mermaid
flowchart TB
    S[Simulation Service]
    A[Admin]

    subgraph System
        R([Update Race Status])
    end

    S --- R
    A --- R
```

---

### UC-11: Create Championship
```mermaid
flowchart TB
    A[Admin]

    subgraph System
        R([Create Championship])
    end

    A --- R
```

---

### UC-12: Create New Team
```mermaid
flowchart TB
    U[User]
    A[Admin]

    subgraph System
        R([Create New Team])
    end

    U --- R
    A --- R
```

---

### UC-13: Read Team Details (player team)
```mermaid
flowchart TB
    P[Player]

    subgraph System
        R([Read Team Details - Player])
    end

    P --- R
```

---

### UC-14: Update Team Attributes
```mermaid
flowchart TB
    P[Player]
    A[Admin]

    subgraph System
        R([Update Team Attributes])
    end

    P --- R
    A --- R
```

---

### UC-15: Read Available Drivers
```mermaid
flowchart TB
    P[Player]
    TA[Team AI]

    subgraph System
        R([Read Available Drivers])
    end

    P --- R
    TA --- R
```

---

### UC-16: Update Driver Contract
```mermaid
flowchart TB
    TM[Team Manager]
    A[Admin]

    subgraph System
        R([Update Driver Contract])
    end

    TM --- R
    A --- R
```

---

### UC-17: Read Available Staff
```mermaid
flowchart TB
    P[Player]

    subgraph System
        R([Read Available Staff])
    end

    P --- R
```

---

### UC-18: Update Staff Contract
```mermaid
flowchart TB
    P[Player]
    TM[Team Manager]

    subgraph System
        R([Update Staff Contract])
    end

    P --- R
    TM --- R
```

---

### UC-19: Update Driver Skills/Age
```mermaid
flowchart TB
    SCH[Scheduler]

    subgraph System
        R([Update Driver Skills/Age])
    end

    SCH --- R
```

---

### UC-20: Update Team Budget
```mermaid
flowchart TB
    F[Finance System]
    G[Game Loop]
    A[Admin]

    subgraph System
        R([Update Team Budget])
    end

    F --- R
    G --- R
    A --- R
```

---

### UC-21: Create New Driver
```mermaid
flowchart TB
    A[Admin]
    S[System]

    subgraph System
        R([Create New Driver])
    end

    A --- R
    S --- R
```

---

### UC-22: Create New Staff Member
```mermaid
flowchart TB
    A[Admin]
    S[System]

    subgraph System
        R([Create New Staff Member])
    end

    A --- R
    S --- R
```

---

### UC-23: Delete Championship
```mermaid
flowchart TB
    A[Admin]

    subgraph System
        R([Delete Championship])
    end

    A --- R
```

---

### UC-24: Create Custom Track
```mermaid
flowchart TB
    D[Designer]
    A[Admin]

    subgraph System
        R([Create Custom Track])
    end

    D --- R
    A --- R
```

---

### UC-25: Update Track Characteristics
```mermaid
flowchart TB
    A[Admin]

    subgraph System
        R([Update Track Characteristics])
    end

    A --- R
```

---

### UC-26: Delete Track
```mermaid
flowchart TB
    A[Admin]

    subgraph System
        R([Delete Track])
    end

    A --- R
```

---

### UC-27: Read Staff Performance Modifiers
```mermaid
flowchart TB
    S[Simulation Service]
    U[UI]

    subgraph System
        R([Read Staff Performance Modifiers])
    end

    S --- R
    U --- R
```

---

### UC-28: Update Driver Appearance
```mermaid
flowchart TB
    P[Player]

    subgraph System
        R([Update Driver Appearance])
    end

    P --- R
```

---

### UC-29: Update Team Branding
```mermaid
flowchart TB
    P[Player]
    A[Admin]

    subgraph System
        R([Update Team Branding])
    end

    P --- R
    A --- R
```

---

*End of diagrams.*
