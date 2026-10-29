# Sheep Tag archive requirements and decision ledger

Source: the player's uploaded **SE_Sheep_Tag_Complete_Design_Archive.docx**, prepared **11 October 2026**, “§E · Moonbell Meadow · Sheep Tag — Complete Gameplay & Design Archive.” The archive is the design reference for the verified v10.1 starter and remains the gameplay scope for the v10.5 play-run recorder candidate. The uploaded binary is not copied into the repository. Its attribution, decisions and implementation boundaries are recorded here so development can continue without relying on chat memory.

The archive separates visible/reported prototype behavior, player ideas, assistant brainstorming and unset balance choices. Its reported wolf/building and fog shortcomings are priorities to address and test; they are not evidence that every old release lacked every attack path. It describes a local playable prototype, not validated network multiplayer.

## Current v10.5 candidate · Editor play-run recorder

In any project or starter editor, open **Run recorder**, enable **Record Play run**, close the panel and use the native **Play** button. Recording starts off by default. When enabled, **Full · every simulation update** captures every observed native update; **10 snapshots / second** and **2 snapshots / second** offer smaller state logs while retaining timed commands and game events. Settings stay on this device and do not enter native project or Map Creator saves. The toggle applies across custom projects and every native starter: Default, MOBA Arena, Dragon Den, Starforge, Ghosts in Different Forms and Sheep Tag. Generic runs capture actor transforms, hierarchical part poses, live spawned units, camera, input and observed health/lifecycle changes; Sheep Tag adds its match-specific rules and events. **Simulate** does not create recordings.

A run retains its starting map, rules and actual random seed, a catalog of authored objects, timed world-state changes, camera lens/orientation, body and limb poses, construction and economy, orders, traffic, captures, wisps, rescues and match results. Checkpoints support seeking through the state log. Written 3D observations describe X-east/Y-up/negative-Z-north positions, height differences, movement, nearby objects and each object's recorded state. Player visibility and camera-frustum membership remain separate observations; they do not assert unobstructed line of sight.

After **Stop**, reopen **Run recorder** to scrub the completed run, orbit a spectator schematic, follow a recorded object or use **Recorded player camera**. Review includes objects hidden from the player, so review and export stay unavailable during Play or Pause. The game retains its normal fog and controls. Stop seals the final runtime world before restoring the authored scene. Restart creates a separate run; a match result finalizes its run once. The latest **three finished runs** remain in this tab; export a run to keep it after closing the tab.

**Export JSON** downloads the complete structured `.swyrl-run.json` evidence. **Export text** downloads `.swyrl-run.txt` observations and events for later reading or analysis. **Export spectator HTML** downloads a standalone `.swyrl-run.html` viewer that works offline, with its own timeline, orbit/follow controls and written observations. **Open saved JSON** reviews a previously exported run without replacing the editor map. The viewer reconstructs captured states as a schematic; it does not rerun game logic, reproduce the original artwork or export a rendered video. Recorded data is not silently truncated; a capture failure marks the record incomplete. JSON viewer imports have an explicit 200 MB limit.

