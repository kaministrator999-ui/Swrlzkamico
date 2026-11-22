# §E v11.544 · Geometry-anchored mannequin material + safe paint recovery

## Actual user evidence and failure

Owner loaded the supplied hand-painted sci-fi image into the native mannequin. In a three-quarter side view, the humanoid *face landed across the chest* and decorative *hands landed on the torso/sides*. The mannequin's native v11.542 atlas was already valid (84 non-overlapping xatlas charts), but the assistant had painted a **fictitious six-anatomical-island 2D diagram**. A rectangular-looking patch in the atlas does not prove it belongs to the head, back, palms, or shins.

The correct direction is 3D surface → real UV pixels. Painting a third guessed atlas would recreate the same mistake.

## Source-first correction

\`authoring/build_humanoid_semantic_material_v11_544.py\` loads the immutable authoritative native v11.542 model. The authoring baker:

1. Reads exactly 8,792 UV vertices, 13,932 triangles and all actual 3D local positions. It computes smooth 3D normals across UV seams using the welded geometry.
2. For each *actual UV triangle* in the unchanged 84-chart atlas, rasterizes pixels, computes each pixel's **barycentric 3D position and surface normal**, and evaluates deterministic white-ceramic/graphite/teal robot paint in 3D coordinates.
3. Applies anatomy filters in world/model coordinates: head over Y=4.08, arms extended along X near Y=3.65, front face/chest toward +Z, back/spine toward -Z, and legs below Y=2.35. Painted face/eyes cannot appear in torso islands because of a semantic 3D head mask. No explicit illustrated hands float onto torso geometry.
4. Fills chart gutters with 5px edge bleed, keeps the verified 84-chart UVs, avoids cyan guide lines, and emits a native-compatible PNG, compacting only if the 360k-character embedded texture limit requires it.
5. Produces a **color-coded body-part diagnostic atlas** \`docs/qa/futuristic-humanoid-v11-544-region-diagnostic.png\` and **front, back and left-side 3D reprojections** \`docs/qa/futuristic-humanoid-v11-544-front-back-side.png\`. These are inspectable visual receipts from actual geometry, not AI paintings.
6. Saves the original PNG separately to \`assets/models/futuristic-humanoid-v11-544-surface-anchored.png\`, and embeds the same PNG in one native scene at \`scenes/model-atelier-futuristic-humanoid-v11-544.swyrl.json\`. It does **not** rewrite the historical starter.

## Repair without resetting owner's current project

\`runtime/humanoid_semantic_repair_v11_544.js\` adds **Restore mapped robot texture** beside the current UV preview. It appears enabled only for the exact original native UV-compatible one-piece mannequin (8,792 UV vertices, 13,932 triangles, a dozen verified UV landmarks, same project identity). Clicking it:

- Explains that only the painted material will change; the user must confirm.
- Fetches the verified v11.544 native source and checks the embedded PNG before updating.
- Uses native \`checkpoint()\`, \`checkPart()\`, \`signalEdited()\` and \`select()\` in the original Model Atelier closure.
- Resets old UV image offsets/repeat that could misalign the new paint, leaves all UVs/geometric vertex positions/indices untouched, and makes the paint change **Undoable**. It does **not** automatically save to an account.
- Refuses mismatched meshes or altered UV layouts instead of risking applying the wrong texture.

The stable Starter Models ID \`robotic-humanoid-mannequin\` continues to work and now opens the newly baked material. Old saved projects stay old unless the owner explicitly uses the paint repair.

## Verification and acceptance

\`scripts/check_humanoid_semantic_paint_v11_544.py\` tests geometry and UV **array equality** with the old scene, validates exact shipped PNG bytes, size and actual region/face/torso landmarks and the three projection previews. \`tests/humanoid_semantic_repair_v11_544.cjs\` verifies cancel/confirm, original texture retention on failure, one Undo checkpoint, no automatic file downloads or account save, and refusing edited UVs.

This procedural material has *correct 3D anatomical registration*. It is not yet a hand-authored hero-grade armor PBR set (nor does it redesign the geometry, rig or UV packing). Final mobile/Quest screenshot acceptance remains with owner. To inspect on device: open latest Starter Models → Futuristic Humanoid · Surface-Mapped Robot; or on the currently open mannequin, go **UV Editor → Restore mapped robot texture**, confirm, inspect front/back/sides, and Save Project if satisfactory. Undo restores the prior paint before saving.
