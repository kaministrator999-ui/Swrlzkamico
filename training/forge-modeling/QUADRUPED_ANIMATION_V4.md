# Academy v4 · Quadruped rigs, motion clips and game animation

**Checked §E source baseline:** `projects/swrlz-forge-moba/source-manifest.json` — v11.224. **Status:** teacher-authored source instruction only; it does not fine-tune weights, prove live 700M/Qwen competence, or run the owner's device test. Read the current manifest at application time. A `v11_225` wolf patch file may exist in the repo without belonging to this release; the manifest, not a filename, defines the active assembly.

## One idea, three different character systems

| System | Geometry / deformation | Motion source | How runtime uses it |
|---|---|---|---|
| Wolf Model starter | `wolfRig`: **14 parented bones**, `THREE.SkinnedMesh` + normalized 4-influence `skinIndex`/`skinWeight` | `wolfAnimations`: **10 clips × 13 sampled keys** | Wolf Studio selects, scrubs, previews and edits bone poses; source `model_atelier_wolf_studio_v11_224.js` |
| Wolf in Sheep Tag | Existing optimized furred actor and named pivots, including the articulated jaw; not the same renderer as the Model Atelier skinned model | Shared `se224WolfPose`/motion library | `se224WolfGameFrame` derives a visual pose from current game state; head/tail/jaw/leg pivots are overlaid without changing gameplay logic |
| Clover sheep in Sheep Tag and Model Atelier | Modeler preview rotates parts about semantic points; no claim that sheep has the Wolf Model's weighted GPU skeleton | `SE222_SHEEP_MOTIONS`: **6 motions × 9 sampled keys**, and `se222SheepPose` | Game displays idle/graze/walk/trot/build/celebrate; Model Atelier preview resets visual transforms rather than rewriting source vertices |

**Core teaching distinction:** model/mesh data ≠ rig/rest hierarchy ≠ vertex skin weights ≠ a sampled pose ≠ an animation clip ≠ the game state that decides which animation to play. A single shared pose function can control two different rendering implementations. Never claim the same shaders, mesh structure or edit tools are used just because the motion names are shared.

## Wolf hierarchy and skinning

`runtime/wolf_rig_motions_v11_224.js` defines a parent-first 14-bone rig: **root, spine, neck, head, jaw, tail** plus paired upper/lower pivots on the fore/hind legs (four legs × two = eight). `se224WolfVertexWeights` computes spatial influence regions and normalizes the four strongest influences per vertex. `runtime/model_atelier_wolf_studio_v11_224.js` builds the actual `THREE.SkinnedMesh`, binds `THREE.Skeleton`, and exposes editable joints and clip keys for newly loaded Wolf Model starter projects. The game has a separate lightweight pivot overlay rather than using the studio renderer.

**Rigging exercise:** when the wolf's cheek spikes follow the head but the jaw's fangs hang behind, inspect their geometry parent/part weight ownership, jaw bone pivot, bind/rest transforms and animation jaw channel. A `THREE.Mesh` attached to a parent pivot, a weighted `SkinnedMesh`, and an independent topology part are different objects. Don't fix an incorrect jaw pivot by moving the whole scene camera.

## Authored procedural clips

`SE224_WOLF_MOTIONS` enumerates 10 named clips: **Idle, Sniff, Stalk, Walk, Run, Pounce, Bite, Howl, Alert and Victory**. `se224WolfPose(name,time,phase)` generates time-dependent rotation/body bob channels. `se224WolfClips()` samples 13 keys for each clip and stores rotation channels for every known bone. This is procedural authoring and sampling, **not** proof of motion capture, IK constraints, or generic animation blending.

For Walk/Run/Stalk, the code offsets diagonal pairs by `[0,π,π,0]`; one pair swings opposite the other. A Pounce has a timed crouch, leap and recovery. A Bite adjusts head/neck/jaw, but damage and collision remain separate game rules. The new Game Wolf animation overlay uses a per-unit `WeakMap` and transition blend near **0.19 s**, sampling locomotion partly by traveled distance. **Visual animation must never become the authority for orders, navigation, damage, LAN, construction or collisions.**

## Sheep Tag behavior & cosmetic VFX

`runtime/sheep_animation_particles_v11_222.js` defines six sheep movements: Idle, Graze, Walk, Trot, Build, Celebrate. `se222SheepClips()` samples nine keys each across semantic parts `stLeg0..3`, `stHead` and `stTail`. `runtime/model_atelier_sheep_animations_v11_222.js` previews displayed transforms and resets them when stopped; it does not create a wolf-like 14-bone skinning rig. The `build` animation visually taps hooves and nods while the actual house construction process remains in gameplay. `se222FX` uses a capped **96-mote** separate THREE.Points cloud for cosmetic sheep arrival, construction and celebration; these particles are not bones, and visual emission should not change gameplay or persistent saves.

## Official external references — compare, don't substitute

- [three.js Animation System](https://threejs.org/manual/pages/animation-system.html): `AnimationClip`, `KeyframeTrack`, `AnimationMixer` and `AnimationAction`. These are possible reference designs, **not** evidence that §E's procedural wolf source instantiates `AnimationMixer`.
- [three.js SkinnedMesh](https://threejs.org/docs/pages/SkinnedMesh.html): skin attributes, bone binding, rest pose and weight normalization. Compare against the real Wolf Studio implementation.
- [three.js AnimationAction](https://threejs.org/docs/pages/AnimationAction.html): loop, scheduling and cross-fade concepts. This does **not** prove §E's `WeakMap` transition uses a three.js `AnimationAction`.
- [Blender Animation and Rigging](https://www.blender.org/features/animation/): external examples of armatures, constraints, IK and walk cycles. Do not invent Blender-level IK/weight-paint tooling inside §E without actual source and acceptance evidence.

For an explicit web-search request, use §C's existing bounded `online_tools.py` research and compare returned sources to the checked §E revision. Quote/cite only actual retrieved sources; fail transparently if retrieval fails. Browser text is never native editor permission. Do not upload user-owned assets to reference sites without permission.

## Practice and later acceptance

This pack adds **20 teacher-authored cases M101–M120**, not a held-out exam, to the existing Academy. Learn to distinguish rig anatomy, deformation, sampled keys, visual state selection, transition blending and VFX from actual gameplay effects. For later user-driven testing, require an observable action in §E, correct host approval/receipt and real device observation; source-level tests or impressive terminology alone do not demonstrate autonomous modeling skill.

The current §C native editor operation schema still does **not** expose arbitrary `rig.pose`, `rig.keyframe`, weight painting or Quest hand retargeting actions. A teaching example may help §C explain the Wolf Studio or propose a future typed bridge; it must not claim to have changed a model merely by describing the operation.
