## v11.14 follow-up

## v11.14 · portrait, silhouette and cloth refinement

The owner requested a closer match to the festival turnaround after reviewing v11.13. This pass refines swept cyan/coral hair into closed elliptical ribbon locks, narrows the round sclera, improves ferret muzzle/eye/ear readability, varies paper edges and color, opens the relaxed A stance, reshapes sock folds and shoes, adds inset garment stitching, and gives the skirt real curved side panels with an opaque fitted underlayer. The separate bunny is moved clear of the wider shoe stance. Front, three-quarter, back and profile views are required; a front-only screenshot cannot reveal missing side cloth.

New native asset: `scenes/model-atelier-festival-refined-v11-14.swyrl.json`; **301 editable parts and 108,260 measured triangles**. Native editor Save model JSON retains the authored result. All three creatures keep independent motion, sockets, detach/reattach, transform keys and exports. The new geometry uses deterministic variation so save/load and OBJ exports reproduce the same surfaces.

Candidate seal: **2,482,877 bytes**, SHA-256 `1154b86d8a8c027fc3b94a39254ff77d5d136a0fcc8283061ef1d0b6d6fe1803`, 84 patches and 37 assets. All 83 predecessor patches/runtime sources and 36 assets remain preserved. Baseline v11.13 was verified live at `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8` before this work. Branch `feature/model-reference-refinement`. Full compatibility CI, the final dedicated deploy request, hosted digest/asset audit and live native controls are release gates; owner visual acceptance remains separate. This is an editable original geometric study, with UV painting and skeletal weight painting still outside the implemented tools.

# Festival reference sculpt and living piñatas — v11.13

The owner's 35055.jpg turnaround governs this native character: swept split cyan/coral hair, expressive warm eyes, asymmetric ivory/coral bodice, teal and gold pointed skirt, bare legs, white socks, dark shoes, two large tissue-paper ferrets gripping real pigtails, and a separate black-faced paper bunny. The new starter is authored as editable §E geometry; it does not import a rendered picture or extract a commercial mesh. Historical model studies remain packaged unchanged.

## Research that informed construction

- [Julien Kaspar, Blender Studio: Stylized Character Workflow](https://studio.blender.org/training/stylized-character-workflow/): design, sculpting and retopology. This course concerns film production; it does not establish a universal game triangle limit. Public descriptions were available; paid lesson contents were not accessed.
- [Anastasia: Stylized Game Character Model and Animation Showcase](https://nastuadesu.artstation.com/projects/41oY1Y): the artist reports 24,784 triangles, Blender sculpting/manual retopology, rigging, skinning, animation and Unity setup.
- [Darena Georgieva: Stinger breakdown](https://80.lv/articles/modeling-and-texturing-an-interesting-hand-painted-game-ready-3d-character): first-person Blender workflow; about 50k triangles and three 4K texture sets. Curves support hair silhouettes, instancing/mirroring repeat elements, and details that do not affect silhouette can be painted. We used the silhouette and repeatable curved-sheet principles, not her asset or textures.
- [Blender glTF manual](https://docs.blender.org/manual/en/4.1/addons/import_export/scene_gltf2.html): object transforms, shape keys and skinning are distinct export/animation mechanisms. §E's new assembly animation is object motion and procedural paper flex, not a claim of skinned bones.

These examples are comparison points, not a requirement to duplicate a triangle total. The current starter measures approximately 82,396 generated triangles in 275 independently editable source meshes. Each ferret contributes 11,248; the heroine 54,988; the bunny 4,912. The live inspector computes actual BufferGeometry counts and reports CPU buffer memory, not welded vertices or GPU memory. Whole-frame GPU calls are not inferred from source part count.

## Reusable engine tools and native data

`project.modelAtelier.assemblies` uses `swyrl-assemblies-v1`. A bounded list of named sockets references real pigtail mesh IDs and local attachment positions. Three independent components own disjoint part groups. Each has an original pivot, socket, attached/free state, offset, Euler rotation, scale, flex amplitude and speed. Attached geometry is transformed from its own rest pivot to the resolved socket. A moved/rotated/scaled pigtail carries its piñata through a saved bind transform. Detachment retains the complete affine matrix, including nonuniform scale, and releases socket following.

Living models → Snap to pigtail / Detach conserves current world transform when detaching; reattachment deliberately returns to the hair rest fit. Each component can have up to 24 ordered transform keys (time, offset, rotation, scale). Offset and scale use smooth interpolation; rotations use quaternion interpolation. With no authored keys, the ferrets approach and grow into the pigtails over 3.6 seconds using a quintic ease. The six-second preview uses real requestAnimationFrame time, can pause, stop and scrub backward deterministically. The paper plumes flex independently with their roots stable. The bunny has its own motion and export.

Motion keys override the built-in approach for that model. Values are relative to the resolved socket/rest pivot. Clear keys restores the approach. Each model exports its own native part catalog, socket and motion data. Whole model JSON and native project Save/Load preserve all three components. OBJ exports actual currently rendered triangles, including the previewed transforms and flex; it is a static geometry export, not a skeleton or animation interchange file.

The new surfaces include tapered portrait-head shaping, organic swept hair and anatomical limbs with corrected outward normals, three-dimensional overlapping torn paper sheets on every side of each plume, curved fabric panels/piping, and the bunny's thick tissue fringe. Individual paths/radii, transforms, colors and materials remain editable. The original v11.12 default is embedded as an explicit legacy fixture so its detailed pose/editor regression continues independently.

## Verification and visual limits

Required: native desktop/phone views, actual front/profile/rear screenshots, independent motion/key interpolation, world-preserving detach and socket movement, actual JSON/OBJ/component downloads, invalid-import rejection, Undo, legacy import and all existing game/animation browser suites. The release uses 83 append-only patches and 36 packaged assets. Earlier 82 patches/runtime modules and 35 assets must stay byte-identical. The model-first workspace reserves a practical tall viewport on phones and a separate desktop inspector.

This is a closer original geometric study, not a claim that the reference's sculpted topology, hand-painted maps, skinning and rendering have been reproduced exactly. UV painting, production retopology and weighted skeletal deformation remain future editor work. Owner visual acceptance remains distinct from passing source and browser checks.
