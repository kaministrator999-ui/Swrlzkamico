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

### Inherited full-station execution ownership

`§tart §E` inherits the **Cross-chat full-station execution ownership** rule from `§wyrlz_§tart.md` even though it routes into a separate engine lane.

For §E work:

- the user owns fundamental engine/product/design decisions;
- §wyrlz owns implementation/finishing, validation, dedicated-engine deployment handoff, and repair of §wyrlz-caused implementation/deployment defects;
- a syntax/build/package/deploy defect introduced by §wyrlz is repaired and revalidated/redeployed in the same work turn when safely possible;
- a failure showing the underlying engine behavior/design itself must change returns to the user for that product decision;
- retries remain bounded and evidence-driven, and must reuse the existing §E GitHub/Hugging Face lane rather than creating replacement infrastructure.

A fresh ChatGPT conversation must reconstruct this behavior from the repository; do not depend on prior-chat memory.

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

## Current v8.9 candidate · Camera-safe Pop-Up Storybook

Android playback revealed the v8.8 set/desk card and book obscuring the actors. Source patch `projects/swrlz-forge-moba/patches/v8_9_cinematic_staging.py` lowers the animated book, makes the foreground a thin bottom border with transparent upper pixels, and enforces behind-the-cast architecture and effects. Tests check first/later scene occlusion geometry at phone and desktop sizes. v8.9 source: **48 patches**, `swyrl_engine_v8_9.html`, **647,639 bytes**, SHA-256 `da9f48941543c81062a232417ed8897e8c82e912852474cf2154e209c12ddf37`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_9_CINEMATIC_STAGING_SAFE`. [Desktop/mobile Play/Save acceptance passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728474772); live deployment receipt pending. Previous v8.8 remains the last served/verified production release.

## Current v8.8 candidate · 3D Pop-Up Storybook Video Creator

The **same Ghosts in Different Forms anime starter** now owns a proper popup-book miniature stage in the §wyrl§ Engine. A physical two-half-book/page model opens below individually hinged scenery planes: moonlit fantasy city, swirling atmosphere, gothic arches, decorated workshop, magic runes and desk props. **Kami** is the taller horned main wizard, **§wyrlz** the smaller book-wielding wizard, each a separate CanvasTexture cel and independently toggleable/animatable layer; the unrequested mascot is absent during the video cinematic.

**✦ Pop-Up Director** in the existing editor and cinematic controls authors each layer's Z depth, lateral offset, parallax, unfold delay and animation duration, serialized under `project.animePopUp` with safe bounds and included by **Save Project**. The first scenes pop open from a book rather than just replacing a flat slide.

- Patch: `projects/swrlz-forge-moba/patches/v8_8_popup_storybook.py`, appended after v8.7 (47 governed patches).
- Contract and honest art limits: `projects/swrlz-forge-moba/POPUP_VIDEO_CREATOR.md`.
- Regression test: `projects/swrlz-forge-moba/tests/native_anime_playwright.mjs` checks Play, director docking, individual cels, hinged pop-up cards, real project JSON save, mobile fit, Pause/seek/Explore/Stop.
- Governed v8.8 HTML: `swyrl_engine_v8_8.html`, **644,951 bytes**, SHA-256 `06c55a0d090bd6ffa9383ff44f914b922a841de7dc03284a50955cb4036478cd`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_8_POPUP_STORYBOOK_DIRECTOR`.
- Candidate source and desktop/mobile Chromium editor + Play + Save verification [Actions 37726896000](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37726896000) passed; dedicated production deployment and exact live-host receipt still required.
- Existing projects and the separately bundled 2D Episode 01 remain intact. Native arbitrary keyframe editing, imported art assets and video export are **not yet implemented**.

## Previous v8.7 source authority · Layered 2.5D Anime Cels

The Anime Studio **Ghosts in Different Forms** starter is now a **2.5D cel/parallax experiment**: six independent sprite-depth layers (background sky, atmospheric effects, midground buildings, character cels, magical FX, foreground framing), original illustrated anime-style figures, and a real Three.js perspective camera for parallax. During **Play**, 3D editor actors/signs are temporarily hidden to keep shots readable, then restored on **Stop/Explore Set**. Subtitles are phone-safe; the in-cinematic **Layers** control toggles each render layer. Other starter project Play modes remain unchanged.

