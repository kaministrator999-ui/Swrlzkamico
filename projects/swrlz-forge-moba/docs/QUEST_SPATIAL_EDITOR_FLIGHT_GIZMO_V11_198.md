# §E v11.198 — Quest spatial editor flight, grasp, gizmos and control legend

## Owner observation
VR editor flight feels slow and awkward, object grabbing cannot reliably pull a mesh **toward the controller/headset** in depth, the colorful translation gizmos cannot be selected directly by laser, and button mapping is difficult to recall. Quest screenshots also show large controller markers, bright rays and visual helpers overlapping the wrist menus.

## Native implementation
- **Fast, smooth wisp flight:** left stick remains head-relative horizontal translation; movement has velocity-based acceleration/braking and speeds 1.5/3.2/6.4/12.8 world units/s selectable from EDITOR > FLIGHT. Hold **left thumbstick click** to boost ×2.6. Hold **left grip** and use **right stick Y** for climb/descent. Right stick X keeps familiar comfort snap turns, with 15/20/30/45-degree adjustment. Preferences persist only on the current device, independent of cloud project data.
- **Stable camera translation:** the editor reuses the single stable WebXR reference-space base already deployed for Sheep Tag. After snap-turn the reference base is reset before translating again; repeated flight no longer nests transformations per rendered frame.
- **Direct 6DoF grip:** hold **right grip** on a selected/hit native actor. The object's world transform follows actual physical controller-position delta in X, Y, and Z; pulling your controller toward you pulls the object closer. It preserves initial offset, applies modest smoothing, commits the final exact target on grip release and saves a single native history transaction only for actual moves. Parent groups use existing world-to-local transforms.
- **Real ray-selected gizmos:** select a native actor, then point the controller's ray at the red X, green Y or blue Z handle. Hold **right trigger** to move on that axis; releasing ends the drag and commits native undo history. Separate slightly oversized hit targets improve Quest selection without changing authored actor geometry.
- **In-headset key legend:** EDITOR > LEGEND displays VR button mappings in a readable spatial panel; the same editor wrist radial offers FLIGHT, GIZMOS, PREFABS, SELECT and CAPTURE (under GIZMOS or LEGEND) while existing game/menu radials remain untouched.
- **Presentation fixes:** reduce the visual controller grip model to 55% of its previous size, reduce ray halo and spark opacity, and suppress known legacy transform-gizmo helper roots in VR (restoring their prior visibility on exit). Modal radial takes precedence over gizmo/actor picking, and editor gizmos/legend are hidden during clean screenshots.
- **Session safety:** release event closes trigger-axis drags; exiting VR finalizes active transactions, removes temporary meshes/textures and input listeners, restores native gizmo helpers, and clears locomotion velocity.

## Hardware acceptance checklist
Tests cover controller world-motion including pulling Z toward viewer, axis projection math and parallel-ray guard, speed boost, pause/Play/menu isolation, undo and settings persistence, source integrity, existing Sheep Tag and Model Atelier boundaries. The owner must test smoothness, actual grip alignment, button placement, stereo geometry occlusion, legend readability, and high-speed comfort on the physical Quest 2.

## Strict source receipt
§wyrl§ Engine v11.198, 230 ordered patches, 68 original packaged assets, built HTML 7,320,589 bytes, SHA-256 `c5e42de3a9c6dca98d72843b70c4cb2eb549c22589aae4a7fb0d4f7e8ba00f0f`. Original project JSON, §C Chat and native non-VR editor remain independently saved. Release via verified source merge followed by a separate exact-SHA deploy-request commit.
