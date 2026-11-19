# §WYRL§ Engine v11.520 — Quest Model Studio QA fixes

**Source lineage:** v11.519 + append-only v11.520 patch. **Scope:** regular Meta Quest Browser 2D viewport versus immersive WebXR must remain distinct. Preserve source geometry/UV/rigging, account project revisions, the native right tool rail → middle operation list → left setting panel, controller profiles and one WebXR frame loop.

## 1. Immersive WebXR — UV-painted sculpting

Repro: Open a model with a UV paint image, enter immersive VR, choose Sculpt and a brush, hold right Trigger while pointing at its surface. Previous behavior could show no mesh deformation. Exact surface hits can fail on textured back-facing UV triangles, and sparse original mesh vertices may fall outside a small brush.

v11.520 changes: The existing **precise** WebXR pick path first tests original triangles as before. Only when that fails in Sculpt mode does it try a double-sided raycast on UV-painted source geometry, reverting material sides immediately (no material or UV mutation). The native Sculpt operator uses the same preserved position/UV geometry and save/Undo. On UV-painted meshes, when the user’s brush radius is smaller than the distance to every source vertex, it uses a bounded effective radius so a stroke influences actual vertices instead of silently doing nothing. Native status reports that adaptation once per stroke. The source UV coordinates and paint PNG remain unchanged.

Accept: A simple textured sphere and an authored UV-textured hat visibly respond to Push/Indent/Pull and Smooth where geometry permits. Image stays aligned during and after native save/reload/Undo. Nontextured mesh sculpt behavior and lasso constraints unchanged.

## 2. Meta Quest Browser 2D — actual mesh versus boundary

Repro: Open **regular Quest Browser** modeling page, select a sphere, then aim with the controller and click near its selection boundary. Previous behavior may pick a BoxHelper instead of a mesh.

v11.520 changes: Three.js BoxHelper selection bounds become raycast-inert in the 2D viewport while remaining visible and controllable with the existing Show/Hide Bounds button. The final controller tap reconciles any legacy selection from native hit-testing against the **actual model mesh**. Current gizmo drags, multi-mesh selection, component editing, and immersive VR are not overridden.

Accept: Click selected mesh → deselect; click different mesh → select it; click a bounding line over empty canvas → it cannot select a helper; drag XYZ gizmos continues normally; toggling bounds affects only helper visuals.

## 3. Immersive WebXR — trigger-held continuous model movement

Repro: Select model, switch to Move or Grab, point at selected mesh, press and hold right Trigger and move controller. Previous behavior used Trigger primarily for selection, Grip for movement, and only captured Trigger drags on actual XYZ gizmos.

v11.520 changes: A Trigger press on an **already-selected mesh** in native Move or Grab now begins the established native transform transaction. On a continuous hold, 14 mm controller movement engages ongoing native group translation; it rebases the initial pose without a jump. Every subsequent XR frame streams a preview. Trigger release calls the existing single-step commit; B, tracking loss, profile changes, or a sub-threshold tap cancel the pending gesture without a phantom edit. Menu panels and actual visible transform gizmos retain priority. Pressing a previously unselected model still selects it rather than moving it. Other modes keep their original Trigger semantics.

Accept: Trace a slow 10–20 cm controller movement with held Trigger, see continuous movement **before** release, release to save once, Undo once. Quick Trigger tap does not shift mesh, and selecting a different part is still a selection.

## 4. Immersive WebXR — headset-facing spatial menus

The existing far-right main tool rail, middle operation list and native left modifiers all remain inside the original scene-owned panel. Every XR frame, after the original menu updater, the panel rotates its **front** to face the tracked headset. It preserves the current world anchor even while changing head position or dragging a menu with Grip. It does not recenter menu positions, change operation ordering, change controller ray hit priority or attach to the camera.

Accept: Turn head or physically move around the world-space menu; its front faces the headset continuously without relocating. Grip-place it, turn again, and it still faces the headset from the new saved location. Current menu operations remain selectable.

## Verification and limits

CI reconstructs the full source from the governed patch chain, checks generated inline JavaScript and the precise release marker, and runs native Three.js r169 and compiled-source regression checks for textured sculpt, direct Trigger move/no-op taps, menu facing, Quest 2D picking, native rig, previously saved projects and UV/topology.

GitHub Actions tests **do not substitute** for actual Quest 2/3S headset interaction testing. The release is not considered live until separate source-sealed Hugging Face deployment succeeds.
