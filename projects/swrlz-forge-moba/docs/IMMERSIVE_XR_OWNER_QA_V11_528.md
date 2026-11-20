# §E v11.528 — Immersive WebXR owner QA follow-up

Scope: **Meta Quest Browser immersive WebXR** in Model Studio, not the regular 2D Quest Browser editor. Preserve the original three-stage VR menu, controller profiles and native Model Atelier document.

## Projects

The permanent Projects category now opens a larger, in-world dialog instead of a slim list, using the existing spatial palette's CanvasTexture styling. Four card-like project entries per page are shown with Device / My account / Starters tabs, pagination, Refresh, Open, Save to device, Save to account, Clone, and Close. Content and operations come from the preexisting authenticated `se517XRProjects` library. The active model, account identity, and XR session remain native; modal ray capture blocks background editing. Save-to-account requires an authenticated §Chat session; failures are not reported as success. Account load normalizes prefixed project IDs and confirms an actual loaded cloud revision.

## Posed meshes and Push/Pull

When the native sculpt guard rejects a skinned mesh with `SCULPT_REQUIRES_BIND_POSE`, the existing VR interface offers **Set Rest Pose** or **Keep Pose**. No automatic pose change occurs. Confirm validates zero joint rotations against the existing rig schema, stops playback, checkpoints in native rig history, updates the same rig and marks a project edit. This does not change weights, UVs, or keys. The user should retry Push/Pull after confirming. Cancel leaves the pose unchanged.

## Gizmo ray movement

Trigger and Grip on a visible X/Y/Z transform gizmo use the tracked controller aim ray intersecting a stable transform plane, rather than deriving the edit solely from grip position. Move projects onto the selected axis, Rotate uses the selected axis, Scale uses ray displacement; existing `se350Tools().beginGroup/updateGroup/endGroup`, preview, snapping, precision rebasing, safety checks, B cancellation and project undo remain authoritative.

## Adjustment groups and Meta buttons

Where the native context panel has complementary minus/plus tools, a grouped parameter toolbar displays those controls together, live values when available and their original action IDs. Duplicate originals are hidden while the toolbar is shown. The Meta Quest left controller Menu button toggles the existing tool menu **only if** its button 6 is exposed by the browser; the mapped X shortcut is retained for OS-reserved controllers.

## §Chat and My Projects cloud saves

Both surfaces invoke the same authenticated editor-cloud save path with stable active project IDs, local snapshot first, confirmed durable cloud-save receipt and explicit failure feedback. Google credentials remain in the existing §Chat-origin authenticated bridge; no additional server or new OAuth protocol.

## Acceptance

- Inspect the large Projects window in Quest immersive mode; source tabs, four cards, pagination, selection/open/confirm, save and close should work without editing objects behind the dialog.
- Pose a rigged object and try Push/Pull; Keep Pose must preserve the pose, Set Rest Pose must return to neutral and be undoable.
- Select an object and drag its Move, Rotate and Scale gizmos with controller aim ray; release commits once, B cancels.
- Inspect Sculpt and rig-weight +/- controls; parameter grouping must be legible, clickable, and retain correct underlying values.
- Test left Menu where supported and X fallback; right OS Menu must remain owned by Meta.
- With a signed-in account, save from Chat and My Projects, refresh list and reopen on account; test failures/no sign-in without false success.
- Preserve previously verified Select, Sculpt, Create, Display, Draw, rig, project journal and texture workflows.

Automated checks validate source structure and assembled syntax; hardware interactions and actual authenticated cloud round trips require owner testing on Quest and connected account.
