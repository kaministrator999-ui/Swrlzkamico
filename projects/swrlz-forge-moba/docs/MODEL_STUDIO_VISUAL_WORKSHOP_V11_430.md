# Model Studio v11.430 — learn through real modeling tools

This first overhaul makes the existing Model Studio easier to understand while adding a bounded manual mesh workflow. It uses the same native editor, inspector, camera binding, editable topology and project history. The [pre-change audit](MODEL_STUDIO_AUDIT_V11_430.md) records which capabilities already existed, which were hidden or defective, and which remain incomplete.

## What already worked

The editor already had primitives, object and component transforms, multi-selection, duplicate/delete, persistent flat assemblies, sculpt brushes, local triangle refinement, indexed edge splitting, planar boundary filling and winding repair. It also had wireframe/overlay/X-ray display, reference-image alignment and movable reference windows, UV tools, rigging/animation, import/export, and guarded project save/clone paths.

Several capabilities were difficult to discover. Numeric face/vertex indices dominated advanced topology controls, the unified inspector could hide the component-mode dock, and a newly added object defaulted to a sphere. Existing “Face Extrude” operated on one triangle; VR outline extrusion added thickness to an outline. Neither was a general connected face-region tool. The previous six native direction presets were perspective views with small angular offsets, rather than exact orthographic views.

## What changed

| Area | Result in this checkpoint |
| --- | --- |
| Tool discovery | The existing Add control gains a primitive choice. Object/Vertex/Edge/Face modes and current selection information stay visible. Existing assembly controls are available through an organized inspector mode. |
| Teaching | A shared catalog supplies meaningful SVG/Canvas icons, plain explanations, selection requirements, practical examples and optional Before/During/After diagrams. The lessons sit inside the existing inspector and VR console. |
| Context | Native operation availability determines whether Preview/Apply is enabled. Reasons explain incompatible selections and how to proceed. Amount changes cancel a stale preview before another Apply. |
| Vertex correctness | Vertex-selection ordinals resolve through the actual representative vertex, so UV-seam duplicates no longer cause a different point to move than the highlighted point. |
| Manual geometry | Explicit plain-primitive conversion, connected coplanar-region selection, convex planar Inset, signed connected Extrude, selected-face deletion, and bounded planar Solidify produce ordinary editable native topology. |
| Existing topology tools | Midpoint edge split, local triangle refinement, planar hole filling and winding repair use the same preview/apply/cancel workflow where the selection is eligible. |
| Native camera | True orthographic/perspective projection, exact Front/Back/Left/Right/Top/Bottom views, selection-group/component framing, Frame all and a compact orientation control reuse the existing renderer. |
| VR | Manual planar-region modeling and shared animated lessons use the existing controller dispatcher, native transaction bridge and independent world-space console. Headset projection remains perspective. |

The teaching catalog contains 22 entries. General bevel, merge, mirror and loop examples are marked incomplete rather than receiving pretend Apply controls. Text labels and accessible names remain alongside icons. Diagrams are generated from small controlled shapes; no large tutorial video or additional WebGL renderer is introduced. Optional animation advances from the existing editor/XR loops and respects reduced motion.

The original advanced inspector remains available. Existing sculpt, display, clipping/interior inspection, reference, UV, material, rig, animation, project and export systems remain the authority for their established operations. The v11.411 Quest NPC frame-budget work and other engine/§C integrations are preserved by this scoped source patch.

## Learn a manual cube-to-container workflow

Use an independent blank project or a copy of an existing project. The walkthrough navigates real tools; its steps do not generate a finished model or automatically commit edits.

