# §E v11.343 — Surface-following selector and corrected camera controls

## Motivation
After v11.342 optimized dual-hand hover, Quest 2 hardware testing found that the ring reticle was anchored at the intersection with a model *bounding box*, not the glove surface. The left/right sticks operated in opposite view directions to the owner's expectations.

## Engineering changes
- The existing `Box3` test remains a cheap broadphase. A successful candidate is followed by raycasting against a **simplified but continuous topology** created from the native mesh, with a hard desired budget of 3,600 triangles. It shares live skin/bone transforms; no proxies enter saved model data or normal render draws.
- It uses spatial vertex clustering, per-bone cluster identity to preserve finger separation, and a cache keyed by mesh/geometry version. Proxy geometry is disposed when the source changes or the XR session ends.
- The visible dot and ray distance are now based on the **surface hit**, not the bounding box intersection. The bounding box can remain as a selection outline only; on a proxy miss, no false surface reticle is shown.
- Exact native triangle picking still happens on Trigger and Grip. Native Undo/Redo and model editor ownership remain unchanged.
- Pan X/Y and orbit yaw/pitch signs were reversed to make left-stick pan and right-stick orbit follow the intended camera viewpoint movement. Right-stick click + vertical zoom remains unchanged.

## Verification
The first single-point ring regression failed due to aiming exactly at a geometry seam. The revised test compared rays against the original visible surface at five non-seam ring positions with max difference 0.00349 Three scene units; all five passed. The test separately demonstrated the empty hole does not produce a surface hit, and the skinned proxy follows a translated bone. [Focused test: success](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42450424824). No physical dimensions are assumed from arbitrary Three units.

The candidate source build with 354 patches produced `7f34d4884d8491515789052b4c36a5564cdd298c5901debb9824cfe0b2dee2f6` at 9128756 bytes; packaging and external asset checks are repeated during release verification. Physical Quest 2 FPS and alignment testing remains with the owner.

## Test on Quest
Point one then both controllers at the hand while watching FPS. Move a ray from empty space between fingers across a knuckle and fingertip: the reticle should follow the glove instead of the rectangular bound. Trigger and grip should still select the actual triangle surface. Confirm left-stick pan, right-stick horizontal/vertical orbit, and right-stick press+vertical zoom are no longer reversed.
