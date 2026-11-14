# §E regular-browser satchel tutorial — v11.442

2026-11-14. Implemented under AGENTS.md / RELEASE_PROCESS.md. Verification and hosted publication are recorded below; a source change alone is not a live-release claim.

## The regular-browser workshop

Projects → Tutorials → Start new satchel quest creates an independent editable lesson. The same seven objective IDs, ordinary body cube, native manual workshop, inspector, parts list, material tools, checkpoints and Save Project remain in use. Existing lessons and saved progress stay compatible. No new geometry editor or bag generator is introduced.

The original panel is moved into its own **nonmodal dialog** above the Model Studio rather than cloned. Existing objective, verification, Show Me, ghost and checkpoint listeners remain on the same nodes. The window is independent of the inspector's scroll. It has:

- A touch/mouse titlebar with pointer capture, arrow-key movement, Shift + arrows for larger steps, and Home/reset to recover its position.
- Collapse/expand with accessible state, a minimize button and compact launcher, 44px controls, Escape to collapse, and unrestricted Tab navigation.
- Separate desktop/mobile layout preferences, stored locally without adding window coordinates or state to model geometry or saved projects.
- Bounds based on the visual viewport, including rotation/resizing and keyboard space. No full-screen backdrop or focus trap blocks the editor.
- A compact initial mobile state. Open the tutorial to read a task, then collapse/minimize or drag it aside while working. An XR-state hook hides only the flat DOM window; the existing scene-owned VR quest and tool windows are preserved.

The previous scene-relative drag/fold handlers are removed before the adapter takes ownership. This prevents two drag controllers from competing. Native project and studio changes retain the existing lesson eligibility rules.

## Manual mobile recipe

Use the normal primitive picker/Add controls and **Meshes → Transform**. Triples below are X/Y/Z; rotations are zero. Phone number entry retains the existing press-and-hold gesture to open its keypad, followed by Clear, digits and Apply. The tutorial explains that gesture and native Undo.

| Piece | Position | Scale | Actual operation |
| --- | --- | --- | --- |
| Body | 0, 1.5, 0 | 1.4, 1, .65 | Original cube → Make mesh editable → Face/Top → tap top → Select flat region → Inset .20 → Preview/Apply → retain inner faces → Extrude −.75 → Preview/Apply |
| Flap | 0, 1.75, .355 | 1.3, .5, .06 | One separately added thin cube; its back touches body front at Z .325 |
| Left strap leg | −.66, 2.37, 0 | .08, .98, .06 | Ordinary added cube, fitted at the bag side |
| Right strap leg | .66, 2.37, 0 | .08, .98, .06 | Another cube or duplicate of the left leg with changed X |
| Strap bridge | 0, 2.84, 0 | 1.32, .08, .06 | Ordinary cube joins both legs, leaving the middle empty |
| Clasp | 0, 1.68, .465 | .08, .08, .08 | Small sphere; native sphere Scale is its radius; back touches flap front at Z .385 |

The body is **one connected cavity mesh**. The three strap sections use the existing supported segmented-strap checker. The learner sets the values and performs every edit; navigation/help never generates these pieces or applies geometry. Brown matte leather on the body/flap/strap and gold metal on the actual clasp complete the materials objective. Shape inspection remains guidance, not certification of artistic finish or perfect seams.

## Discoverability and numeric corrections

A historical array-index rewrite replaced Transform after Assemblies was inserted ahead of it. The correction gives Mesh identity a named insertion and preserves the original nine-field Transform group. The same values no longer live only in Additional meshes controls. Position/Scale axes and radian Rotation axes have clear accessible labels.

Native HTML numeric constraints were inconsistent with usable values: `.05` steps combined with scale minimum `.006` rejected fine dimensions, and several manual-tool defaults did not align with their HTML step base. Transform and flat manual-amount controls now use `.001` precision, matching the inspector's three-decimal display. Native range, finite-value, mesh-validity, preview/Apply and Undo checks remain in place. VR gesture steps and snapping are unchanged.

Flat Show Me uses explicit existing tool routes. The cavity helper distinguishes Convert, Face/Top, original top-region selection, operation, amount, Preview and Apply; it does not pick faces, expand regions, set geometry parameters, create previews or commit edits automatically. It avoids expanding the inset rim again after Inset. Construction objectives also offer Size & position. Final Save targeting is scoped to the visible Model Studio control rather than a hidden project-library wrapper.

## Verification and publication

The final exact-source Android-sized Chromium walkthrough **passed all seven grouped checks**. It uses real touch taps, a 430ms press through the existing number pad, visible editor controls and read-only public inspectors. The sealed HTML is routed unchanged, with no editor-operation calls through evaluate, hidden-control forcing, generated/imported model fixture, or account write.

