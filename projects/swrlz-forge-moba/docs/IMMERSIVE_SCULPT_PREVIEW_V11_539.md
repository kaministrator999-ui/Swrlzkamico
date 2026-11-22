# §E v11.539 — Immersive VR sculpt responsiveness, hover footprint and project handoff

Date: 2026-11-22. Owner report: [#479](https://github.com/kaministrator999-ui/Swrlzkamico/issues/479).

**Environment:** Meta Quest Browser **immersive WebXR** / native Model Studio. This change does not target the regular 2D Quest Browser editor.

## Observations preserved

Two headset screenshots showed a large detached Sculpt Surface dialog, a Sculpt brush list, detached Radius/Strength parameters, a primary tool panel and a status banner, overlapping the model field. The existing cursor was a flat circle. During Pull, deformation initially worked but began lagging significantly when movement stopped, changed region, or Trigger was released. Opening Smooth Witch Hat from within immersive VR did not reliably work.

## Source-grounded causes addressed

- The previous native `se350UpdateStroke` could execute precise surface raycast and `sculptUpdate` every headset frame. The edit operator traversed every vertex and recomputed triangle normals and spatial bounds per sample. The new bounded sampling cadence is approximately 30Hz with accumulated elapsed time. It retains the native stroke result and a final sample on Trigger release.
- Replaced per-vertex temporary coordinate arrays and per-vertex `map` allocations with in-place typed-array clamp/mask handling and sparse commit differences. Native `checkpoint()`, validation, `signalEdited()`, Undo and renderer authority remain unchanged.
- The old `se350UpdateBrush` generated a flat `RingGeometry`. The replacement creates one pooled, non-raycastable hemispherical displacement envelope, a selection ring and a capped source-geometry wire overlay. The envelope height follows strength and signed Push/Pull direction. Mesh edges use real source positions and radial falloff weights, with optional region-mask filtering and a bounded triangle sample budget.
- The v11.528 parameter surface used a fixed 870px-tall canvas regardless of one or two active groups. It now crops the blank lower tail in place, retaining the original +/- action IDs and physical hit targets. Third-stage parameters stay beside their native modifier controls instead of adding another panel.
- The `se175StarterKinds` native immersive source index lacked the later hat/mannequin starters. Register those existing builders. Native `se517ProjectLibrary.open()` releases the old borrowed Model Atelier root before awaiting startup; the original frame guard could interpret the intentional temporary absence as a lost workspace and exit XR. A transition-aware frame branch keeps the same session rendering until the root is borrowed again.

## Acceptance

1. **Menus:** Quest 2 immersive startup, Sculpt > Push/Pull, Direction toggle, Radius/Strength +/- adjustments, collapse/expand and tool switching. Inspect readability, ray priority and remaining model visibility.
2. **Preview:** Hover textured sphere, cone, Smooth Witch Hat and any saved topology mesh. Inspect real mesh grid alignment, radius changes, pressure-height envelope, inward/outward sign and camera/mesh movement. Preview must never count as saved geometry.
3. **Performance:** Repeated 0.5–2 second Pull and Push strokes on small/large meshes, moving pointer off mesh and releasing Trigger. Record in-headset frame time, peak update/commit timing via `window.SWYRL_ENGINE_IMMERSIVE_SCULPT_538.inspect()`, no long freeze, no lost geometry, correct one-commit Undo and reload.
4. **Loading:** Inside immersive VR, Projects > Starters > Smooth Witch Hat > Open, then reopen another project without leaving headset session. Confirm the original painted UV/texture and mesh topology. On failure, current project must remain recoverable.
5. **Regression:** Native Move/Rotate/Scale gizmos, rest-pose prompt, lasso mask, Sculpt Smooth, Extrude, world-space menu buttons, Cloud project operations, 2D Quest Browser selection and regular phone layout.

## Delivery boundary

Automated candidate checks can validate runtime syntax, ordered patch integration, exact source byte/hash receipt, static package and non-headset logic. **They cannot establish real Quest 2 frame-time or UX acceptance.** Do not mark items #479 fully fixed until owner tests them physically.

Keep `AGENTS.md` and `RELEASE_PROCESS.md` source-of-truth, and publish only after a sealed commit plus the separate `DEPLOY_REQUEST.json` commit.
