# §E v11.434 — Crowded Sheep Tag VR and editor rendering

Date: 2026-11-13. Scope: the existing Sheep Tag renderer, native XR visibility recovery, and shared game-editor shadow rendering. Publication status: source on `main`, separate deployment request succeeded, hosted artifacts verified against the sealed build. Physical Quest acceptance remains pending.

## Findings from the actual implementation

Existing v11.265 runtime building batching, v11.379 frame-cadence safeguards, v11.411 AI building-candidate budgets and v11.419 collision/path budgets were already present. The native seven-bot simulation can construct 76 houses without adding a generator or altering the saved starter. The crowded browser profile was dominated by rendering rather than native `stUpdate` CPU time.

The XR observer also treated a long callback gap as inferred OS focus loss. When rendering repeatedly stalled, that inference could pause camera/input and hide/restore large cosmetic layers despite a visibly active native XR session. A real Meta-menu return resets timing. The owner's clarified symptom starts approximately 20 seconds into play even without head movement: severe lag and screen corruption delay Meta's own OS menu, then the active overlay temporarily improves rendering. That points to sustained workload/backlog as well as possible recovery amplification. The false-focus behavior is an application-side defect supported by source and emulation; it is not established as the sole cause of the physical Quest symptom. Physical compositor flashing/warping and OS-overlay latency were not directly observed here.

The native teammate occlusion path used the desktop perspective camera even during XR. Some useful existing runtime building batching did not cover equivalent authored editor buildings or other compatible scenery. Static game-editor shadows were regenerated during camera-only movement.

## Changes

- **Native visibility recovery:** for crowded Sheep Tag only, visible native XR plus a 650–5,000 ms callback gap no longer invents OS focus loss. Real hidden/blurred states, document visibility, pending held-input release, menu-return grace and longer suspensions keep their existing safeguards. No head-pose, reference-space, view-matrix or XR render-loop replacement.
- **Geometry-preserving submissions:** compatible unnamed opaque sibling meshes with the exact same material/render state are combined. Bounds, indexed triangles, vertex attributes including normals/UVs, named pivots, material identity and parent transforms are preserved. Unsupported/transparent/skinned/morph/custom-render cases fall back. Derived/original geometry disposal is paired. Existing match-building batching remains authoritative; only static scenery and authored editor buildings receive the new factory wrapping.
- **Correct XR occlusion and clearer overlays:** occlusion uses the renderer's cached native XR camera. Busy Auto/Low/Medium VR keeps controlled and selected sheep outlines; High keeps every teammate outline. Ordinary unit models, team/minimap information, non-XR behavior and visibility rules remain native.
- **Shared editor shadow reuse:** unchanged supported caster/light geometry reuses native shadow maps during camera motion. Actor/light transforms, geometry, instancing, layers, visibility and materials invalidate the cache. Skinned/morph/custom-depth/displacement/cutout/clipped/unsupported shader cases use the native path. Play/Simulate always use native updates; returning to Edit forces a refresh. Resolution and filtering are unchanged.

No sheep, house count, collision rule or AI behavior was reduced. Texture fidelity, triangle detail, UVs, normals and authored project data were preserved. Native models/saves/Undo, §C, Model/Particle/Material studios, and existing mobile camera preferences were not replaced.

## Focused native verification

`python scripts/verify_v11_434_release.py --output <package> --three-module <Three169.module.js>` passed, including exact packaging, 77 asset receipts, inline JavaScript syntax and these checks:

| Check | Result |
| --- | --- |
| `sheep_visual_batch_v11_434.mjs` | 12 groups; actual native factories and Three r169; exact transformed positions/normals/UVs, topology counts, bounds, materials, pivots and disposal |
| `engine_editor_shadow_cache_v11_434.mjs` | 11 groups; real Three matrices/lights/materials; camera reuse and geometry/instance/light/material/visibility invalidation, fallback, Play/Stop |
| `sheep_visible_recovery_v11_434.cjs` | 11 groups; true focus/menu/input safeguards, visible-gap handling, High/non-XR overlay policy |
| `model_camera_preferences_preserved_v11_434.mjs` | Packaged v11.433 preference persistence, default/inverted touch directions, both pitch limits, mouse behavior and 56px mobile targets passed |
| Existing v11.379 / v11.411 / v11.419 checks | Native frame cadence, AI construction-candidate and congestion/path budgets passed |

Native per-building draw meshes include farm 30→8, income 48→16, fort 33→7, shop 25→6 and pond 37→7, with unchanged triangles. No duplicate runtime building batch was introduced.

## Browser stress verification

