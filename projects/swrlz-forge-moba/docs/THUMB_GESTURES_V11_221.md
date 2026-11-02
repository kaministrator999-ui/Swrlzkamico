# §E v11.221 — Opposable thumb and gesture animation

## Owner's phone feedback
The user tested v11.220 in the Model Atelier Rig · Pose · Animate studio, showing a full fist, a mid-clip curling hand and the reopened hand. The four long fingers deform visibly; the thumb still moved too much like a sideways hinge and the four buttons provided too few gestures.

## Improvement shipped in this version
**Thumb articulation:** keep the existing 17-bone hand rig and source glove mesh, but use three independent thumb joints for realistic-looking *opposition* (CMC rotates the thumb across the palm), proximal flexion (MCP) and distal flexion (IP). Redistribute the thumb's four-influence skin ownership around its curved three-stage axis so the purple two-turn helix, retention hardware and fingertip follow the thumb as a whole without tearing the palm's saddle attachment.

**New 14-gesture pose library:** Open, Relaxed, Fist, Point, Precision Pinch, OK, Thumbs Up, Peace / V, Rock Horns, I Love You, Shaka / Call Me, Wave / Spread, Grasp, Finger Gun. The pinch has separate thumb and index poses calibrated in the actual glove bind coordinates. The other gestures differ in individual finger curl, finger spread and thumb opposition, not by merely renaming the same preset.

**Native rig studio authoring:** add a compact gesture picker, an Animate Selected Gesture button producing a 1.5s open → gesture → open three-key timeline, a CMC Opposition slider and a separate Thumb Flex/Tip Curl slider. The existing Open/Fist/Point/Pinch quick actions and bone XYZ sliders remain. Manual adjustment returns the gesture selector to Custom Pose. Animation interpolation uses a smooth easing curve without overshoot.

## Scope and persistence
This is an append-only update under `projects/swrlz-forge-moba`:
- `runtime/model_atelier_hand_gestures_v11_221.js` — gesture targets and thumb surface weight projection.
- `runtime/model_atelier_gesture_studio_v11_221.js` — native phone-friendly controls and gesture clip creation.
- `patches/v11_221_thumb_opposition_gestures.py` — scoped modeler code integration.
- Existing named bone hierarchy, existing project and clip JSON structure, native skinning, other model starters, VR controllers, Sheep Tag and §C are unchanged.
- Existing stored rigged models retain their authored poses and keys, but the new skin weighting and gesture options are available when viewed in the updated engine. Unrigged stored models are not silently converted.
- This is an authored gesture library, **not** a physical IK solver or full motion capture interface. The owner remains the authority on visual hand gestures on phone and Quest.

## Source receipt and testing
Version **§wyrl§ Engine v11.221**, **253** ordered source patches, **68** assets.
Generated HTML **7,535,801 bytes**; SHA-256 `1f7f32229504110c2d6d758bf3cadf3c0f048630ad8a79ffdbffc4bac8431f90`.
Narrow candidate JS/Python syntax check, fourteen unique skeletal poses, index-thumb fingertip near-contact, raised-thumb orientation, capsule weight anchoring and source packaging passed. A single mobile-width interaction check and actual owner's phone visual acceptance are distinct gates.
