# §wyrl§ Engine Roadmap & Update Ledger

**Purpose:** chronological source-of-truth for shipped §wyrl§ Engine updates. Read this after `§tart_§E.md` when reconstructing project history.

## Foundation — v4 / v4.1
- Established the browser-based 3D Forge/editor foundation and reconstructable patch-chain source model.
- Preserved the legacy `projects/swrlz-forge-moba` path while separating engine evolution from individual example projects.

## v5.0 — Project system
- Decoupled the engine from the original MOBA example.
- Added the Projects hub, Starter World, MOBA Arena, and Dragon's Den templates.
- Added project identity/metadata and independent editable project state.

## v5.1 — §wyrl§ Engine / Seed Den
- Advanced naming and compatibility toward §wyrl§ Engine.
- Expanded the Dragon's Den seed environment and agent/world roles.

## v5.2 — First-person + twin-stick
- Added first-person play/runtime controls.
- Added mobile twin-stick movement/look controls.
- Kept editor and runtime interaction modes separate.

## v5.3 — Groups + immersive Dragon's Den
- Added hierarchical editor grouping, nesting, duplication, serialization, and world-transform-safe ungrouping.
- Rebuilt the default Dragon's Den as an enclosed immersive cavern with grouped architecture.
- Added Wake Nook, Council Chamber, Creator Alcove, throne/perch sides, exits, memory/inference spaces, and cave-focused presentation.

## v5.4 — Procedural Wisp avatar
- Replaced the default Den visitor capsule with the procedural Wisp Visitor / Creator.
- Added glow sprites, core, motes, trails, hover/pulse animation, save/load reconstruction, and first-person body hiding.
- No copied Warcraft assets are bundled.

## v5.5 — Natural look + dragon anatomy
- Corrected first-person horizontal look direction.
- Reworked procedural dragons into a stronger anatomy/silhouette pass: articulated wings, segmented neck/tail, chest/haunches, four legs, claws, muzzle/jaw, horns, eyes, teeth, ears, and dorsal spines.

## v5.6 — Dragon ground contact
- Added reusable raycast-based `SurfaceFootContact`.
- Dragon feet settle on rocks, pedestals, uneven architecture, and terrain fallback.
- Improved rear paws and multi-finger wing membranes.

## v5.7 — Precision contact + editor camera speed
- Upgraded feet to multi-sample sole contact and averaged surface normals.
- Tucked teeth inside the mouth silhouette.
- Added persistent editor camera speed control from 0.35×–3.00× for rotate/pan/zoom.

## v5.8 — Wisp alpha + support-aware feet
- Fixed visible rectangular Wisp particle cards with transparent/premultiplied additive rendering.
- Added seven-point foot sampling and X/Z support correction for paws near platform/rock edges.

## v5.9 — Soft Wisp + stable support + visible history
- Softened Wisp falloff by removing the hard alpha cutout.
- Replaced accumulating horizontal foot correction with bounded support locking to prevent dragon sliding.
- Surfaced quick Undo/Redo controls in the top bar while retaining the canonical history system.

## v6.0 — Glitch Dragon Den / Fracture Forge
- Preserved the original Dragon's Den / Seed Chamber as its own project.
- Added a second procedural environment: **Glitch Dragon Den — Fracture Forge**.
- Added fractured floor plates, megacavern shell, obsidian buttresses, chromatic crystal veins, central forge dais/core, rune pylons, traversal gates/circuit, glitch lanterns, and three dragon perches.
- Added three themed procedural dragons: **§wyrl§ Glitch Dragon**, **Frost Forge Dragon**, and **Ember Glitch Dragon**.
- External visual research informed design vocabulary only; no external den/dragon assets were imported.
- Deployment marker: `V6_0_GLITCH_DRAGON_DEN`.
- Integrity receipt before the visibility hotfix: 170965 bytes, SHA-256 `747076cbbd43b881887392bcf69a7721905564ffc155e3ab946831ed3a640569`.
- GitHub→Hugging Face deployment run 37456591811 successfully rebuilt, syntax-checked, uploaded, and verified the v6 marker live.
- **Visibility hotfix:** add the missing Glitch Dragon Den card to the Projects hub and remove the stale user-facing “v5.3” label from the legacy Seed Chamber.

## Ongoing rules
- Every release remains reconstructable from `source-manifest.json` + ordered patch chain.
- Validate exact bytes/SHA and generated JavaScript before merge.
- Upload success is not deployment success: the served Hugging Face static host must expose the intended release marker.
- Keep engine core, MOBA example, Seed Chamber, and Fracture Forge logically separate.
- Research may guide original procedural design; do not silently import third-party assets.
- Append future releases/hotfixes to this ledger as part of the release work.
