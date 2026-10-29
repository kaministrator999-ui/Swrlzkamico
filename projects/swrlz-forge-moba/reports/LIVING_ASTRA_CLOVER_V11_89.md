# v11.89 · Living Astra, Clover flock and compact controls

Astra retains his original seated blue/ivory courier design, gear and curled comet tail. The full anatomy refinement uses the native volume/sweep tools to shape shoulders, ribcage, pelvis, elbows, carpal joints, hocks, tendons and connected four-toed paws. The chest tapers beneath the original harness; cheeks/brow/orbits, nose/nostrils, muzzle/jaw, pupils and cupped ears receive separate organic detail. Every biological part outside the preserved curved tail is a saved indexed topology mesh. All 37 original gear and tail/stardust components remain exact. All 55 new anatomical/detail meshes are closed: every edge has two incident faces.

Clover's game copy is generated from the exact v11.87 sheep starter using Model Atelier's native `atelierLODPlan` reducer. It retains all 31 named parts/IDs, colors, materials and 4K bindings. The full 275,872-triangle starter remains immutable. The game copy has 33,087 triangles; all copies share cached geometry/materials and atlas images, while six animation joints are independent. Fleece width is fitted to 0.52 m, within the native 0.54 m sheep diameter. The factory handles every `st-sheep`, including old native saves and starter actors. It does not alter collision/navigation, orders, capture/revival or the match clock.

The previous control enlargement overshot the owner's preference. Portrait sizes now approximate 45% of v11.88 at 926 px; minimum practical touch sizes apply on narrow CSS viewports. The stick returns to the lower-left corner. Right controls use two spaced compact rings. Utility actions clear the minimap in landscape. Original pointer ownership and above-finger drag/release placement remain native.

## References

Anatomical landmarks were informed by the [University of Calgary Faculty of Veterinary Medicine's canine anatomy page](https://vet.ucalgary.ca/community/learning-animal-health/anatomy/dogs-cats), especially forelimb/shoulder and hindlimb muscle groups. The [wolf skeletal proportion illustration](https://dessindigo.com/en/blog/how-to-draw-a-wolf) provided a secondary visual reference. The volume-based organic workflow follows the general remeshing approach described in the [Blender remeshing manual](https://docs.blender.org/manual/en/4.4/modeling/meshes/retopology.html); the actual meshes are authored with §E's own tools, with no external model imported.

## Targeted verification

- `verify_v11_89_release.py`: exact 121-patch/58-asset receipt; freeze 285 prior runtime/patch sources and 56 assets; preserve all 37 original gear/tail parts; validate closed surfaces and per-mesh native limits; compare the compiled Clover game model with its native asset and full-resolution source metadata.
- `test_living_astra_v11_89.mjs`: native model validity, actual loaded 4K images, in-editor organic rebuild equality, material edit/Undo, native JSON save/import and textured GLB export. Emissive surfaces retain base color without requiring a normal map.
- `test_clover_corner_controls_v11_89.mjs`: all eight starter sheep use Clover; six populated animation pivots, original part IDs and shared 4K images; diagonal leg gait and real touch movement/release; seven final portrait/landscape control layouts; actual icon drag/release build; seven-minute timer and saved-duration migration.
- `test_clover_house_gap_v11_89.mjs`: actual touch control of Clover through three rows of existing 0.60 m house lanes from an off-center approach, with immediate release-to-stop.
- Native textured GLB inspection checks actual geometry, normals, UVs, indices, all 92 meshes and exact embedded original 4096px images.

Publication follows the source commit, separate final deployment request, exact-trigger production success and normalized live HTML/SOURCE/asset checks. Owner device acceptance follows publication.

All targeted checks passed. Final artifact: **4,557,192 bytes**, SHA-256 `a9f6b48036c852be5a75150f18ebc9e31633c43acaa28c3b08a79b1d67506ed0`. Native textured GLB: 92 meshes / 547,676 triangles, exact embedded original 4K images. See [machine-readable evidence](../tests/living_astra_clover_v11_89_result.json).
