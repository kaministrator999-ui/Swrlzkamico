# v11.302 — Character UV/normal/roughness pairing

## Source-of-truth and scope

The user accepted continued iteration on the Hooded Vanguard model after v11.301 deployed. A visual hosted browser smoke verified v11.301 loads its 17 editable native meshes and newly painted color maps, including corrected hands, while the editor's overlay obscured the face in the first desktop capture. Do not claim final artistic parity.

This patch continues the **same character texture work** by adding a deliberate low-cost PBR detail layer to those native UVs. It does not replace the skin artwork, undo the neutral A-pose wrists, add new mesh fragments, or affect saved projects.

## Implementation
- **Albedo:** keep v11.301's 384px self-authored UV maps intact; do not resample the illustrated concept sheet, and do not introduce magazine cutouts.
- **Normal:** draw a distinct 256px height pattern for each of 11 material categories; derive correctly encoded tangent-space RGB normal maps with conservative amplitude. Align hood and coat border relief to the edges of those garments' UV layouts, scarves to folds, metal armor to inset engraving, leather to seam lines, and hair to strand direction. Keep skin nearly smooth.
- **Roughness:** produce an independent 256px linear, grayscale roughness map per family with subtle procedural micrograin; metallic armor remains smoother and cloth/skin rougher. Use the proper green channel with material roughness=1 and keep the existing material-type metalness.
- **Performance:** share one map pair per family, 22 cached textures total, 256px each, and do not add runtime full-res baking or geometry. Keep existing albedo atlas cache and all 17 editable mesh identities.
- **Regressions:** focused Node test checks mapping on all families, caching, normal strength, roughness settings, unchanged albedo bindings and no new geometry. The sealed full engine JS/source hash/asset metadata verifier runs separately.
- **Acceptance:** owner Android/Quest front, side, and rear material response and rendering performance remain the final test, not assumed from programmatic source correctness.

Reference design remains the original refined hooded knight concept. Static model only; no weapon, bird or full-body rig.
