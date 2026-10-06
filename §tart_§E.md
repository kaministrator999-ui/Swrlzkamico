# §tart §E — §wyrl§ Engine Build & Deploy Router

**Role:** canonical entrypoint for §wyrl§ Engine / browser world-engine work.

**Invocation:** `§tart §E` or `@GitHub §tart §E` means enter the dedicated §wyrl§ Engine lane, reconstruct current GitHub/Hugging Face truth, and continue independently from the §wyrlz AI Chat/LALM application.

## Canonical lane

```text
§wyrl§ Engine
GitHub: kaministrator999-ui/Swrlzkamico
  -> projects/swrlz-forge-moba/    (legacy path retained for lineage)
  -> .github/workflows/deploy-swrlz-forge-moba.yml
  -> HF Space: kamiloki/swrlz-forge-moba
  -> https://kamiloki-swrlz-forge-moba.static.hf.space/
```

## Startup contract

On `§tart §E`:

1. Read this router and the engine README.
2. Read `source-manifest.json`, `build_space.py`, every listed patch module, and `SPACE_README.md`.
3. Inspect current GitHub main, latest §wyrl§ Engine deployment workflow, and Hugging Face Space state.
4. Preserve the hard deployment boundary from the main §wyrlz AI Chat/LALM Space.
5. Preserve project separation: Engine core ≠ MOBA example ≠ Dragon's Den project data.
6. Preserve source integrity and compatibility aliases.
7. Validate final generated HTML and JavaScript before merge.
8. Merge validated changes to `main`.
9. Follow the dedicated engine deployment to terminal state.
10. Require the actual served static host to contain the current deploy marker before reporting success.

## Current v6.6 source authority

```text
base:
  swrlz_forge_v4.html
  bytes 99591
  sha256 a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856

patch chain:
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

final:
  swyrl_engine_v6_6.html
  bytes 174866
  sha256 602a498245a01e9ddc87c44ca17390d0070b334996fa15c2817cbc5c5a4af72e

marker:
  SWYRL_ENGINE_DEPLOY_MARKER: V6_6_HOVER_DRAGON_IK
```

## Grouping contract

§wyrl§ Engine now supports hierarchical editor groups.

- desktop additive selection: Shift/Ctrl/Cmd
- mobile additive selection: Multi Select mode
- Group creates one transform parent without destroying child objects
- Ungroup restores child world transforms
- groups serialize their IDs and parent/child relationships
- groups can be nested and duplicated
- grouped child collisions use world transforms
- dynamic actors with CharacterMovement, PhysicsBody, LaunchPad, or Combat remain independent for runtime correctness

The default Den must use grouping for architectural assemblies where useful rather than leaving dozens of structural pieces as unrelated root objects.

## Dragon's Den v5.7 contract

The default Den is an **immersive cavern**, not an outdoor/MOBA-style map.

Current organization:

```text
Wake Nook
    ↓
Main Council Chamber
├── Creator Alcove
├── Throne Side
├── Dragon Perch Side
├── Portal Hall Exit
├── Memory Vault Exit
└── Inference Core Exit
```

Environment requirements:

- cave/stone floor palette; no visible creek/grass treatment
- high enclosed cavern shell
- roof may be multi-piece internally but should be grouped as one editor object
- runtime roof/shell must not obstruct ordinary editor visibility
- preserve first-person immersion
- default Den visitor/player avatar is the Wisp form, not the old blue capsule
- Wisp visuals are procedural glow/particle-style geometry; do not depend on copied Warcraft assets
- keep arbitrary launch-pad mechanics out unless explicitly requested

## Engine naming and compatibility

User-facing name: **§wyrl§ Engine**.

Preferred APIs:

- `window.SWYRL_ENGINE_BUILD`
- `window.SWYRL_ENGINE_AGENT`

Legacy `SWRLZ_FORGE_*` aliases remain active for compatibility.

## Deployment truth contract

```text
reconstruct base
→ apply governed patch chain
→ verify final bytes/SHA
→ syntax-check generated module
→ upload dedicated static Space
→ obtain actual HF host
→ fetch served page
→ require the current manifest/release SWYRL_ENGINE_DEPLOY_MARKER
→ SUCCESS
```

Never equate upload success with live serving success.

## Prior verified checkpoint

v5.2:
- GitHub: `c9c9e03d37ab31cac71342390a27eb0c403cadb3`
- HF: `df0b0f58e31e7b66185b615d6bf489d470d6c924`
- SHA-256: `e3ea58f80f83a2b001f087f5852b6ce7fa5a4dbf4af2f5d67c414eb46c196ad8`

A later verified v5.3 checkpoint must supersede this after deployment.


## Verified v5.3 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.3

GitHub source/deploy commit:
659e9b46f804ad69f2a8f4ea04dd58fc6760323e

Final source:
146986 bytes

SHA-256:
ef68a0906430de83a5da464efe864eed26e757f03d6fdce5e81df6411c75f995

