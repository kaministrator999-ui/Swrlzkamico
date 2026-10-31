# §C × §E Design Studio and Interactive Response Capability Contract

**Status:** v1 candidate (source/CI review; not presumed deployed).  
**Owner:** §wyrlz Chat + AI. **Companion:** independent §E native editor / Model Atelier.  
**Source of truth:** §wyrlz_§tart.md, §§§§.md, SWRLZ_HOTFIX_RULES.md, SWRLZ_VERSION_MODULE_EVOLUTION.md, docs/engineering/CHAT_FORGE_EMBEDDING.md, and the native action allowlist in hf_space/forge_chat_actions.py.

## 1. Product outcome

The user should describe a scene, asset, environment or model conversationally. §C should understand the *actual* open §E scene, distinguish intent from authorization, offer a visually inspectable plan, teach the supported modeling operations, and carry an explicitly requested change through native validation and receipts. §C owns human communication, structured response cards, orchestration and reasoning. The editor owns geometry, scene transactions, native undo, project files and actual rendered output.

**North-star flow:** Request → resolve current editor context → interrogate real capabilities → decompose model/scene → show honest preview/steps → review / revise / approve → revalidate → §E native application → confirmed receipt → show outcome + undo path.

Do not conflate a Chat preview with a real mesh, a native receipt with visual acceptance, an avatar screenshot with authoritative geometry, or a user suggestion with a granted edit lease.

## 2. Capability levels and release truth

| Capability | v1 source candidate | Future work required |
|---|---|---|
| Read authenticated current project/scene/model metadata | Existing native integration | Full hierarchies, materials/asset references, mesh topology, dependency graphs |
| Explain actor/mesh counts, distribution and review hints | Existing Workspace Intelligence | Occlusion, contact, clipping and physics observations using actual engine probes |
| Native edits | Existing typed mesh/scene actor allowlist + receipts | Rich tool/brush operators and transactional multi-stage assemblies |
| Natural multi-primitive modeling | Model constrained to validated, independent native operations | Parametric assemblies, true grouping, booleans, curves, sculpt, UVs, rigging, animations |
| Preview before applying | **New v1:** conceptual top/front schematic, scrub steps, fullscreen-in-Chat view | True engine ghost preview and exact persisted approval envelope |
| Approve inside Chat | **New v1:** explicit button submits a *new* human request for re-planning/revalidation | Cryptographically bound frozen plan/snapshot, exact-once approved transaction and signed preview state |
| Native execution truth | Existing receipt-constrained response | Production owner device and visual/model correctness acceptance |
| Native asset export | Current editor's native export paths only where present | Unified artifact/asset versioning + project-file delivery from Chat |

### v1 hard boundary

The new illustrated preview is **not** a rendered Model Atelier mesh and is **not** a frozen-operation grant. The user clicks “Approve · request build in §E”; §C sends a new ordinary Chat request. The server **re-plans from current authoritative context**, validates the result, and the host may reject it. A successful receipt does not establish that the result exactly equals the earlier illustration; users must compare the finished scene. The follow-up plan must not be silently treated as the same immutable proposal.

## 3. Current editor action vocabulary (verified owner)

| Workspace | Native operations | Current limitations |
|---|---|---|
| Model Atelier | mesh.add, mesh.set, mesh.select, mesh.duplicate, mesh.remove | Four addable primitives: box, sphere, cone, cylinder; limited names/transforms/color/material; no generic procedural scripting |
| Scene / Game Editor | sceneactor.add, sceneactor.transform, sceneactor.select, sceneactor.rename | Five advertised prefabs: wall, rock, bush, crystal, pedestal; no arbitrary unvalidated objects |
| Both | project.create, editor.undo, editor.redo (when available) | New project creation must be separate from editor actions; undo/redo single operation; fresh lease after project transition |

