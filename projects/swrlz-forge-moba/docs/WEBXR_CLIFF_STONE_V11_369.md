# §E v11.369: actual WebXR mesh replaces Cliff geometry

## User direction
The 89-piece Rocky Hand was accepted as visually improved; leave it alone. The procedural Cliff Hand's silhouette was rejected after the larger v11.367 anatomy correction. Replace that geometry with a clone of the already approved WebXR hand, applying the original Cliff PBR texture set.

## Source
- Bundled unchanged MIT-licensed `assets/models/webxr-hands/right.json`, extracted from the WebXR Input Profiles generic-hand/right.glb.
- Exact topology 1,360 vertices / 2,314 triangles, 1,360 UV pairs, and original 25 reference landmarks.
- `se358WebXRHandScene('right')` returns a fresh editable native model. The new loader changes **that scene only**.
- Coordinate mapping transforms its normal direction and finger spread from XR local Z to §E horizontal X, aligns wrist/thumb/finger positions with `se220CreateHandRig(se217FingerSpec)`; native 17-bone skin weights are recomputed at render time.

## Existing Cliff stone material, real UV mapping
- Keep the hand's authored UV island coordinates unchanged, to avoid stretching or overlap. Original triangle order is preserved.
- Use `se290CliffMaterial` for the Cliff variant so source `se288AtlasTile` samples the original owner-provided color/moss, normal, roughness and AO maps from `assets/cliff-hand/cliff_pbr_atlas_384.jpg` in the same UV space.
- Bypass `se337DorsalGeodeMaterial` and `se292WristMossKnuckleMaterial` only for this new Cliff material *variant*: the previous dorsal knuckle crystal overlays were authored for the obsolete planar UV coordinates and would land in the wrong spots on real XR UV islands.

## Native project integration
- Override `se284OpenPlainHand` and `createProjectFromTemplate('plain-hand-base')` to use the existing async loading pattern from the WebXR hand starters.
- Keep canonical project ID `plain-hand-base`, existing project grid card, native model scene, 17-bone pose rig, UV editor and save/export.
- Explicitly clear inherited named sockets before native load.
- Do not alter the standalone WebXR reference projects, the 89-part Rocky Hand, the Quest controller project models, or saved user projects.

## Validation
A pure Node test loads the actual source JSON and runs the new scene builder and native load route; checks original source immutability, exact triangle/UV identity, mapped 25 landmarks, 17 valid rig bones, finger order and expected natural wrist/hand bounds. Full ordered build and script-syntax checks must pass before release.
