# §wyrl§ Engine v9.6 candidate · Natural Staff and Painted Faces acceptance

## Current v9.6 candidate · Natural Staff and Painted Faces

The candidate replaces Kami’s stretched staff grip with a compact painted fist. Rear palm/cuff and front curled fingers/thumb sit on opposite sides of one continuous round shaft. The larger skull/flame crest sits above a visible upper shaft; its narrow join follows the saved **Staff → shaft** socket. The grip is part of the articulated hand, so the fingers, cuff and prop follow the same wrist movement.

Both mages use a shared original painted-feature atlas to improve facial readability and match the amber, sepia and bone tones of their robes, armor and skull. The existing expression, blink, mouth, gaze and saved-dialogue controls remain available. The head’s raised paper surface carries the animated features through pose and relief changes. Native Preview Frame, Play and Watch share the character renderer.

Every body piece retains independent **Depth Left**, **Depth Centre**, **Depth Right**, **Paper thickness** and **Costume Flex** settings in **Animation Studio → Character Rig → Character Piece Depth Sections**. Cloth and armor follow saved body movement while limb sockets stay connected. Native Undo/Redo and Save/Load preserve the piece settings, body fits, pose tracks and scenery separately.

The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`. The starter retains its 12-second book opening, 70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, 425 limb/face keys and 341 scenery keys. The candidate has **56 governed patches and 19 media assets**: eight scene JSON exports, ten PNGs and the historical episode HTML. The new artwork is `assets/anime/kami-grip-layers.png` and `assets/anime/mage-faces-painted.png`; all eight earlier PNGs and seven earlier scene exports remain bundled. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_6_NATURAL_STAFF_PAINTED_FACES`; artifact: `swyrl_engine_v9_6.html`.

Validation and hosted deployment are pending. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Production authority belongs to the final `DEPLOY_REQUEST.json`, its exact dedicated deployment run and the hosted audit of the normalized HTML, `SOURCE.json` and all nineteen assets.

## Historical verified v9.5 · Fitted Staff and Character Relief

The v9.5 release is the previous verified checkpoint: [deployment 38013962412](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013962412) and [hosted audit 38013986565](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013986565) passed. Source `49b82022de841a26a4692359751395ca792efc9f`, final trigger `dcab50950603fb4160615e0d6bf5e0ec8558b06e`, seals 55 patches, 1,075,201 bytes, SHA-256 `bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb`, and 16 assets. It introduced the saved staff mount and per-piece character relief. These receipts certify v9.5; the v9.6 candidate requires its own final deployment and hosted verification.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v9.6 candidate requires its own final deployment and hosted verification.


The 54th and 55th patches retain the staff mount and per-piece relief. The 56th, `patches/v9_6_natural_staff_painted_faces.py`, integrates the compact grip, continuous staff and painted facial features; artifact `swyrl_engine_v9_6.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_6_NATURAL_STAFF_PAINTED_FACES`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging includes eight episode scene JSON exports, the historical episode HTML and ten PNGs, for nineteen media assets.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Existing per-character rest layouts, 425 limb/face keys and 341 scenery keys remain independent. The v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all ten artwork PNGs and the historical episode HTML.

`tests/character_relief_playwright.mjs` adds desktop/phone acceptance for all piece sections, actual front/back/edge depth, pose-driven cloth and armor motion, anchored sockets and facial surfaces, native controls, Undo/Redo and fresh-context Save/Load. `tests/socket_emergence_playwright.mjs` adds desktop/phone acceptance for page-emergence progress, snapped socket contact during rotation, the visible staff hand, native connection authoring, Undo/Redo, Save/Load and shared Play/Watch rendering. The existing native cinematic, storybook authoring, character rig, depth theatre and character alignment suites remain required. Reconstruction checks all 56 governed patches; packaging compares all nineteen media assets against committed source bytes and SHA-256.

