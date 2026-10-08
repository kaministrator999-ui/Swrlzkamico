# §wyrl§ Engine Roadmap

Canonical lane: §E / §wyrl§ Engine  
History audited through: **2026-10-07**  
Current source candidate: **v8.8 — Pop-Up Storybook Director (47-patch cinematic stage; browser acceptance in progress and deployment pending)**. Historical releases remain preserved.

Previously verified live release: **v8.6 — Native Anime Studio Play** ([Actions 37719877533](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719877533); exact served HTML and both episode/scene assets SHA-256 verified). Earlier v8.3 live receipts remain in historical sections.

This roadmap is the mandatory release lineage for governed §E GitHub updates. Root `§tart_§E.md` defines the deployment contract.

## v8.5 candidate · Anime Studio starter

Source integration introduces a third independently selectable project, `Ghosts in Different Forms · Episode 01`, using `patches/v8_5_anime_starter.py`. The original 62-actor native scene, eight act zones, three layers, and eight per-scene production workstations are embedded in the governed composite. The animated HTML episode is also distributed as a static asset, screened inside the editor rather than in the 3D runtime. A separate candidate workflow verifies the reconstructed hash and JavaScript syntax before the deploy request.

**Status:** Source candidate; exact artifact, deployment, and live runtime verification are tracked independently. This entry does not redefine or erase the v8.4 checkpoint.

## v8.6 native Anime Studio Play

The Anime Studio starter now begins a real-time native Three.js cinematic when Play is pressed. Eight scripted camera shots, temporary procedural performers, guardian-dragon animation, motes/lighting, and captions driven by each stage's editable `script.md` form an approximately 134-second episode preview. A transport HUD provides Pause/Resume, seek, previous/next shot, Stop, and **Explore Set** to switch to the prior first-person world mode. Other §E starter projects keep their original Play behavior.

Source: `patches/v8_6_native_anime_cinematic.py`; final SHA-256 `1468357c5ce082b71548de983fd11f818cf4eeccb34eca3df92a0f15e3e94dc0`, 611,675 bytes, 45 patches. [Headless Chromium desktop/mobile test run 37719407234](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234) and [candidate compiler run 37719407233](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233) passed. Native authoring of cinematic keyframes, lip-sync and exportable video remain future capabilities.

## v8.8 candidate · Pop-Up Storybook Video Creator

Upgrade the existing Anime Studio starter rather than creating another image or application. Native Three.js book geometry opens under the scene; independent painted book/card/cathedral/workshop/foreground plates rise on animated hinges with perspective parallax. Kami and §wyrlz become separately rendered dark-fantasy wizard cels, echoing the user's two-wizard artwork direction. **Pop-Up Director** saves per-layer depth, parallax, horizontal offset, unfold delay/duration as part of project JSON. The original eight acts, subtitles, Explore/Stop, and unrelated project templates are preserved. See [POPUP_VIDEO_CREATOR.md](POPUP_VIDEO_CREATOR.md) for explicit feature and remaining limits.

## v8.7 candidate · Cel-layer anime cinematics

The v8.6 native Play prototype proved a 3D cinematic could run on the phone, but the first screenshots showed 3D geometry and oversized in-world dialogue signs crossing the camera. The v8.7 starter-pack test adds a true **2.5D depth stack** built from original canvas-drawn anime character cels and six independently inspectable Three.js sprite layers (background sky, atmospheric lights, midground city, character cels, effects, foreground framing). The native camera moves through those Z planes for parallax. The original 3D world actors are hidden for cinematic playback **and restored when exiting**. HUD captions wrap inside mobile bounds.

This is a scriptable experimental compositor with runtime layer toggles, **not** yet a drag-and-drop cel/keyframe editor. It is isolated to the Anime Studio starter; older §E projects and level authoring remain intact. Validation: [v8.7 passed desktop/mobile browser run](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37721928687), exact source 624,633 bytes / SHA-256 `6a58245bc1d19e3513ddc3a280a454c2d69e7c6c836ad18c65821f1b0816747b`; release and served host still require independent acceptance.

## Audited release lineage

