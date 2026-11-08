# §E v11.341 — Model VR hover, bounds and model-centred orbit

## Owner observation
Quest 2 Model Studio VR rendered smoothly until a controller target ray crossed a model or its bounding region. The prior v11.340 workspace performed triangle picking from both tracked controllers every headset frame and repeatedly measured part bounds and the native projection.

## Implementation
- Native hover refreshes about every 55–60 ms per controller; trigger select and grip start call the live raycaster immediately.
- One projection is reused across both controllers in each XR frame, with a second native preview refresh only during active grips.
- Reused raycasters, cached world-space part boxes, and a coarse ray–box reject reduce pointless mesh triangle tests.
- Skinned meshes continue to bypass the coarse ray-box reject; bounding refreshes are time-limited for animated parts.
- Right joystick X/Y continuously rotates the model around the existing centre pivot; hold right stick click while moving vertically to zoom.
- Left joystick pans, with zoom-adjusted speed; Precision lowers navigation sensitivity. Recenter resets pitch and scale.
- Saved model topology, material data, editing history, grip-space transforms, and Game XR code are not modified.

## Verification
Candidate GitHub Actions job 42447030410 built all 352 ordered patches into 9,119,871 bytes of HTML with SHA-256 `8806d47c59544600e189de33500d38f8c5c19b0dd8a09f20e3438c2492e1e8c0`. Source-level JavaScript checks passed. The release verifier validates the rebuilt HTML bytes/hash, bundled assets, and targeted runtime syntax. **Physical Quest 2 hover/frame-time and navigation acceptance has not yet been performed.**

Owner test: point both controller rays away, sweep into a detailed part with no trigger held, then orbit horizontally/vertically, pan, press right thumbstick while moving vertically to zoom, and select/grip/release a part. Verify model changes only on grip release and that other VR modes still work.
