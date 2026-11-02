# §E v11.216 — Move the sheep while choosing a building

## User correction
A v11.214 attempt to prevent camera drift blocked Sheep Tag left-stick locomotion and world-follow movement whenever A/X's quick selection wheel opened. That is incorrect: players must be able to **keep running while they choose buildings or skills**.

## Correct behavior
- Hold **A** (building selector) or **X** (skill selector); menu stays head-relative and yaw-upright.
- LEFT stick always moves sheep via the existing Sheep Tag collision-checked movement and game authority, including while either wheel is showing.
- RIGHT stick chooses a wheel option without rotating/zooming the game camera. This is already separated in the v11.204 `se192Stick` wrapper, while `se204WheelStep` receives right raw gamepad axes.
- The actual game camera still follows the sheep's world movement smoothly during quick selection rather than sitting stationary and snapping to the sheep when the wheel is released.
- Wheel UI keeps v11.214 single-pointer ownership: no extra ground beam or twin controller aura during selection; regular building guidance returns afterward.
- No gameplay house rotation introduced; no changes to editor gizmos, LAN/host authority, native WebXR tracking, or Quest OS compositor.

## Implementation scope
Small append-only runtime adapter overrides **only** v11.214's locomotion cancellation, left-stick suppression and camera-follow suppression by returning control to the original `se214PriorStickIntent` and `se214PriorFollow`, which are already source-backed. It preserves the v11.214 menu positioning, ray suppression and other existing wrappers.

## Verification
Run `node projects/swrlz-forge-moba/tests/test_v11_216_move_while_wheel.cjs` and existing v11.214/211/210/209/204 regressions; seal the deterministic 248-patch 68-asset build before release. Real Quest 2 hands-on test: keep left stick held while bringing up A and X, verify movement never pauses, both wheels stay upright/front-of-view, right stick chooses the item without camera orbit, and only one world guide appears outside the wheel.