The validator currently permits up to 16 operations per plan, finite [x,y,z] coordinates, bounded positions/rotations, positive scales and allowlisted materials. New objects cannot be addressed by IDs within the same proposal that creates them. Names and scene descriptions are data, not instructions.

## 4. User-facing response anatomy

A normal editor response may have these layers, shown only when useful:

1. **Human summary:** precise intent and workspace, in short conversational language.
2. **Live context strip:** project, level, workspace, selection, edit/play mode, sample coverage, freshness.
3. **Status timeline:** reading → planning → preview ready → awaiting user choice → requested → applying → confirmed / partial / rejected.
4. **Visual:** concept drawing, position map, real engine screenshot/render (only when backed by a verified native capture), before/after overlay or object hierarchy.
5. **Build plan:** part names, geometry types, transforms, materials, dependencies, number of operations and budget.
6. **Review checks:** dimensions, symmetry, alignment, clipping, invalid tool requests, scale, potential destructive steps and known uncertainties.
7. **Interactions:** view toggle, scrub steps, expand/collapse, revise draft, copy plan, request build, inspect selection, choose another starter.
8. **Execution receipts:** action count, actual success/failure, project/scene identity, undo availability, independently verified artifact links.
9. **Optional deep evidence:** source/version/operation IDs, method, coverage and explicit “unverified” notes.

Response complexity should scale to the task. A one-box color change should not produce a 12-panel dashboard. A detailed character model may require several iterative design/preflight steps.

## 5. Interactive response vocabulary

### Currently available or actively implemented

- Markdown prose with code/lyrics and copy controls (existing).
- Live stream progress/status separate from answer prose (existing).
- Workspace intelligence card with sampled object counts, type bars, review hints, read-only follow-ups (existing).
- Guided project creation card: blank scene, blank 3D model, advertised starters, name, review and Create click (existing).
- Rich comparison, mathematical graph, 3D model and other typed widgets where their owning implementation is active (existing; not a claim they can render arbitrary imported models).
- **Design Studio v1 card:** conceptual top/front wireframe, numbered placements, construction slider, expanded overlay inside Chat, step details, revision composer, explicit Build-request button (new candidate).
- The Build button *does not invoke the host directly*. It sends an explicit new ordinary user request; a fresh context, native plan, validator and host receipt remain mandatory.
- Existing GitHub work/source widgets and evidence sections remain separate from native editor permissions.

### Proposed, not currently implemented or accepted

- Actual §E engine-rendered **ghost assembly** overlay with semi-transparent material, snapping, dimensions, materials, collision heatmap and bounding boxes.
- Exact approved frozen plan ID tied to verified owner/thread/project/snapshot/lease epoch, revocation, expiry, non-replay and transactional commit.
- Side-by-side before/after mesh overlay; part-level color/material variant picker.
- Object hierarchy explorer with selection/highlight synchronized to native §E.
- Node-less parametric modeling: “add radial copies,” “mirror both limbs,” “extrude these faces,” “bevel these edges,” “subtract holes,” and constraint-based connectors.
- Sculpt-brush action library with stroke paths, falloff, target mesh/topology signatures and undo groups.
- Rigging/weight-paint controls and pose/animation timeline cards.
- Texture paint, UV visualization, material channel previews and lighting preview.
- Multi-asset/scene package and verified downloadable model archive with dependency manifest.
- Model quality review from actual engine geometry (non-manifold detection, normals, UV seams, rig constraints) and native screenshot/renderer probes.
- Live build playback and model-to-scene deployment only after exact editor permissions and receipts.

## 6. Teaching §C to build reliably

**Native-operation literacy:** Learn the §E scene/model vocabulary from the actual current editor catalog. Distinguish world-space x/y/z, radians, scale and material/color constraints. Never invent a mesh kind, ID, function, or hidden tool.

**Shape decomposition:** Translate one user design goal into a small coherent assembly. Example: “stylized turret” → base cylinder, body cylinder, dome sphere, narrow cones. Use descriptive piece names, meaningful scale, bilateral symmetry where wanted, aligned origins, and bounded spatial relationships. Mark it as a primitive blockout.

