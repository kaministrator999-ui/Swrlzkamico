# §E v11.183 — Project UI and loading remediation

## Evidence and changes

- User-provided Android screenshots show a redundant actor summary occluding top-right editor actions, Sheep Tag start-menu chrome from editor visible at the edges, and a cramped Project Levels toolbar.
- The native editor already displays object/selection details in its status bar. The duplicate floating `.engine-stats-pill` was safely hidden.
- The original `#st141LevelBar` children and listeners remain intact. An expandable, dismissible level panel starts as a 44px button and preserves native select/new map/name/next/menu/export functionality.
- Active Sheep Tag menus suppress incidental editor overlay chrome; the native Sheep Tag menu, Start, LAN, and Exit remain intact.
- The v11.141 multilevel project wrapper was invoking `seLevelRawLoadProject` twice for saved packs. v11.183 chooses the active record first and performs one native scene rebuild, then hydrates level-pack metadata.
- Starter cards show load stages and elapsed seconds before synchronous construction. Local and account loads show read/backup/import stages with a render opportunity before heavy work. Neither reports invented progress percentages.
- Account project lists are deduplicated in memory for twelve seconds; manual Refresh bypasses cache and account changes clear it.
- Native undo, account ownership, Cloud/IndexedDB recovery, Model Atelier, VR, gameplay and LAN wiring are unchanged.

## Verification

- Focused JS source checks and cloud dedupe tests passed.
- Mocked saved-level test verified exactly one native scene rebuild, correct saved active level and original options.
- Browser layout/interaction test checked portrait (390×844, 430×932), landscape (844×390), Quest-sized 2D window (980×680), and desktop (1280×800), including real starter-card clicks in 3 sizes.
- Physical Android and Quest testing is outstanding.

## Exact package seal

- Version: §wyrl§ Engine v11.183
- Patches: 215
- Assets: 68
- HTML bytes: 7110847
- SHA-256: `070aad1b47dcf1a05bdfee3e82f48e81991bc4826e9d128bb904d3bc8f1b3145`
