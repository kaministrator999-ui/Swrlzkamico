# Astra · Comet Courier

An independent native Model Atelier project: a proud four-legged celestial fox with navy and ivory fur, tall swept ears, amber eyes, a curled comet tail, a teal travelling mantle, stitched leather satchel, rolled parchment, compass badge and blue lantern. The asymmetric tail supplies the silhouette; the small lantern and brass hardware repeat the celestial palette.

The model is authored through the existing native mesh inspector, organic splines, density, HD surfaces and saved material controls. Six non-destructive assemblies keep face, body, forelegs, hind legs, tail and travel gear independently editable. A separate **New Model Project** card provides a clean one-mesh workspace. The original festival model and all previous source/runtime and 43 assets remain unchanged.

Two original **4096 × 4096** textures are authored at that resolution, without enlarging a lower-resolution picture: base color and a tangent-space normal atlas. Eight atlas regions cover directional navy/ivory fur, woven teal fabric with embroidery, worn stitched leather, engraved brass, comet markings, lapis and radial amber fibers. The deterministic texture authoring source is included. Shared image sources and padded per-region UV transforms avoid one 4K image allocation per mesh. Texture bindings and normal strength are validated, saved and undoable.

**Export textured GLB** bakes actual rendered geometry, normals, vertex colors and atlas UVs, and embeds both full-resolution texture images with named nodes and material properties. Native JSON and the legacy geometry-only OBJ remain available. The GLB exporter uses core glTF 2.0 PNG/JPEG textures, without requiring an external extension or image URLs.

Native authoring: `authoring/comet_courier_authoring_v11_77.mjs`, design controls in `comet_courier_design_v11_77.mjs`, and native assembly/save/export finish in `comet_courier_finish_v11_77.mjs`. The canonical project file is the actual saved/reimported editor result. Browser checks cover project separation, native Undo/Redo, 4K image loading, invalid texture binding rejection, assembly persistence, mobile access and exported GLB geometry/images.

Release: §E v11.77 / `V11_77_COMET_COURIER_MODEL_PROJECT`, 109 ordered patches / 46 assets. Publication follows the current §§§ targeted-test/direct-main/separate-final-deploy workflow in `RELEASE_PROCESS.md`; no unrelated legacy game CI is launched.

Final native build: **106 meshes, six assemblies, 274,980 measured triangles**. Both original 4096px maps are embedded in the validated **16,965,768-byte GLB**. Sealed HTML: **3,149,026 bytes**, SHA-256 `fc67c2bd03d6c90933c40b117e810675cbbacc29b05b2cfb96f6fe57f2088323`. The original canonical scene and 248 prior patch/runtime source files plus all 43 assets retain their exact bytes. The project opens in Studio view; **Edit model** restores the complete editor.


### v11.77 publishing guard correction

The first v11.77 deployment packaged and uploaded the correct sealed model build, then its hosted verification stopped at an inherited 108-patch expectation. The publishing guard now requires the actual **109** ordered patches. This starts a new delivery cycle with the same v11.77 HTML, scene, 4K image assets and integrity digest; no model or runtime artifact changes. A new final dedicated request identifies the corrected workflow source commit and must reach terminal success before completion.
