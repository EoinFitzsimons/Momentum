Props asset integration
=======================

This project supports using simple top-down PNG sprites for infield props (trees, bushes, fences).
If sprites are present in `Momentum/Python/GUI/assets/props/` they will be used automatically.

Recommended source
- Kenney.nl free top-down asset packs (e.g. "Topdown Trees", "Topdown RPG") are a good fit.
  - Many Kenney packs are CC0 / public-domain-like; verify licence per pack.
- Alternative sources: OpenGameArt.org (check licence), itch.io asset packs.

Required filenames
- Sprites should be PNGs with descriptive names. The loader groups by prefix before the first underscore.
  Examples:
    - `tree_oak.png`, `tree_pine.png`
    - `bush_1.png`, `bush_2.png`
    - `fence_wood_1.png`

How the loader works
- At module import, `props_placer` scans `GUI/assets/props/*.png` and organizes sprites by prefix.
- During rendering, the placer will deterministically select one variant per prop and draw it scaled.
- If no sprites are found for a prop type, the renderer falls back to the procedural vector drawing.

Licensing / attribution
- Always check the licence of any asset pack you include.
- For Kenney packs, include a short attribution or licence note in your project docs if required.

Example attribution block (add to your project README or LICENSE-ATTRIBUTIONS.md):

"""
Some art assets (top-down trees, props) used in this project are provided by Kenney (https://kenney.nl).
Kenney assets used: [PACK NAME]. Licensed under CC0/CC-BY/other — see pack README for details.
"""

If you want, I can download a small Kenney pack and add a few example sprites to `GUI/assets/props/` and update the code to reference them directly. I will only proceed after you confirm and provide permission to add external assets to the repo.
