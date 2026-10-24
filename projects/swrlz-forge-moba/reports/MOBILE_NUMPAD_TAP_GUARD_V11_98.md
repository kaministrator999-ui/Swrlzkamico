# §E v11.98 · Touch keypad immediate-dismiss repair

## Reproduction and root cause

On Android, the newly added number pad visibly opens and immediately disappears. Source code showed the pad was made visible during `pointerdown`, while the backdrop accepted a subsequent synthesized `click` from that same input tap, closing the pad. A mobile touch simulation reproduced this directly, including a zero-detail synthetic click, disproving an initial assumption that `detail===0` always indicates keyboard activation.

## Targeted fix

The pad records which actionable element, if any, received the originating pointerdown. The click handler honors a click only if it matches that actionable element. A keyboard click is accepted independently only for the currently focused button. A click landing on the newly appeared backdrop from the input's original touch is ignored. Normal shade dismissal, digit input, Apply, Cancel, clear and numeric field change dispatch remain intact.

No changes to model mesh data, old runtime patches, 68 packaged assets, saved objects, viewport pan/orbit, or desktop input behavior.

## Verification

- Standalone Chromium / Playwright mobile touch simulation verified the previous failure, then passed opening, digit selection, native Apply and subsequent backdrop cancellation using the corrected gesture gate. This is an isolated control test, not full-engine or physical Android owner acceptance.
- v11.98 source preflight measured exactly **6509696** compiled HTML bytes, SHA-256 `9b5033ee9bfcd3714ee4e52c0dd4dc46c2f06b78fb87eae441ffeac33aabe76d`; 130 governed patches, 68 unchanged packaged assets.
- Production deployment remains separate and requires terminal hosted verification.
- Owner acceptance: tap any Scale numeric input on Android. Keypad must remain open, accept Clear/0.7/Apply, update the model, and close with Cancel or backdrop when deliberately tapped.
