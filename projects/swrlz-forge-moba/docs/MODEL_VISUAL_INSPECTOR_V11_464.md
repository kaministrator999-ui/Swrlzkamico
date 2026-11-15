# §E v11.464 — Model Studio depth, X-Ray, selection and inspector polish

## Evidence and constraints
Owner's Moto screenshots from v11.462 show a valid hollow inset and clean topology wires but weak cavity depth, Material shading similar to Solid on a plain cube, cloudy X-Ray, a cramped right inspector, and limited selection contrast. Owner subsequently confirmed camera orbit and draggable dock splitters work; v11.463 restores the native viewport transform/Undo toolbar. The implementation must retain those verified mechanisms, original part IDs, UVs, undo snapshots, face preview transactions, VR hand/controller interactions, and saved project descriptors.

A read-only v11.463 build audit established that native X-Ray clones the material at opacity 0.27 with DoubleSide and depthWrite=false. This lets interior overlapping surfaces accumulate. It also confirmed the native component overlays, studio material code and inspector controls.

## Scope of v11.464
1. Solid/Flat/Clay: reduce artificial emissive wash in their **disposable view-only material** and add soft, neutral key/fill directions to the Model Atelier render scene, not the saved model. Both studio helper lights turn off when the VR bridge borrows the scene.
2. Material: retain authored maps, metallic/roughness parameters and v11.461 crisp hard-surface normals; benefit from the same studio illumination without fabricating texture data or baking any shading.
3. X-Ray: replace cloudy DoubleSide translucent faces with an opaque depth-only visibility helper + a light front-face overlay, low-opacity hidden dihedral edges and strong depth-tested visible dihedral edges. The helper borrows mesh geometry but never owns or disposes it; all display-only materials/edge buffers are safely removed across mode changes.
4. Inspector on touch/narrow layouts: add an explicit **Expand / Dock** action to the existing inspector header. When expanded, the existing inspector is absolutely overlaid within the model body and its occupied dock width is temporarily released. No cloned controls, native splitter changes or width storage rewrites. Escape or Dock restores previous layout.
5. Selection: native selected-mesh box becomes mint and component overlays use high-contrast distinct vertex (mint), edge (sky) and face (amber) colors. Native toolbar refresh also recolors the selected mesh's existing depth-tested edges; active tool indicators use legible outlines.

The original v11.463 always-accessible Undo/Redo toolbar remains untouched.

## Release gate
A fail-closed preparer rebuilds exactly 441 ordered patches, calculates the genuine final bytes and SHA-256, then runs the v11.464 visual regression plus prior v11.463 transform, v11.462 wireframe, v11.461 orbit and v11.460 native view tests. Additional checks validate inline JS syntax, unchanged complete modeler route, 77 asset hashes and release marker. Only then may it seal a manifest, create a separate DEPLOY_REQUEST and trigger the existing Hugging Face Space upload.

**Physical acceptance remains separate**: confirm the original hollow cube under all seven View modes, inspect X-Ray front/hidden edges at multiple camera angles, verify Material preserves maps on textured meshes, use Expand/Dock and both native drags on Moto, and validate that Undo/Redo still remains accessible. Source tests cannot certify browser pixels or Quest comfort.
