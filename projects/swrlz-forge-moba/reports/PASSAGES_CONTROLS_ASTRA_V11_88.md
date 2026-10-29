# v11.88 · Passages, touch controls and original Astra

## Behavior

- A living ground sheep prefers a fitting nearby corridor before the nearest exterior house corner. It aligns to the middle of the lane and continues in the held direction. Every short step still passes native swept building and unit collision checks. Existing 0.60 m passages work; deliberate new lane snapping uses 0.75 m. Reverse/release stop or change direction immediately; old joystick corner paths are cleared when the target changes.
- Viewport-relative control sizes handle both ordinary phone CSS widths and the owner's wide Android portrait layout. Portrait joystick diameter is 65vw, building icons 21vw (main house 22vw), and abilities 18vw. Outer and inner arcs remain separate. Joystick and right-side centers move inward; short portrait clamps against the minimap. Landscape scales from viewport height. Original pointer capture, two-thumb movement, above-finger preview and drag/release construction remain native.
- The wolf starter restores Astra's original blue/ivory palette, face/ears/ruff, traveling gear and huge curled tail. The 24 gear and 13 tail/stardust parts are preserved exactly. Three welded, closed editable anatomical surfaces refine the body/shoulders/haunches, skull/jaw and continuous muzzle, totaling 134,348 triangles. The complete starter has 102 meshes and 399,760 rendered triangles. Original 4096px color/normal atlases remain; the independent Clover sheep starter is unchanged.

## Targeted checks

- `test_sheep_passages_v11_88.mjs`: native swept movement, 160 m map bounds, three house rows, old/new lane widths, off-center approach both directions, exterior corner fallback, rotation, blocked exits, physical traffic, reversal/release, wolf exclusion and 0.75 m construction snap.
- `test_sheep_gap_touch_v11_88.mjs`: actual CDP touch joystick input through three rows of existing 0.60 m lanes; off-center approach centers the sheep, clears all houses and stops on release. Final positions 44.49995/0.000011 at mid-trip and 51.69995/0.0 after traversal; no page errors.
- `test_sheep_controls_v11_88.mjs`: seven portrait/landscape sizes, including 926×1700, control containment and circular separation, minimap clearance, score bounds, diagonal joystick steering/release, enlarged-button drag/release construction and seven-minute timer. Final layout evidence is generated locally for this release.
- `test_courier_v11_88.mjs`: native model validity, actual 4K textures (normal maps on lit surfaces), native volume rebuild equality, editable materials/Undo, native model save/import and textured GLB export. Emissive original parts retain their base-color atlas without a normal map.
- `verify_v11_88_release.py`: exact 120-patch/56-asset receipt; all 281 previous runtime/patch files and 55 previous assets retain SHA-256/bytes; original gear/tail equality; every new surface edge has exactly two incident faces; source build and module syntax.

The source commit and separate final deployment request identify the same artifact. Publication requires exact-trigger production Actions success and normalized live HTML/SOURCE agreement under RELEASE_PROCESS.md. Owner device acceptance follows publication.

Final targeted checks passed, including the native authoring/edit/Undo/save/import/GLB flow and all seven final touch layouts. Exact artifact: **3,371,397 bytes**, SHA-256 `6d4ce7a4f95c2c90fb988d99867ee240c7a505df13b43c7be4b2038f506e4c2e`. The downloaded GLB contains 102 real meshes / 399,760 triangles and exact embedded original 4K images. See [machine-readable local evidence](../tests/passages_controls_astra_v11_88_result.json).
