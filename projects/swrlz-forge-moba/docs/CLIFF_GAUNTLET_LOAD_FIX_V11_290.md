# §E v11.290 — actual hand loader failure and textured cliff gauntlet

## User-visible failure

Owner's November 6 Android screenshot showed a "Could not open Plain Hand Base · Smooth Cliff Hand" toast shortly after opening the starter card. The prior v11.289 code attempted to extend the existing shell with a fixed y-axis taper that assumed the hand's original lower bound lay near 0.57. It only accepted an apparent extension of 0.60–0.81 units.

That assumption does not match the active v11.217 anatomical SDF. At (x=0,z=0) its hand does not occupy y=0.58, but does occupy y=0.90; the natural lower contour is around 0.85. The v11.289 taper added less than the asserted minimum and rejected model construction. The synthetic v11.289 test missed the mismatch by building its sample mesh from y=0.60 instead of sampling the actual hand SDF.

## Fixed implementation

The new runtime `runtime/cliff_gauntlet_surface_material_v11_290.js`, appended by `patches/v11_290_cliff_gauntlet_load_material.py`, changes only the template creation path for `plain-hand-base`.

- Construct the original hand using the same active `se217OrganicHandSkin(se217FingerSpec,...)` anatomical SDF used by its existing native starter.
- Smooth-union a short tapered forearm into the original SDF, with an elliptical-to-round transition from radius ≈0.232 near the wrist to ≈0.322 at its distal end and a planar closure near y=0.20. Generate the geometry through the existing native `SWYRL_ENGINE_HAND_SURFACE.surface/weld` operations.
- Keep a single `topologyMesh` part, the same 17-joint rig, original hand silhouette and open/fist controls. No new separate rock blocks, 3D crevice tubes, armor plates or accessories.
- Reproject continuous UVs across the actually generated hand and forearm extents; no fixed y limits or bottom-of-texture clamping.
- Keep the owner-derived `assets/cliff-hand/cliff_pbr_atlas_384.jpg` as source. Adjust `MeshStandardMaterial` for stronger normal-map relief, AO-darkened cracks, warm matte sandstone and restrained moss; the surface still looks rocky from maps, not geometry.
- Report last actual native gauntlet build error via `window.SWYRL_ENGINE_CLIFF_GAUNTLET_290.status()` for diagnostics, without inventing a success state.

## Validation

`scripts/test_v11_290_cliff_gauntlet.cjs` loads the actual v11.217 anatomy source and v11.290 surface function, verifies a continuous signed-distance interior from forearm through wrist, checks the lower closure and source bounds mismatch, and uses a stub native surface producer to exercise the build contract and actual UV/material functions. The source assembly and JavaScript checks verify the complete engine package separately. **The regression is not a rendered-browser test or a Quest/Android visual acceptance.**

Owner acceptance after deployment: reload the hosted Space, open **Starter Models → Plain Hand Base · Smooth Cliff Hand**, rotate it front/side/back, confirm a connected gauntlet with a clean short forearm, attractive normal-mapped sandstone, selective green moss, and working finger poses. If it still fails, collect the exact toast/console message; do not claim working render from static source tests.
