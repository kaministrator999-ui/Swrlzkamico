# v11.299 Hooded Vanguard: owner-confirmed texture map correction

## Observed on owner Android
The new actual-pixel v11.298 atlas appeared on the model but incorrectly: an entire illustrated face and parts of other graphics were wrapped around body surfaces; the back displayed broad photographic fragments and the coat showed unnaturally streaked white decorations. An image loading success was not a semantic UV match.

## Root cause
v11.298 packs eleven whole illustrated material presentation tiles from the generated concept board and maps each onto a mesh's full local 0–1 UVs. The source illustration was neither a skinned model UV unwrap nor seamless material textures. Full-tile projection copied the white sheet background and visual parts outside material boundaries.

## Focused repair
- Use the previously verified embedded v11.298 generated-image JPEG, preserving image identity/SHA and original 17-part editable geometry.
- For each material family, crop a *painted surface region* from its corresponding 128px illustration tile, not the whole illustrated garment cutout.
- Use source-image pixels to create separate 256px diffuse CanvasTextures; mirror material patches to reduce repeated seams. Replace pale paper holes on dark fabric and armor with a representative base material tint.
- Restore the exact original local UVs by inverting the v11.298 tiled 4×3 atlas transform. Reject nonfinite/out-of-range UVs instead of accepting mismatched islands.
- Apply the painted photographic face region only to frontal longitude, feather toward plain skin at edges and keep the rear surface plain skin.
- Preserve unrelated Starter Models, saved model projects, native Chat tools, Sheep Tag, VR, and previous patches; no new arbitrary geometry, weapon, bird, or full rig.

## Verification and limitations
A narrow Node VM test exercises restoration of all 17 parts and actual image-source pixel sampling, plus no change to non-Vanguard material dispatch. The sealed artifact must pass full JS syntax and SHA verification. Final on-device appearance acceptance is separate. This improves semantic texture alignment, but a 128px-per-original-tile source JPEG cannot become an artist-finished high-resolution UV bake by coordinate arithmetic alone.
