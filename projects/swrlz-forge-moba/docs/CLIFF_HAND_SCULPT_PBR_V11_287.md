# §E v11.287 — Plain Hand Base → Cliff Hand sculpt with PBR material atlas

Owner reference: the **Cliff Hand** turnaround, growth and pose sheet plus the supplied `cliff_hand_separate_material_assets.zip`.

## Scope and native construction

The existing `plain-hand-base` starter card/route now opens `Plain Hand Base · Cliff Hand Sculpt`. It keeps the 17-joint native hand rig and open/fist/open keyframe timeline inherited from the Plain Hand anatomy while replacing its exposed smooth clay mesh with genuinely modeled, separately editable rock. The native solid stone hand builder supplies front/back/side palm, wrist, thumb and three articulated sections for each of four fingers. Additional individually editable layers give the palm/back **32 small cliff strata**; existing weathering rounds harsh corners. Dark matte fissures replace emissive amber accents.

The independent **Rocky Anime Hand** and **Arcane Gloves** remain unchanged. Existing saved user projects are not migrated or rewritten. Selecting the starter creates a fresh authored scene, as with other starters.

## Owner-supplied texture maps

Bundled asset: `assets/cliff-hand/cliff_pbr_atlas_128.jpg`, a **4 × 2 tile atlas**, 128 × 128 px per map, 512 × 256 px total. It was downsampled from files in the supplied reference ZIP for Quest/mobile. No runtime dependency on a remote image service or the original ZIP.

| Tile index | Map / source | Role |
| --- | --- | --- |
| 0 | `10_cliff_rock_with_moss_preview.png` | Moss-composited rock albedo, used only on selected plates |
| 1 | `05_cliff_rock_normal_OpenGL.png` | Tangent-space normal detail |
| 2 | `06_cliff_rock_roughness.png` | Roughness, read from green channel |
| 3 | `07_cliff_rock_AO.png` | Ambient occlusion; skinned mesh gets `uv2` |
| 4 | `01_cliff_rock_albedo.png` | Plain sandstone base color |
| 5 | `02_packed_dirt_albedo.png` | Dirt/soil rock variant |
| 6 | `04_cliff_rock_height.png` | Small bump detail, **not** fake geometry displacement |
| 7 | `09_crack_mask.png` | Authored source retained in atlas for future masking; crevice *geometry* is already dark |

The runtime uses `MeshStandardMaterial`, metalness 0, roughness 0.96 multiplied by the roughness map, AO intensity 0.77, restrained OpenGL normal strength 0.30 and height-bump scale 0.009. The moss composite is applied selectively instead of coating the entire hand green. Native per-part UVs map each stone into one tile, and the atlas is packed into the deployed static Space.

## Validation / acceptance

The source release appends `patches/v11_287_cliff_sculpt_pbr.py`. Validation includes assembled HTML and original inline-JS syntax, the atlas's exact presence in `SOURCE.json`, and model/rig/material source anchors. Live texture appearance and performance are subject to the owner's phone and Quest tests.

Suggested owner check: **Projects → Starter Projects → Starter Models → Plain Hand Base · Cliff Hand**. Rotate to palm, back and both sides; confirm sandstone on all faces, dark crevices, selective green moss, and no smooth glove exposed. Test open/fist posing, select a rock tile in the Parts panel, and test save/reload. The turnaround sheet's 3–15 m growth sequence is **reference-only**, not a newly implemented spell-growth system.