1. In **Meshes → Select & organize**, choose **Cube**, then use the existing **Add cube** control. Frame the selection if needed.
2. Open **Topology → Manual mesh modeling** and choose **Make mesh editable**. This explicit conversion preserves the supported primitive's shape, welds shared positions and regenerates plain UV coordinates. Review that change before proceeding.
3. Choose **Face** mode, use **Top** view, tap a triangle on the cube's top and choose **Select flat region**. The connected coplanar top triangles form one selected region.
4. Choose **Inset**, for example `0.2` (20%). **Preview geometry** shows the inner region and connected border without changing saved geometry or history. **Apply geometry** commits one native Undo step.
5. **Keep the resulting inner faces selected.** Choose **Extrude** without expanding the flat region again. Use a negative local depth, such as `-0.35`, to push that region inward. Preview and inspect the cavity, then Apply. The guard rejects extrusion that would pass another surface or overlap the existing walls; keep a floor.
6. Use **Cancel preview** to discard only the uncommitted candidate. **Undo** reverses an applied operation; Redo restores it. Save or export through the existing project controls to retain the resulting native mesh.

The Face selector operates on triangles. “Select flat region” floods connected coplanar triangles, including an inset rim if expanded again. Inset's returned inner-face selection is transient and retained for the immediate next edit; it is not saved as semantic polygon metadata. After deselection or reopening, use the existing triangle Multi selection to choose the inner cap again rather than claiming that coplanar flood can identify it automatically.

For VR, select the object, open **Studio → Mesh tools → Manual modeling**, make it editable, then point and Trigger a flat face. Choose Inset or Extrude, adjust the amount/direction, and use the spatial **Preview / Apply / Cancel** controls. **Learn this tool** opens the shared diagram on the same movable world-space console. A pending preview must be applied or canceled before another face is selected; B or the first Undo cancels it. The new tools do not turn the console into a head-following HUD.

## Geometry and compatibility boundaries

The new topology-changing path works on one plain independent object at a time. It rejects authored deformation, painted/texture-bound, skinned/rigged, animated, refined or other procedural data when it cannot preserve the correspondence safely. This does not remove those projects' existing editing tools. It prevents old sculpt indices, rig weights or texture bindings from silently being applied to reindexed geometry.

Inset and region Extrude currently require one connected, convex planar region with one simple boundary. Solidify requires the entire convex planar open mesh; curved surfaces and partial open patches are not supported. Subdivide means stitched local triangle refinement, not Catmull–Clark or automatic rounding. Split edge inserts a midpoint, not a complete loop cut. Repair normals fixes inconsistent shared-edge winding; it does not guess a globally outward direction. Hole filling remains limited to a verified simple nearly planar boundary ring.

Candidates are checked against native limits of **9,000 vertices / 16,000 triangles**, position and UV bounds, topology audits and source ownership. Collision work is bounded for interactive use. These operators are conservative manual planar modeling tools, not unrestricted Boolean or self-intersection solvers.

A live preview owns only derived geometry. Apply verifies the unchanged document, revision, source references, object/component selection and native candidate before one checkpoint. Cancel, selection/document changes, close and relevant VR tracking/profile changes discard pending work. New saved geometry uses the existing `{positions, uvs, indices}` topology schema; no parallel recipe format is required.

Persistent **Group/Assemblies** retains separate native objects. **Join** is destructive mesh combination and does not weld seams or preserve every source material. The older accessory workflow's shared text label and transient selected batch are not a persisted `meshGroups` assembly. None of these are substitutes for general vertex merge.

## What remains incomplete

General edge/vertex bevel, vertex weld/merge, boundary-loop bridge, detached-region split, quad loop cut/slide, unrestricted object/component mirror, align/distribute, custom-pivot UI, general vertex/edge/surface snapping, and dedicated general curve/ribbon/tube authoring remain incomplete. Existing sculpt X symmetry, axis constraints and VR transform snapping are separate working features. VR still does not provide the full desktop vertex/edge component editor.

These limitations are visible in the audit and teaching descriptions. The first manual container workflow deliberately uses implemented primitive and topology operations rather than an accessory/backpack generator.

## Verification and delivery

Local focused checks passed **67 groups**: 14 geometry-kernel groups, 17 native transaction-bridge groups, 10 actual Three.js camera groups, six shared-teaching groups, seven regressions against the assembled component-selection resolver, seven VR UI preservation groups and six starter-clone identity groups. Coverage includes a real cube → inset → inward-extrusion cavity with connected walls and retained floor; native validation/audits; source-safe previews; Undo/Redo; protected data; stale-document/resource handling; exact projections/framing; and the UV-seam selection defect. The older shipped resolver fails the new regression as expected.

