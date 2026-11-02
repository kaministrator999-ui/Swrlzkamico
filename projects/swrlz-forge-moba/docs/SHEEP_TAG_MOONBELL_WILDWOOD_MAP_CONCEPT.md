# Sheep Tag §E — Moonbell Wildwood / The Great Escape

**Scope:** Original illustrated design reference for the existing Sheep Tag starter. **No playable scene or runtime was edited, and no deployment was requested.** This is not a native .swyrl file.

## Evidence and gameplay foundations
- Warcraft III Sheep Tag: sheep build farms to create defensive mazes; wolves hunt and destroy defenses; captured sheep enter a central spirit pen, where teammates can rescue them. Gameplay references: https://wc3maps.com/map/89197 and https://sheeptag2.com/guides/sheep/
- Modern independent browser recreation Sheep Tag Online demonstrates a related narrow-gap principle and map features such as ponds, forests, rocks and ridges. Its 96×96 procedurally generated maps, 40-second den, and prices are **not §E's current rules**. Sources: https://sheeptag.online/ and https://sheeptag.online/guides/maps
- Current `scenes/sheep-tag-meadow.swyrl.json`: [-40,+40] X/Z, 20-minute round, 30-second headstart, 80 gold; six sheep, two wolves, centered pen, four corner merchants, two ponds, six rocks and forest-edge trees. See `moonbell-wildwood-blueprint.json` for exact coordinates.
- Native `runtime/sheep_tag_game.js` uses 3-unit building-center snap and a 2.4-unit nominal footprint; 0.6 units between adjacent farm edges is slightly wider than the base sheep diameter (0.54) but narrower than a wolf (diameter 1.36; `sheep_lanes.js` may raise radius to 0.78). Test actual swept collision and avoid making primary corridors this narrow. Native construction limits include 14 live buildings per sheep and 84 total.

## New reference assets
- `assets/sheep-tag/concepts/moonbell-wildwood-art.svg`: top-down styled woodland map in four previously established biome themes: Pinewatch, Moonflower, Amberglade and Willowmere.
- `assets/sheep-tag/concepts/moonbell-wildwood-grid.svg`: same map with brighter 3-unit editor snap grid.
- `assets/sheep-tag/concepts/moonbell-wildwood-blueprint.json`: machine-readable **design** positions and requirements, **not** an editor import schema.
- The corner merchant icons, two wolves, six sheep, two ponds and rocks show the current starter's known actor positions. Border forest trees are illustrated schematically, not an exact full actor survey. Dash-outlined gold farm blocks show a possible player-built fort around the initial owner sheep. None are in the actual scene as placed buildings.

## Build this level in §E
1. Duplicate the existing starter scene before visual remaster; preserve saved projects and native actor identities.
2. Cosmetic-first: add biome coloring, creek/willow ambiance, landmarks, natural-looking paths and a forest canopy, reusing batched/stable render resources on Quest 2. No new collider from decoration alone.
3. Keep cardinal central-rescue corridors wide, keep all four quadrants accessible, and leave open sheep starting sites. Add rock/tree **colliders** only after checking grid-aligned buildable sites, escape passages and wolf paths.
4. Let players construct every fort during the match using existing ground-snapped build previews and radial wheel; never prefill permanent farm walls. Visualize green/amber/red local clearance without conflating it with guaranteed reachability.
5. Place animated building motes and optional floating Arcane Glove helpers later as cosmetic effects that do not affect server-authoritative placement. Opening a VR wheel must not stop left-stick sheep movement or introduce a second raycaster.
6. Use direct owner testing on Moto G Power and Quest 2 for passability, fog stability, camera tilt, FPS and controls. Don't trigger unrelated historical browser suites.

These assets are a concrete art and level-design handoff; they have not been imported to §E, packaged into a live build or physically tested.
