# §WYRL§ Engine v11.514 — immersive rigging through native WebXR menus

**QA:** issue #472, items #10 and #12 (partial implementation) with generic #11 pose deformation coverage.  
**Base:** verified v11.513; this release does not modify specific starter models.

## Menu integration is a strict requirement

No detached DOM menu or new stand-alone VR menu was introduced. The existing `se340CreateModelVRUI` spatial console remains the only immersive menu renderer, hit test, page dispatcher and button animation owner. Its normal opaque panel hit blockers, ray hover, Trigger press behavior, 12-slot pages, Controller/Grip input profile, A/X studio wheel, visual active/disabled states and session reset remain in effect. The **Studio → Rigging** choice and **Studio wheel → Rigging** choice open the same native spatial console's Rigging page.

The **Rigging** page contains previous/next bone, Undo rig edit, X/Y/Z ±5° pose rotation, Weight Painting, Studio and Exit VR actions. There is no newly invented controller shortcut or separate HTML screen. The page header identifies **POSE / NOT REST** to avoid changing bind skeleton when merely posing.

The native **Weight Painting** page contains Add/Erase influence, Stop Brush, radius ±, step ±, previous/next bone, Undo rig edit, back to bone posing, and Exit VR. All are existing `se340ModelXRAction` + `se350Dispatch` paths, with the source UI's existing named native visual buttons and hit blockers.

## Joint manipulation in immersive WebXR

3D bone spheres and connected shafts are `se340XR.scene`-owned controller gizmos that track the model's real bone world transforms. They are only visible while rig tools are in use; they are not persisted as model meshes or UVs. The ordinary headset ray selects a joint **only when it has not hit the native menu**.

Right Grip rotates the selected bone **in pose space**, using the grip's world quaternion delta and the original joint's parent quaternion. The underlying native `se220RigPose` updates actual three.js GPU skin deformation. Release commits once; headset tracking loss, VR exit, controller cancellation and B cancel restore the prior pose. Menu X/Y/Z ±5° increments are bounded to the rig validator's ±2.8 radians and produce separate Undo snapshots. Rest bones, authored UVs and hierarchy are not rewritten.

## Weight painting in immersive WebXR

In Weight Painting, hold Right Trigger over the real skinned target surface. The controller ray uses the same current `se340Hit` geometry picker; native menu targets get precedence. Each brush sample maps its world hit into the existing skinned mesh's local coordinates, uses `se513SkinMath.region` and up to four normalized influences, and updates the real `skinIndex` / `skinWeight` GPU attributes. The brush has smooth radial falloff, configurable radius and strength and capped mesh budget (120,000 vertices).

On release, a valid brush stroke writes explicit `part.skinning` weights for the **current project**, not a new imported mesh, with one model history checkpoint. Cancel restores the initial GPU attributes without persisting. The Rigging Undo control can restore saved paint or pose edits **in VR** without rebuilding the borrowed model scene, and reconciles a corresponding native source-history snapshot when possible.

## Acceptance / exclusions

**Automated checks:** native menu ownership and Trigger passthrough, 3D joint visual gizmos, direct Grip pose rotation, pose cancellation, bone selection, saved weights, live GPU influence, persistence, Undo, model menu navigation, cleanup, 491-patch source rebuild, inline JS syntax, static delivery size and SHA seal.

**Physical headset acceptance still pending:** button visibility/selection on Quest, grip feel and speed, frame budget on large sculpted mesh, bone visual clarity under extreme zoom and account save/reload. The general connected-joint rest-editor #10 and arbitrary complex mesh #11 still need additional device validation. Existing #3/#5/#7/#8 work and prior five pending user QA requirements remain open.

**No specific hat or starter repairs.** This change improves reusable rigging behavior and only extends established immersive XR GUI infrastructure.
