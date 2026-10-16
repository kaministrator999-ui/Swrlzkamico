# Festival reference sculpt and living piñatas — v11.13

The owner's 35055.jpg turnaround governs this native character: swept split cyan/coral hair, expressive warm eyes, asymmetric ivory/coral bodice, teal and gold pointed skirt, bare legs, white socks, dark shoes, two large tissue-paper ferrets gripping real pigtails, and a separate black-faced paper bunny. The new starter is authored as editable §E geometry; it does not import a rendered picture or extract a commercial mesh. Historical model studies remain packaged unchanged.

## Research that informed construction

- [Julien Kaspar, Blender Studio: Stylized Character Workflow](https://studio.blender.org/training/stylized-character-workflow/): design, sculpting and retopology. This course concerns film production; it does not establish a universal game triangle limit. Public descriptions were available; paid lesson contents were not accessed.
- [Anastasia: Stylized Game Character Model and Animation Showcase](https://nastuadesu.artstation.com/projects/41oY1Y): the artist reports 24,784 triangles, Blender sculpting/manual retopology, rigging, skinning, animation and Unity setup.
- [Darena Georgieva: Stinger breakdown](https://80.lv/articles/modeling-and-texturing-an-interesting-hand-painted-game-ready-3d-character): first-person Blender workflow; about 50k triangles and three 4K texture sets. Curves support hair silhouettes, instancing/mirroring repeat elements, and details that do not affect silhouette can be painted. We used the silhouette and repeatable curved-sheet principles, not her asset or textures.
- [Blender glTF manual](https://docs.blender.org/manual/en/4.1/addons/import_export/scene_gltf2.html): object transforms, shape keys and skinning are distinct export/animation mechanisms. §E's new assembly animation is object motion and procedural paper flex, not a claim of skinned bones.

These examples are comparison points, not a requirement to duplicate a triangle total. The current starter measures approximately 82,396 generated triangles in 275 independently editable source meshes. Each ferret contributes 11,248; the heroine 54,988; the bunny 4,912. The live inspector computes actual BufferGeometry counts and reports CPU buffer memory, not welded vertices or GPU memory. Whole-frame GPU calls are not inferred from source part count.

## Reusable engine tools and native data

`project.modelAtelier.assemblies` uses `swyrl-assemblies-v1`. A bounded list of named sockets references real pigtail mesh IDs and local attachment positions. Three independent components own disjoint part groups. Each has an original pivot, socket, attached/free state, offset, Euler rotation, scale, flex amplitude and speed. Attached geometry is transformed from its own rest pivot to the resolved socket. A moved/rotated/scaled pigtail carries its piñata.

Living models → Snap to pigtail / Detach conserves current world transform when detaching; reattachment deliberately returns to the hair rest fit. Each component can have up to 24 ordered transform keys (time, offset, rotation, scale). Offset and scale use smooth interpolation; rotations use quaternion interpolation. With no authored keys, the ferrets approach and grow into the pigtails over 3.6 seconds using a quintic ease. The six-second preview uses real requestAnimationFrame time, can pause, stop and scrub backward deterministically. The paper plumes flex independently with their roots stable. The bunny has its own motion and export.

Motion keys override the built-in approach for that model. Values are relative to the resolved socket/rest pivot. Clear keys restores the approach. Each model exports its own native part catalog, socket and motion data. Whole model JSON and native project Save/Load preserve all three components. OBJ exports actual currently rendered triangles, including the previewed transforms and flex; it is a static geometry export, not a skeleton or animation interchange file.

The new surfaces include tapered portrait-head shaping, organic swept hair and anatomical limbs with corrected outward normals, three-dimensional overlapping torn paper sheets on every side of each plume, curved fabric panels/piping, and the bunny's thick tissue fringe. Individual paths/radii, transforms, colors and materials remain editable. The original v11.12 default is embedded as an explicit legacy fixture so its detailed pose/editor regression continues independently.

## Verification and visual limits

Required: native desktop/phone views, actual front/profile/rear screenshots, independent motion/key interpolation, world-preserving detach and socket movement, actual JSON/OBJ/component downloads, invalid-import rejection, Undo, legacy import and all existing game/animation browser suites. The release uses 83 append-only patches and 36 packaged assets. Earlier 82 patches/runtime modules and 35 assets must stay byte-identical. The model-first workspace reserves a practical tall viewport on phones and a separate desktop inspector.

This is a closer original geometric study, not a claim that the reference's sculpted topology, hand-painted maps, skinning and rendering have been reproduced exactly. UV painting, production retopology and weighted skeletal deformation remain future editor work. Owner visual acceptance remains distinct from passing source and browser checks.
