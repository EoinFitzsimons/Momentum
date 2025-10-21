# Momentum - Top Navigation Bar Spec

Purpose: define a wide, branded top navigation bar for the game UI (both web/CSS prototypes and Unity UI 2D). Includes button list, layout rules, accessibility notes, CSS variables, and a Unity ScriptableObject snippet for colors and spacing.

Recommended buttons (based on `Momentum/Python/README.md` features):
- Home — Dashboard / Current season summary
- Inbox — Messages, notifications, event log
- Team — Team overview, roster, finances
- Parts — Vehicle components, development status
- World — Calendar, global championships, tracks
- Standings — Championship tables, leaderboards
- Training — Driver training, facilities, schedules
- Staff — Staff management, hiring, salaries
- Races — Quick access to upcoming races and race simulator
- Settings — App and account settings

Layout rules
- Full-width bar anchored to top of screen.
- Height: 72px for desktop; scale down to 56px on small screens.
- Left area: Project logo (48px square) + app title.
- Center area: primary nav buttons (Home, Team, World, Standings, Races).
- Right area: utility buttons (Inbox with badge, Training, Staff, Parts, Settings, user avatar).
- Overflow: collapse lower-priority items into a "More" dropdown when horizontal space is limited.

Interaction
- Hover: subtle lighten of background on hover (use 8% lighter than brand background).
- Active: underline + fill accent (Racing Red #DD2D4A) for active section.
- Focus: 3px focus ring using Charcoal Grey with 30% opacity.
- Keyboard: Tab order left-to-right; Enter to activate; Space to open dropdowns.

Accessibility
- Contrast: text must meet WCAG AA against the bar background (use Snow White for text on Charcoal Grey background). Use bold 600 weight for nav labels.
- ARIA: nav element with role="navigation" and aria-label="Main Navigation". Dropdowns use aria-haspopup and aria-expanded.

CSS variables (web prototype)
:root {
  --brand-cyan: #B9F2FF;
  --brand-charcoal: #353839;
  --brand-red: #DD2D4A;
  --brand-white: #F5F5F5;
  --nav-height: 72px;
  --nav-padding: 16px;
  --nav-font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
}

.top-nav {
  height: var(--nav-height);
  background: linear-gradient(180deg, var(--brand-charcoal) 0%, #2C2D2D 100%);
  color: var(--brand-white);
  display: flex;
  align-items: center;
  padding: 0 var(--nav-padding);
  gap: 12px;
}

.nav-left { display:flex; align-items:center; gap:12px; }
.nav-center { flex:1; display:flex; justify-content:center; gap:8px; }
.nav-right { display:flex; align-items:center; gap:8px; }

.nav-button { padding:10px 14px; border-radius:8px; background:transparent; color:inherit; font-weight:600; }
.nav-button:hover { background: rgba(255,255,255,0.03); }
.nav-button.active { color: var(--brand-red); border-bottom:3px solid var(--brand-red); }

Badge example (Inbox):
.badge { min-width:18px; height:18px; padding:0 6px; background:var(--brand-red); color:var(--brand-white); border-radius:12px; font-size:12px; display:inline-flex; align-items:center; justify-content:center; }

Unity ScriptableObject snippet (C#)
-----------------------------------
using UnityEngine;

[CreateAssetMenu(fileName = "UIStyle", menuName = "Momentum/UI/Style", order = 0)]
public class UIStyle : ScriptableObject {
    public Color BrandCyan = new Color(185f/255f, 242f/255f, 1f, 1f); // #B9F2FF
    public Color BrandCharcoal = new Color(53f/255f, 56f/255f, 57f/255f, 1f); // #353839
    public Color BrandRed = new Color(221f/255f, 45f/255f, 74f/255f, 1f); // #DD2D4A
    public Color BrandWhite = new Color(245f/255f, 245f/255f, 245f/255f, 1f); // #F5F5F5
    public float NavHeight = 72f;
    public float NavPadding = 16f;
}

Unity UI wiring notes
- Create a Canvas (Screen Space - Overlay). Add an empty GameObject `TopNav` anchored to top stretch with height bound to `UIStyle.NavHeight`.
- Split into `Left`, `Center`, `Right` Horizontal Layout Groups to match CSS sections. Use Content Size Fitter and Layout Element for flexible spacing.
- Use `Button` prefabs with TextMeshPro labels. Create an `InboxButton` prefab with a small `Badge` child (TextMeshPro) to show unread counts.
- Implement a `TopNavController` MonoBehaviour responsible for:
  - Loading `UIStyle` ScriptableObject
  - Populating button active state based on current scene or route
  - Calling backend endpoints for Inbox and quick navigation (use UnityWebRequest)

Suggested API mappings
- Home -> GET `/` or `/stats` (for dashboard summaries)
- Inbox -> GET `/notifications` (if exists) or poll `/simulate/race/events` for recent events
- Team -> GET `/teams?discipline={type}` and GET `/drivers`
- Parts -> GET `/parts` (add if missing) or reuse `/teams` endpoints for component status
- World -> GET `/tracks` and `/championships`
- Standings -> GET `/standings` or compute from `/race_results` (backend)
- Training -> GET/POST `/training` (create if missing) or use staff endpoints
- Staff -> GET `/staff` and POST `/staff/hire` (if implemented)
- Races -> GET `/races/upcoming` and POST `/simulate/race`

Assets and sizes
- Logo: 48px, 128px, 512px variants (PNG). Keep PSD in `Assets/Branding/PSD/`.
- Icon sprites: 40x40 px for nav icons. Use 2x versions for high DPI.

Deliverables in this change
- `Branding/navbar_spec.md` (this file) — contains the spec and wiring notes

End of spec
