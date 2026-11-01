# §E v11.202 — wider Quest camera composition, joystick-only, frame-time reduction

## User observation
The Quest 2 Sheep Tag camera is still too close, with the sheep too low in the user's field of view. Joystick locomotion makes click-to-move unnecessary. The previous camera/house improvements helped lag, but dense construction still costs excessive CPU time.

## Quest composition
The camera is pulled back **22 horizontal world units** and raised **25 units** per unit zoom, from 14/26 in v11.200. Default zoom increases from 1.4 to 1.5 and adds 3.5 units rearward. **The sheep stays attached to the game-world follow point** rather than to an on-screen HUD/camera overlay. This moves the sheep higher in a neutral down-looking VR view as an approximate composition goal, but **cannot lock it to the exact same screen coordinate while the headset physically turns**. WebXR head pitch/yaw and translational tracking remain completely natural, without screen pitching or motion-induced camera rig feedback. Right stick still adjusts orbit and zoom.

## VR input
An empty-ground right trigger stops issuing `stUiCommand('move')`. Left joystick remains the sole movement path in immersive Sheep Tag Play. The original trigger can still select and inspect a unit/house, build at a valid site, attack as wolf, or rescue a captive. Editor selection, Play on touchscreen and non-VR input are unchanged.

## CPU / XR performance
- `se202PreviewOwner()` uses authoritative `stSession.controlledId` instead of serializing full `stViewStatus` with large fog arrays every VR preview. `se202VisibleBuildings()` uses `stSeenByRole` for each visible building; unseen enemy structures are never exposed.
- `se202ShouldRefreshPreview()` avoids costly native `stCanBuild` and clearance calculations when the ray moves less than 0.07 world units, the navigation version and active build/owner/resources are unchanged, and less than 520ms has elapsed; periodic refresh catches mobile units entering the footprint.
- `se202ObstacleSnapshot()` reuses the native collision obstacle list for direct gamepad motion until a build/removal navVersion change or a raised wall crosses its completion threshold. Native AI navigation, networking and original stObstacles remain untouched.
- At most every 650ms the 3D foundation overlay checks for a nav change or meaningful controlled-sheep movement and updates using visible native entities. It avoids expensive full 2D HUD/state construction and adds no separate game loop.

## Regression coverage
Runtime mock tests assert upper-framing geometry/no sideways bias, cache invalidation and original 2D mode fallback, same-aim preview skip, visible-only buildings and cooldown, cleanup. Exact post-build code verifies the formerly emitted VR ground move is gone, while building/attack/rescue remain. Existing v11.201 through v11.181 editor, fog, XR, Sheep and ARPG tests must pass in CI. Real Quest 2 comfort and performance tests are required before claiming physical acceptance.
