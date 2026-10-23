# Solid blockers and furred Astra · v11.90

## Changed behavior

- House contact alone never relocates sheep. Construction over the builder rejects instead of ejecting it.
- The held joystick approaches the blocking face, then follows an actual local visibility-graph route through clear corners and lane portals. Routes cache until geometry/input changes; deadzone, reverse and release cancel them. Movement always consumes native analog-speed budgets with swept building and traffic checks. No solution means stop.
- Cranium and both outer pinnae share one welded indexed surface, with deeply overlapping roots and inset velvet liners. Shoulder muscles blend into a tapered ribcage/waist. 1,100 curved closed fur locks root into the existing pelt on torso, ivory bib and four limbs.
- The native detailed starter retains 37 original gear/tail parts exactly, original 4K maps and all material/edit/export controls. Its game copy uses the engine's mesh reducer plus whole-lock fur sampling, with compatible game buffers merged per animation joint.

## Targeted evidence

`verify_v11_90_release.py` proves the append-only 122-patch lineage, all 290 previous runtime/patch hashes, all 58 previous asset hashes, 60 packaged assets, exact compiled HTML seal, original 37 gear/tail parts, closed manifold edges for every detailed biological/fur mesh, and a single connected skull/ears surface. Each part stays within the existing 65,536-vertex / 120,000-triangle limit.

`test_solid_blockers_v11_90.mjs` runs the real native movement and collision functions: contact before detour, no idle displacement, release, reverse, rotated houses, traffic, blocked routes, existing 0.60/0.75 m multi-row lanes in both directions, and vertical lanes. It compares 200 obstructed/rotated segments against the old narrow phase. For 100 short clear segments with 300 distant houses, exact narrow-phase intersection calls fall from 180,000 to zero; this synthetic work count is not an FPS claim.

`test_furred_astra_v11_90.mjs` exercises the actual editor: 96 valid native parts, 639,772 rendered triangles, loaded 4096×4096 color/normal images, exact native tool rebuild, material editing and Undo, detailed JSON save/reimport, actual textured GLB export and front/side inspection. `check_furred_astra_glb_v11_90.py` validates exported geometry, indices, normals, UVs and exact embedded original 4K images.

`test_furred_game_v11_90.mjs` uses actual CDP touch input in the game for the wall approach/detour, release-to-stop, idle contact and overlapping placement rejection without relocation or charge. The live renderer reports 29 meshes / 69,471 triangles per wolf, loaded original 4K images and all six animation joints. Recorded-run sampling is exercised with the native game clock: 331 frames over 32.8 seconds at the effective 0.1-second cadence, with no errors. `test_furred_wolf_animation_v11_90.mjs` verifies actual wolf joystick movement, all four alternating leg joints, independent cloned animation trees, shared 4K images and immediate release-to-stop.

## Performance scope

The old wolf rendered 106 meshes / 274,980 triangles per instance; the new optimized visual renders 29 / 69,471 (about 73% fewer mesh draws and 75% fewer triangles per wolf). Detailed authoring remains 96 / 639,772. Game meshes share template geometry/materials; joints remain per actor. Standard game materials preserve atlas color, normal and emissive bindings without the editor's extra physical-material effects.

Collision footprints cache only for the current session/navigation version. The swept broad phase conservatively includes every obstacle whose world AABB can affect the segment; native sample locations and exact circle/rotated-footprint tests are unchanged. Construction/destruction navigation invalidation refreshes the cache. No fog, rescue, sanctuary or gameplay visibility rule is relaxed.

Full-rate phone recording otherwise serializes the growing scene every render update; 10 Hz world sampling retains explicit command captures/events and marks the effective cadence in the export. Explicit 0.1/0.5-second settings remain unchanged. Hardware/browser FPS varies; software-rendered automation does not establish performance on the owner's phone.

## Assets and publication

Two new saved native scenes are packaged from lossless compressed source. All older assets and runtime/patch files remain immutable. The source is committed directly to main, then a separate final DEPLOY_REQUEST-only commit identifies that exact source and seal. The production workflow must succeed and verify the exact live HTML, SOURCE receipt and all 60 assets before delivery is called live.
