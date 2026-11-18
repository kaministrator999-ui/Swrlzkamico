# §WYRL§ Engine v11.517 — QA #5 and #7: rotation isolation and immersive projects

**Environment:** Meta Quest Browser **immersive WebXR Model Studio**, not the normal 2D editor. Native project/account source and project history are reused. The original 3-stage VR menu (far-right tool rail, middle operation rows, left modifier panel) remains the only VR GUI. No new HTML dialog, extra WebXR input listener, or OAuth path is introduced.

## #5 — camera orbit versus object rotation

- Right-stick orbit changes the XR view/reference space while keeping source model transforms untouched.
- Choose a model with the Trigger, then use **Rotate** and controller Grip or native Rotate gizmo. The existing native group-transform system applies actual selected-part TRS around its pivot, checkpointing only once on release and rolling back on cancel/tracking loss.
- The added guard refuses Rotate with no selected model and cancels any in-progress Rotate gesture if its camera yaw/pitch state changes unexpectedly. This does not prevent legitimate head movement.
- **Acceptance:** with two meshes, orbit the camera and verify neither authored rotation changes. Then rotate only mesh A and verify mesh B, the workbench, and HMD orbit state remain unchanged. Confirm Undo and reloading show the model rotation saved.

## #7 — My Projects and Starters in immersive VR

Open the existing **Projects** primary tool rail. The native middle operation rows offer **On Device**, **Google Account**, and **Starters**; Previous/Next page, four clickable named projects per page, Open, and Cancel. Rows are the existing native canvas/raycast buttons; the project's name appears on the corresponding row, and selecting it highlights the row. Clicking Open selects a saved model in-place without ending the VR session.

The project list originates from the existing IndexedDB records, the authorized §Chat account connection, and the native starter registry. Google credentials do not enter the WebXR renderer. Only projects suitable for **Model Atelier** may actually open inside this modeling session. Unsupported game-scene projects remain unmodified; the user is told why a switch cannot proceed.

Before switching, the existing persistent local project store saves an **independently named recovery copy**; storage failure prevents any source mutation. When unsaved work is present, Open requires a second explicit confirmation and offers Save first through the existing controls. The native loader, project history, account validation, and identity remain authoritative. Failed loads restore the previous project when possible. A starter becomes a new independently identified project, never a modification of its canonical source.

The active WebXR session, scene, renderer, spatial menus and controller bindings are preserved. Switching temporarily suspends the XR model-identity frame check, releases the old Model Atelier root from the presentation, invokes the native project loader, then borrows the new native model root. It invalidates prior picking/hover/skin display caches, resets selection/inspect mode and recenters the new model.

## Validation and remaining owner acceptance

Automated tests cover permission and catalog boundaries, local/account/starter selection, verified backup-before-load ordering, startup project identity, recovery after invalid load, storage quota failures, cancellation, native menu hit targets/name refresh, and camera/model transform separation. Tests also preserve original Three.js r169 skeleton and VR menu regression coverage.

**Still requires physical Quest confirmation:** head movement and right-stick orbit vs. selected object rotation on multiple meshes; actual Google connection and My Projects listing; selecting a project after unsaved edits, both cancellation/confirmation branches; opening different saved models and a starter while staying in WebXR; after opening, check materials, rigging, Undo, source name, and device/account reload. Avoid using a unique unsaved project for the first manual session-switch test.

No physical headset acceptance has been inferred from GitHub Actions.
