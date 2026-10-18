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
| Local true subdivision | RefineTools: 1 or 2 detail levels from selected surface lasso; conforming shared-edge splits, reversible per-object layers, caps and UV/color interpolation | Passed geometric no-T-junction/UV/color tests AND desktop/mobile original-head Save/Undo/Reload (48,768 → 50,454 triangles); isolated draft preview |
| Face reference → editable mesh | References → Create sculptable UV face sheet; oval/rectangle triangulation, normalized crop and U/V density, independent textured part, native UV-preserving brush/lasso deformations | Passed desktop/mobile creation, UV geometry, crop/density editing, sculpt, Undo and JSON reimport; not automatic full-head reconstruction |

## v11.23 additional direct Codex controls (integration candidate)

| Capability | Real editor control | Scope |
| --- | --- | --- |
| Numeric vertex group editing | Vertex Matrix → select source indices → **GroupTools** Translate / Rotate / Scale, XYZ, Object / World / Surface-normal | Native `sculptVertexEdits` per-vertex movements (not synthetic mouse clicks); Undo, JSON and evaluated OBJ. Disable active refinement layers before editing source indices. |
| UV face volume closure | Select a separate `faceSheet` → **Closed head depth** (0 open; positive manually modeled rear) → Update mesh | Closed oval cap with shared rim edges, normals and UV registration. Does not replace the official character head or automatically reconstruct its likeness. |
| UV stretch inspection | Select face sheet → **Show UV distortion heatmap** | Non-destructive viewport diagnostic, using surface-edge stretch on the front image triangles; UVs are not altered. |

**Additional evidence:** closed-face synthetic geometric manifold/UV test, numeric object/world/surface-space transform test, and full browser Save/Reload/Undo tests are required at the exact final commit. A build deployment alone never suffices. The production mainline is unchanged.

### Controlled Codex head-refinement job recipe

1. Open the [candidate editor](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-sculpt-preview/index.html?project=model-atelier). Export native baseline JSON before editing.
2. Import the provided front/profile screenshot(s) through **References**. Match the camera to each angle and inspect Shaded / Wireframe / X-Ray before sculpting.
3. Select `model-0001` **Anatomical head**, not the reference face sheet. Preserve its eleven native skull/cheek/mandible sections.
4. For cheek/jaw/chin correction use connected-surface brush with modest strength and a narrow selected radius; verify the highlighted footprint before applying. Use **LassoTools** and **RefineTools** when extra local triangles are needed; stay below the phone triangle cap.
5. For exact geometric corrections, select explicit source indices and apply **GroupTools** numeric transform. Do not rely solely on touch-drag tests. Rotation and scaling are supported through individually serialized vertex delta arrays.
6. Confirm the right/left three-quarter and side profile after each small operation; record actual before/after inspector values, front/profile screenshots, model part count and export JSON. Undo any worsening contour.
7. Use a separate UV face sheet **only for study**, with independent source image and deliberate closed head depth if a three-dimensional reconstruction experiment is wanted.
8. Never change production or merge the draft from this recipe. An actual Codex/browser control session must execute the operations; writing a PR or a report does not itself sculpt the character.

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
- Custom freehand face silhouette cutting and multi-view depth reconstruction remain unimplemented. A **manually adjustable** watertight oval back cap and front UV stretch heatmap now exist in the candidate preview; full photogrammetric reconstruction remains out of scope.
- Numeric rotation/scale of selected existing vertex groups is now implemented; visual rotation/scale gizmo handles, symmetry, interior camera clipping and complete mesh/edge/triangle topology editing are not.

## Codex operator boundaries

1. Operate the real interactive editor and verify browser-visible actions. Never claim a UI action occurred if no editor/browser interaction took place.
2. Start from the actual original Codex anatomy head, preserve 283 original editable scene parts and the separate piñata assets. Do not replace the character with a user-provided OBJ.
3. On facial shells use front or connected mode by default; through-volume only when intentional.
4. Boundary pins modify a lasso region, not mesh topology. Vertex gizmos and region morphs actually displace existing vertices.
5. Before/after save: inspect front/profile/three-quarter beside the imported reference, use native Undo, save JSON, reload and check equivalent geometry.
6. Production and protected source manifests remain unchanged until gates pass. Do not merge draft PR automatically.

**Verified v11.23 acceptance:** [real browser and CPU results](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39126576476) · [exact published preview](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39126576523). The original 283 parts stay unchanged unless a user deliberately adds a separate face sheet.

## Acceptance gates from the design

A — references: core implemented; B — vertex pins: core implemented; C — surface brush: core implemented and targeted tests; D — editable polygon lasso: core preview only; E — conforming local subdivision/reversible layers: core verified desktop/mobile; F — UV face-sheet starter: core verified desktop/mobile; explicit watertight oval closure and UV distortion preview added in the next candidate. Manual construction remains necessary.

**The complete advanced authoring specification is not yet implemented. Codex can use the controlled, tested editor tools, but should not assume freehand UV reconstruction, arbitrary inside-out topology editing, decimation or automatic skull closure exists.**
