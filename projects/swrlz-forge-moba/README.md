# SWRLZ Forge · Editor v5

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the Forge engine workflow. Forge remains deployment-isolated from the main §wyrlz AI Chat/LALM application.

## v5 architecture change

The engine is no longer the MOBA.

Forge now owns a **project system**, and game-specific content is loaded as a project/template:

```text
SWRLZ Forge engine
├── Starter World          ← default
├── MOBA Arena             ← example project
└── Dragon's Den           ← example project
```

The existing folder name `projects/swrlz-forge-moba/` is retained for deployment/source lineage, but MOBA semantics no longer own the editor startup state.

### Starter World

The default project is a neutral sandbox with terrain, river/scenery, a playable pawn, a physics prop, and component examples. MOBA waves, bases, paths, and validation rules are inactive.

### MOBA Arena example

The original Forge three-lane map is preserved as `MOBA Arena Example`. Creating that project restores lane paths, bases, towers, camps, minion spawning, tower combat, and MOBA-specific build validation.

MOBA prefabs were removed from the always-visible core sidebar and moved to `/Examples/MOBA` in the Content Drawer.

### Dragon's Den example

Dragon's Den is a separate editable project containing:

- §wyrlz Dragon — primary LALM avatar
- Forge Dragon — world-building agent avatar
- Coder Dragon — coding-reasoner avatar
- Kamilion Throne — human-author seat
- Council Rune Dais
- Memory Crystal
- Inference Core
- Spatial Voice Anchor hook
- Code Portal
- World Portal
- Arcane rune crystals
- cavern perimeter
- visitor/player pawn
- Ascension Pad

New actor types include `dragon`, `crystal`, `portal`, `throne`, and `pedestal`. Project actor metadata now serializes `role`, `tags`, and `visualColor`, giving the later LALM/voice layer explicit world anchors without pretending spatial audio is implemented yet.

## Project workflow

Use **Projects** in the editor to create a template. Each created template becomes normal editable project state.

```text
Create template
→ edit actors/components
→ ghost → Bake
→ Save .forge.json
→ Load later
→ Simulate / PIE
→ Export standalone HTML
```

Project JSON now includes:

- project name
- template
- project kind
- environment preset
- editor state
- actors/components
- paths
- scene settings

Build validation is project-aware. MOBA rules only run for MOBA projects; Dragon's Den has its own checks; sandbox projects use generic checks.

## Runtime separation

MOBA wave/minion/tower runtime systems only execute when `currentProject.kind === 'moba'`. They remain engine capabilities available to the example without leaking into every project.

The exported playable HTML follows the same project-kind gate.

## Agent surface

`window.SWRLZ_FORGE_AGENT` advances to `forge-agent-v3` and exposes project inspection/creation in addition to actor editing, components, validation, camera control, terrain snapping, and Bake.

## Source integrity

Base v4 source:

- bytes: `99591`
- SHA-256: `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`

Patch chain:

```text
patches/v4_1.py
patches/v5_projects.py
```

Final v5 source:

- artifact: `swrlz_forge_v5.html`
- bytes: `120501`
- SHA-256: `c5b44363460fc29ec3a119967c082c1fd95b035d781c50a4affa9d8ecd686593`
- marker: `V5_PROJECT_TEMPLATES_DRAGONS_DEN`

The v5 candidate was materialized and Node syntax-checked against the exact reconstructed v4.1 source before entering the release branch.

## Deployment

Target Space remains `kamiloki/swrlz-forge-moba` for continuity.

Live static host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`

The deployment workflow must rebuild exact source, verify final integrity, upload the dedicated static Space, then fetch the actual Hugging Face-reported host and prove the v5 marker is live before success is reported.
