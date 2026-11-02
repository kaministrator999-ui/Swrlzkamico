# §E v11.207 — Quest Sheep Tag Play movable/tiltable world menu

## Why
Kami found that Meta's OS-owned floating windows could be angled and moved in 3D while Sheep Tag kept playing. Our §E menu previously followed a one-time head-relative default location and could not be grabbed, rotated or pinned.

## First spatial-menu capability (not the full multi-panel workspace)
- **In Sheep Tag Play:** point the **right controller's** ray at any part of the actual §E radial. Hold **right grip**. The existing menu attaches to a constant controller-relative translation and rotation; move and tilt the physical controller in 6DoF. Releasing grip pins the §E menu exactly where you left it.
- The menu remains available as a world-pinned UI when reopened or when navigating between existing BUILD, CAPTURE, SESSION and VIEW pages. All selection and gameplay input stay modal and retain the foreground cursor from v11.205.
- While grabbing, right thumbstick vertical changes size within 72%–140% of the chosen base. Ordinary right-stick orbit/zoom is suppressed during grip only. No new building rotations.
- **SESSION → LAYOUT** includes PIN, RECENTER, SMALLER, LARGER and BACK. RECENTER clears the pin and delegates to native safe Quest HUD placement.
- Small grip handle and cached outline attach once to each cached menu root; no per-frame mesh/texture creation. The controller's live world transform drives position/quaternion using preallocated vectors and quaternions.
- **Reset on XR exit:** do not persist raw Quest world XYZ across sessions, which may have different tracking origins.

## Scope and safety
This initial change manipulates one §E-owned gameplay menu at a time. It does not interact with Meta Quest operating-system panels, modify existing §E Game Editor/Model Editor gizmos, change Sheep Tag building rotations, change authored project scene data, add game colliders, or alter LAN authority.

## Remaining issue #320
True multi-panel camera/build/skill inspectors with independent pins and saved per-user layouts; richer radial icon/prefab previews; map re-authoring beyond v11.206 biome artwork; fog capture validation; Quest 2 FPS acceptance.

## Verification
Run node projects/swrlz-forge-moba/tests/test_v11_207_spatial_menu.cjs for menu grip-hit required, 6DoF translation/tilt, pin across page switch, right-stick modal handling, resize/recenter actions, no editor impact, OS overlay interruption and XR lifecycle reset. All v11.206–v11.181 regressions and a strict 239-patch source hash verifier remain release gates.
