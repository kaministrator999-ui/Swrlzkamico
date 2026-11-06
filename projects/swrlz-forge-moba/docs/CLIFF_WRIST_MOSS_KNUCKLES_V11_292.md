# §E v11.292 · Material-only sandstone knuckles and lower-wrist moss

## Owner screenshot correction

The v11.290 short Cliff Hand gauntlet opened correctly, but the moss appeared across fingers and much of the palm. The rock knuckles also needed more definition, specifically in the **materials** and not by adding more meshes.

## Implementation

- Source: `runtime/cliff_knuckle_wrist_moss_v11_292.js`, appended by `patches/v11_292_cliff_knuckle_wrist_moss.py` after the independent v11.291 Hooded Vanguard model.
- Keep `model.parts=[stone]` and the native connected hand/forearm SDF, the actual 17-bone rig, existing UV topology, loader and saved-model behavior. No new rock, cuff, knuckle or crevice meshes.
- The existing high-resolution owner-supplied `assets/cliff-hand/cliff_pbr_atlas_384.jpg` is used unchanged as an input. At material initialization, create four **384×384** local CanvasTextures, once for the hand: rock albedo, normal, roughness and AO. Preserve original crack and surface relief patterns.
- Copy **tile 4** (clean sandstone albedo) across the full UV hand; overlay original **tile 0** moss-composited sandstone only through a soft alpha gradient near image y=275–384, equivalent to the **lowest ~23% of the gauntlet UV**. Palm, thumb and fingers have no moss overlay. This is a material-only region mask, not geometry.
- Place four individually varied knuckle stone-facet markings at normalized UV centers `(.454,.648),(.592,.654),(.738,.644),(.868,.625)`, based on the source four metacarpal roots. Draw rough outlines, subtle top-left chiseled highlights and recessed short seams in **albedo**; pair them with localized tangent normal relief and ring AO shadowing for apparent rock thickness under light.
- Keep existing roughness atlas and nonmetallic stone shading. Canvas textures are updated after the local atlas image loads; if it fails, keep safe placeholder channels and report an error in `window.SWYRL_ENGINE_CLIFF_MATERIAL_292.status()` rather than fabricating a success.
- Preserve the unrelated v11.291 Hooded Vanguard, other starters, VR/Sheep Tag and user projects.

## Focused verification

`scripts/test_v11_292_cliff_material.cjs` mocks the actual canvas/texture creation route and checks clean sandstone source tile, gradient wrist-only mask, all four knuckle positions, normal/AO image edits, material channels and no extra geometry. Engine build and standalone/assembled JavaScript syntax checks accompany the SHA-sealed release. These source tests cannot establish how the lighting looks in a browser.

## Phone acceptance

Reload §E, then **Starter Projects → Starter Models → Plain Hand Base · Smooth Cliff Hand**. Inspect palm/back, all fingers and knuckles; green moss should concentrate on the lower gauntlet, with warm sandstone on fingers/palm. Turn the knuckles into light to judge the normal-map relief, and exercise pose/open-fist. Request a localized texture-only refinement if needed.
