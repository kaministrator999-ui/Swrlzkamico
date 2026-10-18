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
| Surface lasso | LassoTools polygon, large draggable boundary pins, exact XYZ snapped to triangles, add/remove pin, regions, feather, morph displacement | v11.22 passed desktop/mobile UI & persistence tests |

## v11.23 newly implemented, acceptance status

| Category | Operator controls / code | Status |
| --- | --- | --- |
| Local true subdivision | RefineTools: 1 or 2 detail levels from selected surface lasso; conforming shared-edge splits, reversible per-object layers, caps and UV/color interpolation | Core implementation; isolated no-T-junction/UV/color test passed; whole-head mobile Save/Reload regression gate required |
| Face reference → editable mesh | References → Create sculptable UV face sheet; oval/rectangle triangulation, normalized crop and U/V density, independent textured part, native UV-preserving brush/lasso deformations | Core implementation; requires full phone/desktop end-to-end verification; not automatic full-head reconstruction |

## Codex editor operation contract (narrow scope)

1. Open ONLY the verified isolated §E draft preview, and export a baseline native model JSON. Production branch and original 283 editable character parts must not be overwritten.
2. Import or select separate front/profile pictures in the reference studio; use camera presets and wireframe modes to document real profile differences. A reference picture is guidance, not automatic mesh geometry.
3. Select original Anatomical head object. Use Surface targeting: Connected where shell safety matters; Front otherwise. Through-volume is prohibited unless the operator intentionally needs both sides. Preview vertex footprint before any stroke.
4. Make small numeric extrusions and intrusions at the cheek, jaw, chin or brow, one checkpoint per operation. Capture front/profile/three-quarter before/after. Prefer reverting one failed stroke over rebuilding the head.
5. For narrow features, create a surface-attached lasso with at least three pins; use Add/Move XYZ to snap pins to actual triangles, then refine one level only if the visible triangle budget permits. Boundary pins are NOT mesh vertices. Refinement is recorded as an editable native layer.
6. Optionally create a separate sculptable face sheet from a reference to investigate the image relief. Never replace the official head with the sheet or claim a 2D image alone determines anatomical depth. Side/profile construction and complete skull closure remain deliberate manual modeling.
7. Verify Undo/Redo, wireframe topology, native JSON export/import equivalence and original part IDs. Do not merge or publish production automatically. A Code/CI success is not itself proof of an accurate character likeness.
8. Codex must operate the REAL editor controls using a supported browser/computer session; this report does not grant Codex browser access or claim that it has run the sculpt. Avoid touching unrelated files, paid services, or production deployments.

## Explicitly NOT yet complete

- Surface occlusion-accurate visible-only selection, freehand/brush-painted lasso and complete inside-out/backface operation modes.
- Fully generalized density goals/decimation, true runtime LOD profiles and independently reorderable sculpt-displacement layer stacks. A bounded conforming local subdivision core is available in v11.23.
- Custom freehand face silhouette cutting, UV distortion visualization, multi-view depth reconstruction and closure into a manifold head. A separate cropped oval/rectangle UV face-sheet starter is available in v11.23.
- Full rotation/scale gizmos, symmetry, interior camera clipping and complete mesh/edge/triangle editing.

## Codex operator boundaries

1. Operate the real interactive editor and verify browser-visible actions. Never claim a UI action occurred if no editor/browser interaction took place.
2. Start from the actual original Codex anatomy head, preserve 283 original editable scene parts and the separate piñata assets. Do not replace the character with a user-provided OBJ.
3. On facial shells use front or connected mode by default; through-volume only when intentional.
4. Boundary pins modify a lasso region, not mesh topology. Vertex gizmos and region morphs actually displace existing vertices.
5. Before/after save: inspect front/profile/three-quarter beside the imported reference, use native Undo, save JSON, reload and check equivalent geometry.
6. Production and protected source manifests remain unchanged until gates pass. Do not merge draft PR automatically.

## Acceptance gates from the design

A — references: core implemented; B — vertex pins: core implemented; C — surface brush: core implemented and targeted tests; D — editable polygon lasso: core preview only; E — conforming local subdivision/reversible layers: implemented core pending browser acceptance; F — UV face-sheet starter: implemented core pending browser acceptance, complete head closure pending.

**The complete advanced authoring specification is not yet implemented. Codex can use the controlled, tested editor tools, but should not assume freehand UV reconstruction, arbitrary inside-out topology editing, decimation or automatic skull closure exists.**
