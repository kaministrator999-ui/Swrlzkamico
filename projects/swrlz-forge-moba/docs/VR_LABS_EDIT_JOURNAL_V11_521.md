# §E v11.521 — Immersive Modeling Studio Labs and project history

## Scope and source of truth
This release modifies the existing native Model Atelier project document and one grippable world-space XR menu. It does not create another viewport, XR input dispatcher, workspace model, cloud host, or project history owner. The append-only patch is `patches/v11_521_model_labs_persistent_history.py`, placed after v11.520 in the ordered source manifest. The native project history implementation is `runtime/model_edit_journal_v11_521.js`.

## Permanent Menu 1 layout
Top (never changes lab): **Labs**, **Projects**, **Display**.
Contextual middle (Modeling Lab): **Select**, **Transform**, **Sculpt**, **Create**, **Draw**, **Objects**, **Face Tools**.
Bottom (never changes lab): **Undo**, **Redo**, with a visual gap above the two buttons.

Save lives in **Projects**. Delete is a guarded, second-press-confirmed action in **Transform**. The existing Grip moveable world-space menu, three-stage leftward expansion, native UI interaction priorities, and controller profiles remain in place. Menu 2 under Labs offers Modeling, Rigging, Animation, and Texture & Materials. Switching labs changes only the middle-category menu entries and tool context, preserving the model and project.

Transform Menu 2: Move, Rotate, Scale, Grab (freehand), Precision, Snap, Delete selected. Native Trigger gizmo and selected-mesh interactions remain; Grip manipulates the already selected model through existing transform gestures. Unselected meshes remain Trigger-selectable. Gesture cancel/commit ownership is unchanged.

Rigging Lab currently exposes native bones and weight controls; Animation Lab exposes limited existing keyframe/playhead functions. Texture & Materials Lab establishes category navigation, but several of its detailed immersive editing operations are explicitly placeholders. Do not report those as production texture painting.

## Durable edit journal
Each model document carries `modelAtelier.editJournal` with schema `swyrl-edit-journal-v1` and an append-only `events` array. An event stores monotonic `seq`, UTC `time`, `type` (edit/undo/redo), the originating lab, a label, and either reversible field deltas or an undo/redo target sequence number. Events are never removed when undoing/redoing; the active state of each lab is derived from the chronological log.

The journal is **document-scoped**, not an editor-global undo stack. Opening another project binds a different document and its journal. Reopening a saved project restores its own log; an empty newly initialized journal does not invent pre-release history. Each lab's Undo/Redo only considers edits made in that lab. Reversals of fields subsequently modified by another lab fail safely on conflict instead of discarding later geometry. The current implementation records authored model-part and rigging deltas; future advanced operations need explicit coverage tests as their submenus are refined.

History information is available through the native project journal runtime interface. A paged, user-facing visual history explorer belongs to a later submenu pass and is **not** claimed as completed in this release. Persist by saving the project; autosave/account sync availability still follows existing project-save services.

## Engineering acceptance
1. Source manifest names 498 ordered patches and matches the built byte count and SHA256.
2. Native journal unit tests demonstrate consecutive undo/redo without undoing history events; cross-project separation; saved reload continuity; texture-vs-model lab isolation; rig undo/redo; dependency-conflict rejection.
3. Native menu includes the fixed top, contextual lab middle, Undo/Redo bottom, proper live actions, and 12 rig-weight rows without a duplicate workbench.
4. New and existing targeted Node/Python tests pass; static Space pages and JS load as inline browser media (not attachments).
5. On Quest headset, manually validate menus from multiple head angles, Grip menu placement, Trigger and Grip transform, project switching, save/reload, and lab-level Undo/Redo. The tests are not a substitute for headset acceptance.

## Release limitations
Texture/Materials immersive authoring controls and the paged visual history explorer are follow-up submenu tasks. Continuous edit capture depends on native authoring checkpoints and signal hooks; new tool families must be connected to the journal as they are implemented. Existing older history that was never persisted cannot be reconstructed retroactively.