| Version | Date | What changed |
|---|---|---|
| v3 | 2026-10-05 | Unreal-inspired editor architecture: components, PIE/SIE, content drawer, undo/redo, snapping, viewport modes, validation, agent API. |
| v4 | 2026-10-05 | Solid terrain, locked authoring views, mobile tools, hardened physics/camera semantics, live-deploy proof. |
| v4.1 | 2026-10-05 | Grounded hero, clean PIE chrome, relocated jungle blockers, deterministic patch-layer verification. |
| v5 | 2026-10-05 | Project system; MOBA separated from engine core; Starter World and Dragon's Den became loadable templates. |
| v5.1 | 2026-10-05 | §wyrl§ Engine naming; Dragon's Den — Seed Chamber became default while other projects remained loadable. |
| v5.2 | 2026-10-05 | First-person PIE, camera-relative movement, mobile twin sticks, pointer-lock look, reticle/runtime cleanup. |
| v5.3 | 2026-10-05 | Hierarchical groups, multi-select, hierarchy persistence/grouped collisions, immersive Den redesign. |
| v5.4 | 2026-10-05 | Procedural Wisp visitor avatar replacing the default capsule while preserving controls and persistence. |
| v5.5 | 2026-10-06 | Natural camera look correction and Dragon anatomy v2. |
| v5.6 | 2026-10-06 | Detailed articulated wings/rear paws and reusable slope-aware surface foot grounding. |
| v5.7 | 2026-10-06 | Multi-sample precision paw contact, jaw/teeth correction, persistent editor camera-speed slider. |
| v5.8 | 2026-10-06 | Cleaner Wisp particles and bounded support correction for dragon paws on rocks/pedestals. |
| v5.9 | 2026-10-06 | Softer Wisp, stabilized planted feet, visible Undo/Redo/history. |
| v6.0 | 2026-10-06 | Researched Glitch Dragon Den / Fracture Forge introduced. |
| v6.1 | 2026-10-06 | Fracture Forge exposed in Projects hub; project router fixed; Seed Chamber version presentation clarified. |
| v6.2 | 2026-10-06 | Glitch Den made an exact structural variant of the regular Dragon Den. |
| v6.3 | 2026-10-06 | Apex Nexus experiment added as a second Glitch Den. |
| v6.4 | 2026-10-06 | Duplicate-project experiment removed; Apex ideas folded into one Fracture Forge; Dragon anatomy v3. |
| v6.5 | 2026-10-06 | Wisp first-person runtime restored in Fracture Forge; Glitch Den made default. |
| v6.6 | 2026-10-06 | Wisp hover/collision and planted dragon idle/contact rig. |
| v6.7 | 2026-10-06 | Wisp movement/contact correction, mobile hover controls, organized mobile Tools. |
| v6.8 | 2026-10-06 | Legacy Den-2 dragon lift offsets removed; hard ground snap to lowest-paw support. |
| v7.0 | 2026-10-07 | Fracture Forge Ascendant production pass plus Command Deck and navigation landmarks. |
| v7.1 | 2026-10-07 | Expanded Den breathing room and mobile viewport declutter. |
| v7.2 | 2026-10-07 | Wisp horizontal locomotion collision-deadlock repair. |
| v7.3 | 2026-10-07 | Unified Wisp flight controller and runtime diagnostics; historical lineage repair. |
| v7.4 | 2026-10-07 | Professional File/Edit/Create/View/Play/Tools/Window/Help menus and game-design workspace launcher. |
| v7.5 | 2026-10-07 | Mobile editor chrome consolidated behind one compact §E workspace trigger. |
| v7.6 | 2026-10-07 | Desktop editor chrome polish: dedicated menubar lane, duplicate Command Deck suppression, docked hints. |
| v7.7 | 2026-10-07 | Saved revision-142, 120-actor Moonfire Sanctum promoted to the sole canonical Glitch Dragon Den starter. |
| v7.8 | 2026-10-07 | Retractable desktop Outliner/Details docks plus persistent multi-object editor layers and visibility. |
| v7.9 | 2026-10-07 | Editor-authored Sanctuary & Makers Grotto promoted to the canonical Dragon Den; project-local scripting namespace established. |
| v8.0 | 2026-10-07 | Embervault Atelier: three physical tiers, native structural assets, height-aware walking, six persistent project stations, and editor/layer integrity fixes. |
| v8.1 | 2026-10-07 | Graphics scalability, Auto quality, persistent render/shadow/frame-cap controls, independent Editor and Play FPS/frame-time overlays, and controller delta-time audit. |
| v8.2 | 2026-10-07 | Bootstrap-order repair: initialize performance controls after engine state and before canonical project hydration. |
| v8.3 | 2026-10-07 | Safe named zone travel, refined Embervault wayfinding, independent Starforge Observatory starter, project-owned environments/recovery, and editor authoring fixes. |
| v8.4 | 2026-10-07 | Parallel native wayfinding refinements in Embervault and Starforge; optional editor-only destination rings/heading arrows and axis-preserving destination framing. |
| v8.5 (candidate) | 2026-10-07 | Anime Studio starter selectable from Projects; 62 editable actors, eight stages, eight notes stations, integrated canvas screening, source-packaged episode; next-step native cinematic animation gap documented. |
| v8.6 (candidate) | 2026-10-07 | Project-scoped native 3D cinematic Play with movable camera, performers, dragon, editable-script captions, timeline controls and Explore Set; desktop/mobile Chromium acceptance. |
| v8.7 (candidate) | 2026-10-07 | 2.5D layered sprite/cel backgrounds, midground, character, FX, foreground parallax; scene sign occlusion and caption clipping repairs; temporary layer visibility. |

