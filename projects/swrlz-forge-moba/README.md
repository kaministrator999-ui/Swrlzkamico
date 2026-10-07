# §wyrl§ Engine · Maker v7.6

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the dedicated §wyrl§ Engine lane. This engine remains deployment-isolated from the main §wyrlz AI Chat/LALM application.

## Current engine: v7.6

v7.6 adds a professional editor navigation shell: File, Edit, Create, View, Play, Tools, Window and Help menus plus a mobile-friendly workspace launcher for Level Design, Content, Gameplay, World, Play & Debug, Console, Project and Build workflows.

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

## v5.7 precision contact + camera speed slider

The v5.6 single-ray foot planting was still vulnerable on rock edges. v5.7 replaces it with **multi-sample sole contact**:

- center, four corners, and toe sample rays per paw
- highest valid contact determines vertical foot placement
- nearby contact normals are averaged for stable slope tilt
- foot/rock penetration is reduced on uneven rocks and pedestal edges
- surface meshes are collected once per frame for all dragons
- failed rays still fall back to terrain
- contact height and tilt remain clamped

Dragon teeth were also shortened and moved upward into the mouth so they no longer protrude through the lower jaw.

The editor now has a persistent **CAM speed slider in the top bar**. It continuously controls OrbitControls rotation, pan, and wheel/scroll zoom speed from 0.35× to 3.00× and remains accessible on mobile editor views.

## v5.6 wing detail + surface foot contact

v5.6 keeps the v5.5 anatomy pass and adds the missing contact details:

- rear feet are explicit, larger, and positioned behind the haunches so all four paws read clearly
- rear paws include heel geometry and claws
- wings gain four articulated finger bones, four membrane panels, inner membrane variation, and vein struts
- dragons now carry a reusable `SurfaceFootContact` component
- each foot raycasts downward against baked scene meshes and terrain
- planted feet can settle onto rocks, pedestals, and uneven Den architecture
- lower shins re-aim toward planted paws for a simple two-bone IK effect
- foot tilt follows sloped contact normals within a safe clamp
- failed/invalid rays fall back to terrain and leg stretch is clamped

This grounding system is written as reusable engine logic rather than a one-off perch offset.

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

Agent version: `swyrl-engine-agent-v3.7`

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
patches/v5_6_dragon_ground_contact.py
patches/v5_7_precision_contact_camera_speed.py
patches/v5_8_wisp_alpha_foot_support.py
patches/v5_9_wisp_soft_contact_history.py
patches/v6_0_researched_glitch_dragon_den.py
patches/v6_1_glitch_den_project_card.py
patches/v6_2_glitch_den_parity.py
patches/v6_3_glitch_den_apex.py
patches/v6_4_single_glitch_den_dragon_v3.py
patches/v6_5_glitch_den_runtime_default.py
patches/v6_6_wisp_hover_dragon_ik_idle.py
patches/v6_7_contact_tools_fix.py
patches/v6_8_den2_ground_snap.py
patches/v7_0_fracture_forge_ascendant.py
patches/v7_1_fracture_forge_breathing_room.py
patches/v7_2_wisp_locomotion_repair.py
patches/v7_3_engine_health.py
patches/v7_4_editor_workspaces.py
patches/v7_5_mobile_editor_chrome.py
patches/v7_6_desktop_editor_polish.py\npatches/v7_7_canonical_glitch_den_project.py
```

Final v7.6:

- artifact: `swyrl_engine_v7_6.html`
- bytes: `279207`
- SHA-256: `75aef1f830dd7117c5675ac1666bdf70755c7be007c26f986c4acb169293bf25`
- marker: `SWYRL_ENGINE_DEPLOY_MARKER: V7_7_CANONICAL_GLITCH_DEN_PROJECT`

## Deployment

Infrastructure remains:

- Space: `kamiloki/swrlz-forge-moba`
- live host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`
- workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

Deployment only succeeds after exact reconstruction, final byte/SHA verification, JavaScript syntax validation, Hugging Face upload, and live-page marker verification.


## Release governance

Every §E GitHub update must synchronize version surfaces when applicable, update ROADMAP.md, press the dedicated DEPLOY_REQUEST.json final deploy button, follow that run to terminal state, verify the served Hugging Face marker, and return both the Actions run link and live §wyrl§ Engine page link. Root §tart_§E.md is authoritative.
