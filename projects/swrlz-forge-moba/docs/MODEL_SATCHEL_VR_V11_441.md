# §E Apprentice Satchel VR workshop — v11.441

Implementation and bounded native verification, 2026-11-13. This update follows the published v11.440 modeling corrections, including native outline thickening, current controller/menu poses and touch-border selection. `AGENTS.md` and `RELEASE_PROCESS.md` govern delivery. The local native and emulated-controller lesson checks passed; hosted publication is recorded below. Controller emulation does not establish physical Quest acceptance.

## What changes

A new independent Apprentice Satchel lesson starts with **one ordinary solid cube**, named `Satchel body · practice cube`, at useful bag proportions `[1.4, 1, .65]`. It contains no prebuilt cavity or separate floor/wall boxes. The learner uses existing native modeling tools to form the opening, separate flap, strap and clasp. Native project creation, topology, Preview/Apply/Cancel, Undo, checkpoint confirmation and Save remain the owning implementations.

The earlier immersive instructions asked for independently sized thin boxes, while the exposed VR creation/Grab controls resize uniformly. The new VR path uses Draw outline and Thicken outline for its flat components, followed by Grab for fitting. Flat-editor instructions still permit numeric thin-box sizing and segmented straps. Both paths retain the same seven objective indexes and existing progress storage.

| Objective | Actual learner operation | Verification and visual review |
| --- | --- | --- |
| 0. Meet your one-cube body | Trigger selects; Grab + Grip moves/turns; right stick with Grip changes overall size; Y undoes | Useful body proportions; the cube is still solid |
| 1. Inset and hollow the same body | Mesh tools → Manual modeling → Make editable; Trigger top; Inset `.20` → Preview → Apply; retain inner faces; Extrude `−.75` → Preview → Apply | One connected inset rim, inner walls and recessed floor; inspect the opening from above |
| 2. Make a separate pointed flap | Front view; Draw a wide pointed outline in open space; release; Thicken outline with a short Grip pull/release; select Grab and fit it to the upper front | Separate closed thin geometry overlapping the upper front; inspect rim/hinge contact from the side |
| 3. Make a strap with an empty middle | Trace the OUTER U, return along the INNER U and close a band; release; add Grip thickness; choose Grab and fit both ends at the sides | Closed elevated strap with two side endpoints and empty central space; inspect attachment depth and joins |
| 4. Fit a small clasp | Create a small Sphere, or draw/thicken a small diamond; Grab it onto the flap front | Actual separate clasp geometry; Metal is not required at this stage |
| 5. Finish leather and metal | Select the actual body and flap separately for Leather; select the clasp for Metal; optional Shade | Sphere-clasp bounds match the native radius-1 primitive; material checks apply to the detected body/flap/clasp; unrelated metal does not complete the clasp |
| 6. Inspect, save and reopen | Check top/front/sides/back; Projects → Save project; reopen My Projects and confirm editing | Geometry cannot establish saving; the final objective requires the learner's review and completion mark |

The Extrude suggestion `−.75` applies only while the active lesson is on its cavity objective and remains visible/editable in the real tool. SHOW does not convert, extrude or Apply geometry. The learner retains the inner faces selected by Inset rather than selecting the whole flat region again. The depth is in the native mesh's local coordinates, not a direct measurement of the scaled bag's world depth.

A drawing plane is fixed in front of the controller when a native stroke begins; the ghost is not a tracing surface. The lesson therefore teaches drawing in open space and fitting afterward. Choosing Grab after thickness is explicit. New outlines receive contextual default names `Satchel flap`, `Satchel strap` and `Satchel clasp`; existing names and geometry are preserved.

## Guidance and geometry checks

`runtime/model_satchel_lesson_v11_441.js` supplies the seven objectives, short VR tasks/hints, native tool navigation and reference ghosts. SHOW routes to the actual current Convert, face-pick, Preview or Apply control during the cavity step. Once a real cavity exists, it frames the work for inspection instead of requesting another extrusion. Material SHOW opens the existing quest Materials row and leaves the actual part selection to the learner.

The first VR hint explicitly teaches gripping the quest window to move it aside before selecting geometry. This retains an independent world-space window.