## Artifact authority

| Version | Artifact | Bytes | SHA-256 |
|---|---|---:|---|
| v3 | swrlz_forge_unreal_pass_v3.html | 89746 | 5459e050394a7cbab9bcf0cde16598975611dd0896273f9c04a21e45c309a2a9 |
| v4 | swrlz_forge_v4.html | 99591 | a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856 |
| v4.1 | swrlz_forge_v4_1.html | 100610 | 647a80a6a1062e8e4068c63593cca3c5566fe8ee9da5dcdcbc1810d42673132f |
| v5 | swrlz_forge_v5.html | 120501 | c5b44363460fc29ec3a119967c082c1fd95b035d781c50a4affa9d8ecd686593 |
| v5.1 | swyl_engine_v5_1.html | 129398 | a653064ce2be625d67d561a1db249a1bb4fa0637dc69377480cf6311e43fdf51 |
| v5.2 | swyrl_engine_v5_2.html | 135148 | e3ea58f80f83a2b001f087f5852b6ce7fa5a4dbf4af2f5d67c414eb46c196ad8 |
| v5.3 | swyrl_engine_v5_3.html | 146986 | ef68a0906430de83a5da464efe864eed26e757f03d6fdce5e81df6411c75f995 |
| v5.4 | swyrl_engine_v5_4.html | 151952 | add2c872e99097285a4ed68372aae3c6f7a42dff4cac4315771c56e8e9c0aea5 |
| v5.5 | swyrl_engine_v5_5.html | 155355 | 76410c2340664c0754ad2a50e7be858f7223787e89cb6f10c4360577cc27f4e2 |
| v5.6 | swyrl_engine_v5_6.html | 161347 | c4c0d88febfdfa2bf1c9b02925c6abd9ddafe05010ec5917dac2cd8eb05886e4 |
| v5.7 | swyrl_engine_v5_7.html | 163645 | 62fbe228f4ee412c17be53429239159a400bc02bd1f94b5c1b7760f85645c04a |
| v5.8 | swyrl_engine_v5_8.html | 164651 | 0fc3981d582c4ad5ddf07bd01c514463852a4774b3f81e1ff0518c3cb3456a7a |
| v5.9 | swyrl_engine_v5_9.html | 165545 | aafba38d59b520147aa0c625609db0c2e215e31c1f0a6cebaccc1c5faba51eef |
| v6.0 | swyrl_engine_v6_0.html | 170965 | 747076cbbd43b881887392bcf69a7721905564ffc155e3ab946831ed3a640569 |
| v6.1 | swyrl_engine_v6_1.html | 171506 | 2cf327bebbe857e91ca1a82045427018737eaf5ccac0bbae785ddd82d486f15e |
| v6.2 | swyrl_engine_v6_2.html | 168023 | 30504d0b7abeb6eefb7751f3a870d8006ed11966a5ee4f201208a70c0a72c8cd |
| v6.3 | swyrl_engine_v6_3.html | 172048 | 595552ab6f711d333866db9ffeea854f25799393a33463a346b67396774c2c8a |
| v6.4 | swyrl_engine_v6_4.html | 171486 | 98cd0c5a8d376a18ccbe2b958556b98cdc546bb6dc7f6930c4d4916b6d25704d |
| v6.5 | swyrl_engine_v6_5.html | 171694 | f0c3a048c2189a4b761c091971ee6737bcac06c12fb52125a5c2f31045e23a1f |
| v6.6 | swyrl_engine_v6_6.html | 174866 | 602a498245a01e9ddc87c44ca17390d0070b334996fa15c2817cbc5c5a4af72e |
| v6.7 | swyrl_engine_v6_7.html | 178252 | d71cc0f3c57692b1c78830d76ea73069804a9306838b29ae89ae0bafd91222d2 |
| v6.8 | swyrl_engine_v6_8.html | 178783 | 98e383e3795926c5375eace3b5db22dca92b498caeaa1935e51fc2bafd489613 |
| v7.0 | swyrl_engine_v7_0.html | 183813 | 4af05dc4d26819571c9e586703a36c5b5c7300a43611a3d2ec3d1499c917c6b7 |
| v7.1 | swyrl_engine_v7_1.html | 184471 | 35fedcc5decf0f00e4682315311470d9cc05f8c072d2c085daa40c4cacf1d053 |
| v7.2 | swyrl_engine_v7_2.html | 185212 | 3d03e66d04f26659f365d43a2da531692474f4bc5122e1ddffbe9dc515277132 |
| v7.3 | swyrl_engine_v7_3.html | 185760 | 4967a5b527223b8c3d5bfd7ea7ef9a413a6c8582351b2c317cf9c4bc9d0f0e3c |
| v7.4 | swyrl_engine_v7_4.html | 194122 | 822d4d58aad205a4710401c040cd954337585e6346bb337fe7866de73e02f25e |
| v7.5 | swyrl_engine_v7_5.html | 195495 | 0de92bd93af0e4a7d7b9ae22270ee964168e23cf049a11f780cd8563c1ce21e6 |
| v7.6 | swyrl_engine_v7_6.html | 197128 | 409f42adc579b8da5ade1a55c9d5d09d58ef67539ff6e9f0562b119de9ea7f80 |
| v7.7 | swyrl_engine_v7_7.html | 279207 | 75aef1f830dd7117c5675ac1666bdf70755c7be007c26f986c4acb169293bf25 |
| v7.8 | swyrl_engine_v7_8.html | 286002 | 1bf5d8d65f2e1a7af9c30311c119b2bed3fa5688a5ea6e0ff0995a87f38f38cc |
| v7.9 | swyrl_engine_v7_9.html | 285613 | 220a9e5cc7e54fd23e8edc084467101cfcc1c099b5033b1d0150fd2160065251 |
| v8.0 | swyrl_engine_v8_0.html | 383338 | 92ddfc3770f874b5f8f91fc7fad536b15961c1627146be5995936c4355805a88 |
| v8.2 | swyrl_engine_v8_2.html | 393393 | d7dc50a0697eb9bf5286131ff6dcaaae4fda7f3db7a3ecede90e8e1b0ef38935 |
| v8.3 | swyrl_engine_v8_3.html | 528670 | ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548 |
| v8.4 | swyrl_engine_v8_4.html | 533612 | 58252d18ee4fedf3acb9b5ccbb8e19dbc10c421345deb507a016151ab1ceca62 |

