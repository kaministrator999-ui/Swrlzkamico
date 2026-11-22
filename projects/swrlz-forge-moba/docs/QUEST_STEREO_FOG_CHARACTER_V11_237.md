# §E v11.237 candidate — stereo right-edge graphics and sheep mesh disappearance

## Real Quest 2 observations
- Quest VR Sheep Tag ground and fog start shifting after a while in Play.
- A right-side stereo graphics clipping/rendering artifact appears.
- When lag becomes severe, parts of sheep meshes disappear; earlier optimizations improved some stuttering but not these symptoms.

## Current source findings
- `runtime/sheep_clover_organic_walk_swurv_v11_127.js` produces a native multi-part Clover sheep from Model Atelier organic topology, which is cloned in the game. These are many separately culled meshes and rig pivots.
- `runtime/sheep_quest_meadow_fog_polish_v11_206.js` renders a separate transparent meadow-art plane just above original ground. `runtime/sheep_quest_biome_landmarks_fog_depth_v11_208.js` puts the authoritative fog presentation plane at renderOrder 14 while retaining depthTest.
- `runtime/sheep_xr_world_quality_metrics_v11_210.js` gives transparent decorative waymarker instanced meshes `depthWrite:true`; an unnecessary occlusion risk for fog and other translucent art.
- `runtime/engine_xr_sheep_spotlight_v11_200.js` already decouples normal head movement from the gameplay world anchor. The v11.234 Quest frame-budget candidate in PR #362 is **draft and unmerged**, so it cannot be credited for improvements seen in the live client unless integrated by an independent change.

## Candidate fix
- In **immersive Sheep Tag Play only**, avoid per-submesh frustum culling on the *controlled* sheep/wolf. Other actors keep their native bounds and culling.
- Avoid frustum culling of the two large permanent map planes and the real fog presentation plane while VR is active. One ground plane and one fog mesh are comparatively cheap, and stereo view boundaries must not make them disappear.
- Make decorative transparent waymarker depthWrite false to avoid writing erroneous depth that can clip later fog. The authoritative fog material, fog pixels, occlusion rules and discovery masks remain unchanged.
- Restore original mesh culling and cosmetic material settings on round stop, VR exit, or controlled-unit switch. Limit repeated world checks to every ~240ms.
- Include current guard counters in the debug VR image JSON receipt via `SWYRL_ENGINE_QUEST_STEREO_GUARD_237.diagnose()`.

## Hardware test after future publication
1. On Meta Quest 2 in a new match, look left/right at neutral head position and walk a sheep through a fog edge.
2. Watch whether the far-right visible graphics tear/disappear in only the right eye or in the shared view. If one-eye-only persists, prioritize WebXR eye projection/camera framebuffer issues next rather than more fog overlays.
3. While walking and while head-turning, look for missing parts of the controlled sheep and compare with non-controlled sheep and wolf.
4. Open/close the Meta OS camera menu and check for VR stutter; Quest's own compositor remains outside webpage control.
5. Confirm no fog knowledge leak, building placement changes, sheep joystick changes, or unexpected extra draw cost. Use the existing §E metrics and debug capture if needed.

## Release gate
This change is **not deployed**. It is a reviewable additive candidate on top of main v11.236. To publish under §§§: append patch to ordered `source-manifest.json`, regenerate exact build bytes/SHA-256 using official builder, synchronize all version metadata and release verifier, merge to `main`, commit `DEPLOY_REQUEST.json` separately, and verify live `SOURCE.json`. Do not claim hardware acceptance without user's real-device check.
