# §E v11.223 — Stronger Arcane Glove fist and wrist-driven wave

## Owner feedback
After testing the native Rig · Pose · Animate studio on Moto, the owner asked for a tighter clench and a wave that twists the wrist while moving the hand from side to side, instead of a single sideways static wrist pose.

## Actual native rig changes
- **Fist:** Index through pinky now close at individualized MCP angles of 1.06–1.14 radians, PIP at 1.42–1.49, and DIP at .87–.92. The opposable thumb's CMC rotates [.37,1.18,-.48], MCP [.34,.19,.20] and IP [.25,.03,.28] to tuck more firmly across the fingers. The underlying glove topology and helix are unchanged.
- **Wave static pose:** The wrist bends in X, twists about Y, and rolls about Z; palm adds secondary rotation. Finger splay is maintained.
- **Wave playback:** Selecting **Wave / spread** then **Animate Selected Gesture** creates eight native keyframes at 0, .24, .54, .86, 1.18, 1.50, 1.84, and 2.20 seconds. The wrist's Y twist and Z roll alternate sign to swing the whole hand back and forth from the pivot; the palm follows, with subtle independent finger flutter and thumb motion. The clip returns to an open neutral pose and supports loop/scrub/play/save/export through the preexisting keyframe protocol.
- Non-wave animated gesture previews retain their preexisting 1.5-second three-key form. Existing owner-authored animation clips are not rewritten.
- Implemented as new append-only `runtime/model_atelier_hand_motion_v11_223.js` and `patches/v11_223_fist_clench_wrist_wave.py`. The v11.221 and v11.222 historical sources stay unchanged.
- No changes to Sheep Tag, sheep effects, §C, VR inputs, meshes, saved model geometry or general editor architecture.

## Source evidence
Release: **§wyrl§ Engine v11.223**, 255 ordered patches, 68 packaged assets.
Generated HTML: **7,551,989 bytes**; SHA-256 `db352ebd9c49735b4ec5df884ce2f855d412a995138e7bb987bdeb808c296b4e`.
Focused native joint checks passed: all four digits achieve stronger independent flexion, thumb opposition/flex is stronger, wave contains eight valid keys with alternating wrist yaw/roll and finger flutter; exact generated source markers and route parity passed. Phone and Quest motion quality remain subject to owner acceptance.
