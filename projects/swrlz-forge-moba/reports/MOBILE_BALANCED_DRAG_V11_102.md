# §E v11.102 · Balanced Model Atelier inspector and native drag position

## User evidence

Owner's v11.101 screenshot demonstrated a very small lower-right panel. Owner reported it could not be dragged by its Move tools header. Previously oversized versions had consumed nearly half the viewport.

## Root cause

The legacy free-drag pointer handler already calculated valid left and top coordinates and assigned inline inspector styles. New mobile responsive rules pinned `top:auto!important`, `left:auto!important`, `right:20px!important` and `bottom:...` with `!important`, overriding those JS position writes. A UI-only resize patch would not restore drag functionality.

## Surgical fix

- Keep the original free-drag handler, including pointer capture and viewport clamp; augment its existing pointermove with a `se-mobile-inspector-dragged` state and actual left/top CSS custom properties.
- In the dragged state, override right/bottom mobile docking, use those left/top values with `!important`, and remove residual transforms. Unmoved panels retain the original right/bottom dock.
- Mobile default size: `min(34dvh,350px)` high and `min(390px,100vw-44px)` wide. Explicit Expand: `min(43dvh,440px)` high and `min(440px,100vw-32px)` wide. Both adjustable by existing controls, with scrolling and side gutters preserved.
- Context workbench defaults are balanced similarly, without replacing the native context system.
- Source geometry, model projects, materials, input field hold-to-edit and 68 packaged asset files are unchanged.

## Release evidence

- 134 patches and 68 preserved assets; compiled HTML 6525097 bytes.
- SHA-256 `fb2ec79211686c3aa4a69deaaa06570b83e8137abf9fb85b2d7a4869a2b1bb7c`.
- Marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_102_BALANCED_DRAGGABLE_PANEL`.
- Production must independently verify hosted HTML and all assets; owner must verify pointer dragging on physical Android.