- [ ] Complete desktop/phone natural-grip, staff-proportion, painted-face and per-piece section-depth acceptance with visual inspection.
- [ ] Complete all five existing native cinematic, Studio, rig, scenery and body-fit regressions.
- [ ] Seal the generated artifact and pass Node/Python syntax plus remote engine CI.
- [ ] Follow the exact final source/trigger deployment to terminal success.
- [ ] Verify the current marker, normalized served HTML, SOURCE receipt, all eight scene exports, screening HTML and all ten PNGs against committed source.

v9.6 is a source candidate. Desktop/phone acceptance must inspect the compact grip, continuous round shaft and crest proportions, larger painted facial features, expression motion, piece depth and connected sockets in native Play and Watch. All seven existing native cinematic, Studio, rig, scenery, body-fit, book-opening and relief suites, exact sealed reconstruction and six remote engine CI checks must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all nineteen media assets.


---

# Historical verified §wyrl§ Engine v9.3 · Connected Character Pieces

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v9.6 requires its own final deployment and hosted audit.

---

# Historical verified §wyrl§ Engine v9.2 · Layered Scenery and Fitted Face acceptance

The 51st governed patch is `patches/v9_2_depth_theatre.py`; artifact `swyrl_engine_v9_2.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_2_LAYERED_SCENERY_FACES`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging includes four episode scene JSON exports, the historical episode HTML, and eight PNGs including the new transparent `assets/anime/scenery-parts.png` atlas.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`; the v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

The native cinematic, storybook authoring and character rig suites remain required. `tests/depth_theatre_playwright.mjs` adds desktop/phone acceptance for fitted facial surfaces, individual scenery-key edits, three star-depth shells, actual cutout geometry/parallax, shared playhead behavior, native Play/Watch, Undo/Redo, Save/Load and camera clearance. Source reconstruction checks all 51 governed patches; packaging compares every one of the thirteen media assets against committed source bytes and SHA-256.


The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

---

# Historical verified §wyrl§ Engine v9.1 · Articulated Paper Rigs

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

The native editor export preserves 70 actors, 11 layers, nine stage/camera tracks, eight beats and 425 independently saved rig pose/face keys. Each mage has eighteen rigid paper pieces with front/back/silhouette-edge geometry. Existing `tests/character_rig_playwright.mjs` remains required for later releases.

---

# Historical §wyrl§ Engine v9.0 · Native Animation Studio acceptance

Current candidate: `patches/v9_0_animation_studio.py`, 49 governed patches, artifact `swyrl_engine_v9_0.html`, marker `V9_0_AUTHORED_PAPER_THEATRE`. Sealed HTML: **746,616 bytes**, SHA-256 `6a0a9d24e2c888991afbe051d2ae5eba65f38a034c590013e447ca129962d157`. Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Production authority is recorded in the final `DEPLOY_REQUEST.json`, the dedicated deployment receipt, and the exact hosted-release audit.

The native exported starter contains 70 actors and 11 editor layers, including eight new saved paper actors/layers alongside all original 62 production set actors and three layers. Its 134 second episode has eight story beats and nine independent tracks. Generated individual Kami/§wyrlz artwork and separate scenery PNGs are bundled with the scene.

Local desktop and phone-sized Chromium authoring/Play acceptance has been exercised using `tests/storybook_authoring_playwright.mjs`. The suite covers 1440 × 900 desktop and 390 × 844 portrait layouts, native keyframe/title/dialogue controls, deterministic Preview Frame, Undo/Redo, Save/Load, actual editor Play, Pause/scrub, multi-beat camera/depth checks, cast framing, Stop/camera restoration, and separation from Embervault and Starforge. These are local candidate checks, not remote release receipts.

- [x] Native storybook scene export includes separate saved cast/scenery/book actors, owned layers, and the episode timeline.
- [x] Local desktop/mobile authoring and native Play have been exercised; bundled images and portrait framing are included in the candidate acceptance scope.
- [x] Reconstruct the sealed artifact, compile the patch chain, and syntax-check the generated JavaScript.
- [x] Capture Actor Pose transfers native Inspector transforms to a keyframe while preserving the companion track.
- [x] Independent book controls, opaque foreground artwork, low companion-only shots, and null optional visual metadata have regression coverage.
- [x] Saving from Preview/Play preserves the authored environment; a targeted render check confirms physical character folding.
- [x] Remote [native desktop/mobile and authored acceptance](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555) passed against the sealed 746,616-byte artifact.
- Production acceptance requires terminal success of the dedicated deployment with the exact final trigger/source commit.
- Hosted acceptance requires the marker and complete normalized engine, scene, episode, and artwork integrity. See the [deployment workflow](https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/deploy-swrlz-forge-moba.yml) and [independent hosted audit](https://github.com/kaministrator999-ui/Swrlzkamico/actions/workflows/verify-swrlz-v8-9-live-receipt.yml) for final production receipts.

The original Watch Episode 01 button remains a separate historical 2D screening. Skeletal posing, lip sync, audio authoring, and MP4 export are not implemented. [Native authoring workflow](ANIMATION_STUDIO.md) · [Direct starter URL](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01).

---

# Historical §wyrl§ Engine v8.9 · camera-safe scene staging verification

Candidate patch `patches/v8_9_cinematic_staging.py` corrects user-observed v8.8 near-camera book/desk occlusion. The Playwright suite now seeks early and later acts on desktop and phone, verifying the physical book and painted foreground trim stay below Kami and that cathedral scenes stay behind both characters; no default cutout may approach the camera near field. Desktop and phone-sized Chromium tests **passed** in [Actions 37728474772](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728474772). Full engine 647,639 bytes SHA-256 `da9f48941543c81062a232417ed8897e8c82e912852474cf2154e209c12ddf37`. Exact production deployment **PASSED** [37728665723](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728665723); independent fresh live download audit **PASSED** [37728754278](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728754278): normalized HTML 647,639 bytes matching SHA-256 and both bundled episode and scene assets match.

---

# §wyrl§ Engine v8.8 · animated storybook video creator verification

47 governed patches. Candidate HTML **644,951 bytes**, SHA-256 `06c55a0d090bd6ffa9383ff44f914b922a841de7dc03284a50955cb4036478cd`, marker `V8_8_POPUP_STORYBOOK_DIRECTOR`.

- [x] [Source reconstruction and desktop/mobile Chromium acceptance](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37726896000) passed for Play, physical pop-up book, multiple hinged cutout planes, separate fantasy wizard cels, nine layer controls, moving 3D camera, Director editing, Pause, seek, Explore Set, Stop, and project serialization.
- [x] Desktop Playwright downloaded and parsed a genuine Save Project JSON, verifying independent Kami and §wyrlz parameters. Phone-sized Chromium clicked the newly added visible **Director → Save Project** and verified serialized project data; simulated OS download events were not asserted on mobile.
- [x] Fixed phone toolbar collisions: moved Director into Play transport, moved expanded Layers popover above transport, and added a mobile-visible Save Project action in Director.
- [x] Both browser viewports reported zero uncaught script errors.
- [ ] Production deployment and served exact HTML plus episode/scene asset hashes must be verified independently before marking this version live.

Earlier v8.7/v8.6 receipts preserved below.

---

# §wyrl§ Engine v8.7 · layered anime cel/parallax acceptance

Candidate source: **46 governed patches**, **624,633 bytes**, SHA-256 `6a58245bc1d19e3513ddc3a280a454c2d69e7c6c836ad18c65821f1b0816747b`, marker `V8_7_ANIME_CEL_PARALLAX`.

- [x] Exact complete source reconstruction, Python compiler, and JavaScript module syntax ([Actions 37721928687](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37721928687)).
- [x] Desktop Chromium and simulated-phone Chromium acceptance passed: clock, native cinematic camera, six independent depth layers, illustrated cels, Layer toggle, caption bounds, seek, Pause, Explore Set, Stop, and no uncaught JavaScript errors (same run).
- [x] Scene signage and original actor visibility are hidden temporarily during cinematic, with restoration code on exit. Camera moves through real-depth 2D sprite layers for 2.5D parallax. The original editor project and other starter projects remain intact.
- [x] Initial [37721768721](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37721768721) caught insufficient first-frames progress under software WebGL. Adjusted texture resolution for mobile and changed the acceptance probe to require an actual half-second of frames after cold texture upload; the next browser run passed.
- [ ] Dedicated release workflow reaches terminal success and live Space serves exact normalized HTML SHA plus scene and episode asset hashes. Candidate acceptance is not production evidence.

Previous v8.6 verification retained below.

---

# §wyrl§ Engine v8.6 · native cinematic Play verification

Build candidate: 45 governed patches, 611,675 bytes, SHA-256 `1468357c5ce082b71548de983fd11f818cf4eeccb34eca3df92a0f15e3e94dc0`, release marker `V8_6_NATIVE_ANIME_CINEMATIC`.

- [x] Exact patch reconstruction and Node/Python syntax ([Actions run 37719407233](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233)).
- [x] Real Chromium desktop 1280×800 and simulated phone 390×844 ([Actions run 37719407234](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234)).
- [x] Anime Starter **Play** activates cinematic, elapsed time and perspective-camera position advance.
- [x] Captions load from saved stage script files, seek jumps to act five, Pause stops time, Explore Set transitions into ordinary first-person and Stop returns to Editor.
- [x] Both tested viewports report no uncaught JavaScript page errors.
- [x] First production attempt [37719679170](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719679170) rebuilt/validated/uploaded the correct v8.6 engine; **live index SHA matched**, but asset-check failed because the Hugging Face static HTML wrapper was not stripped from the separately served episode HTML. This is a verification normalization defect, not a failed module or a failed asset upload.
- [x] Corrected workflow and production retry [37719877533](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719877533) succeeded: normalized hosted engine HTML SHA and both original episode HTML / scene JSON assets matched.

Existing v8.5/v8.4 receipts retained below.

---

# §wyrl§ Engine v8.5 · Anime Studio starter verification

Source candidate: 44 governed patches, **597,990 bytes**, SHA-256 `1d9111211897151c091a313dd0fbfa59bc3819ac744567dfd0465e7208e39f8c`, marker `V8_5_ANIME_STUDIO_STARTER`. The independent PR check [Actions 37717718014](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37717718014) passed source reconstruction, JavaScript syntax, and Python compilation.

## New native starter

- Projects selector adds **Ghosts in Different Forms** without replacing Embervault and Starforge.
- Canonical scene contains 62 uniquely identified actors, eight stage stations each with script + direction documents, three editor layers, eight teleport zones, one dragon and visitor pawn.
- Separate 24,568-byte original HTML animation is screened in an editor modal and copied into the deployed static Space. This is not a native 3D timeline system.
- Direct route: `?project=anime-ghosts-ep01`. The normal Save Project and Import/Load Project affordances remain available.
- Native browser interaction and live deployment acceptance are **pending** until independently checked; do not infer from Python syntax/reconstruction alone.

## Candidate checks

- [x] Source reconstruction and SHA-256 derived from complete v8.5 patched HTML (CI).
- [x] Generated JavaScript syntax and Python patch compilation (CI).
- [x] Canonical source validates 62 unique actor IDs, eight stations, eight destinations, three layers, and one guardian dragon (patch assertions).
- [x] Packager copies both episode and editable project, with exact bytes/hash parity — [candidate Actions 37717846139](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37717846139) passed complete 44-patch rebuild, HTML byte parity, episode/player SHA-256, and Python/Node syntax.
- [ ] Dedicated production deploy run reaches success.
- [ ] Live HF host serves exact source, `SOURCE.json`, player and scene file hashes.
- [ ] Native browser Projects card, sample asset placement, Save/Load, runtime T-zone travel, Screening open/close, and mobile orientation tested against *served* release.

Earlier release verification retained below without alteration.

---

# §wyrl§ Engine v8.4 verification

This release continues **Embervault Atelier** and **Starforge Observatory** together through engine source, native editor authoring, and desktop first-person Play. The den retains 170 actors, three editor layers, six stations, and eight destinations. Starforge retains 123 actors, three layers, six stations, and seven destinations. Native **Save Project** exports provide the promoted scene data.

## Final v8.4 source acceptance

| Check | Evidence / outcome |
|---|---|
| Den wayfinding | The native arrival-directory assembly is placed at `[-2.9, 0.905, 8.8]`, heading `0.5` radians, beside the approach. All eight actual T-menu journeys and E interactions at all six stations passed without browser errors. Actual walking passed from Arrival through the central approach beside the relocated directory. Prior pause, invalid destination, Stop spawn restoration, and native Save/Load of all eight zones passed. |
| Starforge wayfinding | The Garden guide sits at `[3.6, 4.45, 5.5]`, heading `-0.28` radians, width `2.6`, height `0.68`. Only this sign actor changed; all rails, pads, and building space remain intact. Eight affected walking legs passed without getting stuck, including both lower island bridges and the guide approach; E opened Garden, Code, and Prototype stations. All seven actual T-menu journeys passed with no browser errors. |
| Editor destination previews | **Show destination markers** starts off by default and persists only as a device preference. Landing rings mark authored feet positions with a 0.025m visual offset; arrows show arrival headings. Both are transient noncolliding helpers. They do not change actor counts or enter project saves. Frame Destination preserves the current orthographic viewing axis. All 20 native lifecycle checks passed without page errors. Framing preserves top/front/right axes, distance, and zoom without moving the visitor or changing actors, revision, history, or dirty state. Unique geometry/materials dispose exactly once. Native Save excludes helpers/preferences; Edit/Delete/Undo/Redo refresh markers. An unsupported marker supplies no floor or physical mesh. Play/Simulate hides markers and refuses runtime framing; Stop restores preference. Markers follow Den eight → Starforge seven → Blank zero → native Load eight without stale data; the device preference survives reload. |
| Persistence and isolation | Both native Save/Load checks retain their own scene data and destination lists. Starforge also passed native background/project Save/Load with environment, files, and notes preserved; prior pause and Stop restoration passed. An unsupported visitor start produced a real fall and recovered to validated Arrival at `[0, 2.43, 12.7]`. |
| Final combined native source | The exact governed artifact boots Den at 170 actors/three layers/eight zones/six stations and Starforge at 123/three/seven/six. Both validators report zero issues and zero warnings. Native preview toggle, Projects-card replacement (eight markers → seven), Code/Observatory framing, Play hiding and disabled Frame, Arrival T-menu travel in both scenes, and Stop preference restoration passed. Build v8.4, agent v6.4, preferred/legacy alias identity, and guide text passed with no browser errors. |
| Governed source | The governed 43-patch reconstruction exactly matches `swyrl_engine_v8_4.html`: 533,612 bytes, SHA-256 `58252d18ee4fedf3acb9b5ccbb8e19dbc10c421345deb507a016151ab1ceca62`, marker `V8_4_WAYFINDING_ZONE_PREVIEW`. `build_space.py` and generated JavaScript syntax passed. The final native combined checks passed. |

Both native scene refinements, all 20 native preview lifecycle checks, exact governed reconstruction, generated JavaScript syntax, and final combined native checks passed. Production completion then requires the exact final-trigger Actions run to succeed and the served `SOURCE.json`, marker, and normalized complete artifact hash to match. Source/deploy references resolve from the validated normal release commit and subsequent final `DEPLOY_REQUEST.json` commit; release files are frozen before that trigger.

## Previously verified live v8.3

[Actions 37697374632](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37697374632) succeeded from final trigger `d10953ee23fcefc8e66a6e2ee86b7b2e51421313`. The live host verified marker `V8_3_ZONES_STARFORGE`, served `SOURCE.json`, and complete normalized artifact integrity: **528,670 bytes**, SHA-256 `ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548`. The validated normal source commit was `9c357e8adac2a1728842405dbb9d4c2fc6b806fd`. Both live project boots and six release screenshots passed without page errors. The earlier acceptance evidence follows.

# Preserved v8.3 verification

Verification uses Chromium desktop Play, the native editor, and reconstruction of the governed source on 2026-10-07. **Embervault Atelier** is the default 170-actor Dragon Den with three editor layers, six stations, and eight destinations. **Starforge Observatory** is an independent 123-actor starter with three layers, six stations, and seven destinations. Both scenes are authored with native editor operations and downloaded through **Save Project**.

## Shared v8.3 capabilities

| Check | Evidence / outcome |
|---|---|
| Safe destination geometry | 28 checks cover supported ground/raised pads, authored floor matching, full visitor footprint, transformed/hidden parents, body/head clearance, props, hollow arches, guardrails, Sprite exclusion, invalid zones, and recovery eligibility. |
| Native authoring and persistence | 14 checks cover zone creation, Undo/Redo, project metadata, the global editor zone panel, native Save/Load, actual destination button travel, pause restoration, workspace exclusion, Escape, and Stop restoring the original visitor. |
| Travel lifecycle and recovery | Five additional checks cover a validated raised recovery pad, cancellation restoring running state without moving the visitor, keyboard focus containment, revalidation when a floor changes during the fade, and absence of browser errors. All 47 shared-engine checks passed. |
| Editor authoring regression | An unknown prefab returns `null` without renaming, moving, or otherwise modifying the last selected actor. New blank projects clear inherited layer lists; loading a saved project restores its own layers. Project replacement calls Stop first during an active Play/Simulate session so runtime snapshots and input cannot carry into the new scene. |
| Project isolation and routing | 14 independent composite-browser checks passed with no errors: default Den boot and eight zones; two hub cards; Starforge layers/stations/zones and direct query route; Play/Simulate project replacement; teleport after switching; Stop restoring the new project spawn; Blank clearing layers/zones/environment; Den local-draft isolation after returning; and background edits persisting both scene and project fields. Explicit project imports remain authoritative over local drafts. |
| Accessibility and input | **T / Zones** opens named destinations; Escape closes the menu. Travel releases pointer lock, clears movement input, prevents nested workspace dialogs, and restores the prior pause state. |
| Final governed artifact | Fresh v8.3 boots contain the expected 170/123 actors, three layers, six stations, and eight/seven zones. Both native validators report zero issues/warnings and no browser errors. At 390 × 844, the Play zone button opens eight destinations in a single-column dialog fully inside the viewport. |

The geometry checks and native-browser checks complement each other. Final scene acceptance also requires using the actual saved destinations, physical routes, and workstations; the release gates below track those checks.

## Embervault baseline and refinement

The v8.0 167-actor baseline established the den's supported three-tier layout and station behavior. Its verified routes and document behavior are preserved below; the v8.3 native refinement adds an arrival directory, clearer signs, station travel guidance, and eight authored destinations. All eight native T-menu journeys passed, and E opened all six stations immediately after their destination arrivals. Council uses the verified clear landing `[1.6, 4.63, -9]`, within reach of its station. The same tour passed prior-pause restoration, invalid-destination rejection, Stop restoring the visitor spawn, native Save/Load retaining all eight zones, and absence of page errors.

| Check | Evidence / outcome |
|---|---|
| Native authoring | Reusable prefabs were spawned, positioned, grouped, assigned to layers, configured as stations/signs, and saved with the editor. |
| Walking between tiers | Actual WASD input reached the upper study via the east ramp, crossed both bays, ascended/descended the council connector, and descended the west ramp. Feet tracked the supported mesh tops. |
| Lower circulation | Actual walking reached both workshop stations and the hearth. Side rails blocked attempts to cut across a ramp side; walking through the open mouths completed the route. |
| Bridge clearance | Walking beneath the study bridge remained on the lower floor; upstairs geometry did not pull the visitor upward. |
| Station interaction | E opened Code Studio, Archive Garden, World Forge, Prototype Court, Dragon Council, and the AI Hearth from their actual walk-up positions. |
| Documents | Native New file, text/notes editing, individual download, workspace export/import, and Save Project/reload preserved the expected contents. Temporary verification documents are excluded from the starter. |
| Runtime restoration | Stop restored the visitor spawn while retaining document edits. Opening/closing a station restored the prior pause state. |
| Layer history | Visibility toggle, Undo, and Redo preserved layer state and independent authored actor visibility. |
| Signs | Both faces use their own orientation and remain readable. Text/size updates refresh both faces; shared resources are disposed once. |
| Contact regressions | Physical floor and dragon-contact rays exclude station Sprite labels and editor helpers. Movement checks include grouped/transformed surfaces, rail height filtering, hidden ancestors, edited geometry, and passages below decks. |
| Baseline production receipt | v8.0 Actions run [37664080075](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37664080075) succeeded from trigger `e7a294ba92b681494690bc5ac908906be2ec586c`. |

## Starforge authoring and route fixes

The native scene retains 123 actors, three project-owned layers, six stations, seven destinations, and saved recovery settings (`recoveryHeight: 1`, `recoveryZone: "arrival"`). Authoring moved the lower island links south of the ascending ramps to preserve headroom. Actual walking then exposed low-end rails blocking lateral route crossings; the four ascent rails and two Observatory connector rails now leave the first metre open while guarding the raised sides. The corrected native save passed one continuous Play session with 23 successful walking legs: both lower bridges, the east ascent, both upper islands, the Skywalk, the Observatory rise/descent, and the west descent. E opened all six stations from actual walk-up positions. All seven API destinations validated and landed safely; Stop restored the authored visitor and no page errors were reported. The native T-menu then passed all seven journeys and prior-pause cancellation. Native background edits survived Save/Load with project environment settings, station files, and notes unchanged. Starting the visitor beyond a supported island caused a real fall; the configured recovery safely returned the visitor to Arrival at `[0, 2.43, 12.7]`, and Stop restored the final authored spawn. Use bridge centrelines and the designated ramp mouths when walking between islands; side rails intentionally guard the raised route edges.

## Final v8.3 source acceptance

- [x] All eight native T-menu journeys passed in the refined den; E opened all six stations immediately after their destination arrivals.
- [x] Starforge passed 23 walking legs in one continuous Play session, all six walk-up E interactions, seven safe API landings, and Stop restoration.
- [x] Starforge passed all seven native T-menu journeys, prior-pause cancellation, native background/project Save/Load, station/environment persistence, and actual fall recovery to validated Arrival.
- [x] Independent browser review passed all 14 project-routing, editor-reset, environment, and runtime-restoration checks with no page errors.
- [x] The governed 41-patch reconstruction exactly matches the final composite: 528,670 bytes, SHA-256 `ca4d43e2e560aee39a0fff48b07885d180d96dc64cbeb5c5bd00bdf23490d548`. Generated JavaScript syntax, v8.3 title/build API, v6.3 agent API and legacy aliases, marker `V8_3_ZONES_STARFORGE`, and absence of the temporary movement-measurement draw gate passed.
Production acceptance follows the exact Actions run for the final deploy trigger to success and verifies the served `SOURCE.json`, release marker, and normalized artifact hash. These immutable receipt checks occur after source content is committed; they are recorded in the workflow and final delivery, without changing this file after the trigger.

The headless worker renders with software WebGL. Some walking measurements suppressed raster drawing to keep automation responsive; native input, animation ticks, movement, collisions, support queries, and station logic continued unchanged. Arrival/editor screenshots use normal rendering. This verifies desktop behavior; headset rendering, controller input, spatial comfort, in-room inference, and execution of project code require future implementation and device testing.

The previous live v8.2 release is independently confirmed by Actions run [37689304845](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37689304845), whose head is `177ecda58e928f6d9f590069e1bdb1ddb538145e`. Its normalized served artifact is 393,393 bytes with SHA-256 `d7dc50a0697eb9bf5286131ff6dcaaae4fda7f3db7a3ecede90e8e1b0ef38935` and marker `V8_2_BOOTSTRAP_REPAIR`.

For v8.3, source means the validated normal release commit preceding the final `DEPLOY_REQUEST.json` commit; deploy means that final trigger. Completion requires an Actions run with the exact trigger `head_sha`, successful upload and live verification, marker `V8_3_ZONES_STARFORGE`, and the manifest's exact source hash. Static Spaces add a provider metadata script after `<head>`; verification removes only that recognized prefix before comparing the complete HTML. Repository content is finalized before the trigger; the final delivery supplies its run/live links without altering release files afterward.
