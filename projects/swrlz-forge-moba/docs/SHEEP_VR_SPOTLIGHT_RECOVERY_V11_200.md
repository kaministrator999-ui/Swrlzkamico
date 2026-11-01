# §E v11.200 — stabilized overhead Sheep Tag Quest follow camera

## Verified source diagnosis
v11.199 continuously compared the desired third-person position against `se191XRHeadPose().eye` and called `se195MoveRig` during play. In immersive XR the eye position is itself transformed by both physical headset tracking and reference-space writes, so repeatedly chasing it can cause oscillation and discomfort. Its left-stick path updated `unit.destination` each game tick, keeping the expensive route-solving path active as building obstacles accumulate.

## Change
- A sheep-anchored elevated camera anchor (horizontal 14, vertical 26, zoom default 1.4) gives a ~62° downward third-person vantage, with the sheep mathematically centered on the ground below the camera. It is not left or right offset. Physical headset yaw/pitch remain user-controlled. This does **not** rotate a person's tracked head.
- One initial reference-space camera placement. Subsequent frames translate by the smoothed change in the computed sheep/zoom/orbit **anchor**, never by changing live HMD eye coordinates. Idle head motions do not write reference-space updates.
- Left thumbstick directly moves the controlled sheep using current native collision geometry and short swept checks, with wall sliding and analog speed, no repetitive A* destination or pathfinding while held. The authoritative game clock keeps animation, rescue and capture intact.
- Existing VR radial, photo mode, building placements, natural head movement, right-stick orbit/zoom, editor fly mode and non-VR client paths are preserved.

## Checks
`node projects/swrlz-forge-moba/tests/test_v11_200_sheep_spotlight.cjs` asserts centered projected anchor, first snap, no idle physical-head feedback, wall collisions, no A* calls with 18 houses, and normal-mode bypass. Strict 232-patch integrity and prior VR regressions run in GitHub Actions. Device validation on Quest 2 is still necessary for comfort, especially if a more camera-like downward orientation is desired.
