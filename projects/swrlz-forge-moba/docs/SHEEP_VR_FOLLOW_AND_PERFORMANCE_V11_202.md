# §E v11.202 — wider Quest camera composition, joystick-only, frame-time reduction

## User observation
The Quest 2 Sheep Tag camera is still too close, with the sheep too low in the user's field of view. Joystick locomotion makes click-to-move unnecessary. The previous camera/house improvements helped lag, but dense construction still costs excessive CPU time.

## Quest composition
The camera is pulled **back** to **21 horizontal world units** (previously 14) and gets **2.5 world units of additional rearward bias**. **Height and default zoom are unchanged from v11.200**: 26 units high × 1.4 zoom = 36.4 world units above the focus. It does **not** move the camera upward. **The sheep stays attached to the game-world follow point** rather than to an on-screen HUD/camera overlay. This moves the sheep higher in a neutral down-looking VR view as an approximate composition goal, but **cannot lock it to the exact same screen coordinate while the headset physically turns**. WebXR head pitch/yaw and translational tracking remain completely natural, without screen pitching or motion-induced camera rig feedback. Right stick still adjusts orbit and zoom.

## Sheep selection circle: visual silhouette versus physics
The wool, face, and tail of the sheep model extend beyond the native 0.27-world-unit movement collision radius. A single circle cannot truthfully enclose the entire sheep mesh **and** represent that smaller collision radius. The new selector therefore uses **two concentric rings**, with distinct meanings:

- **Bright cyan inner circle**: exactly `stUnitRadius(unit)`, the native collision radius used for walking between houses (0.27 units by default). The circular perimeter represents the navigation clearance, not cosmetic wool overhang.
- **Very faint golden outer halo**: measured once from the model bounds (or a safe fallback), sized to fit around the visible sheep. This is visual selection only and never used as a blocker.

Both follow the controlled living sheep, update their positions cheaply per VR frame, and release their GPU resources on XR exit, restart or loss of control.

## VR input
An empty-ground right trigger stops issuing `stUiCommand('move')`. Left joystick remains the sole movement path in immersive Sheep Tag Play. The original trigger can still select and inspect a unit/house, build at a valid site, attack as wolf, or rescue a captive. Editor selection, Play on touchscreen and non-VR input are unchanged.

## CPU / XR performance
- `se202PreviewOwner()` uses authoritative `stSession.controlledId` instead of serializing full `stViewStatus` with large fog arrays every VR preview. `se202VisibleBuildings()` uses `stSeenByRole` for each visible building; unseen enemy structures are never exposed.
- `se202ShouldRefreshPreview()` avoids costly native `stCanBuild` and clearance calculations when the ray moves less than 0.07 world units, the navigation version and active build/owner/resources are unchanged, and less than 520ms has elapsed; periodic refresh catches mobile units entering the footprint.
- `se202ObstacleSnapshot()` reuses the native collision obstacle list for direct gamepad motion until a build/removal navVersion change or a raised wall crosses its completion threshold. Native AI navigation, networking and original stObstacles remain untouched.
- At most every 650ms the 3D foundation overlay checks for a nav change or meaningful controlled-sheep movement and updates using visible native entities. It avoids expensive full 2D HUD/state construction and adds no separate game loop.

## Regression coverage
Runtime mock tests assert upper-framing geometry/no sideways bias, cache invalidation and original 2D mode fallback, same-aim preview skip, visible-only buildings and cooldown, cleanup. Exact post-build code verifies the formerly emitted VR ground move is gone, while building/attack/rescue remain. Existing v11.201 through v11.181 editor, fog, XR, Sheep and ARPG tests must pass in CI. Real Quest 2 comfort and performance tests are required before claiming physical acceptance.
