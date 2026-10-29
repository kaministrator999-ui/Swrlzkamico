# Prism Jester — Carnival Ferret-Piñata Model Direction

**Status:** v11.4 original character fidelity study, not a 1:1 extracted asset or production sculpt. **Primary references:** owner-provided screenshots of the *carnival* Scorchette skin, front/side/back; other skins inform visual polish only. Source photos are user-supplied references, not packaged third-party textures or geometry.

## Recognition targets

| Component | Priority | Art requirement | v11.4 implementation |
|---|---|---|---|
| Twin creatures | P0 | Each apparent giant pigtail is a **ferret-like piñata creature** with a separate dark head gripping the colored pigtail | Two head/muzzle/ear/eye/paw assemblies and a pigtail attachment; not just tubes |
| Color/silhouette | P0 | Blue/cyan on viewer's left, fiery coral/red/orange on viewer's right, dramatic arch above the performer, taper downward | Two curved, continuous varying-radius lofts + paper-fringe shingles |
| Face | P1 | Petite tapered anime face, split-color bangs, readable eyes and playful expression | Smooth higher-segment ellipsoid shapes, overlapping hair strands, highlighted eyes/lashes |
| Wardrobe | P1 | Asymmetric mini circus-mage dress, dark sleeve, cream, teal, amber and orange accents, small stage bulbs | Original v11.3 dress layers plus seam, frill and light refinements |
| Material | P1 | Flat matte crepe-paper body, distinct dark velvet ferret heads, gentle skin softness and emissive costume decorations | Per-part roughness/material variations, vertex-shaded spline mesh, independent emissive trims |
| Motion | P2 | Animate creature heads and ribbon-spine flow in future riggable authoring | **Not implemented**; requires bones, attachments, skinning, animation editor |
| Game-ready asset | P2 | Clean sculpted organic topology, UVs, textures, details and optimized export | **Not yet implemented**; current study is procedural primitive/loft geometry and OBJ/JSON |

## Engineering and preservation

- The canonical **Projects → Model Atelier · Prism Jester** tile remains a single native project; v11.4 swaps its default asset to a distinct `model-atelier-prism-jester-ferret-v11-4.swyrl.json` while retaining the v11.3 scene separately.
- New `loft` kind: 2–40 control points, equal number of radius values, bounded positive radii, bounded tessellation, and surface vertex colors; existing position/rotation/scale/material/selection and JSON/OBJ export remain functional.
- Keep existing engine patch chain and all archived project assets unmodified. Avoid any dependency on per-request APIs, image generators, external assets or paid runtimes. Browser performance must be tested on both phone and desktop.
- The editor's existing model-part cap remains 400. V11.4 contains 303 parts, two of them continuous organic lofts. Test schema-valid save/reload, invalid spline import rejection, OBJ non-empty triangles, undo/redo, older v11.3 native model import, native project registration and legacy starters.

## Grounded modeling references

- [Blender: mesh modeling fundamentals](https://docs.blender.org/manual/en/latest/modeling/meshes/introduction.html) — move from primitive blockouts to actual polygon shapes.
- [Blender: sculpting workflow](https://docs.blender.org/manual/en/latest/sculpt_paint/sculpting/index.html) — brush-based shape refinement, still a subsequent editor phase.
- [Blender: UV unwrapping](https://docs.blender.org/manual/en/5.4/modeling/meshes/uv/unwrapping/index.html) — map detail images to surfaces when geometry is stable.
- [Blender: armatures](https://docs.blender.org/manual/en/5.2/animation/armatures/introduction.html) — creature and character rigging, not yet implemented.
- [Three.js: GLTFLoader](https://threejs.org/docs/pages/GLTFLoader) and [Three.js: loading 3D models](https://threejs.org/manual/pages/loading-3d-models.html) — suggested future .glb import/export interchange to retain skinned meshes, animation and textures.

## Honest acceptance threshold

**This release is a silhouette, organic-mesh and face/creature recognition improvement, not a claim of reproducing the exact hero mesh, skin or polished commercial game quality.** The owner's hands-on artistic judgement remains separate from source/CI/hosted integrity.
