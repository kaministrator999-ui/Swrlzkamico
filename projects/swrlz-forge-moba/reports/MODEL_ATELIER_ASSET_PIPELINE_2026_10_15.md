# §E Model Atelier — measured geometry profiler (v11.10 candidate)

## Why
This is the first source-level implementation slice from the 2026-10-15 Modeling Engineering Brief. Preserve original 253/303/539/653/733/749/811-part projects unchanged. One complex Scorchette-inspired, **original** character scene is a production test, not redistributed Honor of Kings art.

## Implemented
- A collapsed **Measured model statistics** inspector section after the editable mesh count.
- Computes triangle count from each generated Three.js BufferGeometry index (or raw position buffer for unindexed geometry), counts buffer vertices, raw geometry attribute bytes, and group totals.
- Excludes non-model stage geometry and selection outline.
- Exports a JSON report with a stable schema and per-group breakdown, including cyan/coral companions where grouped.
- Mobile-first: the inspector scrolls independently, so the statistics do not consume permanent viewport height.
- All measurements refresh after generated geometry is rebuilt (load, import, add, edit, undo/redo).

## Explicit exclusions
Estimated mesh draws **are not measured GPU draw calls**. Buffer vertices are not welded topological vertices. CPU geometry bytes exclude GPU memory, textures and shaders. This change does not claim animation, bones, weight painting, UV painting, production-grade retopology, separate attach/detach sockets, VFX authoring, or LOD generation.

## Planned independent slices (not implemented by this patch)
1. Reversible independent attachments with named sockets, cycle validation, world/local transform conservation and persisted ownership.
2. Hero identity + multiple non-destructive skin variants preserving base mesh and canonical rig topology.
3. Native deforming skeletons, weights and animation timelines with functional pose regressions.
4. Materials, UV and normal baking, LOD/optimization profiles and export-to-import validation.
5. Particle and VFX editor using the **same** entity IDs, scene graph, sockets and event timeline.
6. AI Chat operator issuing constrained and reviewable edits through explicit tool permission/validation gates.

## Acceptance criteria
- Desktop and phone show exact counts matching the Three.js geometry buffer objects in the live loaded scene, not static counters.
- Editing a loft or adding/removing a mesh updates totals, Undo restores and JSON export matches display.
- Counts are grouped by actual source model groups; stage floor/grid/helpers excluded.
- Existing 811-part project and all historical scenes remain loadable.
- Package/hash seal, desktop/mobile browser matrix, manual dedicated deploy and independently audited hosted output remain separate gates.

Use licensed or original production art only; external game imagery is for reference analysis.
