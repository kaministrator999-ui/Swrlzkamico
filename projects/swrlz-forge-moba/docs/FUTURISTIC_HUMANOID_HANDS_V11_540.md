# §E v11.540 — One-body anatomy and genuinely visible hands

This is the follow-up to the original v11.537 178-piece mannequin and v11.538 unified smooth body. The user tested v11.538 on the Moto and reported that the hands were still pointed and the anatomy looked melted. This update targets those observed failures.

## Baked geometry and UV approach

- One manifold *geometric* surface with a continuous torso, head, arms, five-digit hands, pelvis and legs. This is a true indexed native topology mesh, **not** separate primitive parts grouped to look like one.
- Each hand contains four separate tapered finger shafts and one opposable thumb, all integrated into the wrist/palm. Four visibly separated finger silhouettes are checked on each hand at x > 2.53, and the lower opposable thumb at y ≈ 3.40 is checked independently.
- Selectively dense sampling around the horizontal hand region; low-slope body regions remain cheaper, then topology-preserving edge collapse reduces to native device limits (≤9000 indexed UV vertices; ≤16000 triangles). A manifold and connectivity test runs before and after simplification.
- Reworked shoulder caps, chest-to-waist taper, hips, thigh/calf and ankle silhouettes to reduce stacked-ball / blob look. Neutral T-pose remains intact.
- One six-island UV set and the existing original 1024px graphite/satin/teal PNG atlas. UV seam duplication is permitted but the underlying geometry is welded and closed. These are **not** separate floating armor surfaces.
- All authoring (NumPy, SciPy, VTK, scikit-image) runs in GitHub Actions, not on Moto or Quest. Only the final scene JSON is served.
- Remains a Modeling Studio starter and is not promised to be skin-weighted or skeletal-rigged. Existing personal saves are not overwritten.

## Files and tests

- Original procedural source: authoring/build_futuristic_humanoid_v11_540.py
- Native baked scene: scenes/model-atelier-futuristic-humanoid-v11-540.swyrl.json
- Runtime loader: runtime/futuristic_humanoid_five_digit_v11_540.js
- Integration patch: patches/v11_540_humanoid_five_digit.py
- Geometry/UV/manifold/hand test: scripts/check_futuristic_humanoid_v11_540.py
- Starter route and native-load test: tests/futuristic_humanoid_five_digit_v11_540.cjs
- Source and packaging: scripts/verify_v11_540_release.py and scripts/package_static_delivery_v11_540.py

For device acceptance, open Projects → Starter Models → Futuristic Humanoid · Detailed Hands (same template ID and direct link). Check front and rear at close zoom, palms and four finger tips + thumbs, wrist contour, torso and pelvis silhouette, and stable mobile/Quest FPS. Automated tests do not substitute for visual owner acceptance.
