# §E v11.239 — Quest 2 fast head-turn black-edge investigation

## Owner's on-device evidence (2026-11-03)
After deploying v11.238, Sheep Tag Play still shows a hard-edged black region
on the **right** while turning the head rapidly. Ground/fog world graphics have
previously drifted and individual sheep components briefly disappeared during
heavy stutters. Screenshot: first-person browser XR capture with a straight
boundary between the rendered map and black region near the right of the frame.

The screenshot cannot determine whether the physical right-eye display,
Quest's screen-capture mirror, the compositor's reprojection or app WebGL
render targets produced that black region. No camera/projection claim is proven.

## Concrete source performance problem
- `runtime/immersive_xr_gateway_v11_181.js`'s `se181XRRender` runs every
  XR frame and calls `se181XRRaycast` once per controller. That implementation
  collects every visible authored actor and `intersectObjects(roots,true)`
  descends into their submesh geometry.
- `runtime/engine_xr_spatial_editor_v11_192.js` and later Sheep Tag
  v11.193/204/214 already handle independent native gameplay controller input,
  ground targeting and radial menus.
- v11.181 explicitly disallows editor object selection in `playing` or
  `simulating`. Its original full-scene raycast is thus redundant in Sheep
  Tag gameplay and may consume the VR render frame budget as models grow.
- The existing raycaster also checks the dedicated **EXIT VR** surface. That
  must remain interactive even though gameplay scene-actor raycasts are skipped.

## Narrow fix
- Gameplay-only `se181XRRaycast` override avoids recursively ray-testing
  every actor's meshes and only checks the actual EXIT VR plane with one reusable
  raycaster; outside gameplay the original editor actor picker remains.
- Track XR callback gap counters (>20, >35, >70 milliseconds), recent average,
  worst gap, menu open/closed counts through
  `SWYRL_ENGINE_QUEST_HEADTURN_239.diagnose()`.
- Keep native headset tracking and stereo projection entirely unmanaged;
  preserve v11.238 radial and browser editor controls, building placement,
  sheep joystick movement, LAN and gameplay, and original exit method.

## Test on user's Quest 2
1. Play sheep and turn head slowly, then quickly with the app radial closed.
   Compare right-side black clipping and head-turn smoothness to v11.238.
2. Repeat with **VIEW** radial menu open; watch whether callback gaps increase
   and whether the menu remains visible.
3. Check Sheep Tag movement/build placement and the **EXIT VR** scene panel.
4. Exit Sheep Tag and verify §E editor actor pointing still works.
5. If black area appears despite low frame gaps, investigate XR compositor
   reprojection, renderer layer dimensions, and whether the capture mirror is
   cropping a single eye; don't misdiagnose the cause as fog/frustum alone.

## Release status
New source is a candidate pending exact build source SHA-256 / byte receipt
and owner hardware acceptance. This release intentionally does not merge
draft stereo PR #363 or camera-budget PR #362, and changes no renderer quality
setting without evidence.
