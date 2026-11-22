# §E v11.542 — Futuristic Humanoid: geometry-aware paint atlas

## Observed owner behavior

The owner inspected the v11.541 single-body five-digit humanoid in Model Studio on Android and exported a cyan 2048 px UV candidate. The exported candidate showed two long tapered conical-looking forms and undersized unused panels. The editor said, "The model still uses the old UVs until Apply." This is a candidate from the **experimental v11.503 front/back/brim projection**, not evidence that the native starter's original UVs were already replaced.

The source algorithm v11.503 was built for a hat/rim-like silhouette. A whole humanoid with a torso, two arms, fingers and legs violates its projection assumptions. Applying it would also detach the existing painted PNG.

## Implementation

- The native starter keeps **one continuous, watertight geometric shell** and the exact v11.540 triangles, position coordinates, five-digit hands and project ID.
- At build time, xatlas computes a genuine mesh-parameterized UV atlas with chart seams and padding. These are UV seams only; geometry remains one connected mesh. The authored scene is stored at \`scenes/model-atelier-futuristic-humanoid-v11-542.swyrl.json\`.
- The previous 1024 px satin/graphite/teal texture is **reprojected by geometric triangle correspondence** to the new UV coordinates. It is not silently reused with the wrong mapping, nor wiped.
- A matching 2048px wireframe diagnostic PNG is produced at \`assets/models/futuristic-humanoid-v11-542-uv-guide.png\`. The editor's standard Current UV Guide and Surface Directions are still authoritative for the selected mesh.
- The experimental v11.503 candidate is disabled **only** for this humanoid body, with a clear explanation to use the actual current UV and distortion tools. Other model types retain their existing projection workflow.
- Atlas computation and PNG baking run in GitHub Actions, not on Moto or Quest. At runtime, the new starter loads a single ordinary native topologyMesh + embedded UV PNG.
- Previous v11.540 source, historical starter assets and user-saved copies remain untouched. Rig skinning, intentional quad retopology and mobile/Quest visual quality are still distinct acceptance questions.

## Tests

\`scripts/check_humanoid_uv_atlas_v11_542.py\` compares every welded 3D geometric triangle with v11.540, verifies closed and connected surface topology, UV area and density, the 1024px embedded PNG, 2048px guide and existing source limits. \`tests/humanoid_uv_starter_v11_542.cjs\` executes the native project route and experimental-UV guard. The v11.542 release verifier also checks other model, account and VR startup regressions and the exact 519-patch source hash. The static delivery source and hosted CDN must pass the separate publish stage.

## Device acceptance

Open Projects → Starter Projects → Starter Models → Futuristic Humanoid · UV-Ready Hands. Select the body, open the UV Editor, export **Current UV Guide** (not experimental candidate) and examine the real chart layout. Use Painted Preview and UV distortion heatmap to check finger, palm, torso and leg texel density. If satisfactory, use the UV image to paint new material artwork. Apply should never be required merely to use the shipped factory UVs.
