# §E v11.546 — Anatomical UV Robot + 4096 px Export

## Owner goal
Replace the factory UV/material direction with a humanoid *robotic mannequin*: human-like proportions without human facial features. Preserve the connected geometry and five-digit hands, make UV chart regions anatomically recognizable, paint a new robot skin against the new UV coordinates, and provide full 4096×4096 PNG exports.

## Implementation
- Authoring-only Python/xatlas generation starts from the native v11.540 3D source, welds UV-only seam duplicates, partitions faces by **actual 3D anatomy**, then generates charts in grouped atlas regions. Preserve the original 13,932 geometry triangles exactly.
- Attempt seven groups (head, chest, back, left/right arms, left/right legs). Respect the native 9000 UV-vertex budget. If necessary, use six groups (head, combined torso, left/right arms, left/right legs). This is an actual replacement UV mapping, not merely an overlay. The region inspector still distinguishes chest and back by surface direction.
- All UV transformations are isotropic, never stretched simply to fill a label rectangle. Check UV area, texel density, noncollapsed triangles, and raster collisions.
- Bake a **new** pearl-white ceramic / graphite / cyan robotic skin from every mapped 3D surface position and normal: sealed sensor visor instead of a human face, mechanical torso, core, spine, limbs and joints. Never simply reuse the previous texture on different UVs.
- A native 1024×1024 embedded painted PNG is maintained under the current project schema's ~360k encoded-character limit. That storage restriction does NOT restrict UV reference export size.
- Publish true 4096×4096 wireframe and anatomy reference PNGs built from the model's new UVs (not upscaled old heatmaps), and front/back/side 3D texture-placement QA.
- UV Editor's Humanoid UV anatomy inspector gets selectable **4096 px (default) or 2048 px** export sizes. Both color-coded anatomy reference and current actual UV wireframe use the chosen size, downloaded via Blob. Existing UV stretch/overlay diagnostic already supports 4096.
- Only the factory new starter is changed. Historical versions and any user-saved account project copies remain intact. No automatic saved-project migration, geometry changes, or inferred rigging.

## Quality gates
Independent geometric face-multiset equality; 9000 UV vertex / 13932 face limits; 0–1 UV and density bounds; 3D-baked paint registration and raster overlap; native embedded image size; actual 4096×4096 PNG dimensions; source-manifest/packed asset receipts; starter and login/VR regression tests. The creator's phone and VR tests remain separate device acceptance.

## Owner verification
Open Starter Models → Futuristic Humanoid · Anatomical Robot. Inspect front/back/sides, then UV Editor → Humanoid UV anatomy → 4096 px. Export anatomy and current UV wireframe and inspect exact PNG dimensions. These guides are reference layers, not painted robot textures. The original saved mannequin should remain unmodified.