## Git push audit — 2026-10-05 through 2026-10-07

The §E project-path history was re-audited directly from GitHub on 2026-10-07. **174 commits** are accounted for from the initial scaffold (`32657c58`) through the v7.8 deployment trigger (`9a529d94`) at that audit checkpoint. Versioned work is grouped below; counts include implementation, build-chain, validation/integrity, documentation synchronization, corrective and deployment-trigger commits carrying that version label.

| Release bucket | Commits | First versioned push | Last versioned push |
|---|---:|---|---|
| pre-version / governance / bootstrap | 18 | 32657c58 | a3faeb28 |
| v3 | 1 | 018b7351 | 018b7351 |
| v4 | 1 | 948489ba | 948489ba |
| v4.1 | 1 | 5d22b941 | 5d22b941 |
| v5 | 1 | e3dcc4b2 | e3dcc4b2 |
| v5.1 | 1 | f8e3b946 | f8e3b946 |
| v5.2 | 1 | c9c9e03d | c9c9e03d |
| v5.3 | 1 | 659e9b46 | 659e9b46 |
| v5.4 | 1 | afb098ba | afb098ba |
| v5.5 | 1 | e08e45fe | e08e45fe |
| v5.6 | 1 | 3b2f29aa | 3b2f29aa |
| v5.7 | 1 | a68a7f36 | a68a7f36 |
| v5.8 | 1 | 97985778 | 97985778 |
| v5.9 | 1 | 2bc743f9 | 2bc743f9 |
| v6.0 | 2 | 12680bb7 | f02752e7 |
| v6.1 | 9 | 08280e78 | 65f16d52 |
| v6.2 | 7 | d875b83d | fe43548e |
| v6.3 | 8 | 8c92aa0b | e2ed3a5f |
| v6.4 | 7 | 6c082b38 | 54ef0d86 |
| v6.5 | 7 | e3ad8f9e | 5e592b7a |
| v6.6 | 11 | f528b1b0 | c00fc940 |
| v6.7 | 12 | 336c389c | 8a9c1705 |
| v6.8 | 7 | 8902fecb | 27c43586 |
| v7.0 | 7 | e56c2186 | 89d0d64b |
| v7.1 | 7 | 322db34d | 368905b0 |
| v7.2 | 10 | 09dc077f | c5abb8f5 |
| v7.3 | 8 | 22790079 | 19343ce4 |
| v7.4 | 7 | dc4baec5 | 093905e1 |
| v7.5 | 7 | d513f0ae | 246889a6 |
| v7.6 | 7 | cebcaf82 | afebb830 |
| v7.7 | 8 | 73873d71 | 2798e4cc |
| v7.8 | 12 | 83eeeada | 9a529d94 |