- New governed patch: `projects/swrlz-forge-moba/patches/v8_7_anime_cel_layers.py`, placed after v8.6 in `source-manifest.json`.
- Full governed composite: **46 patches**, `swyrl_engine_v8_7.html`, **624,633 bytes**, SHA-256 `6a58245bc1d19e3513ddc3a280a454c2d69e7c6c836ad18c65821f1b0816747b`.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_7_ANIME_CEL_PARALLAX`.
- [CI candidate 37721928687](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37721928687) passed full source reconstruction, generated JS syntax, and actual desktop/phone Chromium cinematic/layer controls.
- **Limits:** The cels and shot transforms are authored programmatically; a general-purpose visual cel/timeline editor and audio/lip-sync/export remain future work. No claim of those features.
- Production success still requires dedicated `DEPLOY_REQUEST.json` triggering, terminal workflow completion, and exact served HTML and asset receipt validation.

## Previous v8.6 source authority · Native Anime Studio Play

Native 3D cinematic Play is now implemented specifically for the **Ghosts in Different Forms** starter. The 45th governed patch is `projects/swrlz-forge-moba/patches/v8_6_native_anime_cinematic.py`. Other engine starter templates continue to use ordinary first-person Play.

- Native Play sequence: scripted moving perspective camera, real-time temporary procedural performers, native dragon actor animation, particles and lighting, station-owned script captions, playhead slider, scene stepping, Pause/Resume, Stop, and **Explore Set** to hand control back to walking first-person runtime.
- Separate `Watch Episode 01` still opens the canvas animation. Do not confuse the 2D screening with the real-time 3D scene.
- The native cinematic shots are currently programmed, not authored through a general-purpose visual keyframe editor; MP4 export and lip sync are not implemented.
- Current governed artifact: `swyrl_engine_v8_6.html`; **611,675 bytes**, SHA-256 `1468357c5ce082b71548de983fd11f818cf4eeccb34eca3df92a0f15e3e94dc0`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_6_NATIVE_ANIME_CINEMATIC`.
- Reconstructed candidate and module syntax verified by [Actions 37719407233](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233). Actual Chromium desktop/mobile Play, timeline, seek, subtitle, Pause, Explore and Stop verified by [Actions 37719407234](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234).
- Production completion still requires dedicated deployment triggered by `DEPLOY_REQUEST.json`, terminal Actions success, served HTML SHA, and both episode/set asset hash checks.

## Previous v8.5 source authority · Anime Studio starter

Governed release candidate **v8.5 — Anime Studio Starter** extends v8.4's verified 43-patch chain with a 44th patch, `patches/v8_5_anime_starter.py`, keeping all existing releases and independent projects.

- Native selectable third starter: **Ghosts in Different Forms · Episode 01** (`anime-ghosts-ep01`).
- Native 62-actor stage scene, three layers, eight production stations, eight Play teleport destinations, guardian dragon, and wisp visitor.
- Original 2m14s procedural anime episode is **screened inside an editor modal**, not executed by a native 3D character/camera animation timeline.
- Scene source: `projects/swrlz-forge-moba/scenes/ghosts-in-different-forms-ep01.swyrl.json`.
- Episode source: `projects/swrlz-forge-moba/episodes/ghosts-in-different-forms-ep01.html`.
- Studio spec: `projects/swrlz-forge-moba/ANIME_STARTER.md`.
- Source manifest: `projects/swrlz-forge-moba/source-manifest.json`.
- Final HTML: **597,990 bytes**, SHA-256 `1d9111211897151c091a313dd0fbfa59bc3819ac744567dfd0465e7208e39f8c`.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_5_ANIME_STUDIO_STARTER`.
- Dedicated Space still `kamiloki/swrlz-forge-moba`; deployed anime entry `?project=anime-ghosts-ep01`.

Candidate check [GitHub Actions #37717718014](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37717718014) reconstructed the source and passed generated JavaScript and Python syntax checks. This is **build evidence, not proof that the live host has deployed v8.5**. The deployment contract below remains mandatory.

## Previous v8.4 source authority

The governed release is **v8.4 — Wayfinding & Destination Preview**. Embervault remains the default Dragon Den. Starforge is an independent celestial workshop with its own scene, workspaces, environment, and travel zones. This contract supersedes the historical default-avatar and layout checkpoints below.

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
  patches/v6_7_contact_tools_fix.py
  patches/v6_8_den2_ground_snap.py
  patches/v7_0_fracture_forge_ascendant.py
  patches/v7_1_fracture_forge_breathing_room.py
  patches/v7_2_wisp_locomotion_repair.py
  patches/v7_3_engine_health.py
  patches/v7_4_editor_workspaces.py
  patches/v7_5_mobile_editor_chrome.py
  patches/v7_6_desktop_editor_polish.py
  patches/v7_7_canonical_glitch_den_project.py
  patches/v7_8_layers_desktop_docks.py
  patches/v7_9_sanctuary_canonical_project.py
  patches/v8_0_sanctuary_primitives.py
  patches/v8_0_layer_integrity.py
  patches/v8_0_workspace_tools.py
  patches/v8_0_walkable_levels.py
  patches/v8_0_embervault_project.py
  patches/v8_1_performance_graphics.py
  patches/v8_2_bootstrap_repair.py
  patches/v8_3_zone_teleport.py
  patches/v8_3_editor_authoring.py
  patches/v8_3_starforge_assets.py
  patches/v8_3_projects_release.py
  patches/v8_4_zone_editor_preview.py
  patches/v8_4_wayfinding_release.py

final:
  swyrl_engine_v8_4.html
  bytes 533612
  sha256 58252d18ee4fedf3acb9b5ccbb8e19dbc10c421345deb507a016151ab1ceca62

marker:
  SWYRL_ENGINE_DEPLOY_MARKER: V8_4_WAYFINDING_ZONE_PREVIEW
```

