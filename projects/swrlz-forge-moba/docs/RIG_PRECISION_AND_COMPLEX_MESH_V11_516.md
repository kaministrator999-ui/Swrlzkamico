# §WYRL§ Engine v11.516 — Generic skeletal rebinding and precise weight targeting

Tracking: QA issue #472 items #11 and #12. Source baseline: v11.515 (492 ordered patches).
Scope: all valid rigged projects sharing the existing `SkinnedMesh`, four-influence GPU skinning, and native project history. This release does not modify starter geometry or create a separate immersive menu.

## New precision controls

**2D Model Studio → Rigging → Editable bone influence:** keep the existing Add/Erase and size/step sliders. New **Target: Region / Single vertex** switch. Region uses existing continuous smooth radial brush and selected bone. Single vertex chooses the nearest *posed surface vertex* inside radius and synchronizes coincident UV seam indices, never the neighboring geometric vertices. GPU `skinIndex` and `skinWeight` are updated during the stroke. Selection is locked until release, and a valid completed stroke is one history checkpoint.

**Immersive WebXR:** the same target switch is now inside the existing far-right Rigging rail → Weight Painting operation list and native details page. It reuses the original 3-stage spatial GUI, controller ray priority, Right Trigger paint input, Grip pose tools, and in-VR Undo. There are no new detached panels, browser DOM replacements, second VR input dispatcher, or new project documents. Switching selected bone during an unfinished paint stroke cancels that stroke rather than mutating another joint.

The existing 2D bone-influence point cloud is refreshed while brushing (with a bounded 100 ms cadence). Immersive WebXR now renders up to 1,200 color-coded influenced vertices inside the existing skeletal gizmo group, following deformed bone positions on the existing WebXR frame loop at a bounded cadence; those markers are non-interactive and never intercept menu/object raycasts. Their scene resources are disposed on VR exit. These overlays are visual aids, not additional editing menus.

All edits use the existing `swyrl-explicit-skin-v1` four-influence format and normalization, rejecting missing topology or invalid weights. Posed-point matching and UV seam co-selection are not specific to any starter.

## Rig binding and hierarchy stability

On a genuine skeleton rebind (for example, after changing bone rest positions or hierarchy), remove the previous native root bone objects and previous `SkeletonHelper` from `modelRoot` before replacing the skeleton, to avoid stale scene nodes and double skeleton visualization. The current target's mesh, geometry, UVs, source project ID, and saved skin weights are not replaced by that cleanup.

## Regression and limitations

The v11.516 test suite covers normalized/nonnegative skin weights under repeated add/erase; precise single-vertex and mirrored seam edits; region falloff and posed-space selection; and rebind/pose/reset tests on box, sphere, torus knot, and open plane meshes, including nested bone rotations, nonuniform mesh and model transforms, changing a joint's parent, inverse bind matrices, and repeated neutral-rest restoration. Previous v11.513/v11.514/v11.515 Three.js r169 tests remain in the release test path.

**Owner-device acceptance remains mandatory:** physical Quest 2 native menu selection, controller tracking/latency, fine vertex targeting, large sculpted meshes near the 120,000 vertex limit, save to account, reload, Undo/Redo and correct influence colors under animated bones. Generic harness tests do not establish bug-free behavior for every possible arbitrary mesh or actual headset performance. Run save/restore on a copy of a project first.
