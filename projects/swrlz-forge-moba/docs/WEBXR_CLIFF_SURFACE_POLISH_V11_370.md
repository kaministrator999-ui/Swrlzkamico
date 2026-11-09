# §E v11.370 — material-only refinement of the WebXR Cliff Hand

## Scope

The owner approved the v11.369 WebXR right-hand geometry and asked to refine only the stone surface: overly uniform dark tile boundaries, uneven moss on front/back, flat-looking stone, and an abrupt cut wrist. Do **not** regenerate geometry or alter UV layout, nor change the improved 89-piece Rocky Hand.

## Material implementation

- New isolated runtime: `runtime/webxr_cliff_material_polish_v11_370.js`.
- Intercept only `part.cliffPBR.variant === 'webxr-cliff'` in `se292WristMossKnuckleMaterial`. All other materials use their unchanged routes.
- Keep the original `se290CliffMaterial` loaded and visibly active until one asynchronous texture bake succeeds. If the atlas fails, keep the original maps.
- Read from the existing **unchanged** `assets/cliff-hand/cliff_pbr_atlas_384.jpg`: clean stone albedo tile 4, mossed stone tile 0 for pigment, normal tile 1, roughness tile 2, AO tile 3, mineral fracture tile 7.
- Rasterize the approved 1,360-vertex, 2,314-triangle hand once into its original 384×384 UV islands, interpolating actual transformed world-local palm/thumb/finger/wrist coordinates. No per-frame shader or any new geometry is required.
- Within covered UV pixels, retain base sandstone tones and rock grain, soften/interrupt some repetitive dark closed tile outlines via the owner's original fracture signal, concentrate patchy moss anatomically around wrist/thenar/dorsal creases, and brighten broad palm/finger pads. Low-wrist color wear subtly softens the straight cuff edge visually; geometry remains the same.
- Preserve normal/roughness/AO spatial alignment. Normalize PBR relief to 0.85, AO 1.07, roughness 0.91, add small in-place roughness and AO deltas at faults/cuffs.
- Reuse the one-time baked maps for future Cliff material instances. Only the original WebXR hand clone receives them. Do not affect saved projects unless the saved part already declares the `webxr-cliff` material variant.

## Checks

- Inspect the real WebXR right-hand JSON and confirm 1,360 vertices, 2,314 triangles, unchanged indices and source UV coordinates.
- Node tests run UV triangle projection and a synthetic tile image of all six original atlas slots to validate normal/roughness/AO alignment, precise anatomy-controlled moss bias, bounded seams and correct fallback/caching.
- Full 377-patch build must generate valid inline JS and a SHA-matched static release. Owner evaluates the actual look on the Moto or Quest 2, including palm, dorsal side and fingertip close-ups.
