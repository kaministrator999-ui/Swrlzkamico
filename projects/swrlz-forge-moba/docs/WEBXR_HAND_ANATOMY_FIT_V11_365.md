# §E v11.365 · targeted WebbXR hand-reference anatomy calibration

## Verified original reference

Bundled source: `assets/models/webxr-hands/right.json` derived from the MIT-licensed public WebXR generic-hand glTF. Measurements use true native joint landmark positions, not screenshots or guessed eyeballing. Normalized tip-to-proximal Y distances:

- index / middle = 0.943
- middle / middle = 1.000
- ring / middle = 0.920
- pinky / middle = 0.746

The 17-joint §E rig cannot directly skin to WebXR's 25-joint reference, so this update deliberately uses measured ratios and conservative shape corrections rather than a replacement/retargeting that could break poses.

## Existing Cliff / Plain Hand Base
One connected SDF shell and original stone mapped PBR remain. Reduce forearm end radius from .322 to .298, trim metacarpal overbreadth, and extend index +.048 and pinky +.042 in existing photo-guided field. Small PIP/DIP/tip radius adjustments soften chunky finger shafts. Palm-side owner photo shape, thenar fold, adjusted ulnar silhouette, original 17-joint skin, UV paint, 4 inlaid geodes and all original save/export controls remain.

## Existing Rocky Anime / Emberstone multi-rock
Keep actual solid rock finger/thumbnail segments, palm foundation and 17-bone rig. Prune exactly 28 small exterior decorative objects only (10 repeated palm strata, 8 side overhangs, 8 finger chips, 2 wrist slabs) while retaining 360-degree structural stone segments and existing fracture seams. Reduce inflated palm width/depth and stone finger radius, ease thumb side inward, make fingers taper naturally and bring index/pinky length ratios closer to WebXR. Remap *only mesh positions*, never UVs, triangle indices, rig/bone weights, texture paint or unrelated projects. Existing mesh groups are pruned of removed IDs. The source scene generator is preserved under `se365OriginalStoneScene`.

## Regression contracts
- Inspect bundled 25-joint ratio evidence.
- New rock starter retains 17 bones, 12 full stone finger segments, 3 solid thumb segments, every original energy seam and valid native topology indices/UVs, but removes exactly 28 redundant decorative parts. Each remaining mesh group references existing IDs.
- Cliff hand stays one mesh, 17 bones, slightly longer index/pinky tips, narrower metacarpal band and wrist base, photo-contour intact. No separately spawned geometry.
- Full exact-source build and syntax validation before live test deployment. Owner's phone/Quest acceptance remains separate.
