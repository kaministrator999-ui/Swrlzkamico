# §wyrl§ Engine · Maker v5.1

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the dedicated §wyrl§ Engine lane. This engine remains deployment-isolated from the main §wyrlz AI Chat/LALM application.

## Naming

The engine maker is now **§wyrl§ Engine**.

Legacy internal names such as `SWRLZ_FORGE_AGENT`, the GitHub folder `projects/swrlz-forge-moba/`, and the Hugging Face Space slug are preserved where changing them would break lineage or integrations. New aliases expose:

- `window.SWYRL_ENGINE_BUILD`
- `window.SWYRL_ENGINE_AGENT`

## Default starter project

The engine now boots into:

**Dragon's Den — Seed Chamber**

This is deliberately an immersive environment, not an open-field game map.

### Seed Chamber layout

- **Wake Nook** — human-scale entry/rest area inspired by the reclaimed under-bridge den
- **Main Chamber** — large council floor with Memory Crystal
- **Creator Alcove** — coding/build workspace
- **Throne Side** — elevated author/throne terrace
- **Dragon Perch Side** — elevated perch for the primary §wyrl§ Dragon
- **Portal Hall Exit** — dormant architectural exit for later travel systems
- **Memory Vault Exit** — dormant deeper-room exit
- **Inference Core Exit** — dormant deeper-system exit
- cavern perimeter, overhead concrete ribs, ceiling, lanterns, and crystal landmarks

There is **no launch/jump pad in the default Den**. Travel mechanics can be introduced later through the intended portal/gauntlet system.

### Scale

The player remains human-scale while the architecture and dragons are deliberately much larger. The chamber uses the full current world footprint, tall cavern wall formations, an overhead ceiling around 10+ world units high, elevated platforms, and dragons scaled well above the visitor pawn.

### Dragon model pass

The old round/flipper silhouette was replaced with a more explicitly draconic low-poly form:

- upright torso/chest
- longer neck
- defined head, snout, and jaw
- large bat-like wings
- four legs
- tapered multi-section tail
- horns, dorsal spines, and glowing eyes

## Project templates

```text
§wyrl§ Engine
├── Dragon's Den — Seed Chamber   ← DEFAULT STARTER
├── Blank Starter World
└── MOBA Arena                    ← example project
```

Each template becomes ordinary editable project state and can be saved/loaded independently.

Project saves now default to `.swyrl.json`.

## Dragon's Den semantic anchors

The starter includes explicit role/tag metadata for later LALM integration:

- §wyrl§ Dragon → primary LALM avatar
- Forge Dragon → world-building agent
- Coder Dragon → coding reasoning agent
- Memory Crystal → memory anchor
- Spatial Voice Anchor → future spatial voice hook
- Forge Workspace Core → creator/world-building interface
- Kamilion Throne → human-author seat
- Portal Hall / Memory Vault / Inference Core exits → future expansion boundaries

These are semantic hooks, not claims that spatial voice or portal travel is already implemented.

## Source integrity

Base v4:

- bytes: `99591`
- SHA-256: `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`

Patch chain:

```text
patches/v4_1.py
patches/v5_projects.py
patches/v5_1_swyl_engine_seed_den.py
```

Final v5.1 candidate:

- artifact: `swyl_engine_v5_1.html`
- bytes: `129398`
- SHA-256: `a653064ce2be625d67d561a1db249a1bb4fa0637dc69377480cf6311e43fdf51`
- marker: `SWYRL_ENGINE_DEPLOY_MARKER: V5_1_SEED_DEN`

## Deployment

Current infrastructure is intentionally preserved for lineage:

- Space: `kamiloki/swrlz-forge-moba`
- live host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`
- workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

The workflow rebuilds exact source, verifies bytes/SHA, syntax-checks the editor module, uploads the static Space, asks Hugging Face for the actual serving host, then requires the current v5.1 marker on the live page before success.