**Mesh construction curriculum:** primitive blockout → symmetry/instances → transform precision → mesh topology → extrusions/booleans → sculpt detailing → materials/UVs → rigging → animation → scene integration. Each step moves from conceptual instructions to native editable implementation only when §E exposes the corresponding capability.

**Editor semantics:** Separate scene and Model Atelier tool APIs. Preserve existing objects and user work. Select correct native project/level/workspace before operations. Never assume a model edit may mutate Sheep Tag gameplay.

**Safety and accuracy:** Any uncertain target or unsupported operation should receive a concise clarification, not a vaguely similar unsolicited edit. Treat metadata-only overlap findings as hints, not proof of collision or screen overlap. Never claim an organic model, finished animation or polished asset when only primitive shapes were committed.

**Receipts:** Always distinguish PLANNED, PREVIEWED, REQUESTED, APPLIED, PARTIAL, FAILED, SAVED, PUBLISHED and USER-ACCEPTED. Each is a different truth state.

## 7. Interaction and approval semantics

### Current v1 candidate

- Explicit design/preview requests and multi-piece additions produce a WIDGET without FORGE_BATCH_READY or any native batch registration.
- The UI allows view switching, step scrubbing, expanded inspection and editable revision text.
- Pressing Build issues a new user message through the normal Chat submit flow. The editor's current lease/context must be rechecked.
- The model plans again; the server validates all allowed operations and action-intent fences; the native host executes and returns receipts.
- A deleted/hidden/disconnected editor invalidates native authority. A stale screenshot or prior card never grants it.
- The v1 UI must say “conceptual preview / new request,” never “exact plan applied.”

### Required future exact-plan approval

1. Generate the normalized operation plan server-side and validate against a signed scene snapshot digest.
2. Store an encrypted, bounded, expiring proposal under the existing Station/§E owner state (not browser localStorage).
3. Show immutable operation hashes, planned diffs and native ghost preview with clear uncertainty.
4. Let the user choose Approve, Revise or Reject inside Chat; separate approval from mere viewing.
5. On Approve, require the same verified owner, thread, host connection, project, snapshot hash and permissions, with atomic single-use claim.
6. Stage a matching native batch, recheck dimensions/assets and execute once; preserve rollback/undo group.
7. Return matched plan/receipt digest and actually applied geometry from §E; show before/after and post-apply check.
8. On expiry, conflict, changed project or partial error, refuse replay and offer re-preview rather than substituting a different plan.

## 8. Presentation design system

- **Structure:** clear hierarchy, short introductory prose, one primary visual, optional detail sections.
- **Color:** dark-slate/ice-blue visual system with subtle violet accents; warnings and approval are distinct but restrained.
- **Motion:** brief, purposeful transitions; reduced-motion and no-motion modes respected.
- **Sizing:** touch controls at least 42–48px, comfortable text input, no mobile browser focus-zoom traps, bounded expanded overlay, keyboard navigation.
- **Density:** show high-value information first; collapse logs, raw operations and long evidence until requested.
- **Truth states:** “Preview only,” “Awaiting approval,” “Request sent,” “Native confirmed,” “Partial/rejected,” “Device acceptance pending.”
- **Security:** use textContent for object names, no HTML insertion from model data, finite numeric SVG coordinates, bounded array lengths, no eval and no credentials in widgets.

## 9. Example responses

**“Design a small stone watchtower in §E.”**  
§C shows native context, proposes 4–10 boxes/cylinders/cones with named positions/scales, supplies a schematic and a build checklist. The user reviews it and presses Build, or edits the draft. §C does not claim a sculpted tower until native geometry is actually verified.

