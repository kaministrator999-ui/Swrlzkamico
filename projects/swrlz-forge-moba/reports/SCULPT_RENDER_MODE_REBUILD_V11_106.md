# §E v11.106 · Retain Wireframe and X-Ray after applying a sculpt brush

## Owner evidence
On an Android screenshot of §E v11.105, the native Render mode selector remained `Wireframe`, but the ball displayed as an opaque white/shaded mesh after tapping **Apply brush**. The prior release was specific to **Remove last stroke** and did not establish an invariant for newly rebuilt meshes.

## Bounded correction
- Introduce a post-render material consistency check, scheduled once after each native geometry-edit call through the existing `signalEdited` function. It finds real meshes by their native part IDs and compares their material/overlay with the requested global or per-mesh editor render mode.
- If the rebuilt mesh is not in Wireframe, X-Ray or Shaded + wireframe, reapply the pre-existing viewport mode shading; shaded mode recovers its native material without modifying saved colors.
- Explicitly set `atelierHDDirty=true` after each geometry edit and viewport rebuild so the conditional HD rendering loop cannot leave a stale shaded frame while mode selectors show Wireframe.
- Preserve prior undo state behavior, sculpt brush geometry, preview marker, floating window size/drag and all touch input handling. No new modeling operation is added.

## Exact build
- 138 ordered patches; 68 preserved packaged assets.
- HTML: 6541671 bytes, SHA-256 `18da40e3e728b97d0822494bb8038a6fe52a299603e11bebc6cd5aae8e4c3356`.
- Marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_106_SCULPT_RENDER_MODE_REBUILD`.
- SHA and bytes measured by fail-closed preflight (preflight intentionally rejects stale v11.105 receipt).
- Production verification and owner Android behavior confirmation are separate checks.

## Acceptance
In a fresh native Model Atelier session, select Wireframe and apply a sculpt brush while camera is stationary. Mesh must remain wireframe immediately afterward. Repeat in X-Ray, tap Remove last stroke, orbit camera, and confirm the appearance mode and selector never diverge. Test Shaded + wireframe overlay and return to Shaded.
