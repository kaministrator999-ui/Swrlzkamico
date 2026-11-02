# §E v11.211 — Meta Quest Camera/system-menu stability

## Owner's on-headset observation
While playing Sheep Tag on Meta Quest 2, opening Meta's own system Camera menu for an extended period causes increasing lag and an apparent camera/head tilt or drift. It may continue as the user returns to the game. This is **not** the in-game §E Capture/wrist menu.

## Evidence
WebXR XRSession visibility states are visible, visible-blurred and hidden. When blurred, browsers can throttle XR animation-frame callbacks and stop controller input; when hidden they may stop XR callbacks entirely (MDN https://developer.mozilla.org/en-US/docs/Web/API/XRSession/visibilityState). This can produce stale frame-time intervals. Meta's WebXR frame-rate guidance also notes that missing frames lead to compositor reprojection/stutter (https://developers.meta.com/vr/documentation/web/webxr-frames/).

## Targeted fix
- Listen for XRSession visibilitychange and check the state each active XR frame.
- Suspend only §E-specific XR camera reference translation, ray/cursor, input-wheel, modal panel, optional decoration and fog-UI frame adapters while the Meta OS has focus. **Never pause the real headset compositor, network/gameplay simulation, authoritative fog visibility or main rendering loop.**
- On return, maintain the prior tracking origin, yaw, pitch, zoom and stable reference-space offset; reset only XR frame-delta timestamps. Avoid forced camera recenter or giant positional corrections.
- Limit the Sheep Tag world-follow **translation** to 3.2 units/sec for about 850ms after return versus its ordinary 13 units/sec. Never modify the native tracked headset quaternion.
- Use a >170ms XR callback gap to trigger brief recovery even if the browser never reports an explicit visible-blurred change.
- Block accidental A/X, alternate stick-click and right grip actions until the user releases them after a focus transition.
- Hide/restores only optional §E decoration and game HUD objects, remembering their original visible state. No change to native quest OS windows.
- Expose state and counters at window.SWYRL_ENGINE_QUEST_OS_STABILITY_211.diagnose() (blur events, hidden events, callback gaps, largest gap, reference writes blocked and frame skips).

## Hardware acceptance
1. Launch v11.211 on Quest 2 and enter Sheep Tag Play; verify ordinary rapid build and headset view.
2. Open Meta's own system Camera pane, keep it open, then return. Repeat the cycle three times, observing tilt/drift and lag.
3. Confirm the world doesn't jump, yaw/roll remains stable, and no accidental building, skill casting or gripping fires.
4. Read §E Metrics and (if available) the new OS-overlay diagnostics. If no focus events or timing gaps are reported during severe lag, the WebXR application may not be informed of Meta's compositor state.
5. If lag or tilt occurs even outside §E or after leaving the webpage, investigate Meta Quest Browser/OS performance separately.

## Limits
Quest OS camera compositing and hardware tracking are **not controlled by web application code**. Automated tests verify app-state transitions but cannot certify headset FPS, comfort or Meta OS behavior. No editor/modeler changes or new gameplay house rotations.