`scripts/check_sheep_vr_stress_v11_434.py` used the actual assembled package in Chromium with official IWER 2.8 stereo emulation. Baseline: sealed v11.433, 410 patches, SHA-256 `025700cca295b514f510ace13bcf091593724a5a46c8180ed442dea1a0a4894d`. Final: the v11.434 receipt below. Test-only observation/setup injection hashes are recorded separately from the canonical source hash.

A fresh guest Wildwood fixture spawned eight sheep and three wolves. Seven native AI teammates built 76 houses by approximately 105 simulated seconds; all eight sheep remained alive. Bounded setup acceleration was excluded from measurement windows. The same native building positions were inspected as a disposable authored editor fixture; user/cloud projects and starter templates were not written.

| Measured view | v11.433 draw calls | v11.434 draw calls | Detail / meaning |
| --- | ---: | ---: | --- |
| Editor, original scenery | 1,963 | 1,767 | 482,845 triangles in both |
| Editor, 76 houses | 4,414 | 2,416 | 515,659 triangles in both; 45.3% fewer draw calls |
| Editor, panning past 76 houses | 4,427 | 2,429.25 mean | 515,871 triangles in both |
| XR, 76 houses, still | 2,610 | 2,140 | Decorative layers remain restored in final; visible geometry differs because recovery is fixed |
| XR, 76 houses, head moving | 2,591.5 | 2,079.33 mean | Stereo head yaw and 12 cm translation; not a device-FPS comparison |

The final run covered editor-empty, game-empty, XR-empty, built/still, built/FOLLOW head movement, built/FREE head movement, built/after-menu head movement, editor-built and editor-pan. An actual emulated native `visible-blurred` event, pause and return to `visible` was exercised. After return: session visible, input not paused, no pending release, cosmetic layers restored, all 76 buildings/eight sheep retained, both eye matrices finite, near 0.05/far 544.765, and no WebGL context loss. Nine bounded visible callback gaps avoided false interruption handling. The editor shadow cache reused 35 of 42 eligible sampled frames by the final pan phase.

Evidence in this execution workspace: `/workspace/outputs/sheep-vr-v11-434/baseline-2/verification.json`, `/workspace/outputs/sheep-vr-v11-434/final/verification.json`, screenshots in those directories, and `/workspace/scratch/verify-sheep434.log`. Both comparison receipts report PASS and the final reports zero JavaScript page errors. Startup texture-not-ready renderer warnings were logged; this checkpoint does not claim to eliminate those warnings.

Chromium used software rendering and small per-view samples. Its callback timings and cumulative pursuit/simulation counters (which include accelerated setup) cannot establish Quest GPU frame time, thermal behavior, sustained FPS or compositor/reprojection correctness. No physical headset was attached. The exact whole-screen clipping/warp and long-session comfort still require the owner to retest the hosted build, including standing still, turning/moving the head, many houses and a Meta-menu return.

## Canonical source receipt

- Version: `v11.434`; deploy marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_434_SHEEP_CROWDED_VR`.
- 411 ordered patches; final `patches/v11_434_sheep_crowded_vr.py` preserves completed v11.433 camera updates.
- Both `index.html` and `modeler.html`: **9,930,780 bytes**.
- SHA-256: `7aa4640a5b02b6c43eb54fe28d28dbf503cd52f1c571c98c0ee455d659395fd8`.
- `SOURCE.json`: 77 asset receipts; 81 packaged files total.
- Runtime changes: `sheep_visual_batch_v11_434.js`, `sheep_visible_frame_recovery_v11_434.js`, `sheep_xray_policy_v11_434.js`, `engine_editor_shadow_cache_v11_434.js`.

## Publication

Live publication verified: [source 638bffb](https://github.com/kaministrator999-ui/Swrlzkamico/commit/638bffbd009119f4838cc3d41043ddcf96c4d1d0), [separate request 20453bf](https://github.com/kaministrator999-ui/Swrlzkamico/commit/20453bf770f988a79e3e792de556b33e66d9bf70), and [successful deployment](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43352719088). The Space is RUNNING at HF revision `2c4fc0698772efd1663444a0c54a7f55ed15e1e5`; both hosted HTML entry points and all 77 asset receipts match the sealed build. The owner's approximately 20-second onset, delayed Meta OS menu and temporary improvement with the overlay remain physical Quest acceptance cases; this release does not claim that complete symptom is confirmed resolved.

Independent revision-pinned downloads of `index.html` and `modeler.html` each measured 9,930,780 bytes and SHA-256 `7aa4640a5b02b6c43eb54fe28d28dbf503cd52f1c571c98c0ee455d659395fd8`. Hosted `SOURCE.json` agrees with the complete 411-patch lineage, source version and all 77 local asset receipts. Receipt: `/workspace/scratch/sheep434-hosted-receipt.json`. This final publication documentation leaves the deployed runtime artifact unchanged.
