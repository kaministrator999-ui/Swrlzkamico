# §wyrl§ Engine · Maker v5.5

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the dedicated §wyrl§ Engine lane. This engine remains deployment-isolated from the main §wyrlz AI Chat/LALM application.

## Current default

### Wisp visitor avatar

The Dragon's Den now spawns the player as a glowing Wisp-style spirit avatar instead of the old blue capsule. The model uses procedural additive glow sprites, a bright core, orbiting motes, wispy trailing particles, team glow, and gentle hover/pulse animation. The Blank Starter and MOBA templates keep their existing player models.


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

## v5.5 natural look + Dragon anatomy v2

The right look stick now uses **natural horizontal look** by default: push right → turn right, push left → turn left. Vertical look remains natural: push up → look up, push down → look down. Desktop pointer-lock mouse X now matches that same direction.

The Dragon's Den dragons were rebuilt from the previous slab-wing / dark-box silhouette into a more anatomical low-poly form:

- chest + haunch body volumes instead of one capsule
- segmented curved neck
- readable head, muzzle, nose, lower jaw, brows, eyes, horns, ears and teeth
- four articulated legs with knees, feet and claws
- segmented curved tail
- articulated bat-like wing bones with triangular membrane panels
- dorsal spines from crown through the back
- tinted belly/shadow materials instead of large pure-black blocks
- subtler idle bob

This remains procedural Three.js geometry, so no external dragon model asset is required.

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

Agent version: `swyrl-engine-agent-v3.5`

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
patches/v5_4_wisp_avatar.py
patches/v5_5_dragons_natural_look.py
```

Final v5.5:

- artifact: `swyrl_engine_v5_5.html`
- bytes: `155355`
- SHA-256: `76410c2340664c0754ad2a50e7be858f7223787e89cb6f10c4360577cc27f4e2`
- marker: `SWYRL_ENGINE_DEPLOY_MARKER: V5_5_DRAGONS_NATURAL_LOOK`

## Deployment

Infrastructure remains:

- Space: `kamiloki/swrlz-forge-moba`
- live host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`
- workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

Deployment only succeeds after exact reconstruction, final byte/SHA verification, JavaScript syntax validation, Hugging Face upload, and live-page marker verification.
