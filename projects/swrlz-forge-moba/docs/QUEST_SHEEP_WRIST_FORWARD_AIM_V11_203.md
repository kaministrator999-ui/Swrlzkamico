# §E v11.203 — Quest neutral-view Sheep Tag and lightweight VR wrist menu

## User reports
1. Opening the Quest wrist menu, especially navigating to capture/camera tools, causes severe lag.
2. Sheep Tag is framed far below a neutral headset gaze, requiring steep downward head/controller aim just to place buildings near the sheep.

## Camera and ground aiming
v11.202: 31.9 world units behind, 36.4 above at base 1.4 zoom = about 49° downward from the eye to the sheep.

v11.203: **same 31.9 behind**, just **9.1 above** at base 1.4 zoom, making the sheep about **16° below the neutral forward eye-line**. This lowers camera height (rather than mistakenly pulling farther back/up), keeps native WebXR HMD pitch/look intact and retains the stabilized camera-anchor-delta tracking. Right joystick zoom/orbit remains.

When a free sheep selects a house from the wrist/menu:
- Neutral forward controller aim is projected onto a virtual, vertical, camera-facing plane through the sheep and then translated onto the actual **game ground near the sheep**. This gives an accessible forward-aim placement method without pretending the actual controller ray touches ground.
- Aiming left/right chooses a lateral offset, up aims farther ahead and down aims closer to/behind the sheep. Offsets are bounded near the controlled sheep.
- With a steep down-aim (direction.y < -0.65), the original physical ground intersection is used. When not building, the native scene selection/attack/rescue rays are unchanged.
- Preview and final placement both use this same mapping; native stCanBuild with all house, player, sanctuary, navigation and anti-trap rules remains the only build authority. The two meaningful sheep selection radii from v11.202 stay intact.

## Wrist/capture UI frame-time reduction
- Original wrist radial labels use newly allocated 512×256 canvases/textures every page change. v11.203 makes 256×128 matching visuals, caches by label, and retains textures for the active XR session.
- Entire radial mesh trees are cached by mode/page. RETURN/BUILD/CAPTURE/SESSION and initial revisits reuse the existing GPU resources instead of rebuilding/updating 5–6 textures and materials.
- Only real XR cleanup disposes cached pages/textures; no leaked texture assets across sessions.
- Live build ghost validation and the foundation overlay do not execute while the wrist menu/photo mode is open; the authentic game clock, host/guest logic, collision and fog still run normally.
- Nonessential animated controller motes/halos are muted only while the menu is visible, while existing point/beam and menu hit targets remain.

**Regression**: run `node projects/swrlz-forge-moba/tests/test_v11_203_wrist_forward_aim.cjs`, then all prior XR v11.202–v11.181, Sheep Tag, editor and modeler checks plus SHA-pinned package verification. The performance improvement is based on fewer texture uploads/mesh allocations and reduced menu-time work; physical Quest FPS/comfort is not established by mocks.
