## Navigation & User Flows — Momentum (Midpoint)

Primary flows (Step 8 coverage)
1) Onboard & Start Race (casual path)
2) Hire Driver
3) Upgrade Car (Garage)
4) Manage Staff/Contracts (optional/stub)
5) Championship / Calendar → Race Setup
6) View Standings/Results

Use these as the single source for the IA diagram (`INFORMATION_ARCHITECTURE.drawio`) and wireframes (`WIREFRAMES.drawio`). Names match the sitemap: Race Setup, Race (Live), Standings/Results, Reports/Telemetry.

---

### 1) Onboard & Start Race
- Path: Dashboard → Start Race (CTA) → Race Setup (defaults pre-filled) → Start → Race (Live) → Standings/Results
- Intent: Minimize clicks to the first race; keep advanced setup optional.
- Notes: Show “Next Race” tile; offer skip/auto-fill for advanced setup.

### 2) Hire Driver
- Path: Dashboard or Drivers → Driver Browser (filters/sort) → Driver Detail → Hire/Offer → Confirmation
- Intent: Make hire action obvious in both list and detail views.
- Notes: Keep filters visible; surface budget impact.

### 3) Upgrade Car (Garage)
- Path: Dashboard (Quick Action: Upgrade) → Garage → Select Part/Upgrade → Apply/Buy → Confirmation
- Intent: Keep upgrade funnel short; clarify if upgrade is stubbed.
- Notes: If limited at midpoint, show a stub message instead of a dead end.

### 4) Manage Staff/Contracts (optional/stub)
- Path: Drivers (or Staff area) → Detail → Offer/Renew → Confirmation
- Intent: Provide a discoverable but non-blocking path.
- Notes: Hide from primary nav if not ready; mark clearly as stub when used.

### 5) Championship / Calendar → Race Setup
- Path: Dashboard → Calendar/Next Race → Race Setup (for selected event)
- Intent: Let users jump from upcoming events directly into setup.
- Notes: Calendar is secondary; “Next Race” should deep-link to Race Setup.

### 6) View Standings/Results
- Path: Dashboard (card link) or Nav → Standings/Results → Race Detail (optional)
- Intent: Make post-race results immediate; expose season context.
- Notes: After a race, auto-suggest navigation to Results.
