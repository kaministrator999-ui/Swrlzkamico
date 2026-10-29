# §E v11.96 · mobile numeric input focus and spherical blank starter
Date: 2026-10-23 (America/Chicago)
Status: source candidate / owner device acceptance pending

## User-reported defects
- On Android, tapping the native Model Atelier numeric transform field prompted full-browser page magnification, obscuring the editor. The 12px source field size contributed to Chrome's standard small-text focus zoom.
- The New Model Project default blockout was nonuniform, `[0.5, 0.6, 0.8]`, causing the egg silhouette.

## Scoped source fix
- Only New Model Project's seed sphere gets equal X/Y/Z scales `[0.6,0.6,0.6]`. Existing models and imported saves are untouched.
- Model Atelier text/numeric/select/textarea controls receive a 16px minimum on coarse-pointer and narrow viewports. No viewport lock, user-scalable restriction, browser zoom suppression, other projects or engine model geometry changes.
- Release patch: `patches/v11_96_mobile_input_round_blank.py`; verifier: `scripts/verify_v11_96_release.py`.

## Build receipt
- 128 ordered patches; 68 source assets unchanged.
- Exact compiled index.html bytes: 6502021.
- SHA-256: `c779e0889632a773341a78cbf0c3162932e5c7c9a6da17b20a60fc1166b3f3f9`
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_96_MOBILE_INPUT_ROUND_BLANK`
- Package checksum measured in the preflight CI build and recorded into the manifest; a subsequent exact-integrity deployment verification must pass before declaring the site live.

## Acceptance / limitations
- The actual phone's browser zoom behavior must be checked by the owner after deploy, including field focus/keyboard open and ability to pinch-zoom intentionally.
- A geometrically uniform primitive does not ensure the user's camera is centered or orthographic; test several view angles.
- No claim that native mesh editing, finger-hole booleans or other functionality has been added.
