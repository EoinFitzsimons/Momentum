# Business Objectives — Momentum IA (Midpoint Scope)

Purpose: align the Information Architecture and navigation with the midpoint project goals so users can quickly play, manage teams, and showcase core systems in the demo.

## Primary objectives (P1)

1) **Fast path to first race (demo-ready):** Make "Enter/Start Race" one click from Dashboard; keep setup steps optional with sensible defaults.
2) **Surface core team controls:** Budget, Drivers, Garage visible within one click from Dashboard; show current budget and next-race status at a glance.
3) **Hire/Upgrade funnel clarity:** Clear paths to hire drivers/staff and apply upgrades; highlight one recommended action (CTA) on Dashboard.
4) **Results & standings visibility:** Make race results/standings obvious post-race; ensure users can find season status quickly.
5) **Stability for demo:** Keep flows short and error-tolerant; avoid dead ends or hidden required fields during the presentation.

## Secondary objectives (P2)

1) **Analytics/telemetry for advanced users:** Provide a way to reach Reports/Telemetry from nav; include filters/sorting for driver/staff lists.
2) **Calendar/championship context:** Show upcoming race/calendar link from Dashboard so users know what is next.
3) **Store/monetization-ready:** Keep a clear route to Store/Upgrades for future expansion (can be a stub if not fully built).
4) **Help/onboarding hints:** Provide minimal guidance (tooltips/labels) where jargon appears (contracts, setups, telemetry).

## Success criteria (IA-level)

- Time to start a race: <= 3 clicks from Dashboard with defaults.
- Key entities reachable: Drivers, Garage, Standings in <= 2 clicks from Dashboard.
- Hire/Upgrade action discoverable on first screen scan (above the fold).
- Results discoverable immediately after a race (link or auto-route).
- Advanced users: filters/sorting present on driver/staff lists; Reports entry present in nav.

## Design implications for IA

- Keep primary CTAs on Dashboard: Start Race, Hire, Upgrade.
- Use a concise top/side nav: Dashboard, Drivers, Garage, Race/Calendar, Standings/Results, Reports (advanced), Store, Settings.
- Preserve simple vs. advanced layers: default paths are short; advanced links remain accessible but not blocking.
