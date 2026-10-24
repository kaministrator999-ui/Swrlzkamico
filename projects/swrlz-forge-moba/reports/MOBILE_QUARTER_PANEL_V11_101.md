# §E v11.101 · Genuine compact phone inspector

## User-reported regression

After v11.100's "compact" mobile tool redesign, the inspector still obscured about half of the phone screen. The actual source defined 49dvh for default and 62dvh for expanded—both inconsistent with the intended compact user workflow. Existing adaptive mobile rules used strong selectors and !important declarations.

## Bounded fix

- New forward patch `patches/v11_101_compact_quarter_panel.py` defines higher-specificity touch inspector rules after v11.100's CSS.
- Default floating inspector: maximum 26dvh / 255 CSS pixels high, 320 CSS pixels wide. Expanded inspector: maximum 38dvh / 385 CSS pixels high, 375 CSS pixels wide.
- Context workbench sizing reduced accordingly while preserving 52px compact/minimized state.
- The left/right internal scrolling gutters, 380ms touch-and-hold numeric editor, sphere starter, shaders and all modeling actions remain unchanged.
- Desktop mouse interfaces unaffected; all previous patches and 68 bundled assets preserved.

## Exact release evidence

- **133 ordered patches**, **68 preserved bundled assets**, **6521969 HTML bytes**.
- SHA-256 `011f44a659a6f0a76d482ba375476735b5f43c038082d3321f19f24bd2416162`.
- Marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_101_COMPACT_QUARTER_PANEL`.
- Source build measured at the fail-closed preflight guard; governed deploy and live artifact verification are separate gates.

## Owner acceptance

Inspect the native Sculpt tool menu on Android, confirm default panel is clearly below half screen in height, vertical swipe margins continue working, Expand makes only a modest increase, Shrink returns to compact size and a short hold invokes the existing numeric keypad.
