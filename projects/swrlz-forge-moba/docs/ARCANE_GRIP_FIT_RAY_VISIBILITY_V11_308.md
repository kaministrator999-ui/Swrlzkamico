# §E v11.308 — Arcane Hands grip fit and hidden controller rays

## Owner observation
The two rigged Arcane Gloves now point the correct way and animate fingers proportionally with analog triggers, but their physical-controller alignment is slightly off. In the Quest screenshot, bright cyan and yellow controller ray lines cut through both gloves and spoil the clean magical hands view.

## Scoped change
**Starter Games → Blank VR · Arcane Hands** is the only project that hides the ray lines or adds glove grip-space mounts.

- A WebXR target-ray pose describes **aim**, which need not match the held Touch controller. When the input source exposes `gripSpace`, mount each rendered glove on `renderer.xr.getControllerGrip(record.index)`. This uses the actual handheld grip pose while retaining the existing handedness selection, v11.307 dorsal-up/thumb-inward alignment, 17-joint rig and analog trigger/grip finger animation.
- Small provisional fit correction: scale the visual glove model from 0.120 to 0.112; adjust local mount from `(±0.014, −0.034, 0.108)` to `(±0.012, −0.022, 0.116)` meters. This is a source-based approximation, **not** a physical controller calibration.
- Fall back to the original target-ray controller if `gripSpace` is unavailable.
- **Hide only** the visible cyan/yellow `record.ray` line objects while Arcane Hands XR is active. Keep the controller records and underlying target ray pose unchanged for spell casting and UI hit-testing; restore line visibility immediately in any other VR project.
- Attach the equipped-spell floating label to the glove's pose source, so it travels with the actual glove rather than with a different aiming-space origin.
- Remove studio-owned grip-space groups when controllers disconnect or the user changes projects/exits VR. Leave all other starter ray models and editor controls untouched.

## Source checks versus owner acceptance
Focused test `tests/arcane_grip_ray_v11_308.cjs` checks that both gloves mount to mocked grip poses, ray lines are visually hidden only in Arcane Hands, rays return for Sheep Tag/other projects, and devices lacking gripSpace fall back to the target-ray parent. The verifier checks complete build integrity, preserved spell-cast origin and the existing XR loop.

**Owner Quest 2 test still required:** hold controllers relaxed, open/close fingers, rotate wrists, cast both sides, change game to confirm ray lines restore, and check whether glove cuffs/knuckles sit naturally. No virtual test verifies actual physical comfort.

## Implementation
- Append-only `patches/v11_308_arcane_grip_fit_hide_rays.py`
- Existing glove model source, historical patches and other game/editor bindings remain unchanged.
- `scripts/verify_v11_308_release.py` and `source-manifest.json` describe the sealed build.
