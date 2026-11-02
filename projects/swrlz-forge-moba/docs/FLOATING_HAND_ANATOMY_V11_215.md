# §E v11.215 — Floating Hand anatomical sculpt refinement

## Owner request
Four mobile orthographic-ish inspection screenshots revealed an overly flat hand, thin slab-like side profile, a straight edge opposite the thumb (hypothenar / ulnar edge), and a thumb that looked attached to a palm rather than flowing naturally out of it. Improve actual 3D geometry in the **Floating Hand · Arcane Glove** native Model Atelier starter rather than making a reference image or viewer.

## Authored changes
- Appended a scoped hand-anatomy geometry builder at runtime/model_atelier_hand_anatomy_v11_215.js, injected by patches/v11_215_floating_hand_anatomy_upgrade.py.
- Reconstructed the signed-distance field of only this starter's connected palm/wrist/four-finger/thumb mesh: deeper rounded palm with convex dorsal arch, blended thenar thumb pad, extended thumb saddle, rounded hypothenar pad on the opposite side, curved ulnar edge, properly forward-angled two-section thumb, and subtly splayed/tapered knuckle-shaped fingers.
- Increased depth sampling bounds to enclose the anatomy, and tightened voxel step modestly from .049 to .047 for smoother transitions.
- Moved the palm medallion/glyphs and dorsal shield/runes out to remain visible on the deeper glove. Preserved the original reference-inspired purple/silver identity, hover rings and editable object groups.
- Added independently editable anatomical crease/rim parts and knuckle details. Entire model is native topologyMesh and standard Model Atelier materials: no remote assets, new render loop, XR input changes, altered validator, rigging or skinned animation.
- Scope is strictly fresh Floating Hand starter instantiation. Existing saved projects, Dragon Den, Sheep Tag, Quest camera/quick wheels and other starters are unchanged.

## Focused browser acceptance
GitHub Actions run #41468763144 compiled the v11.215 source and launched Chromium at phone viewport 390 x 844 with the real modeler.html?project=floating-hand-glove route.

Actual native editor status: open=true, active=true, 53 editable parts, 10 groups, 16,938 vertices in the connected organic glove, no browser console/page errors. Selected mesh cross-section evidence:
- Central palm y 1.53–1.82: 0.718 units front-to-back thickness (z -0.352 to +0.366).
- Opposite-thumb ulnar edge y 1.42–1.90: outer x +0.755 (rounded pinky-side contour).
- Thumb region x below -0.83, y 1.56–2.13: projects forward to z +0.352 and out to x -1.336.
- Exactly four new finger palmar-flexion seam pieces and two ulnar-edge armor pieces.

This shows geometry exists and loads; artistic appearance and performance on actual Moto and Meta Quest 2 still require owner hands-on review.

## Sealed release input
- Ordered patch count: 247; packaged assets: 68
- Generated HTML: 7,490,431 bytes
- SHA-256: 90095eecc2a4e2af538d9332966108c7bede67d6cb041c329219ad475f3cdf1d
- Version: §wyrl§ Engine v11.215
- Root source and deployment request must reference the exact above bytes/hash.

This patch intentionally does NOT claim baked normal/roughness/metalness textures, UV painting, a skeleton, animation rig or live Quest hand tracking. Those remain independent work.
