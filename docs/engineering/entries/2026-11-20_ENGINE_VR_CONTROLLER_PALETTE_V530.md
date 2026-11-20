# v11.530 — immersive controller-follow tool palette and continuous gizmo motion

Scope: immersive WebXR Model Studio only. The owner reports that Trigger-grabbed
model gizmos move briefly, then stop, and that Sculpt → Push third-level
settings look misorganized. When the headset moves away from the original
world-anchored menu, the canvas surfaces become difficult to read.

## Source changes
- The native Trigger move/rotate/scale transaction remains the only authority.
  The ray solver now accumulates continuous world delta; X/Y/Z constrained
  translation remains constrained, while the preexisting selected-model direct
  Trigger gesture may translate freely. Near-parallel intersections use tracked
  grip motion without teleporting the model.
- The same three-stage menu follows the **left controller** at a local forward
  offset and faces the headset. Its existing hit targets, pages, tool choices,
  account project dialog and primary/secondary/tertiary hierarchy remain.
- Sculpt preserves the existing unified Push/Pull operation with signed
  inward/outward Direction. Its selected operation's third panel displays
  a compact operation/direction label and preserves native Direction,
  Falloff, Radius and Strength controls.

## Quest acceptance checklist
1. Select model, choose Move and Trigger-grab each X/Y/Z handle. Hold the
   trigger and drag continuously across a long stroke; release commits once.
2. In Grab or Move, Trigger-drag the already selected mesh (no axis), including
   left/right/up/down. No freeze, jump, or accidental re-selection.
3. Rotate/Scale handles with continuous ray motion. B cancels without history.
   Grip-based free Grab remains available.
4. Move and rotate the left hand at different headset distances: all three
   menu tiers follow at an accessible distance; right-hand ray hit-tests align.
5. Sculpt → Push/Pull opens the focused third-level inspector. Toggle
   Push In/Pull Out Direction, Falloff, and Radius/Strength +/- successfully;
   no invisible cards intercept ray hits. Menu button toggles when exposed by WebXR; X remains
   fallback if reserved by Meta Quest Browser.

This file is a candidate specification until the generated HTML SHA, tests,
Hugging Face delivery and user headset acceptance are independently verified.
