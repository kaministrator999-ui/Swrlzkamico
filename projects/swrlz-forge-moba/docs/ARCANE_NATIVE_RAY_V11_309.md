# §E v11.309 — Arcane controller rays: native aim and complete beam hiding

## Quest observation and source diagnosis
After v11.308, owner reported that the visible §E controller beams pointed conspicuously left and a little above the native Meta Quest pointers. Two distinct graphics subsystems exist:

1. `se181XRMakeController` creates the legacy thin `record.ray` Line.
2. `se192PrepareRay` creates a **different** tapered `record.se192.beam` and `record.se192.dot` reticle, parented to a pivot that uses saved `swyrl.xr.aim.v1` per-controller yaw trim.

v11.308 hid **only** the first Line, so the custom tapered 3D beam was still visible, and its rendered axis could disagree with spell firing (which already uses `record.controller`'s raw target-ray pose).

## Scoped repair
Only in **Blank VR · Arcane Hands** while WebXR is active:
- Hide both independent ray visuals (legacy Line and newer tapered beam/reticle), including a post-frame guard after other render adapters.
- Set the Arcane ray helper's pivot yaw to zero, so relevant VR ray hit tests align with the untrimmed WebXR target-ray controller pose. Do **not** alter headset/controller XR transforms.
- Preserve native gripSpace glove placement from v11.308, both analog-trigger finger puppets, original 17-joint glove rigs, left/right spell selection and casting, and all existing VR input.
- Outside this starter, restore existing Spatial Editor beam ownership and each controller's saved yaw calibration. Sheep Tag and editor UI ray functionality remain unaffected.

## Verification boundary
`tests/arcane_native_ray_v11_309.cjs` exercises two controllers with the original ray renderer mocked, confirms both beam types and reticles are suppressed (even if another renderer re-enables them), tests untrimmed Arcane aim, and verifies ray visibility/owner-saved offsets return when changing project. Source build, inline JS and exact artifact integrity are verified before deploy.

The Meta operating system's native pointer pose is not exposed here for direct numerical calibration. A source-aligned WebXR ray is the available baseline; real Quest 2 visual comparison remains an owner acceptance test.

## Files
- Runtime: `runtime/arcane_ray_alignment_v11_309.js`
- Append-only patch: `patches/v11_309_arcane_native_ray_aim.py`
- Focused smoke: `tests/arcane_native_ray_v11_309.cjs`
- Release verifier: `scripts/verify_v11_309_release.py`
