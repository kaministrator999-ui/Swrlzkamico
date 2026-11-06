# v11.300 — Hooded Vanguard mesh and UV textures as a single operation

## Evidence from owner device
The Android v11.299 front/back views showed an enlarged sci-fi-style hood, photographs or image fragments on a rectangular breastplate, grayscale marbling on the back of the body, and unrealistic spear-like hanging coattails. The previous patch corrected tile offsets but was fundamentally still decorating unsatisfactory geometry.

## Change, not just a texture remap
The new v11.300 fresh Starter Model rebuilds **the real geometry and its UV unwrap in one pass**:
- One continuous rounded head with built-in shallow nose relief, restrained jaw and front-only portrait mapping.
- Close-fitting hair crown plus separately editable front fringe and tapered lateral hair locks.
- Full arched hood opening with upper cloth canopy, rear and side mantle, fabric brow binding and downturned face edges.
- Sculpted neck cowl, V-shaped draped chest mantle, tapered chestplate following torso width, formed shoulder plates.
- Two-sided hanging teal fabric panels with breadth and fabric movement rather than spear/leaf silhouettes.
- Retain five-finger hands, shaped boots, belt, underlying anatomy and the total **17 native editable mesh part IDs**, preventing saved-model mutation.

## Albedo and material mapping
The previously SHA-verified generated owner-image JPEG is reused as the paint source. New 384px per-material canvases sample **only painted source regions** and fill remaining surface with aligned material color. The atlas UV coordinates are authored against the new local mesh geometry; they are not reshaped concept pictures pasted on anatomy. The eyes and lips in the face source only appear across frontal head UV; the back is plain skin. The torso back remains uniform fabric rather than a mirrored photograph. White hood and scarf receive appropriate fabric artwork; breastplate and shoulder plate receive distinct metal artwork; teal cloth receives teal art; leather, hands and boots receive their respective painted surfaces. Metallic, cloth and skin roughness are conservative to keep the illustration legible.

## Scope and acceptance
Historical patches (v11.291–v11.299), save data, unrelated Starter Models, §C integration, VR/Sheep Tag and release history remain intact. There is no bird/weapon/complete animation rig. The source image available in the packed release is a compressed sample, not a full-resolution professionally painted topology-aligned atlas. Check from the owner's **front, 3/4, side and back angles** before calling the result visually complete.

## Tests
Narrow Node test: current 17-part native starter, geometry/UV consistency on all meshes, new topology on changed surfaces, real source pixels sampled for 11 material families, strict no out-of-range indices/UV values, no changes to unrelated material dispatch. JS parse + exact engine source/asset seal through build script. Owner visual acceptance remains independent.