### Audit corrections made

The 2026-10-07 audit repaired roadmap drift rather than rewriting Git history: v3/v4/v4.1/v5/v5.1 were added to the formal lineage; v7.4 and v7.5 were restored as distinct releases instead of being mislabeled v7.6; historical artifact authority was recovered from each release's own Git revision instead of inheriting later global replacements; literal escaped newline artifacts were removed; and the v7.8 artifact was retained as the governing release at that audit checkpoint. Later release entries below supersede that checkpoint.

## v8.4 — Wayfinding & Zone Preview

Both spatial workspaces continue together. The **170-actor Embervault Atelier** retains three editor layers, six stations, eight destinations, and three walkable tiers. Native authoring moves its arrival directory into view beside the approach and clarifies upper/lower directions. **Starforge Observatory** retains 123 actors, three layers, six stations, and seven destinations; its Garden route guide moves to the path perimeter, leaving the central walking route and project pads open. The saved scenes remain independent.

| Patch | Capability |
|---|---|
| `v8_4_zone_editor_preview.py` | Optional editor landing rings and heading arrows, destination framing that preserves orthographic axes, transient helper lifecycle, and editor-only preference persistence. |
| `v8_4_wayfinding_release.py` | Native scene promotion, v8.4 version surfaces, and marker `V8_4_WAYFINDING_ZONE_PREVIEW`. |

**Show destination markers** starts off by default and saves its preference only on this device. The destination previews are noncolliding helpers; they neither add actors nor enter saved project data. Play/Simulate hides them. Travel safety checks and each project's stations, layers, destinations, and environment remain intact.

Native scene acceptance passed: Den has eight actual T-menu journeys, all six E station interactions, the central arrival walk, and Save/Load; Starforge has seven native menu journeys, eight affected walking legs, three affected station interactions, Save/Load, and fall recovery. The governed 43-patch reconstruction, generated JavaScript syntax, and final combined native checks passed with no browser errors. Both scene validators report zero issues/warnings; preview toggling, eight-to-seven marker replacement through Projects, framing, runtime hiding, Arrival travel, Stop restoration, and v8.4/v6.4 preferred/legacy API aliases passed. All 20 native preview lifecycle checks also passed without page errors: device preference/reload, helper and contact exclusion, framing with all three orthographic axes/distance/zoom preserved, no visitor/actor/history/revision/dirty mutation, exact-once resource disposal, Save exclusion, Edit/Delete/Undo/Redo, runtime hiding, Stop restoration, and marker replacement through Den → Starforge → Blank → native Load. The final `DEPLOY_REQUEST.json` commit then selects the exact production run; completion requires successful Actions and matching served marker, `SOURCE.json`, and normalized complete artifact hash. No release content changes follow that final trigger.

