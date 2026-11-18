# §WYRL§ Engine v11.513 — generic rigged-mesh weight editing

**Issue:** #472, items **#11** and **#12** (partial implementation; both VR Browser 2D and immersive VR require separate owner acceptance).  
**Baseline:** sealed v11.512.  
**Design constraint:** do not replace the skeleton, rewrite UV data, import a new mesh or lose My Projects history.

## Underlying skeletal responsibility

The existing Three.js `SkinnedMesh` and four-influence GPU skinning remain the source of truth. A `swyrl-cloth-skin-v1` skeleton has one `targetPartId`; new cloth skinned-mesh creation is restricted to that part instead of quietly applying the cloth skeleton to unrelated objects. Existing parent/child joint definitions, bind transforms, animation clips and saved rest poses are preserved.

The neutral bind, actual pose, reset pose and unrelated-mesh test uses **Three r169** on generic cylinder-based multi-bone fixtures, *not* a Sorting Hat-specific approximation. This tests core bind correctness but does not imply the full Sorting Hat deformation bug is fixed.

## Weight editor

Open **Model Studio → Rigging** on a project carrying a valid cloth skeleton and matching editable target mesh topology. Select a bone by its existing joint list or viewport picker. The existing colored influence preview remains.

The new **Editable bone influence** section has:

- Brush radius (0.02–1.5 local model units).
- Weight step (1–50% of available weight per brush sample).
- **Mode: Add influence / Erase influence.**
- **Paint selected bone weights / Stop painting weights.**

While armed, clicking and dragging the actual skinned surface paints its selected-bone weights, using smoothed finite radial falloff. Four influence slots remain normalized; if a new bone is added to an already full vertex, the lowest-priority original influence gives up a slot. The other retained weights rescale proportionally so vertex mass is always exactly one. A zero-weight vertex defaults safely to the root; erasing the only root influence does not leave an unbound vertex.

Painted samples affect the live GPU `skinIndex` and `skinWeight` attributes. On pointer release, one native project Undo snapshot is made and a validated `swyrl-explicit-skin-v1` array is saved under the existing `part.skinning`. On cancel or tracking/editor change, the native GPU preview is restored without modifying the project. Original vertices, UV maps, materials and part IDs are not rewritten.

If the current topology does **not** match the displayed GPU skin buffer, the editor refuses to paint instead of saving arbitrary vertex indices.

## Limitations / acceptance

- The weight brush in this patch is **regular 2D Rigging Studio pointer input**. Immersive WebXR bone/weight tools are not yet complete; the QA environment scope remains both.
- This is not a promise that the severe Sorting Hat mesh distortion has been isolated. The actual existing rig weight distribution, inverse bind values and complex authored topology require physical inspection and their own validation.
- VR Browser 2D: test selected-bone paints and Undo/Redo on a generic cylinder, show accurate influence colors, save/reload the same project, verify project history, and confirm bone selection/camera orbit work when paint is off.
- Immersive VR: **pending** direct joint manipulators and weight brush interaction, alongside camera/object transform separation, menus, controller labels and project browser from issue #472.
- Never treat CI math, Three.js CPU skin or static build tests as physical Quest acceptance.

**Files:** `runtime/model_rig_skin_math_v11_513.js`, `runtime/model_rig_weight_studio_v11_513.js`, `patches/v11_513_rig_skin_weights.py`, `tests/model_rig_skin_weight_v11_513.cjs`, `tests/model_rig_generic_bind_v11_513.mjs`.
