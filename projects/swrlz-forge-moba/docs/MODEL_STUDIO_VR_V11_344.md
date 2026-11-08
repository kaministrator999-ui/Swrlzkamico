# §E v11.344 — VR pointer calibration, model view presets, trigger optimization

## Reproduction
In the physical Meta Quest 2, the owner aimed §E's ray at the rock hand's middle finger knuckle, then displayed the Meta system pointer and observed it pointing near the thumb tip. The same owner reported a brief but repeatable frame freeze every trigger click. The OS pointer is an external ray controlled by Meta; the WebXR session provides a targetRaySpace but cannot read the OS-overlay ray direction, so aligning them automatically from within WebXR cannot be guaranteed.

## Changes
- **Aim menu**: independent left/right calibration in controller-local degrees: yaw ±2°, pitch ±2°, both limited to ±25°. Select hand L/R; reset hand or both. Saved to local browser storage `swrlz-model-vr-pointer-calibration-v1`, with safe fallback. The visible ray line and actual pick direction both receive the same quaternion. An adjustment invalidates stale hover data.
- **Views menu**: Front, Back, Left, Right, Top, Bottom, Isometric and Focus. Real immersive stereoscopic camera projection is preserved; only the model's presentation rig is oriented. Right joystick resumes orbit, left joystick pans, right click+vertical still zooms.
- **No UI growth**: the original twelve VR tool button surfaces are reused across Tools, Views and Aim pages, avoiding floating panel overlap and redundant GPU textures.
- **Trigger/Grip**: use cached simplified skin surface contact instead of the dense skinned model’s original triangle raycast. The native bridge returns immediately when the clicked part was already selected. New selections still use native selection (which may itself be expensive). `inspect().picking.lastTriggerMs` and `maxTriggerMs` report actual measured click cost on-device.
- Model geometry, persistence, rigging, materials and native Undo history remain authoritative. The Scene/Game VR workspaces are not modified.

## Verification
GitHub [candidate run 42455530224](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42455530224) passed source integrity, JavaScript syntax, real-Three.js r169 local yaw/pitch aim transforms, per-hand persistence/reset, all seven view presets, and source-level fast-picking/no-op selection checks. Generated HTML: 9135955 bytes; SHA-256 `7adec1e91ee56f5eeda364c3d733de3d95d8fb5824753d943ef6382f27bc3d4f`. This does not verify OS ray alignment or physical Quest trigger frame times.

## Owner checks
1. Enter VR and open **Views → Aim**. Select the right hand, hold the controller still, and compare the §E ray with Meta's OS ray. Adjust yaw/pitch 2° per press; repeat left hand. A saved calibration survives a browser reload.
2. Return to **Views** and verify top, front, side and isometric presets. Move right joystick to orbit after a preset. No overlapping palette buttons.
3. Click the already selected hand several times, then a different part, and check whether the momentary freeze remains. Use Model VR inspect's `picking.lastTriggerMs` to correlate it; test grip and precise finger targeting separately.
