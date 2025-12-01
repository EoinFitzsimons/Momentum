# Momentum — Visual Style Guide

This document formalises the Momentum colour palette and provides practical guidance for UI, visual hierarchy, accessibility and implementation (CSS and Unity snippets).

---

## Colour Palette (Primary)

| Name          |         Hex |
| ------------- | ----------: |
| Cyan Blue     | `#B9F2FF` |
| Charcoal Grey | `#353839` |
| Racing Red    | `#DD2D4A` |
| Snow White    | `#F5F5F5` |

### Quick tokens

- Background: `--bg: #353839` (Charcoal Grey)
- Surface / Panel: `--surface: #FFFFFF` (Snow White) — use for panels and cards on top of the dark background
- Primary text: `--text-primary: #B9F2FF` (Cyan Blue)
- Secondary text / on-dark-high-contrast: `--text-on-dark: #FFFFFF` (Snow White)
- Critical / Alert text: `--danger-text: #DD2D4A` (Racing Red)

---

## Application Guidelines

### UI Structure

- Use **Charcoal Grey** (`#353839`) as the overall canvas/background. Large areas of the app should sit on this dark base.
- Use **Snow White** (`#F5F5F5`) for surface panels and cards placed on top of the dark background to create readable containers.
- Use **Cyan Blue** (`#B9F2FF`) as the primary text colour across the app (headings, body copy, labels).
- Use **Racing Red** (`#DD2D4A`) and **Snow White** as alternate text colours where needed — e.g. red for critical labels/alerts, white for very small or low-contrast cases.

### Data Visualisation

- Positive/Improving values: Cyan Blue (`#B9F2FF`)
- Negative/Critical: Racing Red (`#DD2D4A`)
- Neutral or baseline: Snow White at reduced opacity (use panels) or subtle greys laid over panels — avoid relying on Charcoal Grey (background) alone for data marks.

### Discipline theming (recommended)

- Single-Seater: primary accents in Cyan Blue
- Production Circuit: Charcoal Grey base with Cyan Blue accents
- Traverse Stage: Snow White base, Racing Red accents
- Urban Showcase: Racing Red primary, Cyan Blue highlights
- Linear Acceleration: Charcoal Grey + Cyan Blue contrast
- Endurance Campaign: Muted Charcoal and Snow White balance
- Sprint Circuit: Racing Red + Cyan Blue alternation

---

### Accessibility

- The primary colour pairing is **Cyan Blue** text on a **Charcoal Grey** background. Test for text-size contrast: large and medium-sized text will be high-contrast, but very small text may fall short of WCAG AA. Where contrast is marginal, use `--text-on-dark: #FFFFFF` (Snow White) for small captions or low-emphasis copy.
- Use Racing Red (`#DD2D4A`) for critical alerts; always pair with icons or patterns for accessibility.
- For charts/tables, never rely on colour alone. Use shaped markers, text labels, or dual encodings.

---

## Typography (Recommendations)

- Primary UI font: **Inter** (variable weights). Alternative: **Roboto**.
- Heading font (optional): **Montserrat** or **Poppins** for a slightly more geometric headline.

Suggested scale (desktop):

- Large heading (H1): 36px / 48px line-height — weight 600–700
- Heading (H2): 28px / 36px — weight 600
- Heading (H3): 20px / 28px — weight 600
- Body: 14px / 20px — weight 400
- UI small text: 12px / 16px — weight 400

---

## Implementation Snippets

### CSS variables

```css
:root {
  --color-bg: #353839; /* Charcoal Grey background */
  --color-surface: #FFFFFF; /* Snow White panels */
  --color-text: #B9F2FF; /* Cyan Blue primary text */
  --color-text-on-dark: #FFFFFF; /* White for small/low-contrast text */
  --color-danger-text: #DD2D4A; /* Racing Red for critical text */
}

body {
  background: var(--color-bg);
  color: var(--color-text);
}

.panel {
  background: var(--color-surface);
  color: var(--color-bg); /* dark text on light panels if needed */
}

.button-primary {
  background: transparent; /* keep focus on text-based UI — use surface for click targets */
  color: var(--color-text);
  border: 1px solid rgba(185,242,255,0.12);
}

.alert-danger {
  color: var(--color-danger-text);
  background: transparent;
}
```

### Unity (C#) — Color constants and ScriptableObject guidance

Create a C# static class for quick access, or better — a ScriptableObject to edit in-Editor.

`ColorPalette.cs` (example static helper):

```csharp
using UnityEngine;

public static class ColorPalette
{
    public static readonly Color CyanBlue = new Color32(0xB9, 0xF2, 0xFF, 0xFF); // primary text
    public static readonly Color CharcoalGrey = new Color32(0x35, 0x38, 0x39, 0xFF); // background
    public static readonly Color RacingRed = new Color32(0xDD, 0x2D, 0x4A, 0xFF); // critical text
    public static readonly Color SnowWhite = new Color32(0xF5, 0xF5, 0xF5, 0xFF); // panel / alternate text
}
```

Better: create a `UIStyle` ScriptableObject that exposes these colours and typography tokens in the editor for designers to tweak at runtime.

---

## UI Patterns & Layout

### Main Menu (2D)

- Left: Vertical navigation with logo at top (use Charcoal for text, Cyan Blue for active indicator)
- Center: Title/hero area with app title and CTA buttons (Manage Race, Quick Sim)
- Right: Recent events / quick stats card

### Race HUD (3D overlay)

- Top-left: Mini leaderboard (3–5 drivers)
- Bottom-left: Player-specific status (lap, tyre, fuel)
- Bottom-center: Large race timeline / progress bar
- Top-right: Notifications/alerts (use Racing Red for critical)
- Use subtle translucent panels with Snow White background and Charcoal text
