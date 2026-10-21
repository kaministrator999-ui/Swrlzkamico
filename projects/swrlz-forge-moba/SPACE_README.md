---
title: §wyrl§ Engine v11.70
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Maul, Sheep Tag, Model Atelier and Dragon Den
---

# §wyrl§ Engine v11.70

This Space publishes the governed engine build. Project release details, historical verification evidence, and update notes are maintained in `projects/swrlz-forge-moba/README.md` and `§tart_§E.md` in the source repository. Historical Space documentation remains available in Git history.

Model Atelier includes native portrait and cloth shaping, tapered ferret muzzles, selected-part framing, independent piñata sockets and saved model motion.

The current portrait/body starter adds saved chin/nose/skin warmth, surface-fitted facial contours, softer shoulder/arm transitions, HD sampling and native calf/shin anatomy.

Native anatomical head sections define skull, temples, cheekbones, jaw and chin independently. Facial contours fit the rebuilt surface. Release: v11.20 / V11_20_ANATOMICAL_HEAD, 90 patches and 43 assets.

§E v11.59 adds the cumulative precision Model Atelier toolkit: camera-visible connected-surface sculpting, native lasso/mask editing, vertex gizmos, photo references and feathered UV cutouts, controlled topology/UV-aware LOD and geometry export. The original anatomical character scene and historical projects/assets remain preserved. Marker: `V11_59_PRECISION_MODEL_ATELIER`; 91 patches and 43 original assets.

§E v11.60 replaces the fixed bottom phone inspector with a vertical tool rail, collapsible draggable floating controls and a full-height viewport. Native controls, saved 283-part scene and all 43 historical media assets remain unchanged. Marker: `V11_60_FLOATING_MODEL_ATELIER_DOCK`; 92 patches and 43 assets.

§E v11.61 adds the optional ◫ Context secondary split floating tool workbench in Model Atelier: select an operation and adjust actual native properties in the adjacent panel. Supports Meshes, Sculpt, Lasso, Face, Topology, References, Motion and Appearance where actual controls exist, explicit saved presets and original inspector access. This does not add unrelated anime/game editor adapters. Marker: V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH; 93 patches, 43 original assets.


§E v11.62 introduced the mobile-first unified Model Atelier tool sheet above the bottom category rail with Compact/Half/Expanded sizes, operation search and All/Quick/Recent, per-operation favorites, handedness and a return to the original native inspector. Desktop retains its movable workbench. All 283 original model parts and 43 assets persist. Marker: V11_62_MOBILE_ADAPTIVE_TOOL_SHEET; 94 patches. This previous feature release is retained for historical context.

§E v11.63 is a version-only deployment smoke test. No modeling, gaming or animation behavior changes; 95 ordered patches, original 283-part canonical model, and 43 historical assets. Marker: `V11_63_VERSION_SMOKE_TEST`. The verified live deploy receipt determines whether v11.63 is actually hosted.

§E v11.64 is a version-only §§§ release speed test. No modeling, gaming, or animation behavior changes; 96 ordered patches, original 283-part canonical model, and the same 43 historical assets. Marker: `V11_64_VERSION_SMOKE_TEST`. Hosted status requires a successful deployment receipt.

§E v11.65 adds a contextual selection-based mesh transform strip next to the picked model part. Move/Rotate/Scale gizmo axes and plus/minus nudges, multi-mesh grouping and baked Join are native/Undo-enabled. Show vertices opens the existing real vertex-point overlay. U/V steppers make procedural density discoverable for sphere/loft/box/cone/cylinder and face-sheet meshes within bounded geometry budgets; nonparametric topology uses the existing refinement tools. Joined topology mesh material uses the first selected mesh. Original 283-part starter and 43 historical assets are preserved. Marker: `V11_65_SELECTION_MESH_GIZMOS`; 97 ordered patches. Hosted status requires the final verified release receipt.

§E v11.66 repairs Model Atelier mesh transform usability: removes doubled selection BoxHelper, bounds camera-scaled axis dragging to ≤0.45 world units per gesture, adds Undo/Redo/Frame mesh in the selection strip, persists a draggable popup position per-device, and coordinates a cybernetic cyan/indigo visual treatment across existing tool panels. Current mesh functionality, original 283-part scene and the 43 historical assets remain unchanged. Marker: `V11_66_MESH_SELECTION_UX_REPAIR`; 98 ordered patches. Physical-device usability remains owner-tested.

§E v11.67 is a focused Model Atelier performance update: whole-mesh Move/Rotate/Scale commits now update only their existing Three.js mesh transforms and inspector/history state, avoiding the v11.66 full 283-part geometry rebuild on release. Canceled/no-op drags also avoid the rebuild. Undo/Redo/JSON/OBJ remain available. 99 ordered patches; unchanged original 283-part character and 43 packaged assets. Marker `V11_67_MESH_TRANSFORM_PERFORMANCE`; mobile responsiveness awaits owner testing.

§E v11.68 improves touch editing of native Model Atelier parts: while dragging the X/Y/Z gizmo, selected meshes, bounding outlines and transform handles all follow live without rebuilding their geometry or resetting a captured handle. Tapping a different object updates its existing selection BoxHelper immediately instead of rebuilding all 283 character parts. Transform release still uses the v11.67 fast commit path and native Undo/Redo. The canonical 283-part project and 43 original assets remain preserved. Version marker `V11_68_LIVE_MESH_GIZMO_FEEDBACK`, 100 patches. Touch smoothness remains subject to the owner's live Android test.

§E v11.69 corrects delayed mesh drag preview in Model Atelier. Pointer movement updates the already-rendered native geometry and axis handles, computes gizmo location directly from captured pivot and delta (without recalculating mesh bounding boxes every move), and paints a WebGL frame immediately during active drags. No source topology, model geometry, or original material changes. Native saved transforms/Undo/Redo retain v11.67 behavior. A real Chromium pointer-drag regression confirmed both mesh and handle moved before mouse release (9 movement + 9 render updates); Android owner testing is still needed. Original 283-part starter and 43 packaged assets retained. Marker `V11_69_DRAG_PREVIEW_RENDER`; 101 ordered patches.

§E v11.70 improves phone authoring workflow: the viewport top bar groups Render/Target, a horizontally scrollable camera direction row, and a collapsible Display/Wire/Interior section, preserving all original controls and handlers. A compact Fine–Fast transform sensitivity slider in the selected-mesh popup sets persistent **per-mode** Move/Rotate/Scale multipliers from ⅛× to 4× for both pointer drags and ± nudges. This adjusts operation responsiveness, **not vertex count**, which remains in Grid U/V. Undo/Redo and live-gizmo renderer are unchanged. A real Chromium pointer test verified 0.180-unit standard versus 0.0225-unit ⅛× movement for identical 25-pixel drags, mode-specific setting retention, navigation visibility and 390px layout. 102 patches, original 283-part canonical starter, 43 bundled assets. Marker `V11_70_PRECISION_GIZMO_TOOLBAR`.