Hugging Face revision:
33b1405f2628d67e81b70021e03d5c947b8d831c

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_3_GROUPS_IMMERSIVE_DEN

Live verification:
PASS on attempt 1
```

v5.3 is the current observed engine state at this checkpoint. The default Den uses hierarchical architectural groups and the improved cave-floor / vaulted-roof layout.


## v5.4 Wisp avatar contract

Dragon's Den boots with **Wisp Visitor / Creator** as its player avatar.

- visually inspired by the classic glowing Wisp / Sheep Tag readability
- built from procedural additive sprites, a bright core, orbiting motes, trailing wisps, team glow, and hover/pulse animation
- no Warcraft model or texture asset is bundled
- serialized as a normal `hero` actor with `avatarStyle: "wisp"` and blueprint `BP_WispVisitor`
- saved projects reconstruct the Wisp correctly
- first-person camera uses the Wisp's lower eye height
- first-person body hiding includes sprites as well as meshes so the glow does not obstruct the camera
- Blank Starter World and MOBA retain their existing player pawn styles


## Verified v5.4 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.4

GitHub source/deploy commit:
afb098ba8a046640608f4b1f2e23e76ab15e09e2

Final source:
151952 bytes

SHA-256:
add2c872e99097285a4ed68372aae3c6f7a42dff4cac4315771c56e8e9c0aea5

Hugging Face revision:
15d26de311d793b41833a83f2b3dc123444d16b3

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_4_WISP_AVATAR

Live verification:
PASS on attempt 1
```

The current default Dragon's Den player is **Wisp Visitor / Creator** using the procedural Wisp visual system.


## v5.5 camera-look contract

Default first-person look must be non-inverted horizontally:

```text
right stick right → camera turns right
right stick left  → camera turns left
right stick up    → camera looks up
right stick down  → camera looks down

pointer-lock mouse right → camera turns right
pointer-lock mouse left  → camera turns left
```

Do not silently restore inverted horizontal look as the default.

## v5.5 Dragon anatomy contract

The Dragon's Den procedural dragon model is **BP_DragonAvatarV2**.

Required visual direction:

- recognizable dragon silhouette at both near and far camera distances
- articulated bat-like wings; avoid giant rectangular/slab wings
- segmented neck and curved tail
- distinct chest and haunch forms
- four articulated legs with feet/claws
- readable muzzle/jaw/head structure
- horns, brows, eyes, teeth, ears, and dorsal spines
- shaded/tinted belly and dark accents; avoid large pure-black blocks that read like missing geometry
- preserve the deliberately massive scale relative to the Wisp/player


## Verified v5.5 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.5

GitHub source/deploy commit:
e08e45fee17b0fb3cd91057771341b679cd6aefc

Final source:
155355 bytes

SHA-256:
76410c2340664c0754ad2a50e7be858f7223787e89cb6f10c4360577cc27f4e2

Hugging Face revision:
2a7706416cd5c9248c41e0d7347f5cb2d0a11b6c

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_5_DRAGONS_NATURAL_LOOK

Live verification:
PASS on attempt 1
```

v5.5 is the current observed engine state at this checkpoint. The default Den keeps the Wisp player, uses natural horizontal look input, and uses the procedural Dragon anatomy v2 model.


## v5.6 dragon contact contract

- all four dragon feet must be explicit and readable, including rear paws
- wings should use articulated finger bones and segmented membrane panels rather than flat slabs
- `SurfaceFootContact` raycasts each dragon foot downward against baked scene meshes and terrain
- feet may settle onto rocks, pedestals, and uneven architecture
- lower shin orientation follows the planted paw
- slope tilt is clamped to prevent broken poses
- contact range / leg stretch is clamped
- terrain fallback remains armed when no mesh is hit
- this system stays in §wyrl§ Engine only; no chat UI work belongs in this lane


## Verified v5.6 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.6

GitHub source/deploy commit:
3b2f29aac2460d0d184592651b37699477f8329d

Final source:
161347 bytes

SHA-256:
c4c0d88febfdfa2bf1c9b02925c6abd9ddafe05010ec5917dac2cd8eb05886e4

Hugging Face revision:
0e2ed2bdb98b7450931208be0fefe51b3a579f4d

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_6_DRAGON_GROUND_CONTACT

Live verification:
PASS on attempt 1
```

v5.6 is the current observed engine state at this checkpoint. Dragon wings use the detailed multi-finger membrane pass, all four feet are explicit, and dragons use reusable raycast-based surface foot contact for rocks, pedestals, uneven architecture, and terrain fallback.


## v5.7 precision contact + camera-speed contract

