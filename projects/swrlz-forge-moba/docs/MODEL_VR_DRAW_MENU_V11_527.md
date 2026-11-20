# §E v11.527 — immersive Modeling Lab Draw menu

Owner-approved scope: the existing three-stage WebXR spatial menu in immersive Model Studio. Not Quest Browser 2D. No parallel model editor, no alternate geometry backend.

## Operation rail

Draw contains exactly these four actions in order:

1. **Draw Outline** — enter the existing controller-ray plane tracing workflow.
2. **Make Face** — enabled only while a Draw gesture is active and at least three accepted outline points exist. Reuses the current native draw-end validation and commit.
3. **Thicken Outline** — enabled only with one selected mesh that passes the same existing planar, single-open-outline, topology and bind-pose checks as the native Grip extrusion handler. Arms the existing extrusion mode, not a new extruder.
4. **Discard Outline** — enabled only with a nonempty, unfinished Draw gesture. Cancels its preview; committed geometry is not deleted.

The native world-space middle rail visually dims unavailable operations and rejects controller presses on them; action-handler checks also prevent out-of-context invocation. Draw operations are direct actions, so there is no redundant third-stage settings page. Global Undo/Redo remain in the pinned right-side controls, not Draw.

## Native geometry and history

One read-only outline eligibility function supplies both the menu's active state and the existing extrusion's validation. No predicate creates a checkpoint, changes selection, saves geometry, or starts a preview.

Existing controller Trigger-to-trace / release-to-make-face and Grip-to-extrude remain intact; B cancels the current gesture. Existing checkpoints, persistent per-project journal, Undo/Redo, and saved UV/material/rig data stay in their native owners.

The Create, Sculpt, Select, Display, Objects, Transform, Face Tools, Rigging, Animation and Texture & Materials interfaces are not reorganized by this patch.

## Source verification and acceptance

- Compiled source: 504 ordered patches, version/title/build ID and deployment marker v11.527, exact SHA-256 in `source-manifest.json`.
- Regression: `tests/model_vr_draw_menu_v11_527.cjs` validates four actions, all enabled/disabled transitions, controller press guard, read-only shared eligibility and unchanged native extrusion. Versioned Sculpt, Select, Display, Create and UV regressions are retained.
- Inline JavaScript syntax and generated source receipt are checked before deploy.
- **Headset acceptance pending:** In immersive Quest Browser WebXR, verify Draw line preview, Make Face and Discard availability while tracing, Thicken on fresh eligible face, Thicken disabled on arbitrary or already thickened meshes, controller-ray clickability, no extra Draw panel and global history.

Only verified code-build state is a source test; owner headset feedback is the immersive UX acceptance gate.
