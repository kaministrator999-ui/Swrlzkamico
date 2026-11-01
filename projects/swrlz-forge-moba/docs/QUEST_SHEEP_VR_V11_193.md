# §E Quest 2 / Sheep Tag VR v11.193 — candidate implementation and acceptance

## Status and authority

This is a SOURCE-ONLY candidate, NOT a shipped v11.193 Space build. Main branch and the current v11.192 source manifest, 7,210,061-byte HTML integrity receipt and DEPLOY_REQUEST.json remain authoritative until this candidate is rebuilt, resealed and deployed through RELEASE_PROCESS.md. Never invent final bytes/hash.

## Viewport becomes the surrounding world

Dragon Den remains an optional home and hub, not a required editing level. The existing saved default project preference remains authoritative. An interactive flat editor screen inside the Den is a separate phase: normal Quest browser windows are NOT automatically embeddable inside WebXR. Native texture-backed UI and pointer bridging, with a Quest 2 GPU budget, are needed. World editing keeps the flying creator perspective; Sheep Tag uses a zoomed-out strategic view; Model Atelier immersive sculpting needs its own adapter.

## Implemented in this candidate

1. Detect canonical authored Sheep Tag Main Menu, whether editable or playing as a cinematic level. Build ray-selectable Three.js VR title panels, Start, Map Editor and controller-help surfaces. Start uses the real level transition, not a retired menu hook.
2. Position the tracked headset high and behind the controlled sheep with adjustable follow distance and no forced headset rotation. Left stick pans/detaches; right stick orbits and zooms; Y returns to follow.
3. Use the native Quest ray to select/move/attack/rescue/build through the existing Sheep Tag command layer. Include dynamically built farm meshes in selection. The session remains authoritative; no writes to saved map actors.
4. Compact in-world pages for builds, capture and game controls. X shows/hides palette, A cycles buildings, B cancels building or detaches, right trigger acts on aimed targets. Pause, restart and stop use existing buttons.
5. Extend the gameplay-only ray and reticle reach to 140 world units at strategic zoom. Native editor distance remains unchanged.
6. Capture clean PNGs, debug PNGs with JSON metadata and stereo side-by-side PNGs with a single offscreen WebGL target. A conventional browser download button persists after exiting XR in case Quest blocks immersive downloads.
7. Keep the same renderer, XR session, app navigation and account boundaries. No extra animation loop or independent game state.

## Quest 2 acceptance checklist — hardware NOT yet tested

| Area | Acceptance |
| --- | --- |
| Main Menu | Native menu readable in headset; Start enters the actual playable level |
| Editor | Dismiss menu for editor; no menu trigger selects an actor behind it |
| Follow | Large surrounding building area visible while sheep moves; look around independently |
| Free camera | Detach, pan, orbit, zoom and Y recenter work without lurches |
| Building | Ray targets passable terrain and blocked placements safely report errors |
| Runtime houses | Newly placed buildings selectable for further game commands |
| Match controls | Pause, restart and stop preserve original Sheep Tag lifecycle |
| Screenshots | Clean image, debug JSON and two-eye stereo image saved in normal browser after XR |
| Safety | Exit/reentry does not leave panels, gizmos, listeners, render targets or scene mutations |
| Performance | Measure Quest 2 FPS/frame times during play and capture; no claim until actual device test |
| Regression | Desktop/mobile Sheep Tag, LAN, saved projects, Model Atelier and Chat remain intact |

## Release steps

Run node tests/test_v11_193_sheep_vr.cjs plus relevant existing XR tests. Apply patches/v11_193_sheep_vr_capture.py last and update the version, finalArtifact, build identifiers, release verifier, workflow references and current docs. Recompute the ACTUAL final HTML size/SHA using the canonical Python builder, verify all 68 assets and SOURCE.json, and keep integrity enforcement intact. The final DEPLOY_REQUEST.json must be its own commit pinning the exact source commit/hash. Verify successful HF deployment and live revision, followed by physical Quest 2 UX acceptance before declaring the feature live or headset-validated.