Artifact: `swyrl_engine_v8_4.html` · **533612 bytes** · SHA-256 `58252d18ee4fedf3acb9b5ccbb8e19dbc10c421345deb507a016151ab1ceca62` · marker `V8_4_WAYFINDING_ZONE_PREVIEW`.

## v8.3 — Zones & Starforge

Production deployment **succeeded** in [Actions 37697374632](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37697374632) from final trigger `d10953ee23fcefc8e66a6e2ee86b7b2e51421313`. Its normalized served source is **528,670 bytes**, SHA-256 `ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548`, with marker `V8_3_ZONES_STARFORGE`. The validated normal source commit was `9c357e8adac2a1728842405dbb9d4c2fc6b806fd`; live screenshots and both project boots were checked without browser errors before starting v8.4.

Embervault remains the default Dragon Den and gains a native arrival directory, clearer upper/lower wayfinding, station travel guidance, and eight saved destinations. The refined scene has **170 actors, three editor layers, six stations, and three physical tiers**. Its physical ramps and supported walking routes remain available alongside the **T / Zones** menu.

**Starforge Observatory** is a separate native-authored **123-actor** starter with three layers, six independent stations, and seven destinations. Seven stone islands, garden paths, protected ramps, and a quiet constellation sky create a celestial workspace at 2.4m, 5.8m, and 7m. The Projects hub and `?project=starforge-observatory` route open it without changing the default den. Its project-owned environment hides the old terrain/scenery, and its configured fall recovery uses the validated Arrival destination.

| Patch | Capability |
|---|---|
| `v8_3_zone_teleport.py` | Native zone authoring, saved project-owned destinations, accessible travel menu, supported/clear landing validation, pause/input/cancellation handling, and optional project-owned fall recovery. |
| `v8_3_editor_authoring.py` | Unknown prefab requests return `null` without editing the previous selection; valid spawn refreshes editor views; new templates clear inherited layers; active sessions stop before project replacement. |
| `v8_3_starforge_assets.py` | Reusable supported floating islands, constellation sky, brass astrolabe, noncombat visitor/companion assets, and persistent project-owned environment settings. |
| `v8_3_projects_release.py` | Embed both native saves, retain Embervault as default, add Starforge hub/direct routing, and synchronize v8.3 version/marker surfaces. |

Shared engine verification passed **28 geometry/recovery checks, 14 native authoring/history/persistence checks, and five travel lifecycle/recovery checks**, with no reported browser errors. An independent composite-browser review also passed 14 routing, project replacement, local-draft isolation, background persistence, and runtime-restoration checks with no page errors. Starforge passed 23 actual walking legs in one continuous Play session, all six walk-up E interactions, seven safe API landings, and Stop restoration. Its subsequent seven native T-menu journeys, prior-pause cancellation, environment/station Save/Load, and actual fall recovery to validated Arrival also passed. Native scene journeys, workstation access, final reconstruction, and production acceptance are tracked in [VERIFICATION.md](VERIFICATION.md). Headset VR, in-room inference, executable coding sessions, and spatial voice remain future integrations.

The final governed artifact also passed fresh native boot and validation for both projects, plus a 390 × 844 single-column Play-zone dialog check.

Artifact: `swyrl_engine_v8_3.html` · **528670 bytes** · SHA-256 `ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548` · marker `V8_3_ZONES_STARFORGE`. The governed 41-patch reconstruction exactly matches the final composite, and generated JavaScript syntax passes. Title, build API, agent version/aliases, project routing, and absence of the temporary measurement draw gate were verified.

Source/deploy authority follows the final-button contract: the validated normal release commit precedes the final `DEPLOY_REQUEST.json` trigger commit. The exact Actions receipt must match the trigger head SHA and confirm the served marker plus normalized complete artifact hash. This document is committed before the trigger; the receipt and final delivery provide the immutable source/deploy references without a post-trigger content mutation.

## v8.1 / v8.2 — Performance & Graphics, then Bootstrap Repair

