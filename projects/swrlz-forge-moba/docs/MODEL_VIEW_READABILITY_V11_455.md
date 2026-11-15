# §E v11.455 — Solid modeling, view modes and legible Inset

## Owner observation
The November 14 phone screenshot showed a cube with pixel-like transparent patches, bright competing mesh overlays and an inset that was difficult to distinguish from its surrounding rim. Existing display modes (Shaded, Wireframe, Shaded Wire, X-Ray) already exist in the editor but are buried in inspector settings.

## Scope
This pass does not introduce a second mesh editor or replace the native source. It exposes current view modes at the modeling viewport, adds Solid, Clay and Flat, cleans up the default working appearance, replaces triangle-lattice Shaded Wire with angle-filtered actual mesh edges, and adds a subtle selected-face tint only while Inset/Extrude previews are active.

- **Solid (default):** opaque, rough, depth-writing material with the source mesh color; no ghosted back faces. Only the editor material is replaced, never the saved material.
- **Material:** original authored appearance and textures. This is the escape hatch for deliberately transparent and textured surfaces.
- **Shaded Wire:** the existing shaded material with filtered `EdgesGeometry` lines, which suppresses coplanar triangulation diagonals. The native topological inner Inset border continues to use the separate v11.453 source-correct line.
- **Wireframe / X-Ray:** preserved pre-existing modes.
- **Flat:** flat-shaded solid construction; **Clay:** neutral rough inspection material.
- **Camera:** existing Front/Right/Top/three-quarter views are exposed in the same dropdown, delegating to `se430ModelCamera`. The existing axis widget and advanced projection controls remain.
- **Inset/Extrude:** the native candidate mesh and Undo transactions stay unchanged. A temporary low-opacity tint on the selected new cap improves depth reading; both tint geometry and material are disposed when the candidate changes, applies or cancels.

## Safety
The current model, shaders and saved project remain unchanged by display modes. Switching view modes during native geometry preview re-skins the current mesh and requests visual redraw **without** calling `renderParts()`, which previously cancelled the active transaction. Face tint is unselectable editor helper geometry. The previous v11.454 rim-then-depth top slider and the Meta Quest VR tools are untouched. No new camera pointer listeners are attached to the viewport; the View menu stops only events beginning on its own control.

## Acceptance checks
On a new cube, default Solid must show front opaque faces without see-through or checkerboard effects. A valid Inset must have a clearly separated inner cap and outer rim. Use View to switch Solid → Shaded Wire → Wireframe → X-Ray → Clay → Flat → Material while the preview remains active, without modifying the camera, Undo or pending geometry; then Set the rim and depth. Test switching camera views only outside an active geometry preview. Confirm textures appear again under Material on an authored asset. Test portrait-phone layout and Meta Quest menus separately.

Static and executable test coverage is in `tests/model_view_readability_v11_455.mjs`. Native source seal and broad previous modeling suites run under `scripts/verify_v11_455_release.py`.