1. Independent nonmodal dialog supports real header touch drag, collapse/reopen, close/launcher reopen, reset and clamping at 320px, 390px and landscape; collapsed lesson leaves native mesh controls usable

2. Projects → Tutorials → Start new creates one independent cube; touch numeric editing and native Undo preserve it; real Check my work and Save checkpoint work

3. Actual top-face canvas tap, flat-region selection, Inset .20 and Extrude −.75 use native Preview/Cancel/Apply; source remains unchanged before Apply and native Undo/Redo restore exact topology

4. Native Add primitive, visible Transform fields and mobile number pad create a thin box flap, three ordinary strap boxes with an empty middle, and small sphere clasp; real stage checks accept their fit

5. Materials stage initially rejects unfinished hardware; native Material and Color fields paint actual leather parts matte brown and actual clasp metal gold, then Check my work passes

6. Native Views inspect all sides; Save Project and visible My Projects card → Open project load the saved document with a changed document token; final deliberate Mark and second save/reopen retain all six editable parts, materials and seven flags

7. Visible New Model Project still opens the untouched one-sphere starter; reopening My Projects restores the separately saved six-part satchel and all seven flags

The saved document itself retains its seven `se416TutorialState.done` entries. Reopens change the native document token, so comparing the existing active model cannot masquerade as successful loading. The original blank-model starter reopens as its stock one-sphere project; loading the saved lesson again restores six editable parts and all progress.

A separate **desktop mouse dialog smoke passed** at 1280px and 1440px widths. Mobile responsive coverage includes 320px, 390px and landscape. Both suites check the original panel's BODY mounting/nonmodal role, real dragging, collapse/expand, minimize/restore, reset and viewport bounds. The restore launcher is clear of §Chat and the selected-object transform bar. Both receipts report no page errors.

The full canonical **419-patch** release verifier passed, with **266 native modeling/preservation groups**, camera preference assertions, inline JavaScript parsing, focused Sheep preservation and 77 asset receipts. Its actual rebuild matches the candidate assembled from the verified v11.441 artifact: **10,022,666 HTML bytes**, SHA-256 `4a00a190da3c55133de7564061d11d604e1a6e15a40f3519653a8af7b6f69a04`; `index.html` and `modeler.html` are identical. Native preservation checks compare seven complete VR/geometry sections against hosted v11.441 and verify that the flat lesson wrapper delegates VR Show Me and retains effective VR text. No historical snapshot or §C workflow was rewritten.

```text
python scripts/verify_v11_442_release.py --output /workspace/scratch/model-vr340-package --three-module /workspace/scratch/vr340-tools/node_modules/three/build/three.module.js
```

Evidence: `/workspace/scratch/model442-release-verification.log`, `/workspace/outputs/model-satchel442-mobile/verification.json`, and `/workspace/outputs/model-satchel442-desktop/verification.json`. Undo/Redo was exercised through Meshes → Select & organize. The existing camera-orientation widget can intercept a viewport Undo shortcut; that unrelated viewport-layout issue is not claimed fixed. The earlier v11.440 IWER Bottom → Isometric transition and incomplete advanced tools remain documented in their audit.

Physical Android browser/soft-keyboard comfort, physical Quest and authenticated account saving remain untested. This release verifies flat browser interaction and preserves the existing immersive implementation; it does not claim a new physical headset acceptance run. Artistic finish and precise surface contact still require visual review.

**Published and hosted-verified:** [source b97e557](https://github.com/kaministrator999-ui/Swrlzkamico/commit/b97e557fc239e2452fd612215b46c4a493e146ae), [separate deployment request ad21529](https://github.com/kaministrator999-ui/Swrlzkamico/commit/ad2152930cd2d651b2eacdd2800121c09282d919), and [successful deployment 43550132779](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43550132779). The Space is **RUNNING** at HF revision `2418512f0207320566f696b9e8741bac7b574f5f`. Hosted `SOURCE.json` agrees with all 419 patch entries and 77 packaged asset receipts; both pinned hosted HTML entry points match **10,022,666 bytes** and SHA-256 `4a00a190da3c55133de7564061d11d604e1a6e15a40f3519653a8af7b6f69a04`.

Live editor: https://kamiloki-swrlz-forge-moba.static.hf.space/modeler.html — Projects → Tutorials → Start new satchel quest or Resume. Drag the header, use − to collapse, × to minimize, the Satchel tutorial launcher to reopen, and ↺ to reset the position. Local Save needs no account. Receipt: `/workspace/scratch/model442-hosted-receipt.json`.

CI scope: historical version-specific jobs also automatically ran on the source-manifest push and reported failures (for example [the v11.435 verification43550070625](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43550070625)). They were not rewritten or rerun and are distinct from the successful current v11.442 deployment above. Existing §C Files/CPU updates through owner `574b56c57` were preserved.
