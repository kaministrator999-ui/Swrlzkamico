# §E v11.99 · Mobile scroll and panel ergonomics

## Owner-observed issue

In a real Android session after v11.98, the Model Atelier sculpt inspector was difficult to scroll by touch and multiple tool menus appeared too small. The user could not comfortably access the brush settings needed for the bowling ball project.

## Source diagnosis

- The original floating tool dock v11.60 sets the inspector background to `pointer-events:none`; interactions with empty panel regions can fall through, making scroll gestures difficult.
- The earlier adaptive mobile layout uses a narrow 700px media trigger, and on certain phone browser configurations the user sees the desktop tool rail and small panel.
- Multiple copies of the mobile supervisor exist within the assembled runtime; the built v11.99 patch updates matching responsive triggers together rather than modifying old source files.

## Patch boundaries

- New patch `patches/v11_99_mobile_scroll_size.py`: runtime CSS for coarse-pointer and width <=980px menus, with pointer-events:auto on inspector, touch-action:pan-y, overflow-y:auto, touch momentum, bigger tap targets and larger default panel heights.
- Widen existing adaptive mobile media/JS trigger to accommodate touch browsers that report desktop-like widths. Make the tool rail horizontally swipeable.
- Full-size panel remains locally scrollable, and earlier panel controls remain connected to native model editing. No geometry or character starter changes.

## Measured release

- 131 governed patches, 68 preserved assets.
- Exact built HTML bytes: 6513741
- SHA-256: `726cae0905ef5e2f8a381bebc109856b618451c68f7fa4afb5a0401332d2c783`
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_99_MOBILE_SCROLL_SIZE`
- Governance: separate final DEPLOY_REQUEST after sealing and independent hosted HTML/assets verification before declaring live.
- User acceptance still required: swipe blank inspector background and brush content vertically, tap inputs and buttons, swipe tool rail horizontally, verify mobile sheet height and canvas orbit behavior.
