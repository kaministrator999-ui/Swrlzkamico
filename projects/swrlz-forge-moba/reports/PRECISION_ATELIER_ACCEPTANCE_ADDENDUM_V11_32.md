# §E Model Atelier — Precision Acceptance Addendum (v11.30–v11.32)

Date: 2026-10-18. Design basis: owner's private `SE_Model_Atelier_Design_Spec.docx`, 17 October 2026.
Current status: **three independently tested DRAFT slices; full specification INCOMPLETE; original v11.20 production unchanged**.

This addendum **continues** [the v11.29 acceptance ledger](PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md), which preserves baseline architecture, earlier tests, known failure paths, and unresolved requirements. Do not overwrite or replace the earlier record.

## Exact draft lineage
- [#235](https://github.com/kaministrator999-ui/Swrlzkamico/pull/235) v11.30 — grouped lasso surface pins, stacked on prior [#234](https://github.com/kaministrator999-ui/Swrlzkamico/pull/234).
- [#238](https://github.com/kaministrator999-ui/Swrlzkamico/pull/238) v11.31 — locked refinement-layer structure, safe disabled duplication, bidirectional reordering.
- [#240](https://github.com/kaministrator999-ui/Swrlzkamico/pull/240) v11.32 — resizable/pinnable portable reference dock.

Every candidate is a **draft stacked pull request**, not a production engine version, not a merge, and not an automatically accepted character model.

## Specific verified changes

### v11.30 — grouped 📌 lasso pins
- Select up to eight one-based boundary pin indices and apply a bounded object-local XYZ delta to them as one native Undo transaction.
- Each pin is reprojected onto the selected actual mesh; invalid point, input or self-crossing rejects the whole operation. Underlying vertices and triangle topology are never edited.
- CPU + real desktop/Android original-head lasso Save/Undo/Reload: **PASS** [39146901023](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39146901023).
- Further needs: curve interpolation, normal-offset pin controls, Boolean region selection and multi-segment selection operations.

### v11.31 — refinement structural locking and safe disabled copies
- Old saved layers without `locked` remain valid. Optional `locked` is a strict boolean; it blocks deletion/reordering of that layer, including indirect movement across it.
- Visibility remains independently toggleable; locking detail does **not** lock its separate lasso selection region.
- Duplicate generates distinct saved layer identity, always **disabled and unlocked** initially. Copying alone cannot multiply triangles. Existing max-three layers and native validation remain intact.
- New Move Later control complements Move Earlier; Undo/JSON and original 283-part head checked.
- CPU, geometry and real desktop/Android native Save/Undo/Reload **PASS** [39159598679](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39159598679), tested source SHA `e8f72b503ec3f531e4952f711545619ba66cc3e7`.
- Further needs: meaningful continuous deformation-layer blend weights, topology bake/rollback, arbitrary mesh reduction/LOD export and comprehensive layer-stack combinations.

### v11.32 — saved portable floating reference dock dimensions and Pin/Unpin
- Optional `referenceLayout.width` (200–680 integer px), `height` (220–680 integer px), `pinned` (boolean) with backward-compatible layouts if absent.
- Numeric width/height inspector and header Pin/Unpin. Pin protects dock dragging without disabling reference-image pan/zoom or model camera. Mobile CSS caps visual width/height without silently rewriting the saved author's requested dimensions.
- Image bytes and transforms are untouched; changes persist in native JSON with one Undo checkpoint per action. Bad values reject import and no-op against saved data.
- Unit and real desktop/Android browser native Save/Undo/Reload **PASS** [39160149709](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39160149709), tested source SHA `7bf598d64f5fb9a9467bd639f44398921e8ad251`.
- Further needs: independent dockable multi-panels, additional reference slots beyond portable four images, calibrated lens/perspective alignment, linking facial landmarks, and full reference-derived head reconstruction.

## Failures preserved
- v11.30 initial unit check incorrectly demanded exact binary float equality for `-0.075`; corrected to strict tolerance and test rerun passed, without modifying the saved group displacement algorithm.
- v11.32 initial isolated VM harness omitted JavaScript `structuredClone`, causing an infrastructure failure before validating portable layout. Injected the expected standard library function into the harness, reran and passed. Retain earlier failed Actions run [39160097344](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39160097344).

## Unfinished owner-spec scope / next release gates
- **Surface editing:** camera-visible occlusion-accurate brush/selection, true brush-painted lasso, topology-following boundary, add/subtract/intersect region booleans, edge sculpt/retopology and complete normal-offset surface constraints.
- **Topology/density:** arbitrary mesh decimation, exact target vertex-count planning, true runtime LOD meshes/exports, generated topology bake/rollback and weighted editable deformation-layer blending.
- **Gizmos:** on-canvas multi-axis rotate/scale handles for 📍 vertices and 📌 boundary groups, selection simplification/culling on dense scenes.
- **References/face construction:** multi-panel reference workspace and 3D perspective registration, hand-cut reference silhouettes, front+profile geometric reconstruction, facial landmarks and deliberately sculpted watertight neck/back of head.
- **Final approval:** independent full compatibility CI, real desktop/Android resource profiling on dense model, saved JSON/OBJ equivalence, native visual front/side/back comparisons to provided images, owner artistic review, version/manifest/README/ROADMAP sync, governed merge, `DEPLOY_REQUEST.json` as the **LAST source mutation**, matching deployment Actions receipt and exact live hosted marker check.

Do **NOT** announce complete §E v11.32 production or claim that a character-modeling Codex session occurred. Only the focused editor controls and validations above have been demonstrated.
