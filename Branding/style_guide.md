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

- Background: `--bg: #F5F5F5`
- Surface / Panel: usually `#FFFFFF` on top of background (use subtle shadows)
- Primary text: `--text-primary: #353839`
- Accent / Interactive: `--accent: #B9F2FF`
- Critical / Error: `--danger: #DD2D4A`

---

## Application Guidelines

### UI Structure

- Use **Snow White** (`#F5F5F5`) as the canvas and panel base. Keep large areas light to maintain clarity.
- Use **Charcoal Grey** (`#353839`) for headings, body copy and structural UI elements (sidebars, cards).
- Use **Cyan Blue** (`#B9F2FF`) for primary interactive elements: active nav, selected rows, hover highlights and small data accents.
- Reserve **Racing Red** (`#DD2D4A`) for true critical alerts and important attention-grabbing elements. Use sparingly.

### Data Visualisation

- Positive/Improving values: Cyan Blue (`#B9F2FF`)
- Negative/Critical: Racing Red (`#DD2D4A`)
- Neutral or baseline: Charcoal Grey (30–60% opacity for less emphasis)

### Discipline theming (recommended)

- Single-Seater: primary accents in Cyan Blue
- Production Circuit: Charcoal Grey base with Cyan Blue accents
- Traverse Stage: Snow White base, Racing Red accents
- Urban Showcase: Racing Red primary, Cyan Blue highlights
- Linear Acceleration: Charcoal Grey + Cyan Blue contrast
- Endurance Campaign: Muted Charcoal and Snow White balance
- Sprint Circuit: Racing Red + Cyan Blue alternation

---

## Accessibility

- `#353839` on `#F5F5F5` yields very high contrast (~15:1). This comfortably meets WCAG AA and AAA for body and heading text.
- Use Racing Red only for high-severity information and pair with icons/patterns for colour-blind users.
- For charts/tables, never rely on colour alone. Use shaped markers or text labels.

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
  --color-bg: #F5F5F5;
  --color-surface: #FFFFFF;
  --color-text: #353839;
  --color-accent: #B9F2FF;
  --color-danger: #DD2D4A;
}

.button-primary {
  background: var(--color-accent);
  color: var(--color-text);
}

.alert-danger {
  background: var(--color-danger);
  color: #fff;
}
```

### Unity (C#) — Color constants and ScriptableObject guidance

Create a C# static class for quick access, or better — a ScriptableObject to edit in-Editor.

`ColorPalette.cs` (example static helper):

```csharp
using UnityEngine;

public static class ColorPalette
{
    public static readonly Color CyanBlue = new Color32(0xB9, 0xF2, 0xFF, 0xFF);
    public static readonly Color CharcoalGrey = new Color32(0x35, 0x38, 0x39, 0xFF);
    public static readonly Color RacingRed = new Color32(0xDD, 0x2D, 0x4A, 0xFF);
    public static readonly Color SnowWhite = new Color32(0xF5, 0xF5, 0xF5, 0xFF);
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
