# §E v11.545 — real humanoid UV anatomy inspector

## Observed mapping and packing
The v11.544 humanoid uses 8,792 UV vertices, 13,932 faces and 84 non-overlapping xatlas charts. Measuring the actual UV arrays shows the sum of the chart bounding-box areas is approximately 1.287 times the atlas. Organic island silhouettes interleave even when their rectangles overlap. Rectangular packing at equivalent resolution would not fit: naïve repacking sacrifices texel density, and rearranging UVs would misregister the corrected painted texture unless it is properly rebaked.

## Implemented
An opt-in Humanoid UV anatomy view in the selected mannequin's native UV Editor. It colors actual UV triangles using 3D positions and surface direction, not the apparent shapes of islands.

- Head; front, back and sides of torso; left/right arms; left/right legs
- Region selector dims the remaining triangles to make anatomy on the atlas legible
- Read-only 640px preview and 2048px PNG anatomy guide export, explicitly NOT an imported material texture
- No changes to UV arrays, mesh geometry, image, rig, accounts, Undo, old projects or immersive VR
- Enabled only for the selected humanoid-body-unified under robotic-humanoid-mannequin

This is an improvement to chart presentation and paint targeting, not an automatic UV repack. The existing correct 84-chart atlas is still the model's source of truth. Existing current UV Guide, painted preview and stretching heatmap remain available.

## Verification
The node test tests/humanoid_uv_anatomy_v11_545.cjs executes the real v11.544 scene, classifies all 13,932 triangles, requires all 8 anatomy zones present, verifies that the original mesh + texture JSON is unchanged, and rejects an unrelated mesh ID.

## Device acceptance
Select humanoid in Model Studio, open UV Editor, expand Humanoid UV anatomy and filter Head, Torso front/back, left/right arms/legs. Export the 2048 reference. Compare against front, back and side 3D appearance. No Apply, mesh save or re-unwrap required.

Future UV reorganization should use a shape-aware packing algorithm, conservative texel-density threshold, texture rebake and 3D reprojection validation. Do not replace the shipped mapping with a front/back projection.
