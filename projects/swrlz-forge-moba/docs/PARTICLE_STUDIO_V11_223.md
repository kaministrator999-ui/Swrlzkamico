# §E Particle Studio · v11.223

**Owner request:** A creator and editor for reusable particle effects inside §E.

- Entry: Game Editor viewport toolbar → **✨ Particles**
- Native version: §wyrl§ Engine v11.223
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V11_223_NATIVE_PARTICLE_STUDIO`
- Source: `projects/swrlz-forge-moba/`
- Built: **7587913 bytes**, SHA-256 `db3ff358295c7b02d1b55d40973d328534a0686b822d6906549ab6f83ea9d230`, **255** ordered patches, **68** existing native assets

## What to try

1. Open any game/starter scene and select **✨ Particles** in the viewport toolbar.
2. Choose one of ten presets: Arcane Motes, Flame, Smoke, Sparks, Snowfall, Rain, Healing Wisps, Building Magic, Portal Shimmer or Confetti.
3. Choose **Create**; edit the 3D emission shape, rate, burst count, lifetime, speed, direction, spread, gravity, drag, size, spawn radius, beginning/ending color and blend mode. Controls are responsive numeric+range inputs with strict bounds.
4. **Preview all / Stop preview** controls continuous effects in edit mode. **Burst now** tests a one-shot emitter. Press Play/Simulate to render authored emitters with the same engine frame.
5. Position an emitter with X/Y/Z or **Place in view**. Select a native actor then **Attach selected actor** to make the source move with that actor. Detach restores a world-space source position. Already-born particles remain in world space.
6. Duplicate and remove emitters, Undo/Redo changes, and **Save Project**. Import/export a versioned VFX JSON library with bounded validation.

## Source contract

- `runtime/particle_studio_core_v11_223.js`: versioned scene emitter schema, finite field bounds, strict import validation, atomic project/history mutation, GPU point cloud allocation, update and cleanup, actor-local attachment, and public `window.SWYRL_ENGINE_PARTICLES` API.
- `runtime/particle_studio_ui_v11_223.js`: draggable, touch-friendly editor, predefined presets, parameter inspector, preview, placement/attachment, safe import/export, public `window.SWYRL_ENGINE_PARTICLE_STUDIO` UI.
- `runtime/particle_studio_v11_223.css`: mobile and desktop layout with independent scrolling and no replacement of toolbar controls.
- `patches/v11_223_native_particle_studio.py`: append-only patch into **one** native tick and the normal game editor UI; version, marker, notes and integrity lineage governed by manifest.
- `scripts/verify_v11_223_release.py` and `scripts/test_particle_studio_v11_223.js`: strict release digest/asset/source checks, plus focused emitter lifecycle validation.

The scene-level `currentProject.particleStudio` property is included by existing `projectData()` snapshots, restored via `applyProjectMeta()`, and preserved in native project level snapshots. No geometry is added to authored `scene.actors` and no extra gameplay mutation or network packet is introduced. Runtime particle resources are allocated only during display, disposed when projects change, and never saved to project JSON.

**Performance:** Max 12 emitters; one `THREE.Points` draw call per active emitter; up to 96 motes per emitter and 576 total. Particles obey one existing renderer and XR animation frame; inactive previews hide particles.

## Limitations and owner acceptance

This is a practical point-particle VFX creator, not a texture-atlas flipbook editor, fluid simulation or node-based GPU VFX compiler. Initial effects from the previous Sheep Tag release are preserved independently; they are not automatically migrated into editable preset assets. Particle Studio currently authors the **Game Editor scene**, not the separate Model Atelier mesh viewport.

**Source acceptance:** v11.223 candidate assembled from 255 ordered patches and 68 assets, with identical routed Game/Modeler HTML, focused JavaScript syntax, and a mock runtime lifecycle/preview/validation smoke. Deployment proof is a distinct final-request workflow and served-source audit. Real Moto G Power and Quest 2 frame rate, touch/VR overlay interaction, emitter visibility in gameplay, and visual style acceptance remain for the owner to test. No exhaustive browser suite was used.
