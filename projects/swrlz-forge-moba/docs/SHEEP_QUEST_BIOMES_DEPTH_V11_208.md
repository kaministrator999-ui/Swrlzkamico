# §E v11.208 — Quest Sheep Tag four-biome map and fog-depth rendering

## Shipped visual direction
The *original saved, collision-authoritative Sheep Tag world* stays in place. The v11.206 ground atlas is now expanded into a cohesive regional art system:

| Region | Mood / art |
| --- | --- |
| Pinewatch (NW) | Dark emerald pine undergrowth, pale clover, woodland leaves |
| Moonflower (NE) | Cooler misty blue-green grass, small pale accents, slate pebbles |
| Amberglade (SW) | Golden meadow brush, warm moss, honey-colored path edging |
| Willowmere (SE) | Fresh river-green grass, soft willows, pond-side stones |

Each region receives a translucent painted wash and its own muted ornamental landmark. The 80m authored meadow's existing cross/diagonal paths get matched soil/stone shoulders; the 128m Moonbell Wildwood's existing 4K roads are not repainted. Small decorations avoid the sanctuary, roads and existing botanical/rock/pond actor footprints and cannot create misleading collision.

## Render/pipeline decisions
- **Reuse one v11.206 768×768 mipmapped meadow texture.** Paint new washes during its one-time setup, add 95 little art strokes per existing staged frame, and finalize landmarks before the existing single texture upload. This adds no new texture and no GPU reupload after startup.
- **Three or fewer InstancedMesh draw calls** for leaf mats, pebbles and low flower stalks around the already-authored trees/rocks/ponds. A fixed seeded random sequence makes the art deterministic. Rendering is decoration-only and every mesh is excluded from controller raycasts.
- Instances are low, small and non-shadowing, always below the existing fog surface. They are not serialized as editor actors and never added to the navigation/collision array. No navigation invalidation, unit motion changes or house placement rewrites.
- Fog gets a **cosmetic depth-order guard** while in immersive Quest Play: plane height at least 0.24, polygon offset -2.5/-3 and overlay render order 14. All visibility arrays, sight ranges, explored memory, LAN team compositor, server authority and original painters remain byte-identical.
- v11.206's existing fog restoration snapshot remains authoritative when returning to desktop or exiting XR, including original mesh height and polygon offset. The new instances are disposed with v11.206's VR cosmetic layer on match stop and headset exit.

## Acceptance limitations
This is a rendered-world improvement, **not** a full replacement of authored geometry (which would change map layout and the user's saves). Actual fog flicker reduction, depth comfort and GPU headroom must be observed on Quest 2; mocked/CI checks can prove lifecycle and invariants, not headset FPS.

Remaining from issue #320: more ambitious world geometry/material remaster, live device fog reproduction, fully independent world-pinned panels, richer build/skill radial selection graphics, and comprehensive VR controller diagnostics.

## Verification
Focused `node projects/swrlz-forge-moba/tests/test_v11_208_biomes_depth.cjs` plus all v11.207/v11.206 and prior Sheep Tag/editor/ARPG regressions; exact 240 ordered-patch/68-asset checksum-sealed release workflow required before deployment.
