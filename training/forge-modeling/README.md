# §C ⇄ §E Model Atelier Academy · v1→v2

> **Latest §E modeling curriculum (Nov 2, 2026):** [Academy v2 — skeletal hand, posing and animation](ACADEMY_V2.md) adds [31 source-anchored cases](academy_v2_delta.json), M037–M067, [bounded reference v2](model_context_v2.txt), and [rigging, animation & web research lessons](RIGGING_ANIMATION_RESEARCH_V2.md), grounded in §E **v11.220**. Offline source validation: [verify_academy_v2.py](verify_academy_v2.py). The original v1 text below describes the older v11.217 baseline; its statement that rigging is not available refers only to that earlier release. §E now has rig controls for newly created glove starters, but §C still has no native Chat rig/keyframe operation. The first source-grounded §C prompt teaching was deployed in the prior Chat release; v2 source lessons remain subject to their own integration/release. **Neither curriculum is weight fine-tuning nor proof of model competence.**


**State of original v1 data:** SOURCE-GROUNDED TEACHER MATERIAL — **NOT MODEL-WEIGHT-TRAINED**. A bounded v1 instruction lesson has since been published in the Chat runtime; the v2 additions are separate. The machine-readable practice set is open-book and has not been scored against either live model. Do not promote it as independently evaluated training labels.

**Scope:** Teach §C's 700M conversation student and Qwen coder/planner student to understand the current §E Model Atelier, reason about geometry/edit tasks, propose only existing approved native operations, design future modeling capabilities, and distinguish proposals from actual host receipts.

**Repository boundary:** `kaministrator999-ui/Swrlzkamico`, separate Chat runtime and engine runtime. Engine source authority is `main:projects/swrlz-forge-moba/source-manifest.json`, paired with ordered patches and `build_space.py`; the baseline inspected for this teaching pack is §E v11.217. Do not assume the branch-tip stays current. Re-read before any production patch.

## 1. Two different students, one grounded source

**700M conversation student:** correctly parse a modeling instruction versus a question, quotation, negation, approval, or future design idea; keep task context and user intent. Explain the editor with correct nomenclature. Never say an operation completed unless a real native host receipt is available.

**Qwen coder/planner student:** inspect actual editor interfaces and versioned sources, map the task to real data owners, produce bounded typed native proposals where supported, and for unsupported capabilities prepare a **reviewable engineering plan** rather than fictional APIs or injected JavaScript.

**Independent evaluator:** measure outputs with a separate model/run and concrete validators. Teacher-authored answers and self-assessment are *not* evidence of model competence, LoRA success, deployed prompt activation, or real-device success. The canonical weight-learning pipeline governs anything promoted into 700M weights.

## 2. Native §E modeling map (learn exact owners)

| Capability | Actual source | Technical fact |
|---|---|---|
| Part/project model | `runtime/model_atelier.js` | Editable model lives at `project.modelAtelier`, with `parts` and `swyrl-model-atelier-v1` imports; individual `part` records carry kind, material, color and transforms |
| Basic mesh geometry | `runtime/model_atelier.js` | Native primitive kinds include sphere, box, cone and cylinder; full project data is different from the triangulated OBJ export |
| History | `runtime/model_atelier.js` | `checkpoint()` records reversible snapshots before native edit, then `signalEdited()`; do not invent an independent history owner |
| Groups | `runtime/model_atelier_mesh_groups_v11_74.js` | `meshGroups` are flat non-destructive assemblies; group/child selection differs; 2–32 members, up to 96 groups in this owner |
| Component editing | `runtime/model_atelier_components_v11_75.js` | Mesh/vertex/edge/face modes; commits become sparse `sculptVertexEdits`; enabled refinement layers can block base component editing |
| Numeric vertex edits | `runtime/model_atelier_numeric_gizmos_v11_23.js` | Local/world/surface modes; per-component translations limited to ±0.5, rotation ±180°, scaling 0.1–3 for selected vertices; native validation remains binding |
| Sculpt operators | `runtime/model_atelier_brush_ops_v11_27.js` | Neighbor/falloff-driven operations are geometry tools; hovering/preview and committed edits are distinct |
| Floating Hand | `runtime/model_atelier_floating_hand_v11_212.js`, `runtime/model_atelier_hand_proportions_v11_217.js` | Indexed organic surface shell, separate armor/runes; newer proportions differ by finger, taper and ulnar silhouette. It is not proof of UV skinning/rigged animation |
| Packaging and publishing | `build_space.py`, `source-manifest.json`, `RELEASE_PROCESS.md` | Ordered patch rebuild + exact SHA/bytes; source changes do not become hosted engine automatically |

These are **editor capabilities**, not an assertion that the Chat bridge exposes them all.

## 3. Current §C native action surface (hard boundary)

