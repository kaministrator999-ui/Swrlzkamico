# §E v11.105 · Sculpt stroke undo / viewport mode isolation and mobile form spacing

## Observed Android behavior

Following v11.104, the owner confirmed the picked point ring appears, but observed that using **Remove last stroke** while inspecting in X-Ray unexpectedly changes the render mode. The native floating inspector also remains cramped and could be a little wider with more breathing room between labels, fields, buttons and fieldsets.

## Source findings and bounded change

- In `model_atelier_sculpt_brush_v11_21.js`, the stroke removal listener runs `checkpoint(); p.sculptBrushes=...; signalEdited(); select(p.id);`. The latter two functions each call `renderParts()`, causing redundant reconstruction and inspector refresh.
- `atelierViewGlobal` and `atelierViewOverrides` are transient viewport state, independent of editable geometry. New logic snapshots global mode, per-part mode override map, and the All/Selected scope, performs the stroke removal using **one** standard `signalEdited()` path, restores viewport state defensively if unexpectedly mutated, then refreshes the display selection fields. Existing brush history, undo storage and mesh structures stay untouched.
- Mobile inspector uses slightly wider CSS sizing (at most 415px or viewport minus 24px; Expanded at most 465px or viewport minus 20px) without changing its height, drag position or the existing side swipe/scroll affordance.
- Native form spacing uses larger row/column gaps, fieldset rhythm, readable labels, and touch-friendly action gaps. Does not replace any form controls or handlers.
- No changes to materials, model meshes, renderer modes by user choice, new drilling tools, exports, scene assets or historical projects.

## Verification / limitations

- 137 governed patches; 68 preserved assets.
- Exact generated HTML: 6539743 bytes, SHA-256 `d845e5ae1b064f4a6e1d7c41a654d1e561bfa8f4e1e02db227b5443ac9af5d3c`.
- Release marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_105_SCULPT_UNDO_VIEW_MENU`.
- Initial fail-closed preflight measured SHA before manifest sealing. Full JavaScript syntax, deploy provenance, and hosted file/asset checks are separate gates.
- **Physical Android acceptance pending**: switch to X-Ray, make a brush stroke, Remove last stroke, confirm the render-mode dropdown and actual material still show X-Ray; repeat for Wireframe. Check panel width, field spacing, scrollbar, drag and number-pad hold.
