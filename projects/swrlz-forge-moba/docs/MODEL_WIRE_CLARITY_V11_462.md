# §E v11.462 — Clean modeling wireframe and viewport balance

Owner's 2026-11-15 screenshots confirm functional dock drags and a connected inset, while Wireframe exposes faint triangulation, Shaded Wire lacks contrast, Material looks overly smoothed, and an expanded inspector narrows the viewport.

The native renderer now defaults to angle-filtered topology edges rather than all triangles. Its View menu offers optional triangulation and hidden edges, both display-only. Wire and selected edges have higher contrast. Material on bounded editable hard-surface meshes uses planar normals; source materials, UVs, topology and Undo remain untouched. Mobile desktop-style dock sizing reserves a minimum of roughly 35% of available space (240–330 CSS pixels) for the model viewport, without replacing native drag handlers.

This patch is limited to existing ModelAtelier display and sizing pathways; previous Inset/Extrude previews, camera orbit, project saving, VR model tools and lineages remain. WebGL hardware line width is generally fixed, so no deceptive thickness control is exposed.

The v11.462 source must be rebuilt from all 439 patches, passed through the syntax, native wire diagnostics, previous view bridge and asset-integrity verification before the separate Hugging Face publication request. Physical Android/Quest acceptance is not implied by CI.
