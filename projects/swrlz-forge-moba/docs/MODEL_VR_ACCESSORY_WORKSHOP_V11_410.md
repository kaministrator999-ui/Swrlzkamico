# Model VR v11.410 — accessory workshop

This checkpoint adds a direct VR workflow for making a small hip bag inspired by the Crystal Mage reference. The workshop builds ordinary native meshes, then hands them to the same selection, Grab and mesh-editing tools used for existing models.

## Make and fit a pouch

1. Open a model in Model Studio, enter VR, and choose **Create → Accessories → Hip pouch**. This starts a preview; it does not add parts or an Undo checkpoint yet.
2. Use **Body** for width, height, depth, roundness and wall thickness. The starting body is about **14 cm high**, using an immersive presentation scale of approximately 0.1556 metres per recipe unit. The menu displays physical centimetres, including preview resizing.
3. Use **Details** for flap coverage, strap/loop length, stitching, a leaf/star/no emblem, and coordinated Walnut, Plum or Fawn colors. Controls rebuild the preview rather than the native document.
4. Use **Fit** to choose free placement or surface fitting. Point at the hip for surface fit; the bag's back mounting plane follows the hit surface normal while retaining an upright orientation. Align clears additional turning, and Closer/Gap adjusts stand-off spacing. Surface fitting requires a current valid model contact.
5. Move the pointer away from the menu to position the bag. The preview holds its pose while you operate menu controls, keeping it visible in the modeling area. The right stick turns it horizontally and adjusts its overall size vertically.
6. Release the menu click, then press the active profile's primary selection Trigger again to place the bag. A menu click cannot also place it behind the panel. The default eight components become one selected native group, and Grab is active so Grip can move and turn the group immediately.

B cancels a pending preview. The first Y/Undo or Redo action also cancels the pending preview before touching existing history; a subsequent Undo acts on committed edits. Undo after placement removes the entire bag in one step; Redo restores it. Return the stick to neutral before ordinary camera orbit resumes.

The essential workflow uses the available controller buttons and existing profile dispatch; it does not depend on the headset's reserved system Menu button. Both controllers retain menu input priority. Guide, palette visibility and display controls remain available during the preview.

## Geometry and editing boundaries

The recipe creates a thick, rounded open-top shell with a floor, interior and rim; a curved flap; belt attachment loops; a closure strap; a metal clasp; and optional piping, stitches and a leaf/star motif. Component transforms are baked into their topology. Native material identifiers remain the existing matte, silk and metal presets, with coordinated colors rather than an additional material system. Stitching and ornament meshes are combined into a small bounded component set; the default bag has eight parts.

Preview meshes belong to the immersive presentation scene and have separately owned geometry/material resources. Parameter changes replace and dispose these resources without adding native parts. Surface contact work is bounded, and pointing at a menu blocks placement or model selection through it.

Placement validates the source document identity, revision, original part references and full document fingerprint before creating fresh native IDs. All components are checked before one native checkpoint and batch insertion. A document/profile change, tracking loss, editor close or VR exit discards the uncommitted preview; invalid/stale placement cannot partially insert a bag.

After confirmation the result is ordinary editable `topologyMesh` components in a native group. Move, rotate, scale, Grab and mesh/surface tools remain the editing path. The recipe parameters are temporary preview state: reopening Accessories starts another bag, rather than providing persistent parametric re-editing of a previously placed bag. Native project saves retain the resulting meshes through the existing schema.

This checkpoint does not write to the owner's saved cloud mage or change account/project revision safeguards. Reference-based verification uses disposable guest project data; account saving remains an explicit existing project action.

## Source and verification

The feature is implemented in the versioned accessory geometry factory, native transaction bridge, VR placement/interaction adapter and spatial UI, applied through the appended v11.410 source patch. Existing v11.391 Sheep Tag input behavior and the documented withdrawal of the experimental v11.392 FOLLOW throttle remain preserved.

The full source reconstruction and package verifier passed: **391 ordered patches, 9623744 HTML bytes, SHA-256 `2503918d25b268435e6f8c474c74f644386bc4000516dfadf9748a7149b57463`**, 77 bundled assets and 81 package files. Both HTML entry points and `SOURCE.json` agree. Geometry and native transaction tests passed **17 groups**, auditing 97 component variants with no degenerate/nonmanifold/winding defects. The real Three.js UI checks passed **nine groups** for reachability, readable state, idle rendering and resource disposal.

The exact sealed artifact passed **12 actual IWER 2.8.0 Quest controller workflows**, with zero page errors: source-safe parameter edits, stick sizing/turning, surface fitting and menu pose retention, Focus while fitting, deliberate atomic placement, selected group Grab, exact Undo/Redo, B/Y cancellation, tracking loss, Guide and Exit. The emulator package is pinned by byte count and SHA and is not shipped in the engine. A separate bounded mage reference check uses a disposable imported project; its final receipt and the hosted deployment receipt will be recorded after confirmation. Automated WebXR emulation checks source transactions and rendering; physical Quest comfort, tracking feel and sustained hardware frame time remain owner acceptance testing.
