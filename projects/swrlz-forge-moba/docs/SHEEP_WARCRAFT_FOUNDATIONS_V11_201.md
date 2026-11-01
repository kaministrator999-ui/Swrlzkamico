# §E v11.201 — Warcraft-like Sheep Tag collision foundations

Completed structures get a softened, terrain-conforming foundation interior with warm trim. The separate *exact boundary* uses the real stBuildingObstacle footprint; the outer translucent rim reaches stUnitRadius('sheep') out from the structure and shows how close the sheep's center can approach. Decorative rounding does **not** round collision.

When selecting or moving a building ghost, the existing native snapped preview remains green (valid) or red (invalid), while the grid fades quieter and nearby gaps show:
- **Teal:** sheep can pass locally with comfortable clearance
- **Amber:** locally passable, close to minimum safe lane width
- **Red:** blocked; the sheep cannot fit through that local section

Both built and preview corridors use the existing stClarityGap swept collision and stSafeLaneWidth safe navigation threshold. Green represents **local passability, not a map-wide guarantee**. Hidden buildings are not included in the visual overlay. Original game logic, game clock, multiplayer/fog state, editor authored actors, WebXR headset tracking, controllers, and placements are unchanged.

The built-house and gap meshes are batched to seven visual material groups and rebuilt on navigation/visibility changes, not each frame. The live aiming preview reuses its GPU objects and same-size geometry, and cleans up on exit. No new render loop or saved actors.

**Regression:** `node projects/swrlz-forge-moba/tests/test_v11_201_warcraft_footprints.cjs` tests visible geometry, exact stopping band, three gap states, preview caching and cleanup; all existing XR and visual stability regression tests also run. Quest 2/mobile visual acceptance is a separate physical test.
