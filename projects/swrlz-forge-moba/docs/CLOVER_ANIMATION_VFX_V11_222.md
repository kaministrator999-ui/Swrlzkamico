# §E v11.222 — Clover animation and build-spawn particles

Date: 2026-11-02
Authority: `§tart_§E.md`, `RELEASE_PROCESS.md`
Source: `projects/swrlz-forge-moba`
Version: `§wyrl§ Engine v11.222`
Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_222_CLOVER_MOTIONS_BUILD_SPARKS`
Patches: 254; bundled native assets: 68
HTML: 7,550,334 bytes; SHA-256: `27876c460d3c824f23d6628d3207693eb0d2194db9091a72c743122a95e17a35`

## Implemented

- Single new immutable Clover motion definition: Idle, Graze, Walk, Trot, Build and Celebrate; six shared head/tail/leg joint tracks and nine timed keys per clip for native export, with independent scene preview.
- Sheep Model starter loads `sheepAnimations` with authored clips. Model Atelier has a scoped ▶ Preview/■ Stop selector that changes only temporary viewport mesh transforms. Mesh editing, Undo, non-sheep models and saved geometry remain independent.
- Sheep Tag applies shared motion poses over its existing Clover joint pivots after the authoritative simulation, selecting locomotion, construction nod/hoof work or completion cheer. No sheep position, collision or game timer changes.
- Sheep Tag Play produces short spawn sparkle clusters for each sheep, amber construction glints when a native building has actual partial progress, and a teal finish burst when it transitions to 100%. A single bounded `THREE.Points` buffer caps all particle visuals at 96, is explicitly disposed at Stop, and adds no event server/renderer loop.
- Existing source patch chain, scenes, §C deployment, XR camera/control layers and LAN network packets are unchanged.

## Source files

- `runtime/sheep_animation_particles_v11_222.js`
- `runtime/model_atelier_sheep_animations_v11_222.js`
- `runtime/model_atelier_sheep_animations_v11_222.css`
- `patches/v11_222_clover_motion_construction_fx.py`
- `scripts/verify_v11_222_release.py`

## Validation and owner checks

- Narrow feature-branch assembly via existing `build_space.py`: complete 254-patch, 68-asset source, measured exact SHA/bytes.
- Node syntax for both new runtime modules and generated inline JavaScript: PASS.
- Strict source-integrity verifier should match this receipt and the deployed production workflow's exact source identity.
- **Pending actual devices:** On Moto G Power and Quest 2, open sheep-model, play and stop each animation, edit a mesh without accidental model mutation, export model JSON; then open Sheep Tag, enter Play, watch spawn motes, direct a sheep to build, check sparkles during partial progress and finish burst/cheer. Check low FPS/VR menu stability and a two-device LAN house build. These have not been claimed tested.
- No broad automated browser suite was added. Publish only via the existing separate `DEPLOY_REQUEST.json` commit after source validation. A production upload is not user-device acceptance.
