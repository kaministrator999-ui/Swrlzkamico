# §E v11.362 — Quest 2 Touch model labels in immersive Model Studio

## Scope
Use the already bundled MIT-licensed `oculus-touch-v3` left/right mesh and UV texture assets as the *tracked* controller representations. Reuse the existing `renderer.xr.getControllerGrip` objects, native WebXR frame loop, Controller Studio current profile, and Model VR tool/brush state.

Every controller shows small camera-facing text sprites near the actual trigger, grip, thumbstick and face buttons. Left labels are LT/LG/LS/X/Y; right labels are RT/RG/RS/A/B. The native Meta system/home controls are not remapped or labeled.

## Actual active mappings
- Inspect: RT selects, LT multi-selects, RG does not edit, LG moves the workbench, LS pans, RS orbits.
- Move/Rotate/Scale: RG transforms the *existing selection*; LT multi-selects; trigger selects.
- Two-hand: explicitly armed grips transform the selection; does not automatically select geometry.
- Sculpt: RT performs the active brush (Push/Smooth/Flatten/Inflate/Pinch/Translate), LT samples/holds temporary Smooth, LS changes brush radius/strength, RS orbits.
- Draw: RT traces an outline; release creates a native face. Extrude mode uses RG to extrude the selected face.
- Lasso: RT traces a saved region mask for sculpting.
- A/B/X/Y show the selected real profile shortcuts, including tool/brush wheel, cancel, palette and undo. Custom profiles and controller modes are reflected from Controller Studio's `currentProfile` rather than another shortcut list.

The source does **not** pretend UV Slide, advanced rigging, texture paint and other desktop operations are VR tools until native headset tool actions are implemented. They retain the existing studio controls.

## Lifecycle and performance
- Single XR session and renderer. No animation loop, hand tracking or extra raycasts.
- A bundled controller JSON file is fetched lazily once per tracked hand and aborted on exit. Original source mesh geometry is not added to the saved model.
- Texture and geometry are shared per hand; five label textures per controller are allocated once and only repainted when a tool, brush, menu page or profile changes. Button highlight uses sprite tint.
- On exit/disconnect, labels and meshes are removed. If a mesh fails to load, the existing synthetic capsule remains and tool hints still appear.
- Source provenance: `assets/models/webxr-touch-v3/LICENSE.md` (MIT-licensed WebXR Input Profiles reference model). Physical Quest 2 sizing, legibility and tracking need owner validation.

## Test on headset
Enter Model Studio → Model VR, look at both controllers, select Inspect, Move, Rotate, Scale, Sculpt (switch between two brushes), Draw, Extrude and Lasso. Confirm labels follow the same tracked controllers, update only with the actual tool/profile, do not obstruct pointer hits, stay small enough for each hand, and disappear cleanly when leaving VR. The controller tracking does not depend on hand tracking.
