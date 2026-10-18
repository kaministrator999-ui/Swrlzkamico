# §E Model Atelier — Codex operation and precision tool readiness

**Source:** owner's 17 October 2026 Precision Mesh & Reference-Driven Sculpting design specification.
**Status: INCOMPLETE DRAFT PREVIEW. Not yet ready for an unattended full-character sculpt.** Production §E v11.20 and its Codex 11-section anatomical head are unchanged.

## Working editor tools and controls

| Category | Operator-visible controls | Readiness |
| --- | --- | --- |
| Original 283-part model | Model Atelier, anatomy, Undo, native JSON, OBJ export | Existing production base |
| Spherical brush | SculptBrush radius, extrude/intrude, plateau, taper, half-sphere, level, snap | Prior browser-tested preview |
| Vertex matrix | mesh U/V grid, index picker, point/multi-select, drag gizmo, XYZ axis constraints | Prior browser-tested preview |
| Render modes | Viewport mode: Shaded/Wireframe/Shaded+Wireframe/X-Ray, Colors, Textures, Contrast Wire, tint | Prior browser-tested preview |
| Navigation | One-finger orbit, two-finger pinch/pan, desktop Shift/middle pan, camera views | Prior browser-tested preview |
| Reference panel | Four local image references, camera matching, zoom, rotate, mirror, opacity, draggable panel, native save | Prior browser-tested preview |
| Surface brush | SculptBrushSurfaceMode front / connected geodesic / through, separate selection radius and deformation radius, local falloff offset U/V, highlighted footprint preview | New v11.22; targeted tests |
| Surface lasso | LassoTools polygon, large draggable boundary pins, exact XYZ snapped to triangles, add/remove pin, regions, feather, morph displacement | New v11.22; preview implementation, test in progress |

## Explicitly NOT yet complete

- Surface occlusion-accurate visible-only selection, freehand/brush-painted lasso and complete inside-out/backface operation modes.
- Local triangle subdivision, crack-free adaptive refinement, independent editable density/detail layers, robust mesh LOD/decimation.
- Cropped face-image to triangulated sculptable UV-preserving surface, image distortion preview, closure into a manifold head.
- Full rotation/scale gizmos, symmetry, interior camera clipping and complete mesh/edge/triangle editing.

## Codex operator boundaries

1. Operate the real interactive editor and verify browser-visible actions. Never claim a UI action occurred if no editor/browser interaction took place.
2. Start from the actual original Codex anatomy head, preserve 283 original editable scene parts and the separate piñata assets. Do not replace the character with a user-provided OBJ.
3. On facial shells use front or connected mode by default; through-volume only when intentional.
4. Boundary pins modify a lasso region, not mesh topology. Vertex gizmos and region morphs actually displace existing vertices.
5. Before/after save: inspect front/profile/three-quarter beside the imported reference, use native Undo, save JSON, reload and check equivalent geometry.
6. Production and protected source manifests remain unchanged until gates pass. Do not merge draft PR automatically.

## Acceptance gates from the design

A — references: core implemented; B — vertex pins: core implemented; C — surface brush: core implemented and targeted tests; D — editable polygon lasso: core preview only; E — crack-free local mesh refinement/layers: pending; F — UV-preserving triangulated face-plane/head closure: pending.

**The full requested tool suite is NOT yet ready to hand Codex as a complete, autonomous sculpting environment.**