- dragon foot grounding uses multiple sole samples, not a single center ray
- highest valid sampled contact controls vertical planting so rock/pedestal corners do not pass through the paw
- nearby hit normals are averaged before slope alignment
- contact sampling is reused across all dragons per frame
- teeth remain inside the mouth silhouette and must not protrude through the lower jaw
- the editor top bar exposes a continuous camera speed slider
- that slider controls orbit rotate, pan, and wheel/scroll zoom together
- range: 0.35× to 3.00×
- the chosen camera speed persists locally
- mobile editor views must keep the slider accessible
- runtime/PIE look sensitivity remains separate from editor camera speed


## Verified v5.7 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.7

GitHub source/deploy commit:
a68a7f363897c1bb4dbdc092eb051e2d176126b5

Final source:
163645 bytes

SHA-256:
62fbe228f4ee412c17be53429239159a400bc02bd1f94b5c1b7760f85645c04a

Hugging Face revision:
12e481b45ffd5b808047ee183ea9b6a9bd79fcca

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_7_PRECISION_CONTACT_CAMERA_SPEED

Live verification:
PASS on attempt 1
```

v5.7 is the current observed engine state at this checkpoint. Dragon feet use multi-sample sole contact to reduce rock/pedestal penetration, dragon teeth are tucked inside the jaw, and the editor top bar includes a persistent 0.35×–3.00× camera speed slider for rotate/pan/scroll zoom.


## v6.x + mandatory §E update protocol

v6.6 preserves Dragon's Den — Seed Chamber and makes Glitch Dragon Den — Fracture Forge its exact structural variant: same architecture, layout, rooms, placements, exits, collision structure and camera framing, with the glitch identity layered on top.

Every intentional GitHub mutation involving §wyrl§ Engine (§E), its source/build/deploy files, or its §E documentation is a governed §E update. For EVERY such update:

1. Reconstruct current main and live Hugging Face truth before editing.
2. Apply the §E change while preserving the Engine / MOBA example / Dragon's Den project-data boundaries and the separate §wyrlz AI Chat/LALM lane.
3. Synchronize the engine version everywhere the shipped/versioned state changes. Manifest, generated artifact, README, Space README, deploy marker, workflow verification, §tart §E router, and roadmap must not disagree.
4. Update projects/swrlz-forge-moba/ROADMAP.md in the same update. Record what changed, version/marker, source/deploy commit, deployment status, and live verification. Governance-only updates may retain the current engine binary version but still require a roadmap entry.
5. Validate reconstruction, bytes/SHA, generated JavaScript, and compatibility aliases.
6. Commit/merge the governed §E update to main.
7. After every intended §E source/code/UI/docs/version/roadmap change is finished and validated, the **LAST repository mutation** is the deliberate deployment-button update to `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`. Updating this dedicated trigger file is how ChatGPT manually presses deploy. Do not use ordinary §E files as deployment triggers.
8. That final trigger-file commit starts the dedicated production deployment workflow. No §E release content may be changed after pressing it; any required fix starts a new update cycle.
9. Follow the deployment workflow run to terminal state and require that its source/head commit is the final trigger commit.
10. Require the actual served static host to contain the expected current SWYRL_ENGINE_DEPLOY_MARKER. Upload success alone is not live success.
11. In the user-facing completion response, ALWAYS provide both the exact GitHub Actions workflow-run link started by the trigger-file commit and the live §wyrl§ Engine page link: https://kamiloki-swrlz-forge-moba.static.hf.space/ . Do not report completion before both checks pass.

Canonical roadmap: projects/swrlz-forge-moba/ROADMAP.md

### Final deploy button procedure

The production workflow watches **only** `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`. This file is the intentional final deploy button; it is not ordinary release content.

When the §E update is completely ready — source/code/UI work finished, version surfaces synchronized, roadmap updated, exact build/integrity validation passed, and all normal release commits already on `main` — **press deploy exactly once by updating `DEPLOY_REQUEST.json` as the final repository mutation**. Record the release version/marker, current source integrity SHA-256, and a reason identifying the completed release. Commit that trigger update to `main`.

The workflow must not watch patches, manifest, README, router, workflow definition, or other normal §E files. Those can be edited freely during development without deploying live. Do not add broad push paths back to the production workflow.

After pressing the deploy button:

1. Make no further §E release mutations while treating that deployment as current. If something is wrong, begin a new update cycle.
2. Find the Actions run created by the `DEPLOY_REQUEST.json` trigger commit and verify its head/source commit matches that final trigger commit.
3. Follow the exact run to terminal success.
4. Inspect deployment receipt/state and verify the served static page contains the expected current marker/version.
5. Return the exact Actions run URL and live §wyrl§ Engine URL to the user.

**Mental model:** BUILD/EDIT → VERSION → ROADMAP → VALIDATE → FINAL NORMAL COMMIT → update `DEPLOY_REQUEST.json` (PRESS DEPLOY) → WORKFLOW → VERIFY LIVE → COMPLETE.

Never substitute `workflow_dispatch`, an arbitrary watched source file, or an intermediate commit for this repo's dedicated final deploy-button mechanism.
