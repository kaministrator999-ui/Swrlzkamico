# Video Creator Starter · 3D Pop-Up Storybook · v8.8

This is an extension of the existing **Ghosts in Different Forms** Anime Studio starter in §wyrl§ Engine, not a separate game, new app, or image.

## Art direction

The staged episode is a dark-fantasy **book theatre**, following the user's wizard sketches and the two-character concept-art direction.

- **Kami:** larger horn-hooded fantasy wizard with layered robes, broad hair coverage, ornamental belts, burning-skull staff and rune details.
- **§wyrlz:** separate smaller hovering skeletal wizard, deliberate pointed mage hat and floating grimoire.
- **Scenery:** hand-rendered CanvasTexture cutout plates for a moonlit distant city, magical atmospheric flourishes, gothic cathedral archways, workshop shelves, painted runes, desk props, and a *real Three.js page-thickness book model*.
- **No extra mascot character** in the cinematic. The original canonical guardian object stays in the editor starter so older dialogue/stations and exploratory project content are not deleted.
- **No external images, generation service or remote asset provider** required at runtime. The artwork is procedural/vector-style; it is a dark-fantasy interpretation of the reference concept, not a pixel-perfect recreation of the earlier illustration.

## Engine behavior

At each of the existing eight episode acts, the physical open book and scenery **unfold from the page** on independent Three.js pivots. Every cutout is an individual depth plane with separate parallax and unfold delay. The perspective camera can travel past those planes without flattening them into a single backdrop.

The Pop-Up Director is available while the Anime Studio starter is loaded. Each layer can separately configure:

| Setting | Range | Stored |
|---|---:|---|
| Z depth | -28 to +6 | Yes |
| Side position | -4 to +4 | Yes |
| Parallax factor | 0 to 1.5 | Yes |
| Unfold delay | 0 to 4 sec | Yes |
| Unfold time | 0.25 to 4 sec | Yes |

**Kami** and **§wyrlz** are individually adjustable character cels rather than a single flattened character image. The older aggregate Characters layer remains as a compatibility visibility toggle. The six historical background/atmosphere/midground/characters/effects/foreground layers remain, with new individual Kami, §wyrlz and Guardian visibility entries.

On phone-width views, **Pop-Up Director → Save Project** explicitly invokes the normal editor's project export, even if the original Save toolbar item is out of view.

Save Project exports all Director values under `project.animePopUp` with schema `anime-popup-v1`. On Load Project, finite numeric values are sanitized and clamped to safe ranges. Project export does not require localStorage, internet or a paid runtime. This setting applies **only** to the Anime Studio starter. The original §E Dragon Den, Starforge and other starter projects retain their Play behavior.

The in-editor Play HUD still provides seek, Pause, next/previous scene, Layers, Stop and Explore Set. Scene script captions remain in the existing editable act workstations.

## Boundaries

The cel artwork is still authored procedurally in the engine source, not yet an SVG/PNG asset-import or skeletal rig/puppet editor. Director supports basic depth/parallax/position/unfold animation parameters, not arbitrary timelines and bone posing. No claim of finished video export, lip sync or full character animation.

## Acceptance tests

- Reconstruct source from every governed patch; verify SHA, bytes and generated module syntax.
- Desktop Chromium and mobile-sized Chromium load Anime Studio and start native Play.
- Eight scripted scenes, physical popup book, at least five distinct hinged scenery plates, separate Kami/§wyrlz cels and ordered Z depth.
- Director UI changes each wizard independently; Save Project downloaded JSON retains parameters.
- Layer visibility toggles, caption bounds, seek, Pause, Explore Set, Stop and original actor restoration.
- No uncaught browser errors; no regression to Embervault and Starforge.
- Deploy only using the repository's governed `DEPLOY_REQUEST.json`; verify the exact HTML/asset receipt from the served dedicated HF Space.
