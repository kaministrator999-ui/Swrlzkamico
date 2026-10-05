# SWRLZ Forge · Unreal-Inspired Editor Pass v3

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the Forge engine workflow. The canonical router is [`/§tart_§E.md`](../../§tart_§E.md). It reconstructs the current engine source/deployment state and keeps Forge development separate from the main §wyrlz AI Chat/LALM deployment lane.

SWRLZ Forge is a browser-native 3D game editor/runtime prototype. The v3 pass deliberately studies Unreal Editor's proven interaction model—viewport + outliner + details + content browser, Actor/Component composition, world/local transforms, snapping, orthographic views, Play In Editor/Simulate, and Blueprint-style reusable behavior—then adapts those ideas to a lightweight HTML/Three.js engine.

## Source of truth

The exact editor HTML is stored losslessly as gzip+base64 payload chunks under `payload/`.
`build_space.py` reconstructs `index.html` byte-for-byte and verifies the SHA-256 and byte count declared in `source-manifest.json` before deployment.

Current v3 source artifact:

- name: `swrlz_forge_unreal_pass_v3.html`
- bytes: `89746`
- SHA-256: `5459e050394a7cbab9bcf0cde16598975611dd0896273f9c04a21e45c309a2a9`

## Hugging Face deployment

Target Space: `kamiloki/swrlz-forge-moba`

GitHub workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

Deployment-affecting Forge source changes on `main` rebuild the exact HTML, verify integrity, and deploy to the dedicated static Hugging Face Space. Documentation-only changes remain deployment-inert.

This Space is deliberately separate from the main §wyrlz chat/server deployment.

## v3 editor capabilities

### Unreal-inspired editing workflow

- searchable hierarchical World Outliner with folders and per-actor visibility
- Details-style inspector with collapsible Transform, Components, Gameplay, and Physics sections
- transform gizmos with World/Local coordinate space
- translation, rotation, and scale snapping
- Perspective, Top, Front, and Right editor cameras
- Lit, Unlit, and Wireframe viewport modes
- configurable editor camera speed
- visible selection bounds
- Undo / Redo transaction history with Ctrl+Z / Ctrl+Y
- Content Drawer with asset search and Output Log
- map Build Validation

### Actor / Component model

Forge actors now carry reusable component metadata rather than putting every behavior directly into one actor type. Current component examples:

- `RotatingMovement`
- `BobMovement`
- `PhysicsBody`
- `LaunchPad`

The default MOBA scene includes reusable Blueprint-like examples such as `BP_JumpPad`, `BP_Rotator`, and a physics-enabled rock.

### PIE / simulation workflow

- Play In Editor
- Simulate In Editor
- Pause / Resume
- Keep Simulation Changes
- Play From Here
- runtime execution of editor components

### MOBA/runtime foundation

- prebuilt three-lane arena
- terrain height variation and depressed river
- trees, bushes, rocks, walls, camps, towers, cores
- hero movement, gravity, jump, terrain following, and blocker collision
- minion waves and lane combat
- tower combat
- simple PhysicsBody gravity/bounce
- exported standalone HTML runtime with component behavior support

### Collaboration / agent foundation

Forge keeps the existing translucent ghost → Bake authoring boundary and now exposes a bounded browser agent API:

`window.SWRLZ_FORGE_AGENT`

Current commands include scene inspection, actor listing/spawn, transform mutation, component addition, Bake, and validation. This is the intended tunnel for future AI/orb collaborative building without making the agent impersonate mouse input.

## Unreal study notes

See [`UNREAL_STUDY.md`](./UNREAL_STUDY.md) for the specific Unreal Editor concepts studied and how they map into Forge rather than being copied blindly.

## Rebuild locally

```bash
python projects/swrlz-forge-moba/build_space.py --output /tmp/swrlz-forge-space
```

The output folder contains the exact deployable Hugging Face static Space package.
