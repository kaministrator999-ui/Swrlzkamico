# §E v11.490 — Sorting Hat rig playback + last workspace restoration

This release follows v11.489 without altering user-owned model geometry, UV atlases, saved account revisions, or the original five hat animation clips.

## Playback defect and safe fallback

A cloth rig can be valid in the Rig · Pose · Animate panel while its rendered part is a plain Three.js Mesh. Joint keyframes then change pose data, but cannot deform vertices. The v11.490 render hook checks the exact target part and, **only when it is not already a SkinnedMesh**, constructs a proper skinned version using the existing validated four-weight rig, preserves the scene transform and selection ID, and rebinds the skeleton. Native play/scrub paths remain authoritative.

The supplied owner-specific new resting pose is an independent private .swyrl.json file. It has not been committed to GitHub or silently applied to the owner's cloud record; use the existing selected-card Update Model action.

## Per-project resume

Persist small, project-scoped UI metadata on-device, also carrying it in the next explicitly saved model project:
- Camera exact world position, focus point, projection, view.
- Primary mesh selection, current native tool category/mode.
- Current animation clip and scrub time, rig panel open/closed.
- Native dock mode/widths/collapse states, tool rail fold and inspector scroll.

Restore only if metadata validates and belongs to the currently loaded project. Reuse the existing v11.251 dock controller and v11.476 camera restoration; do not reset mesh topology or replay a save to restore a view.

## Verification and limitations

Run the new Node workspace regression and syntax check, full 467-patch assembly, exact SHA receipt, static browser artifact verification, then the normal dedicated HF deploy. Owner phone/Quest visual acceptance still required. A same-device view is retained even before a manual account save; across-device restoration requires an explicit project save to carry the editorWorkspace metadata.

No third-party service, authentication token or full mesh data is written to localStorage.