The Chat ⇄ Forge contract `docs/engineering/CHAT_FORGE_EMBEDDING.md` allows, within an authenticated, visible, leased host bound to the current thread/project/generation:

- **Model Atelier:** `mesh.add`, `mesh.set`, `mesh.select`, `mesh.duplicate`, `mesh.remove`.
- **Native history:** `editor.undo` and `editor.redo`, isolated in their own batch.
- **Project creation:** `project.create` only with a current advertised starter ID and explicit name; it must be its own single-operation batch. Newly opened projects require fresh context/lease before further edits.
- **Game/editor scene actor** operations have their own type namespace; don't substitute scene actor mutation for Model Atelier mesh editing.

The bound contract caps native batches at 16, uses original snapshot IDs and validated primitive/material/color/transform limits, and denies stale/missing host authority. Grouping, arbitrary sculpt vertex writes, UV authoring, rigging, skeletal animation, WebXR hand-pose recording, file-system writes, dynamic JavaScript and engine deployment are **NOT** native Chat action names in the present allowlist. They may have editor UI implementations or require future code; the model must distinguish that.

A proposed edit ≠ an approved edit ≠ a host-executed edit ≠ an observed/persisted project revision. Use the native host receipt, not model prose, to report mutation success. Do not infer current 3D IDs/positions from screenshots or stale chat messages.

## 4. Teaching sequence

1. **Intent and context:** ask-vs-act, quoted/destructive text, reference sheets versus real geometry, current project, selection and workspace.
2. **Model representation:** `project.modelAtelier.parts`, native JSON, primitives, materials, transforms, groups and metadata.
3. **Visual anatomy:** front/back/side/top silhouette, finger segmentation/taper/splay, thumb saddle/web, palm and ulnar hypothenar; preserve independent armor components.
4. **Editing mechanics:** selection, gizmo X/Y/Z, group/child behavior, sparse vertex/edge/face edits, brush radius/falloff, preview, checkpoint/Undo/Redo, model validation.
5. **Model asset pipeline:** mesh topology vs textures/UV islands vs skeleton/weights vs animation; these are separate stages, especially for the v11.217 Floating Hand. Do not claim Quest hand tracking automatically rigs existing topology.
6. **Native Chat planning:** route existing `mesh.*` operations with exact current IDs and approval/receipt, or explicitly classify unsupported current native action.
7. **Source engineering:** engine patch + source-manifest + deterministic build + focused evidence + distinct protected release; separate §C from §E.
8. **Correction loop:** reproduce actual UI/code failures, inspect source and native receipts, make the minimum safe correction, record evidence; never rewrite historical failure into success.

## 5. Example distinctions the students must pass

- “**Explain** deleting a glove part” is a teaching request, not `mesh.remove`.
- “**Move** the selected wrist” without an active editor selection needs fresh context; no ID invention.
- “**Group** these three armor meshes” is currently an *editor UI workflow*, not a `mesh.group` Chat tool.
- “**Sculpt** the pinky-side bulge” means geometry/anatomy work, not resizing the whole model to hide a mismatch.
- “**Rig and animate** the Floating Hand” is a future skeletal/weight/pose integration task, not something v11.217 automatically finished.
- “**Save to Google**” is distinct from a local browser project save.
- “**Make it live**” requires the §E dedicated guarded release—not a Chat HF Space publish.

## 6. Practice, scoring and promotion

`academy_v1.json` contains **36** public examples with requested behavior, routing decision, evidence path/anchor, positive invariants and a concrete failure trap. Use it for open-book prompting, targeted conversation and coding rehearsal. Keep a **separate hidden held-out set** for genuine evaluation; don't contaminate it by training on these public prompts. The Python `verify_academy.py` script checks only the data structure, routing categories and source evidence anchors on the checked-out repository. A static corpus PASS is **not** a model PASS.

When making real training examples, recover the exact original model output, evaluator fixture, corrected independently validated response, revision and provenance. Stage separately for 700M and coder; independently evaluate both. Do not run LoRA, alter runtime model routes, or imply enhanced deployed behavior merely because these lessons are committed.

## 7. Immediate integration plan (not yet performed)

- Feed **only the relevant compact lesson** into §C's existing Brain-controlled bounded context after intent classification; never stuff the entire curriculum into every turn.
- Teach the planner to output typed native **proposals** without bypassing `forge_embed.py` host leases or changing the current allowlist.
- Probe each student using these 36 examples, record actual outputs and run independent scoring; keep failures append-only.
- Promote verified samples through the existing student/teacher/evaluator and weight-learning pipeline. Test real Model Atelier on phone and Quest separately.

**No new production inference route, live prompt injection, model weight update, §E runtime patch, or HF deployment is part of this v1 corpus commit.**