Each construction objective has one noneditable reference example: body cube, connected cavity, pointed flap, one U strip or sphere clasp. Ghosts have no ray interaction and are excluded from editable parts, history and saving. The Academy obtains its scene root through the existing native API; toggling or rebuilding a guide does not rely on a free scene variable. The references demonstrate silhouette/fit. They do not generate the learner's model.

`runtime/model_satchel_workflow_v11_441.js` runs on explicit Verify and reads native descriptors/indexed topology. It does not select parts, invoke editor tools, change geometry, commit history or save. It returns body/flap/strap/clasp/material check results, detected IDs and bounds, plus `visualReviewRequired: true`.

- A body must pass the existing connected-cavity recognizer; a plain cube or an explicit body ID cannot bypass that check. The new lesson's persisted `one-body-v1` method tag rejects a legacy floor-and-walls body.
- A drawn flap and strap must have valid closed topology and nonzero volume. A body cannot count as a separate strap. The U-band check requires both side endpoints, elevation and an empty middle; a filled rectangular plate fails.
- Fit is checked in the body's local basis, so common translation, rotation and uniform scaling preserve recognition. Bounds/tolerances guide placement; they do not establish a flush physical seam or artistic quality.
- Materials follow geometry. The checker interprets colored `matte`/`silk` descriptors as the supported leather-like finish and `metal` on the detected clasp as hardware; it does not infer a material from an unrelated object.
- Already-saved five-piece body/box-flap/three-section-strap projects remain recognized by the compatibility path. New lessons teach one connected body; compatible segmented straps and flat-editor thin flaps remain usable.
- Duplicate IDs, malformed topology, open unthickened components, detached pieces and budget overruns do not pass. Parts with sculpt/deformation layers are listed for manual rendered-geometry review rather than approved from their base mesh.

Inspection is bounded to 400 parts, 9,000 vertices/16,000 triangles per topology part, and 48,000 vertices/80,000 triangles in aggregate. Exceeding the budget requests manual review without editing the project. Assembly transforms and posed/deformed render geometry are not reconstructed by this checker. Optional sculpting, seam detail, rigging and export are later extensions, not hidden beginner prerequisites.

The integration patch `patches/v11_441_satchel_vr_workflow.py` also filters hidden quest controls out of controller ray targets. Guide and Materials share a physical row; an invisible guide button must not intercept a visible material control. Trigger and Grip also use the same menu-contact authority as hover, so the quest can be moved even when its plane overlaps nearer model geometry. The controller diagnostic measured the body hit at 0.62247 m and the visible quest target at 0.85268 m: choosing the nearer body prevented quest drag. The first hint now teaches moving the window aside. The fix preserves the original world-space quest/tool windows and native modeling transactions.

## Research basis and access limits

The original research handoff is `/workspace/scratch/model439-satchel-plan.md`; its provisional v11.439 feature names were later moved to v11.441 to preserve the owner's separate v11.438/v11.439 releases. The sources support technique and teaching choices, not §E runtime correctness. Only concise original summaries are used; no tutorial imagery, video assets or copied lesson text is embedded.

