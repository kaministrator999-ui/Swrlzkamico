# §E v11.276 · Quest left-controller Nerd Stats

## What the screenshots actually show

The screenshots show the ordinary floating **Quest Browser window** with the existing on-page Sheep Tag Nerd Stats HTML panel on its right side. That is **not** an immersive WebXR rendering surface, even though the user is wearing the headset and pointing Quest controllers at the browser window. HTML running in a floating 2D browser window cannot follow the physical tracked left controller: its position is limited to the browser document/window.

## Immersive XR behavior

After entering genuine immersive WebXR Sheep Tag Play, the existing Three.js three-page **metrics** canvas panel follows the **left controller** every native XR frame (the existing `se193XRFrame` wrapper, no new animation loop). Its local offset is `(+0.13,+0.24,-0.18)` in controller coordinates, keeping it above and in front of the left hand. A normal `Object3D.lookAt(head.eye)` orients the panel's **+Z texture front** to the viewer; the previous use of a camera-style `Matrix4.lookAt(panel,head)` could show the reverse side of the double-sided texture. The controller-follow does not alter headset camera tracking or player movement.

Left joystick press **L3** continues to toggle the existing panel. Right controller ray still handles panel hit tests and page cycling. If the left tracked controller is unavailable, the same panel moves to a readable head-relative spot instead of following the right controller. No changes to native multiplayer authority, AI scheduling, model/particle/rendering budgets or browser HUD.

## Physical test

On Quest 2:
1. Observe the browser window HUD and confirm it remains 2D while still in the floating Quest Browser window.
2. Enter **immersive VR** in Sheep Tag.
3. Press **left thumbstick (L3)** to open Nerd Stats, rotate the left controller in front of the headset, and verify the panel follows the left hand and words remain readable instead of mirrored.
4. Tap with the right controller ray to change the page; verify L3 hides and reopens it. Check the panel is not blocking build input or sheep movement.
5. Optionally disconnect/reconnect the left controller to confirm safe head-relative fallback and automatic restoration.

Automated checks cover exact assembled source integrity, JavaScript syntax and version/provenance; physical Quest behavior remains owner acceptance.
