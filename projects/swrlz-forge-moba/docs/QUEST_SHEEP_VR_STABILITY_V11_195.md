# Quest Sheep Tag VR stability v11.195 — implementation and hardware acceptance

## Observed Quest 2 issues
Sheep-follow camera visibly offset left; match lag after a short time; unstable meadow/fog appearance; rays passing through VR menus; duplicate Exit VR signs; oversized menu dialogs; authored menu cinematic not appearing naturally in XR; need controller models, polished glowing rays, compact right-hand radial and reliable photo captures.

## Implementation
Source remains append-only at patches/v11_195_quest_sheep_stability_radial.py and runtime/engine_xr_sheep_stability_v11_195.js. This is one adapter over the existing engine WebXR, authored actor scene, Sheep Tag authority and capture writer, without a second renderer or game state.

1. The headset's tracked eye follows the controlled sheep from a wide elevated position, using live session units instead of serializing the complete stStatus snapshot on every frame. Natural head rotation is never overwritten. Left stick detaches/pans, right stick orbits/zooms and Y recenters.
2. Retain a single stable post-arrival XRReferenceSpace base and accumulate offsets against that base, rather than nesting transforms every frame. Rebase on game/menu/editor transitions to avoid drift and accumulated transform overhead.
3. Quest Sheep-only 0.72 framebuffer scale is selected BEFORE session activation; an extra shadow pass is disabled only during Sheep XR and restored afterward. The expensive 2D camera/HUD/minimap isn't updated in immersive gameplay. Cheap terrain ray tests are used per hover frame and full actor picking only on trigger.
4. Keep native fog/vision/AI authoritative, but paint the *cosmetic* fog texture about 3 times per second; separate its mesh from the meadow texture and apply a depth offset to combat stereo z-fighting. Do not skip gameplay vision calculations.
5. Starting authored Sheep Tag Main Menu in VR invokes the real cinematic actor animation. Headset viewing position moves gently near the sheep; the default orbit is slow/shallow without forcing the headset to turn. The orbit can be toggled off.
6. Replace tall VR panel stacks with one 5-spoke right-hand radial tethered near the pointer. It includes Game, Build, Session, Editor/Prefab, Aim calibration, Photo and Help. X toggles, trigger selects. An open radial is modal: controller beams and trigger input cannot pass through and hit underlying houses.
7. Retire duplicate in-world Exit VR signs; Meta system menu and normal §E browser Exit button remain. Existing black-screen watchdog remains active.
8. Lightweight grip-space controller indicators, calibrated target-ray glow halo, tapered beams and eight animated motes per controller. Dispose visual resources on exit.
9. Photo mode freezes gameplay for framing (restores prior pause state on exit); trigger captures, X returns to radial. Capture options include clean PNG, debug PNG + JSON and stereo pair. Debug data includes XR FPS estimate, draw calls, fog paints, current camera mode. Images remain downloadable through the normal browser after exiting WebXR.

## Quest controls and behavior
- Left stick: detach/pan
- Right stick: orbit/zoom
- Left Y: follow sheep/recenter
- Left X: summon or hide wrist radial
- Right A: cycle buildings when radial is closed
- Right trigger: select menu option or gameplay target; in photo mode take screenshot
- Right B: cancel pending build or detach camera
- Meta system menu: exit VR

## Acceptance boundaries
The Node regression suite and ordinary Chrome Play/Stop smoke can verify code, menu precedence and existing desktop paths. They cannot establish actual Quest 2 FPS, stereo image quality, controller grip alignment, long-run stability or user comfort. We need hands-on Quest acceptance with screenshots and optional debug JSON before claiming all visual artifacts resolved.

The Dragon Den floating desktop workstation and full Model Atelier VR sculpting are not part of this change. Neither are multiplayer protocol changes or saved project migrations.

## Integrity
227 ordered patches, 68 packaged assets, 7,288,202 HTML bytes and SHA-256 7fa6242cfeeb6f9b44e8887cf86b905ed5e6ee9c55e7e12696a64fc77a0a31ad. Strict verifier: scripts/verify_v11_195_release.py. Deploy only after success in a separate pinned DEPLOY_REQUEST.json commit, followed by a hosted-source audit.
