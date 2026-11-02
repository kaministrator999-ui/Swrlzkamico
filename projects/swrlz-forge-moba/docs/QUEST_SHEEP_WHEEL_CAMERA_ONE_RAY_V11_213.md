# §E v11.213 — Sheep Tag Quest game-camera / quick-wheel conflict

## Observed on actual Quest 2
When opening the in-game quick-building radial in Sheep Tag Play: the sheep and camera continue moving while the radial stays at a fixed world position; looking around produces world drift/snaps and lag; another raycast/controller beam appears concurrently with the building ray.

## Verified source causes
- v11.204 `se204WheelPosition()` computes root position only at wheel creation/show, using the current headset pitch and `root.lookAt(pose.eye)` while the v11.200 follow camera continues translating the XR reference-space offset in response to sheep position and stick input.
- v11.199/v11.200 sheep locomotion uses the LEFT stick during the thumbstick wheel. v11.204 only suppresses the RIGHT camera stick while the modal wheel is open.
- v11.203's world-ground virtual building guide only checks `stUi.build` and the legacy full tools radial. It does not check the v11.204 A/X wheel. The later render adapter can re-create an additional world-space beam **behind** the game modal; v11.195 also creates a separate full-length controller aura/particles around the calibrated v11.192 beam.

## Corrective design
- The **in-app A/X quick selector** is a modal thumbstick UI, not a 3D object editing interface. Update its position every XR frame, 1.08 m ahead of the horizontal headset heading and slightly below eye height. Build its facing quaternion from a world-up, yaw-only lookAt; **never** inherit headset pitch/roll for menu layout. When looking straight down, retain the last valid horizontal heading.
- Hold the sheep movement and the game-generated XR camera *world-reference translation* only while the A/X wheel is open. On selection/release restore original gameplay; no game tick, LAN authority, fog or native HMD tracking suspension.
- Make the quick wheel the **sole pointer owner**: its selections use the right thumbstick, so the legacy v11.203 ground ray and native calibrated controller beams + aura + ground reticles are hidden only for the wheel. While regular Play resumes, restore the original one-pointer model; keep the decorative controller aura disabled across gameplay to eliminate a second beam.
- Do not interfere with full §E world-pinned SESSION panels (v11.207/210), Editor model/object rotation, the Model Atelier hand starter, or Meta OS Camera compositor guards (v11.211).

## Quest 2 acceptance
1. Enter Sheep Tag Play. Confirm regular sheep follow, build aiming and no duplicated hand/controller beam.
2. Hold **right A** to open Houses. Move your head physically (yaw, pitch, roll) normally; the menu should stay front-of-view and upright, not stick in the world or drag the gameplay camera in a spring-like chase.
3. Try the **left joystick while holding A**: the sheep should temporarily stay put. The right stick still chooses the selected house; release A equips, then tap A builds repeatedly.
4. Repeat with **left X** skills. Confirm no unexpected casts or accidental actions while choosing.
5. Close the quick wheel and confirm sheep locomotion and camera follow resume, and the regular single forward building guide is back when a house is equipped.
6. Open Meta's separate OS Camera menu to confirm the previous v11.211 focus safeguards still behave.

## Limit
WebXR always preserves real physical headset tracking. The app must not forcibly zero native HMD roll/pitch; this fix stabilizes the world camera **movement authored by §E**, not the person's actual head orientation. Physical GPU frame time/Quest compositor health can only be evaluated on-device.
