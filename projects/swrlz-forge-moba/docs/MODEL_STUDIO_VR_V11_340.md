# Immersive Model Studio — v11.340

Lifecycle: IMPLEMENTATION_APPROVED; SOURCE_VERIFIED; XR_EMULATION_VERIFIED. Source publication, hosted confirmation and physical-headset acceptance are recorded separately.

## Workspace and supported controls

Open a native model in Model Studio, then choose **Enter model VR** in a WebXR headset browser. The actual native model appears on a presentation workbench with a stable world-space palette to the left. Trigger selects model parts. Inspect is the default and does not edit through a grip. Choose Move, Rotate or Scale to edit a part with a tracked grip; release applies one native history step. Rays, hover/selection outlines, target reticles, cached text feedback and optional haptic pulses indicate interaction state.

| Control | Model VR action |
| --- | --- |
| Trigger, either hand | Select a hit part or activate a visible palette button |
| Grip with Move / Rotate / Scale selected | Move by grip-space displacement, rotate by wrist pose, or scale by grip height |
| Right A | Cycle Inspect / Move / Rotate / Scale |
| Right B | Cancel a live preview; otherwise return to Inspect |
| Left X | Hide/show the tools; reopening positions them once near the current view |
| Left Y | Undo; during a live grip, cancel that preview first |
| Left stick | Pan the model presentation |
| Right stick | Turn the model presentation in 30° steps and change view size |
| Palette | Redo, Focus, Recenter, Precision, Snap, Help and Exit |

Precision uses quarter-speed transforms. Snap uses 0.01 model units, 15° rotation and 5% scale steps. Presentation framing, turning and view scale never change saved model geometry. The palette background blocks model selection through it; missed rays cannot grab an old selection. Cancel wins over a simultaneous grip release from either hand. Tracking loss, headset visibility/reference changes and session end cancel transient edits and require a fresh grip release before another gesture.

These are the native Model VR defaults. The historical VR Controller Studio's custom-profile simulator is not claimed as live profile dispatch. In-headset mesh sculpting, vertex/edge editing and rig-pose authoring retain their existing capability boundaries; this release provides inspection and native part transforms.

## Native ownership and editing

The adapter borrows the actual Modeler root, including its geometry, materials and rig bones, into a dedicated XR scene using the existing main renderer and animation loop. It does not copy Game actors or clone skeletons. The ordinary browser Modeler keeps its native pose/update logic while flat-canvas draws pause. Exit restores the original root parent, child order, local transform, helper visibility and normal browser rendering. No borrowed geometry or material is disposed by the XR adapter.

Controller gestures preview derived meshes only. Saved descriptors stay unchanged until a validated release: one native checkpoint, one descriptor update, one native edit signal. No-op, cancel, tracking loss and source replacement do not consume history or erase Redo. Document, part and projection identities prevent a stale gesture from overwriting later native/Chat edits. Grip conversion respects native assembly bases; off-centre topology geometry rotates/scales around its own centre. Attached skins temporarily retain the starting inverse bind matrix for a live affine preview, then restore the exact native update method/inverse state before cancel, invalidation or commit/rebind. Skeletons, bind matrices and geometry remain native.

The existing Game/Arcane XR path stays separate. Model VR enters before Game tick/controller handlers and uses its own session state; leaving it restores the native renderer/orbit state. The permission request stays in the original user activation. Playing/simulating, duplicate sessions, denied permission and unavailable immersive browsers leave the normal editor usable.

## Canonical source and integrity

Integrated on owner v11.337 request `6d3631a457b6998d0936541621ac326d6d4c24a3`, preserving hand/atlas/anatomy/geode and UV-guide patches 331–337 plus all earlier source. Model VR appends patch **351**.

Canonical reconstruction: **9,118,381 bytes**, SHA-256 **`a940121424bf3cabd2336f51938a337922a3bbddc2aa021ea2c99e9bbde224ff`**; index and Modeler are identical. Strict packaging verifies **71 assets / 75 files**, every asset's bytes/hash, source receipt, runtime title/build/provenance/marker, and the dedicated verifier/workflow version. No integrity check is waived. Test-only IWER, dependencies, private fixtures and screenshots are excluded from the package.

## Bounded verification

- Strict source build and assembled JavaScript parsing pass.
- **13 real-Three native cases** cover affine/assembly bases, automatic off-centre pivots, attached-skin live previews and cleanup, single native commit, no-op/cancel/Redo, invalid transforms, projection rebuild, document/part replacement and borrowed-root ownership/disposal boundaries.
- The preserved native routing, material, Arcane grip/ray and current owner hand/geode tests pass. No unrelated 22-case game workflow was run.
- The actual engine renderer, XR session and two Quest Touch input sources pass with pinned **IWER 2.8.0 / Meta Quest 2**. Trigger selection, inspect/miss safety, grip-space transforms, same-frame release, both-hand cancel priority, Undo/Redo, disconnect, tool edges/guide/toggles, exit/reentry, native Game XR afterward, document replacement, denied permission and unsupported-browser fallback pass with **zero page errors**. The tested HTML hash exactly equals the canonical seal above.

```sh
python projects/swrlz-forge-moba/scripts/verify_v11_340_release.py --output dist/swrlz-forge-moba
python projects/swrlz-forge-moba/scripts/check_model_vr_v11_340.py --html dist/swrlz-forge-moba/index.html --output /tmp/swrlz-model-vr340
```

The portable browser check uses isolated guest profiles, public native fixtures and verified-TLS CDN/guest Chat requests. It uses a checksum-pinned test emulator, never an account session or cloud save. Software emulation establishes session/controller/editing contracts and visual structure; physical Quest comfort, hand alignment, haptic feel and sustained performance remain owner headset acceptance.

## Publication

Pending the cohesive source commit, separate request-only commit, deployment and independent hosted confirmation.