**“Teach me how to sculpt a dragon head.”**  
§C explains the relevant geometry/topology stages; it checks which current Model Atelier tools exist. If sculpt strokes are unavailable to Chat, it can show a planning guide and a primitive blockout while clearly marking sculpting as unimplemented through the Chat tool contract.

**“Analyze Sheep Tag and tell me where the UI overlaps.”**  
§C may read the actual native actor metadata and inspect potential duplicated positions. It cannot conclude screen-space UI overlap from actor positions alone. That requires rendered DOM/bounding-box evidence and a device viewport probe.

**“Move this model and make it blue.”**  
For one supported native operation, §C can perform the current direct authenticated request and report only a real receipt. A preview can still be explicitly requested.

**“Create a rigged character with blinking eyes.”**  
§C can propose a modeling/rigging sequence; it must not claim rigging, morph targets, paint weights or eyelid animation unless corresponding native tools, tests and engine receipts exist.

## 10. Staged engineering plan

**Stage 1 — Candidate:** preview-only planning, primitive schematic, step slider, expanded overlay, user-initiated follow-up, constrained modeling instructions, explicit starter fix and deterministic regression tests. No changes to §E engine or account backend. Source and CI are not live verification.

**Stage 2 — Exact approval authority:** durable single-use proposals and snapshot-bound confirmation; per-operation before/after diffs; partial rollback/undo and native overlay capture. Requires security review of the existing forge_embed/Station store and real-account integration tests.

**Stage 3 — Native modeling bridge:** §E registers actual supported symmetry/duplicate/group, curves, extrusions, booleans, face/vertex operations, topology and brush actions with schema/version, capabilities and tests. Model Atelier and Game Editor own separate tool families.

**Stage 4 — High-fidelity visual:** native ghost-render overlay, orbit camera, lighting/material previews, pixel-diff/image capture, regression screenshots for Android/Quest/desktop and performance envelopes.

**Stage 5 — Creative workflow:** reusable asset recipes, procedural patterns, rich hierarchy and material cards, multi-stage verified model builds, rigging, animations, asset export, versioned workspace archives and project-scoped teaching.

## 11. Acceptance and regression requirements

- Intent: quoted text, explanation questions, negations, code requests, old chat messages and data names do not authorize native writes.
- Preview: one or many supported operations yields a bounded widget, no native batch registration and no user-data modification.
- UI: correct top/front view; step slider updates diagram; overlay opens/closes on desktop/mobile; keyboard focus works; reduced-motion respected; names rendered as text.
- Build click: explicit, current user gesture only; no silent auto-click; no existing unfinished draft overwritten; no stale host source accepted.
- Execution: native typed validator and session/owner/project/grant boundary stay unchanged; accurate complete/partial/failure receipt handling.
- Preservation: current project/starter copies, Google account identity, Chat history, stream truth firewall, saved settings, and independent §E hosting untouched.
- Testing: Python deterministic native intent/plan tests; browser fixture for widget and click; exact-source HF candidate CI; post-release actual live source; owner Android/Quest visual acceptance.
- Audit: camera events and logs correlate request, widget kind, plan and native receipts without logging bearer tokens or private project content.

## 12. Engineering handoff / source files

**Candidate changes:** 
- hf_space/forge_design_preview_v1.py — truthful schematic payload and preview intent.
- hf_space/forge_chat_actions.py — preview path without native batch; existing live receipt path reused.
- hf_space/brain_forge.py — primitive assembly instructions and hard unsupported-feature boundaries.
- hf_space/forge_project_setup_v1.py — explicit Model Atelier starter outranks generic blank model.
- chat/§wyrlz/index.html — accessible interactive preview surface and explicit Build-request event.
- hf_space/test_forge_chat_actions.py — regression tests.
- tests/test_forge_chat_browser.cjs — two-origin UI acceptance fixture (when extended).

**Do not deploy the engine** for these Chat-only changes. Main's guarded HF Space request is the only terminal production path, after exact-candidate CI and authorized release decisions. Unverified content remains labeled as such.
