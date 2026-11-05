# §E v11.278 — Quest wrist clearance + performance comparison

## Observed issue

Owner screenshots show a Quest 2 immersive Nerd Stats panel working in front of the controller, but too close for comfortable reading. Gameplay also slows when menu panels are open, against a baseline that already changes drastically with world density: 17 houses / 1,806 draw calls / 26 FPS versus 38 houses / 3,092 draw calls / 10 FPS. The screenshot comparison does not isolate menu overhead because scene load changed.

## Focused changes

- Keep the full-size native three-page panel and left-joystick (L3) toggle, but change the left-controller-local anchor from `(.13,.24,-.18)` meters to `(.13,.30,-.30)`: 6 cm more vertical clearance and 12 cm farther forward.
- Reuse a shared `THREE.Vector3` for the controller-local-to-world transformation instead of allocating a new cloned offset on every native XR frame.
- Existing VR CanvasTexture text refresh happens approximately every 960 ms; throttle only the Nerd Stats panel to about 1.85 seconds. Force fresh pages when the center action changes the page or a panel is first built.
- Add 4th optional Nerd Stats page to compare approximate callback frame intervals with neither panel visible, stats alone, radial menu alone, or both. One small constant-time accumulator for each state runs inside the *existing* native VR frame callback. No new timing loop, GPU query, WebGL canvas, layout panel, collider, physics or shader changes.
- Existing three pages of gameplay and fog metrics, right-controller ray selection and L3 toggle remain available.

**Limitations:** Browser/WebXR callback cadence is not GPU render time; the "both open" values may include different world complexity than the "neither" values. For a useful comparison, test all four configurations within the *same* match and similar camera/house state. Initial values marked “not enough samples” until 8 or more frames are available.

## Owner Quest 2 test

Enter immersive Sheep Tag. Click left joystick to open Nerd Stats and confirm more clearance while tracking the left controller. Tap the panel center three times with right-hand ray to reach Page 4/4. Hold the same camera view and observe FPS/frame intervals while toggling Nerd Stats and opening/closing the radial building menu. Prefer comparing matched house counts; record unexpected jumping and what menu was open. Close/reopen metrics with L3 and verify movement/placement remains unchanged.

Source verification proves integrity and JavaScript syntax only; hands-on Quest performance acceptance remains with owner.
