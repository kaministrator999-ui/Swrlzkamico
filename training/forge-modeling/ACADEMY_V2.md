# §C ⇄ §E Model Atelier Academy v2: hand skeleton, posing, keyframed animation

**Status:** 31 new teacher-authored, source-anchored public practice cases; not independently scored model outputs and not fine-tuned weights. Owner will test hands-on later. Source baseline: §E `main` v11.220 (`0a8382bcadba676ad86e0ad3e80a7d26584cb66e`), Chat last guarded source `d7d44c82412adb3b78afc3d0afa2a052adb9e018`.

## What's new compared with Academy v1
The v1 primer saw a v11.217 hand with organic geometry but **no hand rig**. The canonical engine advanced: `patches/v11_220_hand_skeletal_studio.py` now integrates a **real weighted SkinnedMesh-based hand rig** and a dedicated **Rig · Pose · Animate** panel for freshly opened `floating-hand-glove` models. Teaching must reflect both the new capability and the old limitations; never repeat that *all* §E hand rigs are absent.

### Concrete editors' architecture
- `runtime/model_atelier_skeletal_core_v11_220.js`: `se220CreateHandRig` defines **17 hierarchical bones**: wrist and palm, four sets of MCP/PIP/DIP, and thumb CMC/MCP/IP. It stores `project.modelAtelier.rigging` with `swyrl-hand-skin-v1`, `linear-blend-4`, rest transforms, named bones, digit parameters, pose, timeline, clip duration and looping.
- `se220RigWeights` produces **four skin influences per vertex**. `runtime/model_atelier_rig_studio_v11_220.js` uses `THREE.SkinnedMesh` and `THREE.Skeleton`; posing changes skeletal rotation rather than merely translating unskinned geometry.
- The rig UI exposes joint selection and **Curl/X**, **Twist/Y**, **Spread/Z**, an optional skeleton pivot overlay, **Open / Fist / Point / Pinch** presets, Save/Delete keyframe, time scrubber, Play/Stop, loop, duration and local pose undo.
- `se220RigValidate` enforces schema, ordered parent chain, rest coordinates, bone IDs, non-finite rejection, duration and timeline validity. The UI accepts at most **32** skeletal keys and requires at least **two** for animated playback; studio slider limits and JSON import validation are distinct surfaces.
- Native JSON save/import retains the rig and clip; the v11.220 OBJ pathway transforms vertices to the visible pose, but OBJ is not an armature/keyframe project format. New starter only; existing saved hand projects are **not** silently rigged or migrated.
- v11.220 release source exists; browser/deployed-host/Quest acceptance require their own evidence. A source-level rig is not a proven VR sensor retargeting system.

### Chat authority remains separate
The **Chat native contract still does not include** `rig.pose`, `bone.rotate`, `rig.keyframe.add`, `mesh.sculpt` or WebXR hand tracking actions. Existing Chat native tools are `mesh.add/set/select/duplicate/remove`, plus isolated `editor.undo/redo` and separate `project.create` with a fresh authorized project snapshot. Qwen can explain the native Rig UI and plan a safe source implementation for a future typed Chat bridge, but must not send arbitrary JavaScript, hallucinate operation names, alter stored rig JSON or state a bone was moved without actual host validation/receipts.

## Structured progression for both students
1. **Identify user intent:** question vs current mutation; model geometry vs armature pose vs animation; ask about current project and whether the starter is newly created or an older saved copy.
2. **Explain first principles:** parent-first transforms and rest joints; linear blend four-weight deformation; editable neutral mesh vs runtime posed geometry; thumb joints differ from three-phalange fingers.
3. **Modeling diagnosis:** front/back/side/top silhouettes; improve finger length/taper without pretending bone rotation changes anatomical length; preserve separate purple finger rails and armor/rune meshes.
4. **Pose:** choose an existing named bone, rotate its axes through Rig studio controls, verify skeleton deformation and compare against the unposed silhouette. Do not rename a part as a bone or assume a mesh ID equals a joint ID.
5. **Animate:** create valid poses, scrub time, save two or more keys, interpolate and play with stated clip length/loop; recognize that display of the static pose is not successful playback.
6. **Persistence:** differentiate native project save/JSON import with rig state from OBJ posed-vertex export; keep old saved non-rigged projects untouched until an owner-approved migration exists.
7. **Permission-aware planning:** answer how-to without actions; identify when §E UI already supports the operation, and when §C Chat lacks a native bridge method; never imply approval/receipt from text alone.
8. **Source engineering:** future typed `rig` actions require precise target/epoch/lease validation, host implementation, per-operation user approval, independent tests, history, deterministic §E and §C deployments, and real-device acceptance.

## Practice / later evaluation
`academy_v2_delta.json` adds **M037–M067**, on top of the original 36 cases. They intentionally include difficult counterexamples: older saved hands, unsupported Chat bone rotation, Quest sensor assumptions, exactly one keyframe, invalid rig imports, OBJ skeleton loss, mixed project-create-and-pose, stale object IDs and successful-output hallucinations. They are public open-book teaching drills, **not held-out tests**.

When Kami chooses to test, collect the **actual** 700M/Qwen outputs with source SHA, model revision, genuine native context where authorized, and observed editor receipts. Separate conversation explanations, typed native proposals, approved host executions and physical Quest/Android validation; mark any model failures `REPAIR_REQUIRED`, keep immutable evidence, and only then consider weight/LoRA promotion under the canonical weight-learning pipeline. No automatic device trial, VR capture or model retraining is authorized by this teaching commit.

## Source authority and version caveat
These notes are grounded in the v11.220 source named above, not a promise that the user's active saved project or browser already has a rig. Re-read `source-manifest.json` and the concrete Rig source before editing or when §E advances. Current UI availability never automatically expands `forge_chat_actions.py` action allowlist.
