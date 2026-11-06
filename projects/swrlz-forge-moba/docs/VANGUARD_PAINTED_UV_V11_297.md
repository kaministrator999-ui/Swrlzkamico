# §E v11.297 · Hooded Vanguard UV-painting & sculpt revision

## Request and reference
The owner requested **actual remastering inside the native §E Model Atelier**, following prior hand-painted Warcraft III texture discussion and a new generated artwork presentation sheet. The image is a **visual texture guide, not an actual UV-unwrapped bake** for the current geometry: pasting it onto the pre-existing UV layout would misplace patterns and labels.

## Changes
- Build 11 intentionally authored canvas albedo tiles at 384px each using color gradients and hand-painted-style anatomical/armor/clothing shapes, with distinct painted eyes and lips, hair strands, gold-edged pale hood, white fabric folds and jewelry, engraved chest/shoulder armor, teal cloth embroidery, fitted under-layer seams, dark leather belt, stitched gloves and boots.
- Each painted base-color tile is addressed by the existing native topology mesh's explicit UVs; matching conservative tangent normal and per-material roughness maps are derived and cached. Surface ornament remains **texture art**, not collections of trim meshes.
- The native starter remains exactly **17 editable parts**, including ten finger/thumb digit shapes, with rounded facial geometry, a head-covering hood crown and side/back drape, folded scarf, softer hair locks, and narrower flowing teal cloth tails.
- The original v11.291 and v11.296 generator patches remain untouched in append-only source history. Saved projects, Chat geometry tools and other starter IDs do not change.
- No claim of directly using the UV presentation PNG as a bake; it has no matching mesh UV unwrap. This update instead follows its layout and color/detail design, mapped to actual native part UVs.

## Verification
- Reconstruct and hash exact 328-patch HTML; parse assembled JavaScript.
- Native geometry regression checks 17 part IDs/UV cardinality, non-degenerate rounded head, full hood crown, independent five-digit hands and coat geometry.
- Hosted Android-size browser test should confirm actual material atlas creation and active Model Atelier; owner visual acceptance still pending.
- Character remains static with no skeleton/weapon/bird.

## Files
- runtime/hooded_vanguard_painted_v11_297.js
- patches/v11_297_painted_uv_vanguard.py
- scripts/verify_v11_297_release.py
- tests/hooded_vanguard_painted_v11_297.cjs
