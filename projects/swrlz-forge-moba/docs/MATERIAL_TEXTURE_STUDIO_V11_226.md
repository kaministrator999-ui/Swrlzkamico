# §E v11.226 · Material & Texture Studio and four native workspace tabs

**Preserved baseline:** v11.225 Astra Wolf native rig / Sheep Tag animation patch precedes this studio patch; prior Particle Studio stays active. Wolf visual hardware acceptance is pending.

**Owner request:** Build a material and texture editor/creator inside §E; promote the existing Particle Studio and new Material & Texture Studio into their **own top-level workspace tabs** beside Game Engine and Modeling.

**Exact source:** 7673681 UTF-8 HTML bytes; SHA-256 `d078e04df1f1f140289960f6e080ac0952aa080a302d669c7bc80c208efa64ce`; 258 ordered patches, 68 existing assets.
**Marker:** `SWYRL_ENGINE_DEPLOY_MARKER: V11_226_MATERIAL_TEXTURE_STUDIO_TABS`
**Routes:** main game and modeler pages remain `index.html` and `modeler.html`; new studio tab URLs share the game page with `#studio-particles` / `#studio-materials` hashes. No non-existent static HTML pages or second native renderer.

## Particle Studio workspace

- Four native tabs appear in both Game and Modeler. Particle Studio gets its own full-viewport workspace and docked touch inspector; original standalone floating ✨ Particles entry routes to the tab. Legacy 10 effect presets, particle schema, 12 emitter/96-per emitter/576 overall cap, GPU point clouds, actor attachments, current-project persistence and VFX import/export remain unchanged.
- Switching tabs retains the same game scene/WebGL context and modeler scratch document. Native scene continues as the 3D effect preview; no new game tick or renderer.

## Material & Texture Studio workflow

1. Click **Materials & Textures** in the top workspace tabs.
2. Create a preset material (steel, gold, wood, stone, masonry, fabric, leather, arcane glow, glass or ceramic); duplicate/delete designs.
3. Edit base and accent colors, emissive color, roughness, metalness, glow, opacity, pattern complexity, seeded variation and UV repeat.
4. Choose one of eight textures: solid, checker, stripes, noise, brick, wood, dots, or image. Generated textures are 256×256; procedural layers use a fixed seeded generator.
5. Paint directly on the texture preview with touch/stylus/mouse; change brush color and width, undo last stroke or clear paint. Painting is stored as bounded normalized 2D stroke points and re-rendered deterministically.
6. Import local PNG/JPEG under 750 KB (decoded dimensions max 4096 and downsized to 256×256, encoded PNG must fit a 360,000-character project limit), or export the rendered PNG. Export/import a strict versioned material library JSON for reuse; importing clears foreign actor assignments.
7. Choose the intended native **Game Editor scene actor**, then **Apply material** to assign actual PBR materials in the shared Three.js scene. **Restore original** removes the assignment without deleting the asset. The material sample sphere appears in the native viewport while this tab is active.

## Architecture and safety

- `runtime/material_texture_core_v11_226.js`: strict schema `swyrl-material-studio-v1`, color/number bounds, imageData cap, max 12 materials, max 160 strokes and 220 normalized points each, unique material IDs, assignment validation, deterministic 256×256 CanvasTexture generation, MeshStandardMaterial derivative and original material restoration. Project definitions and actor assignments reside in `currentProject.materialStudio`.
- `runtime/material_texture_editor_v11_226.js`: touch-friendly PBR controls, texture paint, actor selection, PNG/image import/export and portable JSON library import/export.
- `runtime/studio_workspace_tabs_v11_226.js`: four tabs with keyboard navigation, in-place workspace switching and history-backed fragment routes, keeping Game and Modeler controllers authoritative.
- `runtime/studio_material_texture_v11_226.css`: dedicated studio workspaces, live 3D viewport, mobile bottom-sheet inspectors and no unrelated controls loaded.
- `patches/v11_226_material_texture_workspace_tabs.py`: append-only patch, source metadata, release notes and one material refresh call inside existing native frame. Does not alter native actor serialization.
- `scripts/test_material_texture_v11_226.js`: isolated material authoring, validation, procedural texture construction, assignment/reversion and source project switch checks.
- `scripts/verify_v11_226_release.py`: governed source/asset/version proof.

GPU textures, material clones and temporary sample spheres are allocated at runtime only, never written into actor JSON. Material assignment is explicit and Undo/Redo-aware. Existing cloth/hair/skin textures are preserved until a user explicitly applies a new material; **Restore original** resets the baseline.

## Honest boundaries

This is a real point-and-paint material creator with PBR controls and procedural base patterns, not a full node-based shader editor, UV unwrapping or real-time raytraced renderer. Direct assignment to a Model Atelier individual mesh part is not in this release; exported texture PNG and material JSON can be reused through asset workflows. Creator UI and source integrity are validated by targeted checks, not a full Quest 2 or Android visual run. The owner still needs to confirm touch sizing, gallery use, real scene shading, and VR usability on physical hardware.