| Reference | Relevant principle | Access represented by the handoff |
| --- | --- | --- |
| [Kamil Fauzi — Finalising Character Models & Rigging](https://kamil.myblog.arts.ac.uk/2021/10/31/finalising-character-models-rigging/) | Cube-based bag and planar strap geometry given thickness | Relevant original artist process section read |
| [Vismay Soni — Creating a Stylized Leather Bag Prop](https://80.lv/articles/creating-a-stylized-leather-bag-prop-in-maya-zbrush-substance-3d-painter) | Establish silhouette/proportions before detail; readable exaggerated flap/strap and restrained wear | First-person artist breakdown read; its Maya/ZBrush/Substance tools are not presented as §E controls |
| [Sherymon Roy — Making a Stylized bag in Blender](https://www.blendernation.com/2022/09/30/making-a-stylized-bag-in-blender/) | Broader modeling/sculpting/UV/texturing process | Author process/timelapse post read; embedded video not played |
| [Fusako — Creating a Character Model with Blender! 17: Shoulder Bag](https://www.youtube.com/watch?v=tQy39wbZ138) | Optional shoulder-bag/strap tutorial reference | Indexed title/description found; direct video fetch failed; full instructions not watched |
| [Blender 5.0 — Inset Faces](https://docs.blender.org/manual/en/5.0/modeling/meshes/editing/face/inset_faces.html) | Inner region and surrounding border; retain the useful selection for the next edit | Official indexed text retrieved |
| [Blender 5.0 — Extrude Faces](https://docs.blender.org/manual/en/5.0/modeling/meshes/editing/face/extrude_faces.html) | Extend selected geometry with connected boundaries | Official indexed text retrieved; §E retains its constrained signed-depth operator |

## Verification and delivery status

The final current-version release verifier passed **37 satchel groups** with real Three r169, alongside the existing **224 modeling groups**, camera preference assertions, inline JavaScript parsing, source/package checks and focused Sheep preservation checks. Historical patches/tests, owner simulation/render/pursuit implementations and §C workflows were preserved.

```text
python scripts/verify_v11_441_release.py --output /workspace/scratch/model-vr340-package --three-module /workspace/scratch/vr340-tools/node_modules/three/build/three.module.js
```

The 418-patch package contains 77 asset receipts and identical `index.html` / `modeler.html`: **9,992,821 bytes**, SHA-256 `62d71652fdf0bf91054e8899cf8f9a775ab12105ab451f15f3b9891b914ad82e`. Log: `/workspace/scratch/model441-release-verification.log`.

The complete controller walkthrough **passed all five grouped checks** on this exact sealed source using Chromium, official IWER 2.8.0 Quest 2 controllers, actual controller poses/buttons, native spatial menus and native geometry transactions. It created four editable parts, totaling 100 triangles, from ordinary native operations. The test-only routed response adds read-only observations and passive input traces; its instrumented SHA is `b3966f74ac62026f5e71e4594ee53098271bb6b480bafb0509fa6d1f5e7ca762`. The canonical artifact remains unchanged.

1. Native Tutorials Start new creates one independent cube; default tutorial leaves the model pick clear, either-hand Grip moves only its own window, and head motion preserves the layout; Trigger/Grab/Y Undo and confirmed checkpoints preserve the body

2. Actual menu and controller top-face selection perform Inset .20 and inward Extrude -.75 with uncommitted Preview, B Cancel, retained cap, native Apply, Undo and Redo

3. Actual Trigger strokes create separate pointed flap and concave U-band in open space; real Grip gives closed thickness, explicit Grab fits them, and the strap retains its empty middle

4. A native thickened diamond clasp passes geometry before Metal; actual quest Materials-row rays paint the selected body/flap Leather and clasp Metal, then finishing Verify passes

5. Actual angle controls inspect top/front/sides/back; native Projects Save then My Projects reopen preserves all editable parts/materials and the method flag; final deliberate Done and second Save/reopen retain all seven checkoffs

Receipt: `/workspace/outputs/model-satchel441-vr/verification.json`. No page errors. Both native My Projects reopens wait for a changed document token and a closed project hub; the existing hidden advanced select is not treated as the user-facing Open control. Saved geometry, materials, independent lesson identity/method and all seven checkoffs survive. Exiting VR restores the native model parent. The final objective remains deliberately learner-marked after save/reopen; geometry cannot prove the user's saving action.

The default quest now uses the existing viewer-based placement at 1.25m forward / 1.40m right. Its existing enlarged .87×.653m size, initial-anchor guards and `positioned` / `userPositioned` behavior remain intact. Native stereo projection checks put the whole panel clear of the canonical body/strap from both eyes, with over 4° margin. The browser also verifies the first body pick before moving a window, actual right- and left-Grip repositioning without moving the tool console or changing model/history, and unchanged quest world pose during real emulated head movement. The panel stays where the user places it; no head-following HUD was added.

Physical Quest comfort, controller tracking fidelity, exact seams/artistic finish, physical Android, hand tracking and authenticated account saving remain untested. The checker explicitly requests rendered review for sculpted/deformed parts. The v11.440 audit's known IWER Bottom → Isometric Trigger transition and incomplete advanced tools remain documented; this satchel update does not claim universal tool or physical-device acceptance.

Hosted publication: pending the repository's separate deployment-request commit and artifact confirmation.