Adds an engine-level **Graphics & Performance** panel while preserving the v8.0 Embervault project data. Presets are Auto, Low, Medium, High, and Custom. Manual controls expose 50–100% render scale, dynamic shadows, 512/1024/2048 shadow maps, and Unlimited/30/45/60 render caps. Auto watches sustained frame time and adjusts render resolution without changing gameplay simulation timing.

FPS diagnostics are independently configurable for **Editor** and **Play/Simulate**. The overlay reports FPS, smoothed frame time in milliseconds, effective render scale, and Auto state. Preferences persist in local storage. The Play controller audit confirmed movement and stick-look were already delta-time based; the performance patch explicitly clamps controller delta to the existing 50 ms maximum to prevent pathological long-frame input jumps.

Artifact: `swyrl_engine_v8_2.html` · **393393 bytes** · SHA-256 `d7dc50a0697eb9bf5286131ff6dcaaae4fda7f3db7a3ecede90e8e1b0ef38935` · marker `V8_2_BOOTSTRAP_REPAIR`. Exact reconstruction and generated JavaScript syntax passed during the v8.2 baseline verification. Production deployment **succeeded** in [Actions 37689304845](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37689304845) from trigger `177ecda58e928f6d9f590069e1bdb1ddb538145e`. Its exact normalized live artifact, marker, and 167-actor canonical boot were rechecked before starting v8.3.

### v8.2 bootstrap regression repair

Repairs v8.1 startup ordering: performance settings had been applied before the engine session-state declarations, causing a temporal-dead-zone ReferenceError when the FPS overlay read `playing`. The shell rendered but canonical project hydration never ran, producing 0 actors and an empty viewport. v8.2 defers performance UI/application until immediately before canonical project load, after engine state is initialized. Validator asserts the order `sun → playing declaration → performance init → canonical project load`, the 167-actor canonical payload, and generated module syntax.

## v8.0 — Embervault Atelier

The canonical Dragon Den becomes **Embervault Atelier**, a 167-actor spatial workspace authored through the native editor and intended for future VR project work and conversation. This release adds depth through three connected physical tiers: a lower workshop at 0m, Code Studio and Archive Garden on a 3.4m study gallery, and a 4.6m Dragon Council. World Forge, Prototype Court, and the shared AI Hearth occupy the lower floor. Two full ramps and a short council ramp connect the levels; rails guard the exposed gallery and council edges.

The den plan in `DEN_DESIGN.md` lists the rooms, assets, editor requirements, and author → Play → fix loop. Scene placement and station data remain project-owned in `scenes/embervault-atelier.swyrl.json`; five governed engine patches provide the reusable capabilities:

| Patch | Capability |
|---|---|
| `v8_0_sanctuary_primitives.py` | Vault canopy/ribs, oculus, chamber wall, support columns, restrained work-floor trim, desktop grid/Play fixes, and authored transparency preservation. |
| `v8_0_layer_integrity.py` | Separate manual/layer/runtime visibility, transactional layer membership and controls, and consistent save/load/undo/runtime restoration. |
| `v8_0_workspace_tools.py` | Native station components and signs; editable text/code files and notes; local drafts, file download, workspace JSON transfer, and project save/reload. |
| `v8_0_walkable_levels.py` | Reusable ramps, gallery decks, and rails; visible mesh-top support; height-aware collision and passages below elevated floors. |
| `v8_0_embervault_project.py` | Canonical 167-actor scene embedding, v8.0 version/marker promotion, correct startup routing, and preservation of hydrated station data. |

The three editor layers organize Architecture & Wayfinding, Atmosphere & Guardians, and Project Spaces independently of the physical tiers. The walking Guest visitor is the default player; Wisp flight remains supported. The six station identities are Code Studio, Archive Garden, World Forge, Prototype Court, AI Hearth, and Dragon Council. Chat stations link to the existing LALM application. Headset rendering, VR controller input, executable coding sessions, and in-room inference are future integrations.

Artifact: `swyrl_engine_v8_0.html` · **383338 bytes** · SHA-256 `92ddfc3770f874b5f8f91fc7fad536b15961c1627146be5995936c4355805a88` · marker `V8_0_EMBERVAULT_WORKSPACE`.

