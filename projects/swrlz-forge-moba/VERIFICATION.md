# §wyrl§ Engine v8.6 · native cinematic Play verification

Build candidate: 45 governed patches, 611,675 bytes, SHA-256 `1468357c5ce082b71548de983fd11f818cf4eeccb34eca3df92a0f15e3e94dc0`, release marker `V8_6_NATIVE_ANIME_CINEMATIC`.

- [x] Exact patch reconstruction and Node/Python syntax ([Actions run 37719407233](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233)).
- [x] Real Chromium desktop 1280×800 and simulated phone 390×844 ([Actions run 37719407234](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234)).
- [x] Anime Starter **Play** activates cinematic, elapsed time and perspective-camera position advance.
- [x] Captions load from saved stage script files, seek jumps to act five, Pause stops time, Explore Set transitions into ordinary first-person and Stop returns to Editor.
- [x] Both tested viewports report no uncaught JavaScript page errors.
- [x] First production attempt [37719679170](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719679170) rebuilt/validated/uploaded the correct v8.6 engine; **live index SHA matched**, but asset-check failed because the Hugging Face static HTML wrapper was not stripped from the separately served episode HTML. This is a verification normalization defect, not a failed module or a failed asset upload.
- [ ] Corrected workflow normalizes only the recognized provider script for every served HTML file and validates original episode JSON/HTML hashes. Production retry and exact host acceptance pending.

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
