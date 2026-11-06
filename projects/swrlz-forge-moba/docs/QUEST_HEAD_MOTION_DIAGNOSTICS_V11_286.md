# Sheep Tag Quest 2 head-motion diagnostics · v11.286

Scope: **immersive Sheep Tag gameplay only**, using the already-existing Quest controller Nerd Stats panel. The headset rendering and WebXR tracking pipelines are unchanged.

## Using it on Quest
1. Enter Sheep Tag **Play** mode in VR.
2. Press the **left thumbstick (L3)** to open existing Nerd Stats; use its center to cycle to pages **5/6** and **6/6**.
3. Stand still without moving the controller or sheep for a few seconds, then turn your head horizontally/vertically for a few seconds. Repeat while gameplay is running with more buildings and with/without the radial menu.
4. Compare **MOVING (M)** versus **STILL (S)** in the stats. If the headset view lags, note whether the >35 ms callback gap counter increases predominantly during motion.

## What is measured
- The direction change between successive **existing** headset pose reads (degrees per frame); translation measured in centimeters after subtracting §E's accumulated gameplay camera-rig offset.
- Frame callback gaps (not GPU execution time), count of gaps over 35ms, and approximate previous-render draw calls per classified frame.
- Existing head-pose reads and gameplay raycast counts per classified frame; camera reference-space moves, spatial panel placements, and HUD CanvasTexture repaint counts by category.
- Classification thresholds: **0.18 degrees** angular change or **0.8 cm** position change between sampled frames. Slow movements below both thresholds are classified as still. The angle uses the view direction and does not separately measure head roll.
- Counts are **correlated observations**, not proof that head movement *causes* any particular engine event. Headset compositor, GPU timings, and device thermal throttling are not measured.
- Full counters are available to diagnostics through `window.SWYRL_ENGINE_QUEST_HEAD_MOTION_286.diagnose()`.

## Interpretation
If callback gaps increase mainly during head turns while game-state work stays roughly constant, test view-dependent rendering, visibility/culling and GPU fragment workload next. If pose reads, reference-space writes, rays or UI updates rise sharply during motion, inspect those specific handlers. Controlled Quest 2 testing remains required.

The stats remain visible with the existing left-controller panel. Existing four pages, map simulation, controller mappings, network authority, scene assets, and rendering fidelity are preserved.
