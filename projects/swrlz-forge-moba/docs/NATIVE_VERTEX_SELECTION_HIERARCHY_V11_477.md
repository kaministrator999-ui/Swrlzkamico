# §E v11.477 — Operation-first modeling tools, native points and selection shapes

## UX hierarchy

**Right family rail → left operation flyout → first horizontal selection-type bar → second horizontal shape bar → right parameters.**

On selecting Sculpt, the flyout lists actual modeling operations (Extrude, Inset, Subdivide, Split Edge, Solidify, Delete Faces, Fill Hole, Repair Normals). It does not list Vertex or ring options as tools.

Choosing Extrude or Inset activates the **Vertex** component selection mode by default. The first bar just beneath the native transform controls offers **Vertex / Edge / Face**. A second bar beneath it offers contextual selection shapes:

- Vertex: **Single vertex / Vertex ring / Filled vertex ring**
- Face: **Single face / Face region**
- Edge: **Single edge / Box select / Lasso**

The right inspector is hidden after choosing a tool, and opens only when the selected component type or shape needs actual parameters. The two narrow strips independently scroll horizontally on mobile.

## Model and data ownership

The original `atelierComponentOverlayBuild` renders real `THREE.Points` for selectable vertices and preserves the original native touch-picking, gizmo, checkpoint and Undo flow. The additive v11.477 entry adapter chooses a unique visible mesh automatically, or lets users tap the desired mesh when multiple exist. Vertex tool entry never creates fake points, duplicates the mesh, or edits UV mapping.

The existing v11.466 ring bridge selects connected topology graph rings and filled radius segments. It **requires editable welded topology** and one selected center vertex. It cannot make arbitrary hand-drawn closed regions on ordinary primitives. The user must explicitly convert a primitive to editable topology before topology-only ring operations.

Face Inset/Extrude requires a selected valid native face region. Native ring-boundary extrusion is supported for complete open boundaries only; a closed interior crown is not a legal boundary extrusion. Vertex or edge selection by itself must not be misrepresented as a completed Inset operation. Existing native Preview/Apply/Cancel remains authoritative.

## Verification

- 454 ordered source patches, deterministic HTML SHA-256 and bundled assets.
- Native script syntax and static component/shape hierarchy tests.
- Chromium touch tests for both compact mobile and desktop-site mobile: select Sculpt, Extrude, inspect rendered vertex points, inspect both selection strips, switch Ring/Fill, Face, and Inset.
- No destructive testing of actual owner-saved projects; the browser fixture creates its own temporary sphere.
- Physical Moto / Quest acceptance remains separate.