Final assembled checks passed on the exact source-sealed artifact: **12 desktop + 12 Android touch-profile + nine IWER controller + five startup/Projects checks**, all with zero page errors. Real UI interactions exercise primitive creation, face selection, preview/cancel/apply, inset and inward extrusion, native Undo/Redo, six exact orthographic views, projection/framing, contextual unavailable actions and teaching, persistent assemblies, portable reference import, native export/import, closing/reopening, and independent starter-derived local saving followed by reopening and saving again. VR checks exercise real controller rays, the same manual mesh transactions, cancellation, Undo/Redo, shared teaching and world-space console placement. Source publication and the separate deployment request are complete, and hosted publication is confirmed by the receipt below. Automated emulation does not establish physical Quest comfort, haptics or sustained headset performance; those remain owner acceptance testing.


The combined build preserves current v11.425, including Satchel Academy, native VR iconography and tutorial highlights, Object Index, stable world-space menus, Projects/tutorial/level controls and the startup observer guard. The seven additional VR UI preservation checks are included in the 67 focused local groups.

The integrated browser checks exposed a starter-clone identity defect: native level hydration could restore a starter flag after the independent clone had loaded. The appended patch clears that flag only on the cloned level records and the newly stamped independent project, retaining the commit-before-switch and original-starter protections. Six regressions exercise the actual clone/save functions, failure recovery and subsequent level reload; real local Save Project now succeeds. Account/cloud saves are not exercised by guest browser checks.


On Android-sized layouts, **Settings → Views** opens the existing camera controls; close Settings to return the full viewport. The inspector uses one vertical scroll area so mode selection and help can scroll away while real operation fields remain reachable. The existing mode buttons scroll horizontally to expose advanced tool cases. For direct touch face selection, use **Hide inspector → Frame selected**, then restore **Show inspector** to adjust operation fields. The Android test uses this actual focus-workspace path and chooses an unobstructed interior face point: Chromium redirects taps near the floating toolbar to its enlarged touch target. No synthetic selection or forced hidden-control clicks are used.

The source package has been reconstructed from all **407 ordered patches**: **9,894,655 HTML bytes**, SHA-256 `fee6c64e7263311aa0bc5dca8e1d4abe9d66bb92c39da7df80d92f5565e02774`. Both HTML entry points and `SOURCE.json` agree; all 77 asset hashes across 81 package files passed. Five actual Chromium checks on this exact source preserve the authored 170-part startup scene, hydrated level selector, responsive event loop, native Projects scrolling and all three Projects tabs with zero page errors.


Focused evidence paths in the execution workspace: `outputs/model-studio-beginner-v11-430/final-model-studio/desktop/verification.json`, `android-final-8/android/verification.json`, `vr-final/verification.json` and `startup-final/verification.json`. The browser fixture serves the exact sealed HTML and packaged assets under the real static origin with a disposable guest practice project; it is not a claim of hosted-browser or physical-device acceptance.


## Confirmed publication receipt

- Source: [`d995a3c1b0b0ccf450398a8bcd9c9a2088b6befb`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d995a3c1b0b0ccf450398a8bcd9c9a2088b6befb).
- Separate request-only commit: [`04d1f2ec01055c5b46c770b651a98fccaed82509`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/04d1f2ec01055c5b46c770b651a98fccaed82509).
- Deployment: [run 43258217243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43258217243), completed successfully.
- Hugging Face revision: `90aef084a5fc8491ac67c8fc1db9dae3be1b78b2`; Space runtime **RUNNING**; [open §E](https://huggingface.co/spaces/kamiloki/swrlz-forge-moba).
- Independently streamed revision-pinned `index.html` and `modeler.html`: **9,894,655 bytes each**, SHA-256 `fee6c64e7263311aa0bc5dca8e1d4abe9d66bb92c39da7df80d92f5565e02774`. Hosted `SOURCE.json` matches the version, all 407 ordered patches and all 77 packaged asset receipts.

This documentation closure changes no runtime source, manifest, deployment request or artifact. Physical Android/Quest acceptance and account cloud-save testing remain owner checks.
