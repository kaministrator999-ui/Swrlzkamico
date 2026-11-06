# §E v11.288 · Smooth Cliff Hand (owner screenshot correction)

## What changed

**Previously (v11.287):** The Plain Hand Base starter was visually assembled from ~121 separate closed 3D stones, small palm plates, finger rocks, crease tubes, and other geometry. This looked like boulders stacked into a hand and failed the reference.

**Now (v11.288):** The Plain Hand Base starter creates **one connected native hand topology mesh** from the original anatomical hand surface; zero separate rock, crack, fingernail, or plate objects. The mesh determines smooth silhouette, finger proportions, knuckles, thumb, palm, wrist, and natural bending. The material determines *all* visible cliff strata, polygonal rock edges, fracture/crevice shadows, surface roughness and sparse green moss. The user can select and sculpt the single native mesh.

## Exact implementation

- Source: `runtime/smooth_cliff_hand_v11_288.js` appended through `patches/v11_288_smooth_cliff_pbr.py`. Existing `se284PlainHandScene` template routing calls the newly implemented `se288SmoothCliffHandScene` rather than executing the historical (now unreachable) v11.287 stone assembly.
- Shape: the original organic/watertight `se212HandScene` finger/thumb/palm/wrist shell. `model.parts=[stone]` with native `topologyMesh`; no new geometric rock chunks. The existing 17-bone `model.rigging` is kept.
- UV: one projected continuous X/Y UV layout across the whole hand; slight Z-dependent coordinate correction on the curved sides. The UV coordinates are stored in native editable topology data, so texture and the rest pose persist in the model project.
- Material: `MeshStandardMaterial`, metalness 0, roughness 0.96 multiplied by a roughness map, matching diffuse/albedo, tangent-space OpenGL normal map (strength 0.68) and ambient occlusion (strength 0.90). No actual rock displacement or geometry cracks.
- New atlas: `assets/cliff-hand/cliff_pbr_atlas_384.jpg`, 4×2 tiles of 384×384 each (1536×768). Maps are downsampled from the user's uploaded `cliff_hand_separate_material_assets.zip`: (0) sandstone + selectively blended moss, (1) OpenGL normal, (2) roughness, (3) AO, (4) clean sandstone, (5) packed dirt, (6) height, (7) crack mask. The atlas is shipped as a local static asset; no remote dependency. Tiles 4–7 are retained for future material-editor variations; the active smooth hand material uses 0–3.
- The old 128px atlas and v11.287 chunky-rock source remain for historical reproducibility, but are **not used** by this starter path. The independent Rocky Anime Hand continues using its own solid-rock geometry.

## Owner acceptance

Open **Projects → Starter Projects → Starter Models → Plain Hand Base · Smooth Cliff Hand** after reload. Rotate all around to verify a smooth continuous silhouette, no stacked boulders or 3D crack tubes, clear dark stone separations from the material, subdued moss, and full connected fingers/thumb. Test pose/open-fist animation and Save Project. Material tiling/lighting quality and real headset frame cadence require owner inspection; a passed static source build is not equivalent to a visual test.

The reference's growth sequence, character scaling and impact gameplay are not introduced by this material-only correction.