### Current projects and editor contract

The third Anime Studio starter joins Embervault and Starforge as an independent project; it is editable and saveable in the native scene editor. The integrated episode screening is a static HTML media asset, **not** a native in-engine cinematic timeline. See current v8.5 source authority above.

Embervault Atelier is a spatial workspace for future VR, project work, and conversation. Its native saved scene lives in `projects/swrlz-forge-moba/scenes/embervault-atelier.swyrl.json`. The 170-actor assembly has lower workshops at 0m, a study gallery at 3.4m, and the dragon council at 4.6m, with physical ramps between them. It has six stations and eight teleport destinations. Three organizational editor layers are distinct from these physical elevations.

Starforge Observatory lives in `projects/swrlz-forge-moba/scenes/starforge-observatory.swyrl.json`, with seven floating islands, six stations, seven travel zones, and three organizational layers. Its lower islands, upper archives, companion chamber, and observatory use supported bridges and ramps. Project-owned environment settings control sky, fog, exposure, terrain, and scenery. A project-configured fall threshold returns a walking visitor to the validated Arrival zone.

Both projects store text/code files and notes at their workstations, support file download and workspace JSON import/export, and preserve work through Save Project/reload. Explicit imported project data is authoritative over local drafts. Chat stations open the existing LALM application. Headset rendering, VR controller input, executable coding sessions, and in-room inference remain future integrations.

In Play, **T** or **Zones · T** opens a project-specific travel menu. The editor’s Teleport Zones panel authors name, description, world feet position, yaw, and accent without needing an actor selected. Travel requires a visible approved supporting surface with clearance for the walking visitor; invalid, hidden, blocked, edge, or airborne pads are rejected. Travel releases pointer lock, clears movement, uses a short fade, and preserves prior pause state. Zones persist with project history and Save/Load.

### Destination preview contract

Both projects continue through native editing and Play. The Den's compact arrival directory sits beside the central route, and its signs distinguish lower workshops from upper study. Starforge's Garden guide sits at the perimeter, keeping the Observatory and twin ascents in sight.

The global Teleport Zones panel offers opt-in **Show destination markers** and **Frame destination**. Device-owned preview preferences create transient editor-only rings and heading arrows at authored world feet coordinates. Helpers are not actors, saved project data, selectable objects, supports, or collision blockers. Load, history, destination edits and project changes refresh them; Play/Simulate hides them. Framing is Editor-only, follows the chosen world point, preserves orthographic axes, and leaves visitors and project data untouched. Landing safety still requires testing in Play.

Preserve manual actor visibility separately from layer toggles and runtime shell visibility. Dynamic visitors remain world-root actors. Native prefab calls must return null for unknown assets without modifying the previous selection. New templates must reset inherited empty organizational layers. Use engine source, native editor authoring, and actual Play together; fix capabilities when authoring or walkthroughs expose missing behavior. Plans live in `DEN_DESIGN.md` and `STARFORGE_DESIGN.md`.

### Performance contract

Graphics & Performance retains Auto/Low/Medium/High/Custom presets, render scale, shadows, render caps, and independent FPS/frame-time overlays. Preferences persist locally. Scaling changes rendering, not project data or simulation semantics. Initialization runs only after scene creation at final bootstrap.

### v8.4 release receipt contract

This documentation stages the release; it does not claim production completion. Source authority resolves to the validated normal release commit immediately preceding the final v8.4 `DEPLOY_REQUEST.json` commit. Deployment authority resolves to that trigger and the dedicated Actions run whose `head_sha` matches it. Require terminal success, marker, and exact served-source integrity after removing only the recognized Hugging Face creator script. Report the exact run and live page after verification, without mutating release content after the trigger.

Previous verified release: v8.3, 528670 bytes, SHA-256 `ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548`, deployment [37697374632](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37697374632), trigger `d10953ee23fcefc8e66a6e2ee86b7b2e51421313`, validated normal source `9c357e8adac2a1728842405dbb9d4c2fc6b806fd`. Its exact live SOURCE/marker/hash and both desktop projects were verified.

Historical verified release: v8.2, 393393 bytes, SHA-256 `d7dc50a0697eb9bf5286131ff6dcaaae4fda7f3db7a3ecede90e8e1b0ef38935`, deployment [37689304845](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37689304845), trigger `177ecda58e928f6d9f590069e1bdb1ddb538145e`.

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

## Historical Dragon's Den v5.7 contract

The default Den is an **immersive cavern**, not an outdoor/MOBA-style map.

Organization at this checkpoint:

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

The default Dragon's Den player at this v5.4 checkpoint was **Wisp Visitor / Creator**, using the procedural Wisp visual system. The current v8.0 default is defined above.


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

Historical v7.6 preserved Dragon's Den — Seed Chamber and made Glitch Dragon Den — Fracture Forge its exact structural variant: the same architecture, layout, rooms, placements, exits, collision structure, and camera framing with the glitch identity layered on top. The current v8.0 canonical project is Embervault Atelier, defined above.

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
