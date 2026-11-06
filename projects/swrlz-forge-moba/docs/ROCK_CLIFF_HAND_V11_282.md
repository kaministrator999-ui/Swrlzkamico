# §E v11.282 · Rocky Anime Hand: cliff-rock anatomy (owner screenshot revision)

## Reported problem
The v11.281 starter looked like **smooth palm and fingers wearing sparse rock armor**, contrary to the generated rock-cliff-hand reference and the owner's screenshot. The target is **a hand formed from jagged cliff rock**, with no exposed smooth glove.

## Implementation
The new v11.282 starter generator **replaces** all v11.281 model parts on fresh opening:
- A connected-looking, fully faceted rock palm volume from base wrist to knuckles, including the **back, palm, sides**. No original organic surface remains in the created model.
- Thick overlapping rocky outcrops wrap both sides of the hand and the palm/back. The silhouette is irregular and angular, not anatomically smooth or styled as equipment.
- **Four fingers × three solid full-circumference rock shaft segments**, not just dorsal and palmar plates; lateral chips and small orange fault seams between joints.
- **Three full-circumference thumb stone sections** along the native anatomical diagonal thumb path.
- A broad rooted wrist with overlapping basalt chunks rather than a bracelet.
- Hard faceted shading via unshared mesh triangle normals. All parts are native editable indexed topology meshes with simple slate/purple-gray materials; amber emissive fault lines are 3D geometry.

Preserves 17-bone rig, keyframed open/fist gestures, native save/export/sculpt, gallery card and direct URL. Existing saved projects are not silently rewritten. No changes to the original or mirrored Arcane Glove, the VR starter game, Mage Spell Lab, Sheep Tag or §C.

## Validation
Focused actual scene-generator smoke validates stone segment count, solid volume dimensions, mesh indices, part IDs, groups, lack of organic surface and 17 bones. Source build and syntax receipt verify release integrity separately. Real phone/Quest visual acceptance remains pending.
