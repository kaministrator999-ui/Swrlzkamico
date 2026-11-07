# §E v11.305 — Hooded Vanguard complete geometry and native UV reconstruction

## Why this change exists

The owner's Android model inspection found meaningful progress in the chest and shoulders, but the full character still had stiff hood/scarf geometry, poor cloth drape and wrist/finger directions that did not follow the arms. Prior character workflows sometimes reused 2D projected UVs over anatomy, or mapped reference art before the final sculpt was coherent. The owner explicitly requested a **whole-model mesh and UV update together**, not another checklist or texture-only patch.

## Source changes

The new [runtime/hooded_vanguard_full_mesh_uv_v11_305.js](../runtime/hooded_vanguard_full_mesh_uv_v11_305.js) overrides **only newly constructed native Hooded Vanguard starter scenes**, retaining the old 17 editable part IDs and all historical code. Each replacement mesh is constructed from a parameterized surface and receives its UVs in the same step.

- **Body:** true radial longitudinal UV seams for the torso front/sides/back, separate swept sleeves and forearms, and anatomically tapered legs. The former planar whole-body mapping cannot paint the back as though it were another front.
- **Face:** retain the v11.303 head topology/768px aligned painted portrait, with two shaped ear cartilage patches in lateral UV regions. Retain hair geometry and contour where already improved.
- **Hood:** fitted open-top canopy, rounded forward face aperture, draping back mantle and face frame, all modeled as contiguous editable cloth surface patches in the same part.
- **Scarf:** gathered collar with real folds and two diagonal intersecting strips over the chest, rather than a rectangular apron.
- **Armor:** retain the earlier approved breastplate and shoulder surfaces and original mapped UVs, but add real back/metal thickness and closed, UV-trimmed exposed edges. Do not redesign their successful front silhouette.
- **Teal cloth:** two distinct draped panels, each with visible front and back, and UVs running along fabric flow. No leaf-shaped thin ribbons.
- **Belt:** belt radius matching torso waist, with a real small buckle surface whose UVs align with the painted leather/buckle artwork.
- **Hands:** replace the old vertically oriented five-finger shapes rotated afterward. Palms, four individually tapered fingers, thumb, and cuff are built **in forearm direction** from the elbow–wrist vector, with local radial UVs. No painful wrist hinge.
- **Boots:** swept ankle shafts, rounded toe volume and cuff, with correct orientation of leather UV patterns.

Keep the **11 existing art-directed albedo texture families, PBR normals and roughness maps**, without bringing back literal image magazine cutouts. True geometric silhouettes and UV flow carry visual information; source textures provide surface detail. No new model part dependencies or 3D character rig.

## Verification

The narrow [tests/hooded_vanguard_full_mesh_uv_v11_305.cjs](../tests/hooded_vanguard_full_mesh_uv_v11_305.cjs) checks all 17 part IDs, geometry/UV parity, finite vertex/UV/index values, torso front/back seam correspondence, ear volume, hood/scarf/coat/boots geometry, limb-aligned fingertips and preserved approved metal panel front geometry/UVs. Release build must retain prior v11.304 loaded-document integration and pass source checksum/asset verification.

No claim of artist-final likeness, fully baked unique UV islands, skeletal animation or real-device acceptance is implied by those code tests. Owner device front, ¾, side and rear renders are the art-quality acceptance gate.
