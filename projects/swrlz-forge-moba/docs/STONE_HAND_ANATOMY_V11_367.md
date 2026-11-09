# §E v11.367 — correct hand anatomy without reducing rock detail

## Correction of the earlier approach
The user observed that the Cliff Hand hardly changed and that the Rocky Hand should remain made of many individual rocks. Fewer rocks are not the solution. This release changes the *positions and proportions of the rocks themselves*, while retaining their separate geometry and the original rock art.

## Cliff Hand
The original plain-hand-base starter continues to use one connected signed-distance-field mesh. The native gauntlet generator now calls se367CliffField(math), which wraps the existing photo/ulnar/geode hand field with a visibly narrower metacarpal palm, stronger wrist taper, controlled finger barrels and naturally joined opposable thumb. It remains one editable UV-painted model with all 17 animation bones, stone fractures and inlaid crystal shader.

## Rocky Anime Hand
The original all-stone v11.283 scene is preserved as se365OriginalStoneScene; the *new* se281RockScene points at se367AnatomicalRockScene, not the destructive v11.365 61-piece filtered scene. Every original stone part survives, including 20 palm strata, 10 solid outside blocks, 12 optional finger chips, 12 closed stone finger shafts, 3 closed thumb stones, wrist rocks and 25 glowing seams. Individual coordinates are remapped around anatomical finger joint centers, a narrower palm envelope and diagonally connected thumb, preserving all UVs and face indices.

## Automated acceptance
The existing all-rock source model is compared to the remapped output: both must retain all 89 parts, original identifiers and matching UV/face data; every anatomical rock class is still represented. Geometry width/depth must change for core palm, each finger and thumb. A separate SDF comparison measures the new Cliff silhouette around palm, wrist and fingers relative to v11.365, without creating any extra geometry. The exact sealed HTML SHA and native JavaScript syntax are verified before deployment. Phone and Quest 2 viewing remains owner acceptance.
