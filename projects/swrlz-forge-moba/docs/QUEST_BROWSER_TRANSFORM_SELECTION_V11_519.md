# §E v11.519 · Quest Browser 2D transform gizmos, deselection, bounds

**Scope:** This update concerns the ordinary **Model Studio webpage inside Meta Quest Browser**, not the immersive WebXR workspace. The original native Model Atelier source, project structure, mesh topology, rig weights, and current 2D transform drag/Undo code are retained. The separate VR #5/#7 and v11.518 immersive project/runtime fixes remain intact.

### 1. Transform gizmos must move the selected object

The Meta Quest Browser emits projected mouse-like controller events. The previous native 2D gizmo picker used mouse-sized 12px targets and rejected events when `elementFromPoint` returned the canvas container instead of its actual canvas, even for a canvas-originated pointer. v11.519 uses a **28 CSS-pixel** projected target for Quest controller pointers, larger on-screen gizmo visuals, and accepts pointer ownership only when the original target is still the canvas and the element below is the canvas or its direct container. It also accepts a non-primary Quest controller input for gizmos, preserving native pointer capture, preview, clamped object transforms, history and Save/Undo. Actual menu/panel presses cannot be converted into model events.

**Test:** select an object, use Move then Rotate then Scale, and press/drag X, Y and Z gizmos with a Quest pointer. Verify transforms commit on release, Undo restores the original values, grabbing a gizmo never changes object selection or camera rotation, and the controller can click its tip or visible outer shaft.

### 2. Tap the selected mesh again to clear it

A Quest 2D click on the exact same **visible model** toggles selection off, but only if (i) the pointer has not moved more than 12 CSS pixels, (ii) no native transform/component/precision gizmo captured the pointer, (iii) mesh selection mode (not vertex/edge/face) is active, and (iv) multi-selection grouping is not active. Clicking another mesh preserves existing native mesh switching; dragging retains selection. No source geometry or project history entry is created by deselecting.

**Test:** click a sphere once (selected), click it again (deselected), select the cone (selected), drag a selected gizmo (sphere stays selected) and try group selection or vertex mode (original behavior remains intact).

### 3. Show/Hide selection bounding box

Add an accessible **Hide bounds / Show bounds** toggle in the existing 2D viewport controls. It controls only the native Three.js `BoxHelper` selection boundary, not the actual rendered model, wireframe overlays, rig guides, camera, controller gizmos or UVs. Reapplying a saved project, refreshing the model rendering, or rebuilding gizmos preserves the chosen display state for the current page.

**Test:** toggle off the gold/yellow selection cuboid visible around the selected sphere; verify it disappears but red/green/blue transform handles remain usable and the mesh itself stays visible. Toggle it back on and verify the box returns.

### Existing v11.518 fixes included in the v11.519 release

The immersive VR startup `se220RigAvailable is not defined` error is fixed by v11.518's native Model Atelier bridge. User-selected startup projects and authenticated same-revision IndexedDB cloud cache remain separate from this 2D-only change. On first signed-in cloud load a full project download is required; on later opens the cached copy is reused if the account still confirms the same revision, with a full fetch on revision change.

### Acceptance limits

Automated synthetic event tests and compiled-source checks are *not physical Meta Quest Browser acceptance*. Test in the Quest 2 headset and report any remaining controller-specific capture issues or unintended boundary-helper visibility changes.
