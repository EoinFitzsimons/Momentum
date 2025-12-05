# Information Architecture Plan — Momentum

This document is a step‑by‑step Information Architecture (IA) plan adapted from Nick Babich’s 10‑step IA process, customised for the Momentum motorsport management simulator. Each step lists concrete actions, artifacts to produce, and suggested deliverables.

Goal: produce a clear, user‑centred IA that supports quick play for casual users and deep data access for simulation enthusiasts.

Estimated cadence: 1–2 weeks of focused work to produce a reviewable sitemap, wireframes, and a short usability validation.

---

## Step 1 — Understand user goals (Deliver: 3 persona cards, mental models)

- Actions:
  - Use the existing personas (Casual Manager, Competitor/Challenger, Data‑Driven Strategist).
  - For each persona: list top tasks, success metrics, and typical flows (e.g., Start Quick Race, Hire Driver, View Standings, Filter Drivers).
  - Capture mental models: how each persona expects to find information (Dashboard centric vs. Reports centric).
- Artifact: `personas.md` (or include in Technical Report appendix).

## Step 2 — Define business objectives (Deliver: prioritized objectives list)

- Actions:
  - Translate project goals into IA objectives (example objectives below). Confirm priorities with stakeholders (or assume pragmatic defaults if stakeholders are not available).
- Suggested primary objectives:
  1. Make it trivial to start and run a race (support the demo / midpoint presentation).
  2. Surface primary team controls (Budget, Drivers, Garage) within 1 click from Dashboard.
  3. Provide a clear path for hiring/upgrading monetizable features (Store, Upgrades) for future expansion.
  4. Offer analytics and filtering for advanced users (Reports, Telemetry).
- Deliverable: `business_objectives.md` with prioritized list and brief rationale.

## Step 3 — Competitor analysis (Deliver: IA pattern notes)

- Actions:
  - Quick review of similar managers (Motorsport Manager, F1 Manager, Football Manager) for navigation patterns and labels.
  - Extract 5 IA recommendations (e.g., top-level categories, common label terms: Drivers, Garage, Standings, Calendar).
- Deliverable: `competitor_ia.md` (short report).

## Step 4 — Content inventory & audit (Deliver: `content_inventory.csv` + summary)

- Actions:
  - Enumerate screens and data entities from the repo and `INFORMATION_ARCHITECTURE.drawio` / `WIREFRAMES.drawio`.
  - Create a CSV with columns: `Screen ID`, `Screen Name`, `Primary Content`, `User Task(s)`, `Priority (A/B/C)`, `Notes`.
- Deliverable: `content_inventory.csv` placed in the `diagrams/` folder.

## Step 5 — Categorize & prioritise content (Deliver: category map)

- Actions:
  - Group related content into top-level categories and secondary groups.
  - Use persona goals & business objectives to set Priority A/B/C.
- Seeds for categories: Dashboard, Drivers, Teams, Garage, Championships, Calendar, Race, Reports, Store, Settings, Help.

## Step 6 — Create a sitemap (Deliver: update `INFORMATION_ARCHITECTURE.drawio` + PNG)

- Actions:
  - Produce a draft sitemap showing parent/child relationships and primary navigation (recommend left sidebar for power users + top-level quick actions for casual users).
  - Mark where primary CTAs appear for each persona (e.g., Enter Race on Dashboard; Hire on Driver Browser; Upgrade on Garage).
- Deliverable: updated `INFORMATION_ARCHITECTURE.drawio` and exported PNG.

## Step 7 — Label content (Deliver: label glossary)

- Actions:
  - Create consistent labels for navigation and content (e.g., `Hire` vs `Contract` — pick one and use everywhere).
  - Provide short definitions for domain terms (Driver, Contract, Upgrade, Championship).
- Deliverable: `labels_glossary.md`.

## Step 8 — Design navigation system & user flows (Deliver: flow diagrams)

- Actions:
  - Design primary navigation and secondary menus; map breadcrumbs and contextual links.
  - Draw 6 priority flows: Onboard & Start Race, Hire Driver, Upgrade Car, Manage Staff, Create Championship, View Standings.
- Deliverable: flow diagrams in `CONTEXT_DIAGRAM.drawio` or new flow files.

## Step 9 — Prototype user flows (wireframes) (Deliver: annotated wireframes)

- Actions:
  - Update `WIREFRAMES.drawio` with low‑fidelity annotated wireframes for priority screens (Dashboard, Driver Browser, Driver Detail, Garage Upgrade UI, Race Setup, Standings).
  - Optionally create a clickable sequence (PDF or image-based prototype).
- Deliverable: `.drawio` + PNG exports.

## Step 10 — Validate design (Deliver: short usability report)

- Actions:
  - Run 3–5 lightweight usability sessions (team or remote participants). Tasks: start a race, hire a driver, apply an upgrade, locate standings.
  - Collect task success rates and qualitative feedback; prioritise fixes.
- Deliverable: `usability_report.md` with top findings and remediation plan.

---

## Quick artifact map (where to put files)

- `Planning/Technical Report/diagrams/INFORMATION_ARCHITECTURE.drawio` — sitemap master
- `Planning/Technical Report/diagrams/WIREFRAMES.drawio` — wireframes
- `Planning/Technical Report/diagrams/content_inventory.csv`
- `Planning/Technical Report/diagrams/personas.md`
- `Planning/Technical Report/diagrams/labels_glossary.md`