Release status: **verified live**. Deployment run #50 (`37664080075`) completed successfully from trigger commit `e7a294ba92b681494690bc5ac908906be2ec586c`. Native authoring, actual walking between tiers and beneath galleries, all six stations, document transfer, Save Project/reload, and layer/pause/Stop restoration passed. Generated module syntax passes; exact reconstruction is required before the final trigger. Live completion requires the exact Actions receipt and served artifact, as described below.

Deployment repair: the first v8.0 run [37663564970](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37663564970) passed exact reconstruction and JavaScript syntax but Hugging Face rejected the card description for exceeding 60 characters. The description is shortened and its metadata length validated. The engine artifact, authored scene, and integrity remain unchanged; a fresh final trigger deploys this packaging correction.

Live verification adaptation: run [37663777249](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37663777249) uploaded v8.0 successfully but its raw served hash guard failed. Static Spaces prepend a creator-metadata script after `<head>`. The raw served page therefore differs from the uploaded HTML by that provider wrapper. Verification removes only the recognized Hugging Face metadata prefix, then checks the full source hash plus release marker. This keeps exact artifact verification while accounting for the hosting service; the v8.0 engine bytes remain unchanged.

Source/deploy references use the final deploy-button contract: source is the validated normal release commit immediately before the v8.0 `DEPLOY_REQUEST.json` commit; deploy is that final trigger commit; the exact dedicated Actions run must have a matching `head_sha`. The workflow receipt and live host must confirm the v8.0 marker and source integrity. These references resolve from the final trigger and receipt, so completing deployment requires no mutation of release content after pressing the button. These v8.0 checks subsequently passed in deployment run #50; v8.2 is the later independently verified live baseline recorded above.

## v7.9 — Sanctuary & Makers Grotto becomes the canonical Dragon Den

The 120-actor editor-authored **§wyrl§ · Sanctuary & Makers Grotto** save is promoted directly into the canonical `dragon-den` project identity. It replaces Moonfire Sanctum as the default/original Dragon Den rather than becoming a second starter. The saved Code Studio, Archive Garden, World Forge, Prototype Court, Arrival and Guardian Alcove layout now opens through the normal project loader. A project-owned scripting namespace (`swyrl-project-scripts-v1`) is established on project metadata so future §wyrlz§cript/§form§cript assets remain project-local instead of engine-global.

Artifact: `swyrl_engine_v7_9.html` · **285613 bytes** · SHA-256 `220a9e5cc7e54fd23e8edc084467101cfcc1c099b5033b1d0150fd2160065251` · marker `V7_9_SANCTUARY_CANONICAL_PROJECT`. Validation PASS.

## Preserved v7.8 state

v7.8 preserves the canonical v7.7 Moonfire Sanctum starter and adds persistent editor layers plus retractable desktop docks. Layer membership is serialized with project state; layers can independently hide/show sets of objects without destroying hierarchy or transform groups. Outliner and Details can collapse to reclaim viewport space, especially useful on narrow desktop-mode displays.

v7.8 artifact authority: `swyrl_engine_v7_8.html` · **286002 bytes** · SHA-256 `1bf5d8d65f2e1a7af9c30311c119b2bed3fa5688a5ea6e0ff0995a87f38f38cc` · marker `V7_8_LAYERS_DESKTOP_DOCKS`.

v7.9 artifact authority: `swyrl_engine_v7_9.html` · **285613 bytes** · SHA-256 `220a9e5cc7e54fd23e8edc084467101cfcc1c099b5033b1d0150fd2160065251` · marker `V7_9_SANCTUARY_CANONICAL_PROJECT`.

Historical v7.8 deployment trigger: `9a529d945f2e35e2427ebef18c6de6b31810eed6` · deployment run #45 succeeded.

## Mandatory update protocol

Every §E GitHub mutation is a governed update. Each versioned engine update must synchronize applicable version surfaces, update this roadmap, validate/reconstruct the exact artifact, and use the dedicated `DEPLOY_REQUEST.json` final deploy-button mechanism. The resulting Actions run must be followed to terminal state and the live Hugging Face marker verified before the release is reported complete.

Documentation-only historical/audit corrections do **not** create a new engine binary version. They must not silently rewrite historical artifact authority; corrections should identify their audit date and preserve the release SHAs they were recovered from.
