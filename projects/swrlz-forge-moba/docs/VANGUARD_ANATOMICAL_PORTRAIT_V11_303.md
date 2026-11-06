# §E v11.303 · Anatomically sculpted face and portrait-mapped UVs

## Owner evidence
The user inspected v11.302 from multiple angles on Android and reported improved armor and shoulders, but facial detail still looked like simple childlike paint marks. Previous v11.301 facial texture was mostly a 384×384 gradient, two tiny eyes and a mouth line laid over an almost featureless ellipsoid.

## Paired construction
- Recreate the existing editable face part ID as a continuous **80×144 UV-parameterized head surface**, with modeled brow bulges, shallow eye sockets, upper/lower eyelid ridges, cheekbones, controlled nasal bridge, tip and wing volumes, philtrum, lip contour, and chin volume. No add-on eyelid/nostril spheres.
- Match the actual painted UV longitude (front = U 0.5; back seam = 0/1) to the feature relief in the geometry. Feature vertical coordinates follow the face parameter, with brows and eye sockets above nose and lips. No duplicated rear face.
- Create a **768px skin-only atlas** using native browser canvas with eye whites, nuanced blue-gray irises, pupil and catchlights, eyebrows, eyelid borders, nostrils, upper/lower lip shading, cheeks and subtle lighting gradients. Preserve existing stylized game-art material textures for all other families. No concept-sheet screenshots/photo crops.
- Shape the scalp cap / forehead hairline and replace the oversized rigid fringe with more controlled side locks and shorter brow-clear sweeping bangs. Keep mesh IDs and existing style.
- Preserve **14 other editable mesh geometries unchanged**, especially successful armor, pauldrons, neutral wrist poses, scarf, teal cloth, boots and clothing. Maintain 17 native part identities and prior material PBR settings.
- Preserve all saved user models, all historical release patches, unrelated game/model starters, §C Chat, Sheep Tag and VR. No bird, weapon or skeletal facial rig.

## Validation and limitations
Focused Node VM regression checks real sculpted geometry, positive nose/lip depth, face UV bounds, high-resolution portrait detail, source-image rejection, material caching and unchanged geometry on every non-head/hair part. Full generated engine JS parse and byte/SHA-256/asset receipt follow. User remains the final visual acceptance gate; code checks alone do not establish professional art quality.
