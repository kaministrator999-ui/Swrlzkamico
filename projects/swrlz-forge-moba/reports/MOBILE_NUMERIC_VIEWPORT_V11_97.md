# §E v11.97 · Mobile numeric entry without browser zoom

Status: source packaged, hosted publication to be independently verified; owner-device acceptance pending.

## Evidence and correction

The user provided Android screenshots with a full-page magnification after numeric field focus despite v11.96's 16px text. The build preflight of v11.96 surfaced three viewport strings, but a more precise document-head check demonstrated **one real active viewport declaration**: `<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1" />`. Two additional viewport strings were packaged runtime templates, not active head tags. No assertion of three active meta tags remains warranted.

## New, bounded implementation

- Replace only the real document head viewport tag with `<meta name="viewport" content="width=device-width, initial-scale=1">`; preserve the user's browser pinch zoom.
- Add `runtime/model_atelier_mobile_numpad_v11_97.js`. Coarse-pointer taps on native numeric inputs open an in-editor keypad with no input focus or browser keyboard. The Apply button validates bounds and dispatches a normal bubbling `change` on the native field. Desktop native keyboard entry remains available.
- Keep the v11.96 16px mobile input styling and uniform blank model sphere. Do not alter existing character scenes, textures, mesh data, or historical runtime templates.

## Package receipts

- 129 ordered patches, 68 unchanged bundled assets.
- Compiled index: 6508578 HTML bytes, SHA-256 `9b3725919cce4c3cb135609dc815b449ceac8711658cc276afd6ba2a80882534`.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_97_MOBILE_VIEWPORT_FOCUS`.
- Required independent validation: exact rebuild/hash, module JS syntax, asset digests, live-host source and asset check, then owner Android testing.

## User acceptance

On Android, open New Model Project, tap Scale X to open the in-editor keypad. Enter a new value with Clear then digits then Apply; confirm native model changes, no global browser zoom, Cancel behavior, valid range rejection, and undisturbed tap/drag/pinch viewport navigation. Browser-specific behavior requires physical-device feedback.
