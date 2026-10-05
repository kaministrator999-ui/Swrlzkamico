# §wyrl§ Engine · Maker v5.3

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the dedicated §wyrl§ Engine lane. This engine remains deployment-isolated from the main §wyrlz AI Chat/LALM application.

## Current default

**Dragon's Den — Seed Chamber** remains the default project.

v5.3 changes the Den from a field-like prototype into a more convincing enclosed place:

- cave-specific stone terrain colors and no river/grass treatment
- flattened cave-floor movement profile
- grouped stone floor assemblies
- a grouped cavern shell
- a grouped vaulted roof
- large supporting pillars
- clearer Wake / Council / Creator / Throne / Perch zones
- dormant exits to Portal Hall, Memory Vault, and Inference Core

The vaulted roof is tagged as a runtime shell: it is hidden while editing so it does not block the viewport, then becomes visible in Play/Simulate.

## Hierarchical grouping

v5.3 adds actual editor groups.

### Selection

- **Desktop:** Shift/Ctrl/Cmd-click actors in the viewport or Outliner.
- **Mobile:** enable **Multi Select**, tap several objects, then press **Group**.
- Shortcut: `Ctrl/Cmd + G` groups; `Ctrl/Cmd + Shift + G` ungroups.

### Group behavior

Grouping creates one parent transform while preserving each child's world placement.

```text
roof slab A
roof slab B
roof rib A
roof rib B
      ↓ Group
Vaulted Cavern Roof
      ↓
move / rotate / scale as one object
```

Groups:

- collapse into one root entry in the Outliner
- can contain other groups
- save/load their hierarchy in `.swyrl.json`
- preserve child transforms
- duplicate as complete grouped structures
- ungroup back into independent objects
- remain compatible with Undo/Redo
- are exposed to the agent API

For runtime correctness, actors carrying `CharacterMovement`, `PhysicsBody`, `LaunchPad`, or `Combat` stay independent instead of being parented into editor groups.

## Default Den uses the grouping system

The starter intentionally dogfoods the feature:

- **Seed Chamber Stone Floor** = grouped floor pieces
- **Cavern Shell** = grouped wall rocks
- **Vaulted Cavern Roof** = grouped roof slabs/ribs
- **Cavern Pillars** = grouped structural pillars
- **Den Lanterns** = grouped lighting props
- **Cavern Rune Crystals** = grouped crystal set

The roof is therefore no longer a pile of unrelated objects in normal editing—it is one selectable structure, while still remaining ungroupable/editable when needed.

## Existing systems retained

- Dragon's Den / Blank Starter / MOBA project templates
- first-person PIE
- twin mobile sticks
- desktop pointer-lock look
- terrain adhesion and collision
- ghost → Bake
- Components
- Undo / Redo
- PIE / Simulate
- standalone export
- structured agent API

Agent version: `swyrl-engine-agent-v3.3`

New agent operations:

- `groupActors(ids, name)`
- `ungroup(id)`

## Source integrity

Base v4:

- bytes: `99591`
- SHA-256: `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`

Patch chain:

```text
patches/v4_1.py
patches/v5_projects.py
patches/v5_1_swyl_engine_seed_den.py
patches/v5_2_first_person_twin_stick.py
patches/v5_3_groups_immersive_den.py
```

Final v5.3:

- artifact: `swyrl_engine_v5_3.html`
- bytes: `146986`
- SHA-256: `ef68a0906430de83a5da464efe864eed26e757f03d6fdce5e81df6411c75f995`
- marker: `SWYRL_ENGINE_DEPLOY_MARKER: V5_3_GROUPS_IMMERSIVE_DEN`

## Deployment

Infrastructure remains:

- Space: `kamiloki/swrlz-forge-moba`
- live host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`
- workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

Deployment only succeeds after exact reconstruction, final byte/SHA verification, JavaScript syntax validation, Hugging Face upload, and live-page marker verification.
