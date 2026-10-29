# §E v11.100 · Compact expandable menu and deliberate numeric editing

## Real-device input

Owner tested §E v11.99 on Android. While its enlarged panel scrolls, the near-full-width inspector is too big. Requested: return to original compact dimensions with a modest user-controlled Expand action, leave clear left and right strips for safe scrolling, and require a brief press-and-hold before a number field opens its editor.

## Source change

- A compact floating inspector uses `width: min(410px, 100vw - 40px)` and `height: min(49dvh, 470px)`, avoiding edge-to-edge overlay. The user can toggle a larger 62dvh / 100vw-40px panel by tapping Expand/Shrink in the original inspector handle. The existing Context and Hide buttons remain.
- Both left and right inspector interior padding are 23px and accept touch-scrolling. The native field controls are inset away from these gutter areas. Context panel uses similar side margins and inset scrolling.
- On coarse touch hardware, native numeric fields no longer open a dialog on pointerdown. A 380ms hold without movement greater than 10px triggers the same existing custom keypad; pointerup, movement, cancel and scrolling abort the pending hold. Quick taps and press events do not focus the browser input. Desktop keyboard inputs and the keypad's original Apply/Cancel handlers remain unchanged.
- Only a new forward release patch is added. Historical patches, scene/model data, assets, export, and saved geometry remain unchanged.

## Build / acceptance

- 132 ordered patches; 68 preserved assets; generated HTML 6519939 bytes, SHA-256 `aca02a1034c5ce79a70b024a2aa692344894493c9b4c79bc1d51b50d25a0eed1`.
- Marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_100_HOLD_SCROLL_GUTTERS`.
- Preflight measured artifact hash; final package verifier, Node syntax and served source/asset integrity are distinct deployment gates.
- Owner Android tests: scrolling with the left and right margins, accidental taps vs. 380ms hold, sliding over numeric boxes to scroll, larger panel after Expand and Shrink, normal sculpt controls, keyboard focus avoidance and sphere retained.
