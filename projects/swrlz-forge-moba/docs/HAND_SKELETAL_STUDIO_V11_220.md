# §E v11.220 — Native hand armature and Rig · Pose · Animate studio

## User request
Add a rigging, posing and animation studio to §E Model Atelier, then properly rig the already-iterated Arcane Glove/Floating Hand. Preserve its visual design, attached finger conduits, and continuously wrapped thumb effect.

## Architecture and actual skeletal implementation
- `runtime/model_atelier_skeletal_core_v11_220.js`: pure skeletal data, rig validation, bind/influence computation, preset poses and timeline interpolation. The rig stores ordered bones, parent links, anatomical rest positions, active joint angles, keyframes and clip settings in `project.modelAtelier.rigging`.
- `runtime/model_atelier_rig_studio_v11_220.js`: native editor integration. When a model carries a validated rig, individual modeled parts are instantiated as THREE.SkinnedMesh, with `skinIndex`/four normalized `skinWeight` attributes per vertex. The existing sculpted geometry, group identity, shader/view settings, and original editable source topology are retained.
- A shared THREE.Skeleton with inverses calculated from the bind pose deforms the connected hand shell and its separate armor/energy/knuckle meshes. Bone rotations change the displayed mesh through skeletal skinning, not merely by translating whole meshes or drawing pretend bones.
- `patches/v11_220_hand_skeletal_studio.py`: append-only glue and v11.220 version identity. This creates the rig **only on fresh Floating Hand starter instantiation**. Existing saved, unrigged models remain unchanged.

## 17-bone hand rig

| Hierarchy | Bones | Purpose |
|---|---:|---|
| Wrist → palm | 2 | Anchored carpal/palm foundation for connected skin and accessories |
| Index, middle, ring, pinky | 12 | Three pivot bones per finger: MCP, PIP, DIP |
| Thumb | 3 | Opposable CMC, MCP, IP pivots on angled thumb axis |
| **Total** | **17** | Named, parented and bind-pose calibrated |

The four fingers use individual base positions, segment lengths and splay from the actual v11.218 glove proportions. Weights are computed spatially from each vertex's rest position; joints blend across boundaries. The thumb has a separate curved two-segment axis and ownership falloff; cuff and palm stay weighted to proximal joints. Four weights are normalized for every vertex.

## Rig · Pose · Animate controls
- The studio handle is positioned below the existing model component toolbar on touch devices to prevent interaction overlap.
- A collapsible, touch-friendly studio panel in Model Atelier appears for projects with a valid rig, replacing the old non-skeletal pose deck *only for those projects*.
- Select any bone and edit rotation along X, Y and Z using mobile-friendly sliders. Show/hide the skeleton helper. Use Open, Fist, Point and Pinch poses.
- Timeline playhead with pose interpolation between user-saved joint keyframes (up to 32), add/replace or delete a key, set loop and clip length, play or stop, undo a rig pose edit.
- A seeded 1.5-second open → fist → open skeletal clip demonstrates motion immediately upon loading.
- Model/project JSON saves and restores `rigging`, including pose and timeline. Imported rig JSON is validated for hierarchy, bone limits and keyframe shapes. OBJ export attempts to apply currently displayed skin deformation where the host THREE API supports it.

## Boundaries and owner acceptance
The studio has a functional implementation for models *carrying a compatible rig* and first ships with the Arcane Glove. It is **not** yet an automatic armature generator for arbitrary imported characters, IK solver, physics-driven ragdoll, motion capture input or GLB animation exporter. There are no new VR control mappings. Older character pose snapshots still work for unrigged models.

Only the new hand starter is rigged by default; existing user-created hand copies are preserved. Final ergonomic, movement and rendering acceptance belongs to the owner on Moto and Quest, using the rapid-deploy → hands-on-feedback loop.

## Integrity receipt
Version: **§wyrl§ Engine v11.220**.
Ordered patches: **252**. Packaged assets: **68**.
Generated editor source: **7,526,079 bytes**.
SHA-256: `7836708947da5ed574608d82c530d3421cedb6c2ac348eec822860c4c3ebe77e`.

Focused JS/Python syntax, 17-bone/skin-weight/interpolation math, assembled source marker and packaging candidate checks passed. Source checks by themselves do not mean hosted runtime/visual acceptance.