Publication appends `patches/v10_5_sheep_run_recorder.py`, `runtime/sheep_run_recorder.js` and `runtime/sheep_run_review.js`: **65 governed patches and 23 unchanged assets**, artifact `swyrl_engine_v10_5.html`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V10_5_SHEEP_RUN_RECORDER`. All 64 earlier patches, earlier runtime modules, map/media assets and payloads remain byte-identical. Native Play/Pause/Stop, project Save/Load, touch placement, house snapping and physical traffic retain their existing behavior. Exact bytes and SHA-256 belong to the final sealed manifest and generated `SOURCE.json`.

Acceptance requires all **six engine workflows**, **twelve desktop/phone browser suites**, including the new `sheep_run` suite, and the existing **13 sealed-source continuous-geometry CPU scenarios**. Recorder acceptance exercises native mouse/touch Play, settings, actual commands, events, exports, offline review and logging-on/off gameplay parity. Final source/deployment commits resolve through the last deliberate `DEPLOY_REQUEST.json`, its successful dedicated Actions run and hosted HTML/SOURCE/all-asset verification. These candidate notes do not assert publication before those receipts succeed.

## Historical verified v10.4 · House lanes and physical creature traffic

The v10.4 release is verified live: merged source `6d04109c27dfcd7e732e2550f3184db82755e999`, final trigger `04ba3ef018d4715cd51fd56ff51b1f96d8530bc6`, [deployment 38317704872](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38317704872) and [hosted audit 38317774602](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38317774602). It seals **64 patches, 23 assets and 1,520,413 bytes**, SHA-256 `f2c2eeb2a28d91239b3cb7afd48c0d189373a260bd12a851e3aaa8fd92524a2d`. All six engine workflows, eleven desktop/phone browser suites and 13 continuous-geometry CPU scenarios passed, followed by 17 live controls cases per layout and exact hosted source/assets. Marker: `V10_4_SHEEP_LANES`; artifact: `swyrl_engine_v10_4.html`.

Sheep can build at their feet, moving to the nearest clear side; blocked construction rejects without moving the builder or charging gold. Houses remain **2.4 × 2.4** and snap flush together or with a **0.6-unit lane**, with preview and collision using the same placement. Wolves retain **0.78-unit** default bodies and approximately 15% larger artwork; sheep retain **0.27**. Wolf bots prioritize reachable visible sheep over buildings. Physical creatures do not overlap on the same floor: blocked ground traffic replans or backs out; raised-route traffic waits. Wisps and decoys stay intangible, rescue chooses a free landing, and native preflight rejects overlapping same-species starts.

## Historical verified v10.3 · Placement above the finger

The v10.3 release is verified live: merged source `de24b04c95e13993313b0abd3496b6fb2602c9be`, final trigger `d0442216bf82ee82fb9df0aaefc8aa345d3f36c0`, [deployment 38312154843](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38312154843) and [hosted audit 38312197696](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38312197696). It seals **63 patches, 23 assets and 1,501,714 bytes**, SHA-256 `6b0f2f461ea2bb1595e0be2ef4dbc58a114ecb39bd8e1828ac745cd0b7ed2653`. All six workflows and eleven desktop/phone suites passed, followed by 13 live controls cases per layout and exact hosted source/assets. Marker: `V10_3_SHEEP_TOUCH_OFFSET`; artifact: `swyrl_engine_v10_3.html`. Touch previews remain above the finger and release builds at that displayed footprint.

## Historical v10.2 controls scope

The player's later request adds **double-tap/double-click selection of the same visible house or building while playing as a sheep** on phone and desktop. Single taps order physical ground movement, choosing a nearby reachable passage when the building blocks the tapped point; wolves keep single-tap attacks. A ground grid and full rotated placement boundary expose each building's extent, using green/red validity and the selected 0.15-unit fine or 3-unit coarse snap. Fine placement has readable 0.6-unit major grid lines with 0.15-unit edge ticks; coarse placement shows 3-unit grid lines. Houses occupy 2.4 × 2.4 units; walls/ramps occupy 2.4 × 6. These guides are transient and excluded from collision and saved maps. This changes input and visibility of placement, without automatically opening deliberately sealed sheep pockets.

The appended `patches/v10_2_sheep_touch_placement.py` integrates `runtime/sheep_touch_selection.js` and `runtime/sheep_placement_grid.js`; artifact `swyrl_engine_v10_2.html`, marker `V10_2_SHEEP_TOUCH_PLACEMENT`, **62 patches and the unchanged 23 assets**. All published v10.1 runtime files, the original 61 patches and map/media assets remain preserved. The focused `tests/sheep_touch_playwright.mjs` raises acceptance to eleven desktop/phone browser suites plus all six engine CI workflows. v10.2 checks and publication must be established independently.

## Fixed intent and prototype scope

| Requirement | v10.1 implementation scope | Acceptance evidence required |
| --- | --- | --- |
| Survival versus pursuit | Sheep survive the timer; wolves win by capturing all real sheep at once. Tagged sheep become central-pen wisps rescued by live allies. | Both wins, capture, bounded wisp commands, actual contact rescue and clean restart. |
| Skillful house mistakes | Fine placement and species-sized collision preserve narrow exits, misleading openings and deliberately sealed sheep pockets. No automatic route opening or player relocation. | A sheep-only gap, wolf rejection, true overlap rejection, a legal self-trap and demolition reopening a route. |
| Legitimate wolf counterplay | Visible attack health/damage, destruction, breach selection, chase/interception, merchant upgrades and bounty. | Earned attacks and rewards; blocked-path wolves choose a useful breach and reroute. |
| Purposeful sheep AI | Formations, escape-lane awareness, allied obstacles, reinforcement/abandonment and danger-aware rescue. | A populated match creates meaningful houses and routes; bots respect collision and observed threats. |
| Uncertain information | Shared-team, individual or disabled fog; player HUD/minimap and AI obey perception and last-known clues. | Hidden enemy coordinates cannot be selected or used by hunt controls; reveal/loss transitions and Stop restore rendering. |
| Separate mini-game | Sheep Tag owns project rules, map and local match; anime/Den/MOBA project behavior remains separate. | Previous nine suites and native project lifecycle isolation. |

The original v10.0 map remains the released **66-actor, four-layer, six-sheep/two-wolf** asset. v10.1 adds `scenes/sheep-tag-moonbell-archive.swyrl.json`; native editor authoring and Save establish **92 actors and six populated layers**, with eight sheep, three wolves, one pen, four shops, one meadow, twelve thorns, two no-build zones and nine paint tiles. It contains no prebuilt houses, walls, ramps or totems: players build defenses during the chase. Counts and starts are editable project data, not a settled global team ratio.

## Player ideas implemented as optional experiments

The new saved map starts with **Archive** enabled: thorns, totems, elevated routes and Illusive Split are on; special events are off. **Classic** independently disables those experiments and events. Each mechanic can then be switched and tuned separately. Numerical values below are provisional test settings; the archive reserved final balance for hands-on matches.

| Player idea | Candidate interpretation | Choices still open |
| --- | --- | --- |
| Thorn contact sometimes exposes a sheep | A probabilistic contact prick grants temporary approximate wolf scent pulses. The affected sheep receives a cue; the signal can coexist with totem concealment. | Chance, duration, pulse frequency/range and retry window. No guaranteed exact location feed. |
| More than eight clustered allied houses earn territory magic | **Nine or more** qualifying houses within a tunable radius allow conversion of one owned house into a stealth-shifting totem. Nearby allies fade in/out over time. | Effect/density radii, stacking, whether a different base buff is preferable, and once-per-match versus cooldown. The earlier 900-second proposal is not a final rule. |
| Castle walls/ramps provide an upper escape route | Connected walkable ramp/deck geometry rises over ground houses and ponds. Upper orders require a physical ground entry; ascent/descent follows connections. Structures can be attacked and routes invalidated. | Prices, durability, height, timing, wolf traversal and route limits. Support-collapse simulation is not adopted. |
| An elevated extraction route may aid wisp rescues | Ground rescue and connected upper escape can be composed by the player; vertical separation matters to contact/tag checks. | Fair entrance protection, proximity to pen, rescued sheep route use and risk. No guaranteed scripted escape. |
| Level-earned Illusive Split | Survival/rescue progression unlocks a plausible mirrored moving sheep. The hostile viewer and wolf target choice do not get an automatic real/illusion answer; contact dissolves the decoy. | Unlock level, cooldown, lifetime, directions, visual tells and interactions. Decoys do not earn economy, rescue allies or count toward the real-flock victory state. |
| Random warned events vary a round | Explicit opt-in uses a configurable controlled pool of provisional hunt-pressure, dense-fog and supply effects, each with warning and duration. Positive match seeds repeat random choices. | Pool membership, rewards, intervals, severity and whether any event belongs in the core rules. Events remain off by default. |
| Accessible game-specific map creator | Curated terrain/forest/hazard/spawn/pen/merchant/no-build brushes; permitted structures; sheep/wolf route previews; native Play/Stop and independent map Save/Load. | Brush usability and guardrails are evaluated with phone and desktop authoring. A future launcher is separate scope. |

## Provisional tuning record

These values document the candidate saved defaults, not accepted Warcraft III rules or permanent product balance. The rules panel exposes them; native map files preserve them.

| Area | Candidate values |
| --- | --- |
| Match and placement | 20-minute survival, 30-second head start, 80 starting gold; 0.15-unit fine snap or 3-unit grid; 28 houses per sheep. |
| Chase and contact | Sheep/wolf speeds 5.4/7.2; collision radii 0.27/0.68; wolf 85 damage every 0.65 s; house/income/fortified health 180/240/650; rescue hold 0.6 s, protection 3 s. |
| Vision | Team sharing; sheep/wolf radius 18/20. Solo and off are selectable. |
| Thorn | 0.35 chance, 15-second scent, 6-second prick retry, 2-second approximate pulse. |
| Totem | Nine-house threshold; settlement radius 8, effect radius 5.5, 3-second fade and 2-second reveal; once per sheep or repeat after candidate 120 seconds. |
| Upper routes | Wall/ramp cost 45/55 gold, health 360/300, height 3.3; connected-ramp wolf traversal selectable. |
| Progression/split | Unlock level 2; 45-second survival progression, 30 rescue XP; 30-second cooldown and 5-second copy lifetime. |
| Events | Off by default; selected pressure/fog/supply pool; 150-second interval, 8-second warning and 15-second duration. Seed zero chooses a new random seed. |

The archive's “more than eight” condition is preserved as **nine or more**. A once-per-sheep limit is a candidate alternative to a cooldown, not a settled decision. Prices, timers, vision, speed, team ratio and all other examples stay adjustable. Classic has to stand on its own before advanced magic is treated as proven balance.

## Explicitly unadopted suggestions

Pond cleansing, advanced illusion tiers or fake building entries, automatic structural-collapse details, every brainstormed event name/reward, and the future Maul/Angel Arena/MOBA mini-game hub are not v10.1 requirements. Their appearance in the archive records discussion rather than approval. The three-event implementation pool is explicitly experimental and does not assert that Blood Moon, Meteor Shower, Golden Sheep or other examples are finalized mechanics.

No Warcraft III map binary, artwork, code or trademarked character model is bundled. The meadow and models are original; classic references remain in [SHEEP_TAG.md](SHEEP_TAG.md).

## Creator and preservation contract

Portable maps use `swyrl-sheep-tag-map-v1`: curated native pieces, finite transforms, layers, saved rules, allowed structures and required sheep/wolf/pen. Import validates the schema and rejects arbitrary scripts/components. Route previews and brush helpers are temporary and cannot enter map exports. Native Undo/Redo, Save Project and Load Project remain available. Play uses the engine's existing loop; Stop restores authored actors, materials, layers and camera rather than saving a match over the map.

The archive implementation is new `archive_sheep_*` runtime source integrated by the appended 61st patch. All prior 60 patches, released `sheep_tag_*` runtime files, old meadow JSON and previous 22 assets remain immutable. The new scene is the 23rd asset. The source manifest, complete generated package and exact asset set are checked before release.

## Staged acceptance and release authority

The archive's stages remain useful test boundaries: classic attack/chase/rescue; purposeful construction and breach AI; fog and thorn information; territory/totem conversion; connected vertical extraction; progression/split/events; accessible creator. Test those interactions with actual native Play on desktop and phone, including self-traps, demolition reopening paths, warning/cooldown state, hidden target protections, live route breakage and saved-map round trips.

The verified v10.1 archive passed its ten desktop/phone browser suites and all six engine CI workflows. Merged source `86aa05b494db007d9aebc073f0c7242756376447` and final trigger `1779223f8b92024f2625e68046ad9582ca80f594` produced successful [deployment 38223924840](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38223924840) and [hosted audit 38224004659](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38224004659): **61 patches, 23 assets, 1,464,129 bytes**, SHA-256 `ef72eb9177a81537c5f6f56f65d620ac9593b4e08da6eae4f1bc4e34b5c9b8f1`. Nineteen live archive cases passed on each layout. These receipts certify v10.1; the verified v10.4 receipts are recorded above. The current v10.5 candidate requires its own twelve-suite matrix, including 16 recorder cases per layout, all 13 geometry CPU scenarios, six workflows, dedicated deployment and hosted audit. Exact current bytes and SHA-256 belong to the manifest and generated `SOURCE.json`.

The dedicated engine lane remains `kaministrator999-ui/Swrlzkamico` → `projects/swrlz-forge-moba` → `kamiloki/swrlz-forge-moba`. Only a deliberate final `DEPLOY_REQUEST.json` update on main triggers production. Completion requires that exact deployment to reach terminal success and an exact hosted audit of marker, normalized HTML, source receipt and every asset. Chat/LALM deployment requests and infrastructure are separate and are not changed by this work.

## Touch construction visibility · v10.3

The preview and ground footprint aim 64 screen pixels above a touch pointer during construction. Drag to aim and release to commit that same snapped site; the aim is constrained to the playable canvas near controls. This interface change preserves the archive rules, map assets and structure collision. Mouse placement and ordinary move/select/rescue orders retain their locations. Publication is certified by the dedicated request, exact successful deployment and hosted package receipt.
