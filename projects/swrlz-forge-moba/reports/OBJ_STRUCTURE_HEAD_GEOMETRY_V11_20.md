# v11.20 · OBJ-informed head construction study

## Inputs / ownership

- Owner-provided **Angle_2d_Character.obj** is an external *technical construction reference*, **not** the target character and **not** an asset to import or reproduce.
- Owner-provided cyan/coral festival **front / side / back / three-quarter turnaround** remains the actual target for silhouette, facial proportions and style.
- Owner-supplied in-game close-up adds eye, cheek, nose and mouth rendering direction.

## What was actually inspected

The Blender OBJ has 3,859 source `v` records, 5,819 faces, and 68 spatially disconnected components (including repeated/linked positions). Its overall bounding box is approximately X [-1.961, 2.047], Y [0.083, 2.338], Z [-0.658, 0.294]. Thus it must **not** be used as if it were a complete watertight head/depth scan. The central upper-head region (roughly X ±0.25, Y 1.64–1.96) contains separate forward/rear connected facial shell pieces, e.g. submeshes with 518, 253, 184 and 168 faces. This illustrates an intentional multi-plane facial construction as opposed to one unmodified ellipsoid.

Some approximate coordinate ranges overlap hair and other parts, so none of these absolute OBJ dimensions are copied verbatim onto the `§E` heroine. In particular, the nose/ear surfaces cannot be uniquely isolated from raw OBJ component counts without material labels.

## Native §E corrective implementation

`runtime/model_atelier_anatomical_v11_20.js` uses the existing native editable vertex mesh and turns it into a designed three-dimensional head:

- Full circumferential reference-fit width sections; cheek/temple mass transitions to narrow mandibular and chin bands.
- Occipital depth reduction through the back hemisphere rather than just pushing the central nose while retaining the spherical rear.
- Differentiated, smoothly connected orbital recess, malar ridge, narrow integrated nasal bridge, tip/alae, philtrum, lower lip, labiomental groove and chin plane.
- Face construction remains a continuous `BufferGeometry`; eye and lip elements retain native, independently editable scene parts and compatible JSON/OBJ export.
- The owner reference fit remains saved in `scenes/model-atelier-festival-anatomy-v11-20.swyrl.json`. The user-provided external OBJ was **not committed to GitHub**, embedded into the webpage, or required at runtime.

## Validation and scope

Shape must be judged using a real front / true three-quarter / profile screenshot beside the owner reference; passing geometry/index and editor tests is not artistic acceptance. Keep all 283 previously editable parts, historical starter files, Undo/Redo, JSON import/export, and stable v11.19 release. New revisions publish via the separately hosted character preview path so the owner can rotate the character between iterations.
