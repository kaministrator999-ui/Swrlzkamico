# §E v11.538 — Futuristic Humanoid, single smooth body

This upgrades Projects → Starter Models → Futuristic Humanoid · Smooth and retains the original robotic-humanoid-mannequin template and direct-link ID.

## Architecture

- One connected, closed sculpted humanoid body shell generated at release time with blended implicit surfaces and Taubin smoothing, not 178 overlapping capsules and spheres.
- Horizontal T-pose; symmetrical anatomy, hand and foot silhouettes, integrated head, neck, shoulders, limbs and pelvis.
- One editable native topologyMesh part: indexed positions, UV coordinates and triangles; native save/clone, sculpt, UV and rigging workspaces remain authoritative.
- Six UV islands for head, torso, left/right arms and left/right legs. UV seam vertices are duplicated as conventional for indexed display meshes; the underlying geometric shell is one component when welded by position.
- One original 1024×1024 embedded PNG color atlas with cool satin-gray polymer, graphite armor-panel motifs and restrained teal accents. No external assets, texture downloads or floating decorative armor parts.
- No per-launch voxel generation on mobile devices: CI bakes the scene as a static native JSON file and ships it with the engine.
- A single mesh does not imply that skeletal bones, skinning or animation have already been configured. Panel zones are texture-painted, not separate native material slots.

## Acceptance

The Python checker scripts/check_futuristic_humanoid_v11_538.py verifies a single part, manifold closed and connected geometry, UV islands, embedded PNG and the native 9000-vertex / 16000-triangle capacity. The Node contract tests/smooth_humanoid_starter_v11_538.cjs verifies the exact baked scene opens through the old starter route, never falling back to the segmented model. The release verifier checks SHA-sealed source and hosted assets. Hardware-level phone/Quest appearance, performance and practical rigging acceptance remain owner testing.

Original geometry and material atlas are authored in authoring/build_futuristic_humanoid_v11_538.py and loaded by runtime/smooth_humanoid_starter_v11_538.js. The existing template ID stays stable, and re-opening a starter does not silently overwrite previously modified user copies.
