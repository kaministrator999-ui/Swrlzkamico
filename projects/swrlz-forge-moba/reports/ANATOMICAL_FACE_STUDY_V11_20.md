# §wyrl§ Engine — anatomical face study candidate (unreleased)

## Owner direction and primary visual target
Follow the supplied original character turnaround and mobile/game face references for stylized proportion, expression, anatomical silhouette and deliberate surface forms. Do **not** extract or redistribute commercial game geometry or textures. The current v11.19 model is the historical baseline. The screenshots of an unrecovered external v11.20 editor sandbox are useful visual evidence, **not** saved source authority.

The goal is **not** a higher polygon count. Each major form should read as a deliberate sculpt instead of a default sphere, capsule or cylinder with surface decorations. Begin with the face; continue later with neck, torso, limb, hands, feet, clothing and creature connectors only after front/profile/three-quarter evidence confirms a coherent direction.

## Implemented on the isolated candidate branch
- New opt-in continuous, section-shaped head BufferGeometry with six bounded saved controls for mandible, zygomatic cheeks, orbit, bridge/tip of the nose, chin and temporal contour. Vertex skin/blush shading is deterministic.
- New non-oval auricle BufferGeometry with editable helix, antihelix, concha relief and inferior lobule.
- Saved native scene `scenes/model-atelier-festival-anatomy-v11-20.swyrl.json`, preserving the original 283-part v11.19 asset and the rest of its parts. Only the new head and the two ears opt into the geometry feature.
- An ordered but **not yet manifested** v11.20 integration patch adds valid import bounds, native Apply/Undo/Redo controls, and tool selection without touching legacy unannotated scenes.
- Isolated baseline rebuild plus browser and CPU acceptance workflow. The experimental artifact is not deployed.

## Required review before this becomes a release
1. Deterministic patch and full generated JS syntax. Save/undo/import/export on desktop and phone.
2. Front, right profile and three-quarter closeups compared to reference. Reject any sharp pointed jaw, boxy skull, recessed/hidden nose, floating lashes/lips, oval stick-on ears, neck seams or self-intersecting hair.
3. Mouth/lid/brow surface-fit to new geometry, with raycast contact constraints and no z-fighting.
4. Historical project preservation and full 18-suite desktop/phone regression.
5. On acceptance, package the separate scene in `build_space.py`, append the patch to the source manifest, re-seal SHA/bytes, synchronize README/Space README/router/roadmap, merge reviewed changes to main, press only the final `DEPLOY_REQUEST.json` trigger, and independently verify served HTML, receipt and every asset.
6. Owner's artistic/likeness acceptance **remains separate** from the technical checks.

### Boundary
This candidate does not implement weighted skinning, UV paint, retopology, animation, or a fully non-primitive **body**. It is one genuine native modeling slice and must not be advertised as a finished game-ready character until multiview geometry and visual acceptance are independently established.
