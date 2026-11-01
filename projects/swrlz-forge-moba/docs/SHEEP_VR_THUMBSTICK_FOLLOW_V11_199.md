# §E v11.199 — Sheep Tag Quest thumbstick movement and follow view

## Request
In immersive Sheep Tag Play, the **left Quest 2 joystick** must move the controlled sheep, and the camera must snap to and follow the sheep from a wider elevated distance.

## Implementation
- Left stick maps to camera-relative forward/backward/strafe/diagonal motion, using the same native movement order, collision/clearance and wall-slide logic as the established touch joystick. Analog strength controls speed. Releasing the stick stops the order. No new game loop or long automatic click-to-move path.
- Sheep Tag camera no longer consumes the left stick as a pan input. On entering gameplay, the XR origin snaps once to the current sheep; the default strategic distance is **1.4×** (25 × 1.4 behind, 17 × 1.4 above), then tracks the sheep smoothly. User head rotation is untouched.
- Right stick remains camera orbit/zoom; the manual Free/Follow toggle is preserved. Only immersive Sheep Tag gameplay is affected; §E editor flight, saved maps, LAN input, flat/mobile controls and Model Atelier are unchanged.
- Cleanup cancels a held VR move order on XR exit. Deadzone and Quest axes use the existing device mapper; collision and navigation remain native.

## Validation
Node mock regression: `node projects/swrlz-forge-moba/tests/test_v11_199_sheep_vr.cjs`. Strict source build/manifest verification must pass before the separate pinned deploy request. Physical Quest 2 verification remains necessary to confirm controller feel, headset comfort and wider framing.
