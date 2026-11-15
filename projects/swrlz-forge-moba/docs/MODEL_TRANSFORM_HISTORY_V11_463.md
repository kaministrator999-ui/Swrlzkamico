# §E v11.463 — Restore top Model Studio transform toolbar after Undo

Owner verified native camera orbit and both resizable sidebars working on Moto 5G Power. The top viewport transform bar (Move/Rotate/Scale, axis nudges, Undo/Redo, UV Slide) disappeared after pressing Undo and could not be recovered without changing state.

## Root cause

The v11.320 source hid the **entire** viewport bar unless `ModelAtelier.status().selected` was truthy. History restore can intentionally clear the mesh selection while retaining the model and a valid Redo operation; the user then loses the only visible top history access. Additionally, the bar installer exited early while the original backing strip was absent during remount.

## Scoped repair

Keep the same original viewport toolbar visible whenever Model Studio is open. With no selection, show `Select mesh · Undo / Redo`, disable transform and UV actions, but keep original native Undo and Redo availability. Reselecting a mesh enables transforms again. Keep the same native event handlers and history transaction; rebind the native strip observer if the backing DOM gets replaced. Refresh after an Undo/Redo frame as well as its immediate click. The bar still hides when the modeler itself is closed/hidden.

Do not change persisted selection semantics, source meshes, checkpoints, undo stack, camera orbit, touch docks, toolbar layout, UVs or VR. No parallel transform implementation.

## Tests and acceptance

Compile and seal all 440 ordered patches. Verify selection → Undo causing no selection → Redo and reselect, native history-disabled states, temporary backing-strip replacement, modeler closed, integrated JS syntax and 77 bundled asset receipts. Source tests do not certify physical phone behavior. Existing §E v11.462 visual modes and sidebar/camera fixes remain part of the complete build.
