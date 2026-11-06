# §E v11.296 — Hooded Vanguard reconstruction

**Owner request:** After the v11.294 loader repair, actual Android appearance remained unacceptable: disproportionate face/chin, ear bulges, wrong mouth, bowl hair, a hood that looked like a flat panel, ball-shaped shoulders and mitten hands. Rebuild the knight based on character modeling, UV and PBR workflow lessons; no weapon or bird.

**Implementation:**
- Keep the old v11.291 generator and historical patches as-is. Replace only fresh Hooded Vanguard Starter Models construction, under the same starter ID.
- Rebuild a continuous head with anatomically restrained jaw/nose and UV-anchored eyes/lips; layered tapered hair with face-framing locks; a wrapping fabric hood shell and forward curved brim.
- Build a separate neck scarf and draped chest shawl, contoured breastplate and shoulder panels, belt, teal fabric coat tails, shaped boots and two **five-fingered** glove meshes (joined palms/digits per hand).
- Use an explicit UV atlas on every native topology mesh. Generate 384px albedo/normal/roughness textures with shared cached CanvasTexture instances, distinct painted trim for different surface categories, normal relief derived from corresponding painted height maps.
- Retain model-level editability; keep anatomy/clothing separate only at natural editing/animation boundaries. No extra decoration/confetti pieces.
- Preserve historical saved models, all other starters, native Chat loft v11.295 fix, tools, history, and VR.
- No bird, weapon or claim of full-body skeletal rig. This is a **static character rebuild**.

**Validation gates:** Exact assembly and hash, JavaScript parse, source receipt and assets, new starter scene factory geometry/UV sanity and native Model Atelier load when run. Owner Android/Quest appearance acceptance is a distinct pending step. Correct any failures; don't claim visual parity with the reference until actually inspected.

**Key sources:** runtime/hooded_vanguard_rebuild_v11_296.js; patches/v11_296_vanguard_rebuild.py; scripts/verify_v11_296_release.py.
