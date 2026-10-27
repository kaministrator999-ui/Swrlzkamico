## §E v11.141 · Project-wide separate editable levels, new maps and connected Play flow (2026-10-26)

Owner correction to v11.140: the menu cinematic must **not** animate inside the editor as an uneditable overlay on the gameplay level. Levels are separately authored, editable maps that may be connected for runtime loading, not scenes that silently run when opened for editing.

**Project-wide level system:** In the native §e editor, opening any project exposes a **Project Levels** selector, **+ New Map**, editable level name, **Next** connection, and **Export Level**. Each level owns a separate native scene snapshot (actors, transforms, editor layers, metadata); switching loads that snapshot in the editor without invoking Play. New blank maps inherit compatible project settings and a Sheep Tag meadow ground, but no phantom bots or unapproved gameplay spawns. The existing native Play command runs the selected map separately; the connected next map is available via the **Next Level** runtime action or the public `SWYRL_ENGINE_LEVELS.transition` API.

**Persistence:** The native `projectData()` now serializes an explicit `project.levelPack` collection with schema `se-levels-v1` and one nonrecursive saved project snapshot per level. Whole-project Save/Export includes all levels and their navigation links even when only one is open. Opening the saved project restores the level collection and last selected level. Individual levels can also be exported as standard `.swyrl.json` scenes. Level switch preserves edited scene snapshots in project memory; the native undo timeline resets per newly opened level, so Save Project before closing the browser/editor.

**Sheep Tag starter first example:** Two native levels: **Main Menu** (separately versioned `scenes/sheep-tag-main-menu-v11-141.swyrl.json`, 13 editable sheep/wolf/house/landscape actors), and **Gameplay** (existing untouched Grand Moonbell Wildwood, 196 actors). The menu UI text, colors and orbit speed are editable in **Menu UI**. Editor view is static. Only the user pressing Play animates the actual authored menu actors with a low-cost chase/house build camera sequence; the visible **Start Game** transitions to the linked Gameplay level and calls native Sheep Tag Play/preflight. Stopping returns to the unanimated authored menu with transforms restored. The retired v11.140 editor-time transient cinematic does not run. No wolves, sheep mechanics, resource rules, Rapid Build or local multiplayer gameplay is changed.

**Acceptance gate:** separate editable menu and gameplay scenes, new project map creation, project bundle Save/Load roundtrip, transition links, no editor-time animation, native gameplay Start Game, original 68 assets preserved and source checksum validated; real Android editor usability remains an independent check.

## §E v11.140 · Sheep Tag starter main menu & 3D attract background (2026-10-26)

**Owner request:** Open Sheep Tag as an actual game with a simple main menu containing only **Start Game**, rather than immediately throwing the player into the native editor/game controls. Behind the menu, show a slowly circling 3D camera, sheep moving/building/fleeing, and a wolf chasing/tagging sheep.

**Implementation scope:** The canonical `stLoadStarter()` completes the existing authored starter load and then overlays a responsive Sheep Tag title, “Build. Flee. Survive.” and one prominent Start Game button over the viewport. Its backdrop is **real Three.js scene geometry**: three sheep, one wolf, a small house cluster, ground/trees, a growing construction house and scripted chase/tag disappearance on a 17-second repeat. It advances from the **existing editor frame loop** with a slowly orbiting camera—no second game clock, render loop, navigation load, bot simulation or online API usage. It does **not** modify actor arrays, saved maps, history, collisions, gold or captured counts.

**Start Game:** The button first removes the overlay and every temporary demo mesh/material, restores the saved editor camera/orbit state, then invokes the existing native `playBtn.click()`. The real match uses its already established preflight, game engine, HUD, bots, timer, rules and fresh source-of-truth session. Switching projects similarly destroys the menu/demo before loading another project. The standard editor toolbars remain outside the viewport overlay; other §e starter projects are unaffected.

**Acceptance:** Check Sheep Tag starter opens at menu, the scene animates while the real timer stays stopped, Start Game works with mouse and Android touch, the demo vanishes completely, match starts with original sheep/wolf/structure counts and physics, pressing Play in other projects remains unchanged, and exiting to a different project cannot leave ghost menu actors behind. Automated source/verifier and synthetic scene/transition checks are distinct from owner Android visual acceptance. Preserve all previous 171 patches, original 68 packaged assets, and local multiplayer being future work.

## §E v11.139 · Safe Rapid near-corner house magnet (2026-10-26)

Owner Android screenshot (v11.138) showed a red house hologram beside a compact cluster of existing Free Houses, with the exact native validator error **"A diagonal crack is not a sheep passage. Join houses or leave 1.20 m."** This is not a lost touch; the existing v11.124 diagonal clearance rule is correctly rejecting an intermediate narrow slit. The ergonomic weakness is that the prior house snap only magnetizes side-aligned footprints, so a close diagonal corner cannot easily snap flush on the phone.

The v11.139 Rapid-only improvement checks the rejected diagonal house against nearby existing house corners. It proposes the closest **fully flush x-and-z corner** when the correction is within the current sheep-safe-lane width (typically 1.20 m), and calls the full previous native `stCanBuild` validator on that candidate. Only a valid return changes the ghost to green and updates the actual build destination; if another house, collision, boundary or route rule rejects it, the original red rejection remains. It never relaxes the 1.20m clear lane, alters occupied structures, creates a building during preview or auto-places a faraway ghost. Rapid OFF and non-house structures behave as before; v11.138 same-screen Rapid cursor memory remains.

Sealed target: **171 ordered patches, 68 unchanged assets, 6,719,389 HTML bytes**, SHA256 `f605af72628643e87d8fca5d97a08fcba438c43f2d9ffa693e4f6014032ce6fb`. The regression tests the red original, legal corner snapping, occupied-corner refusal, other build kinds, Rapid OFF, and assembled patch/marker. Android visual and gameplay acceptance remains pending after hosted verification.

## §E v11.138 · Rapid Build remembers last successful build SCREEN position (2026-10-26)

Owner design request: with Rapid ON, the next ghost should start at **the same spot on the player's phone screen as the last successfully built house**, rather than restarting at the sheep or remaining attached to the old house's world coordinates. This allows sheep to move and the follow camera to pan while maintaining a consistent placement cursor position.

Source behavior: on successful Rapid placement, project the actual validated build center through the current camera and store normalized viewport coordinates, scoped to the current session and controlled sheep. After reselecting the same build tool, seed the next ghost by raycasting that screen coordinate into the **current** world; while idle, camera follow refreshes the ghost without issuing build commands (with throttled re-projection to limit mobile cost). On a new meadow drag, the remembered on-screen site moves by the finger's on-screen delta. Changed camera position must not make the preview jump back to the previous world site. Invalid, canceled, unpaid or blocked placements do not alter the anchor. First build in Rapid remains sheep-origin; turning Rapid OFF and ending/restarting the match clear the memory.

The actual structure is always created only after native movement, resource and collision validation. Single-tap meadow placement, non-Rapid builds, Rapid repeated selection, construction timing, Mirror/Totem, wolves, local multiplayer state, original 68 assets and all existing game behavior remain unchanged. Source seal target: 170 patches, 68 assets, 6,717,316 bytes, SHA-256 `384558ce7af5993f36ef002824455d850fdfebf635a881eea1fe4878931f7385`. Android touch acceptance remains separate from automated checks.

## §E v11.137 · Full-screen meadow-first touch construction (2026-10-26)

The owner confirmed the sheep-origin building hologram appears correctly, but the old continuous touch-drag began from the bottom-right build icon, leaving almost no room to move downward/right on the phone display. **v11.137 separates selection from aiming on touch/pen:** tap Free/Income/Fortified/Ramp/Walkway to select, release to leave the hologram visible at the sheep, then touch *any open meadow position* and drag from that fresh anchor to move the preview. Release on valid ground to place, or simply tap a meadow target for single-tap placement. The button-touch alone cannot place a building or move its preview off the sheep. Native single-placement and optional Rapid repeat both still work. Desktop mouse direct-icon dragging stays available; all existing game/safety constraints remain authoritative.

Source seal target: **169 historical-plus-new patches, 68 preserved assets**; build hash/byte count populated only by the isolated exact-source measurement and verification. Real Android comfort/placement remains owner acceptance. No wolf-side development or multiplayer changes.

## §E v11.136 · Camera-stable sheep preview and capture performance (2026-10-26)

Owner Android gameplay report: v11.135 build hologram now originates at the sheep, but is still slightly inconsistent while dragging; phone frame rate appears to dip when sheep are rapidly captured and their buildings vanish. This is a *source-level optimization* pending Android acceptance, not a claim of measured FPS gains.

The previous sheep-origin drag stored its initial ground ray, which could become stale when the follow camera moved. v11.136 casts the drag anchor and live finger from the same current camera, then offsets the living sheep's current position by their difference; the player still sees/commits the authoritative snapped footprint. The placement grid skips redundant geometry uploads for unchanged snapped destinations while revalidating on changed navigation topology.

Capture still immediately marks each owned building destroyed, removes its scene mesh from visibility/collision, triggers Archive callbacks and makes it unavailable to wolves/sheep. A capture wave now emits **one** navigation cache invalidation rather than one per house. Expensive GPU geometry/material disposal is drained over subsequent update frames (2 per frame) and flushed on match stop. No houses persist in gameplay because their disposal is deferred. The performance diagnostics include capture batches, retired/disposed mesh counts, pending queue and grid skip count.

Scope is strictly Sheep Tag's client simulation and UI. Wolf behavior, capture balance, sheep builds/costs, Rapid toggle, Mirror/Totem, saved maps and all native assets are untouched. The exact release seal is **168 source patches / 68 assets / 6,711,684 HTML bytes**, SHA-256 `b6114ad2b3f8e6c3352869336845df015fdf18da40e580e5cb4ef819fc5476af`. The new regression tests same-camera aiming, single nav invalidation per capture, immediate detachment, bounded disposal, stop flush, and placement grid reuse. Android touch feel and actual phone frame-time still require user acceptance.

## §E v11.135 · Sheep-origin relative hologram, bigger Free House, visible Mirror (2026-10-26)

**Owner Android screenshot:** selecting a house still showed its hologram and placement grid near the bottom-right skill ring rather than visibly originating at the controlled sheep. Free House also needed to trade screen positions with Fortified House and grow larger. Totem was visible, but Mirror/decoy was missing from the sheep's touch HUD. The owner explicitly deferred wolf-side gameplay; no owl scout or wolf behavior is changed in this release.

**Input root and scoped correction:** the previous v11.134 sheep-origin preview only adjusted the ghost mesh after selection. The earlier `sheep_touch_offset.js` camera updater still re-raycast an active touch gesture each frame, and the old v11.84 pointer aim jumped to an absolute finger-based target. v11.135 prevents that re-aim while the placement pointer is active, plants the hologram at the controlled sheep on selection and first meadow contact, then translates it from the sheep using the deliberate meadow drag delta. The initial detached placement grid stays hidden until a target is aimed. One-tap meadow placement remains valid, and final issuance uses the exact displayed and native-validated building site rather than a separate finger ray. Construction costs, permitted structures, resource checks, safe placement, wolf collision and Rapid Build remain unchanged.

**Phone HUD:** Free House occupies Fortified's former slot at 112% of the former large house size; Fortified occupies the former Free slot. Income House stays bottom-right. Mirror and Totem are explicitly attached to the native ability ring with separate visible hit targets for sheep; rules-disabled skills stay disabled rather than overriding custom-map settings. Mouse/keyboard and wolves remain unaffected.

**Source integrity:** 167 ordered patches / 68 original assets; compiled HTML **6,708,052 bytes**, SHA-256 `40cf34d1322b071812e0061d25a3be5353a4ad81820714d32eb06608161a09b5`. Dedicated build and targeted DOM/native regression form the release gate. Hosted publication must still be verified through the dedicated `DEPLOY_REQUEST.json` trigger; real Android placement and button appearance remain separate owner acceptance checks.

## §E v11.134 · Live deployment audit success (2026-10-26)

Protected §E deployment [GitHub Actions #40386472509](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40386472509) completed **SUCCESS**. The Hugging Face static Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING** at revision `eefecb5562811d7c59feee23396d4d4e1ca88df0`. First live verification retrieved and matched the exact **6,700,691-byte v11.134** HTML, SHA-256 `71a6056da0404f81f09337a2dddb45c87b81450ce49b327f8525fccd5d4efdbe`, **166 ordered patches**, all **68 bundled assets**, and the canonical `SOURCE.json` receipt. Source commit `a2c274ede9bdfbef75c7aa97676c7240c62305e4`, deployment trigger commit `f34278515cf9be52971498dd784ca98060b49b70`.

Owner Android acceptance remains separate: switch Rapid ON/OFF while its ghost is unplaced; verify tapping each house starts its hologram on the actual sheep before dragging; verify both Mirror and Totem remain visible (disabled when custom rules require); check the swapped bottom-right Income/Free house buttons do not overlap other controls. Automated source and DOM tests passed, but they cannot certify device-specific touch/visual layout.

## §E v11.134 · Rapid OFF cancels ghost, exact sheep-origin marker, restored ability slots, Free/Income HUD swap (2026-10-26)

The owner's Android acceptance exposed three post-v11.133 problems and one missing skill slot. **Rapid Build OFF** now immediately exits the active build mode and removes any unplaced ghost, touch gesture/placement marker and selected tool; it never removes already constructed houses or interferes with issued build orders. Turning Rapid ON leaves selected tools alone. **Selecting any build skill** immediately displays its hologram at the controlled sheep's *actual* X/Z (not a snapped construction site), on touchscreen, mouse and keyboard; after selection a meadow drag still drives native ghost placement with original collision, snap and resource checks.

**Mobile ability HUD:** both original sheep skills—Mirror and Totem—remain present. If a user-created map disables one in Sheep Tag rules, the icon stays visible but disabled with an accessible explanation; this release intentionally does not override owner's custom rules. The canonical starter's existing enabled ability settings and cooldowns remain unchanged.

**Bottom-right skill circles:** swapped the *physical screen positions* of Income House (now bottom-right) and Free House (now the previous Income slot), updating the circle and SVG sizes. Real game building types, free/paid costs, permissions, keyboard shortcuts, IDs, joystick, decoy, rapid position, and all 165 older patches are unchanged.

**[Full build + UI regression #40385878910](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40385878910) SUCCESS:** exact prior v11.133 seal independently verified, then **166 patches** assembled and JS syntax validated. DOM regression tested Rapid OFF with/without in-flight pointers, automatic exact sheep-centered preview after selecting Free/Income, visible-but-disabled custom-rule ability slots, intact wolf HUD hiding, and positional CSS swaps. Official output: **6,700,691 HTML bytes**, SHA-256 **`71a6056da0404f81f09337a2dddb45c87b81450ce49b327f8525fccd5d4efdbe`**; all **68 original assets** preserved. Protected live deployment and owner's Android real-device test remain separate verification gates.

## §E v11.133 · Deployed; Android owner acceptance pending (2026-10-26)

**Production [GitHub Actions #40382749397](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40382749397) SUCCESS.** The exact guarded release of §E v11.133 was uploaded to `https://kamiloki-swrlz-forge-moba.static.hf.space/` and the **first live audit passed**. Hugging Face Space reported `RUNNING`, revision `e87a981cf9bb48bd54c2109d6f0185b8a5956d5a`. Live audit verified the exact HTML (**6,696,326 bytes**; SHA-256 `2c2b40a507bc91950479ac9983eb365c6c5d9319a5e85c9fe3b7ac18f27860b8`), all **165 ordered source patches**, all **68 original bundled assets**, and exact `SOURCE.json` receipt.

**Owner Android acceptance still needed:** confirm circular Rapid toggle is touchable beside Income (bottom right), visibly changes OFF/ON, selected House skill leaves a hologram at controlled sheep, same-finger skill-to-meadow drag and separate meadow drag both move preview, and successful Rapid orders retain build mode. Existing live sheep occlusion wireframe remains. Passing DOM synthetic click tests demonstrates handler logic, not conclusive Android touch UX.

## §E v11.133 · Rapid next to Income, touchable, and sheep-origin build ghost persists (2026-10-26)

**Owner's actual Android screenshot and test:** §E v11.132 rendered the circular Rapid toggle around mid-screen as an unexpectedly **small square**; owner could not turn it on or off. The house skill also frequently failed to leave a working holographic preview after tapping/dragging, although the **cyan sheep occlusion wireframe already worked**. Owner specified Rapid's intended location **immediately left of the Income house icon in the bottom-right build cluster**.

**Root causes and fix:** The native Sheep Tag HUD root has `pointer-events:none` and only certain child controls explicitly re-enable pointer input; v11.132's free-floating Rapid button inherited the no-pointer policy. The generic HUD button's higher selector specificity also overrode Rapid's circular border. v11.133 mounts Rapid/Rotate inside the actual `.st-builds` skill cluster and positions the circular Rapid ON/OFF icon to the left of Income, with `pointer-events:auto!important`, accessible pressed state, and strong circle styling. Rotation remains context-sensitive.

A second, independent defect: touching the House skill caused native `pointerup` to select the tool and seed its preview at the sheep, **then Chrome dispatched a synthesized click** to the skill button, running `stUiChooseBuild(kind)` again. That function **toggles the already-selected build tool OFF**, removing the hologram. The fix suppresses just the one matching touch-derived click after a handled skill pointer release, not keyboard, mouse or subsequent intentional taps. The ghost is also seeded while the button is held without triggering the old invalid-touch hide path. A continuous drag from icon onto clear meadow now moves the preview when the finger reaches valid ground; a normal tap followed by meadow drag also remains supported. If a skill drag ends above HUD/blocked ground, the selected tool and sheep-origin preview are retained.

**[Full source + Android click/ghost regression #40381957434](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40381957434) PASS:** exact prior v11.132 seal reconstructed; 165 patches compiled and JavaScript syntax checked, `jsdom` reproduced synthetic touch click and verified selection persistence, keyboard/mouse input, clickable Rapid, parent-location near Income, circle/ON/OFF CSS, meadow child canvas hits and all previous §E gameplay integrations. Exact build **6,696,326 bytes**, SHA-256 **`2c2b40a507bc91950479ac9983eb365c6c5d9319a5e85c9fe3b7ac18f27860b8`**, 165 ordered patches and original 68 assets. Owner's live Android acceptance is still needed after deployment; automated DOM events do not prove real Chrome behavior.

## §E v11.132 · Live deployment verified (2026-10-26)

**Official production [GitHub Actions #40379238352](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40379238352): SUCCESS.** Isolated deployment commit `33ac9b0e7a7674e7bf4be8e9f5a45ab88bf38efa` requested exact sealed engine source `41e020d6e92ec432dcbccf0d00ce011b774e0780`. Dedicated static Hugging Face Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING**, revision `374e0eb1fa35699895e0b851f6b19ea0c9acb84a`. **Live verification attempt 1 passed**, matching the entire **6,691,218-byte HTML**, SHA-256 `6d678e0886907007de501b5f9d68916f09246eb25f6fa865a36e56481fa64920`, **164 source patches**, all **68 bundled assets**, and exact `SOURCE.json` source receipt. 

Live publication has succeeded, but the user's **Android gameplay acceptance** is still pending: test meadow drag after tool selection, Rapid mode consecutive placements, cancelable build recovery, three rotated permanent ramp groups, walking under a completed walkway, and occluded sheep wireframe appearing only when visually covered. Physical touch and game feel are not proven by automated test suites.

## §E v11.132 · Dragging sheep-centered hologram, Rapid Build, rotated raised crossings and occlusion wireframes (2026-10-26)

**Owner gameplay report:** tapping House correctly placed the preview ghost at the sheep after v11.131, but dragging on the meadow **did not move the hologram**. The native v11.84 pointerdown callback was discarding the selected tool and calling `stUiChooseBuild(kind)` again; that API **toggles the same selection off**. The final patch differentiates the selected skill-button event from a subsequent meadow drag, preserves the selected active tool on meadow pointerdown, recognizes viewport descendant targets, follows actual pointermove with native preview/snapping, and commits only upon valid pointerup/resource/collision checks. Finger drag on the skill icon is still separate from moving the hologram.

New **circular, accessible RAPID ON/OFF button near the middle of the mobile screen** keeps the selected house/structure after a successful native building order and reseeds the next hologram at the sheep. Off mode restores one-and-done placement. A companion **⟳ rotate control** exposes the existing 90° rotation for player-built ramps and walkways. On actually constructing any new owned building, the sheep pauses automatically for **0.28 s**; a movement order or joystick direction cancels that recovery immediately, while the game clock, captures, effects and AI remain updated.

All nine indestructible authored prebuilt ramp/deck pieces in **three Moonbell crossings** remain: Pinewatch at 0°, Moonflower at 90°, Amberglade at -90°. Opposing ramp high ends still join their real 6 m deck endpoints exactly. **Completed elevated walkways** now admit sheep/wolves travelling at ground level beneath the 3.3 m platform, without changing upper path surfaces; ramps and incomplete platforms remain blocking until complete. Occluded living sheep receive a **cyan see-through wireframe clone of their own actual animated sheep mesh** only when physically under a walkway or when a house/deck blocks the camera's sightline; it hides once clear and never changes unit physics, controls or original materials.

**[Complete 164-patch gameplay CI #40378516848](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40378516848) PASS**. The run rebuilt the exact preceding v11.131 release, assembled all **164 ordered patches** into **6,691,218 bytes**, SHA-256 **`6d678e0886907007de501b5f9d68916f09246eb25f6fa865a36e56481fa64920`**, checked compiled JavaScript syntax, and exercised actual Three.js wireframe materials, underpass blocking, three rotated crossing groups, responsive rapid toggle and rotation UI, interruptible construction recovery, and required assembled native pointer handler changes. Original 68 bundled assets and all earlier behaviors remain intact. Production deploy and real owner's Android touch acceptance remain separate gates.

## §E v11.131 · Production deployment and live-source audit completed (2026-10-26)

**Protected deployment [Actions #40373327088](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40373327088) SUCCESS.** Source commit `e155e7d2bf5acb19443134851a465ddcba2ab45d`; isolated deployment request commit `d4931bcdbddd9ce4a2f414bc135d1041ba510980`. Hugging Face static Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING** at revision `4315ca0665a372b10d000c806ddb73b17403f597`. The first hosted audit verified the exact **6,679,918-byte v11.131** HTML, SHA-256 `ae889b96eaeddf58d290a6214809463cf84930f88a02b5070cda83ae47080218`, **163 ordered patches**, **68 bundled assets**, and byte-for-byte matching `SOURCE.json` receipt.

Owner Android Chrome acceptance is still required: repeatedly tap starter project selections to test page zoom, choose a house and confirm sheep-position preview, hold sheep joystick and drag the Mirror icon to send the illusion in a chosen direction, observe countdown and lifetime. Hosted integrity proves deployment correctness, **not mobile device UX acceptance**.

## §E v11.131 · Drag-directed sheep Mirror decoy and ready-to-use mobile fixes (2026-10-26)

Following §E v11.130's successful **sealed-source** check, the owner additionally requested a **visible cooldown counter on the Mirror/decoy skill**, reliable casting while the sheep is moving, **drag-to-direct** the decoy and **short-lived disappearance**. The real archive gameplay `stArchiveSplit` now creates only a **separate decoy**, routes it toward the direction dragged from its skill button using the existing safe ground/upper path planner, boosts only the decoy's speed, and leaves the real sheep's movement/order/joystick completely untouched. A simple tap aims along the sheep's current velocity or facing direction. A blocked destination rejects without using cooldown, and existing unit validity and Classic-off rules remain enforced.

The Mirror skill icon gains a **live numeric cooldown badge** (not merely an info row) and accessible status label. The existing starter's **12-second Mirror cooldown** still comes from the game rules; successful casting sets the normal `archiveSplitAt`. Decoys expire after **at most four seconds**, or any shorter authored lifetime; they fade their own cloned materials in the final 0.7 seconds and can still dissolve earlier on wolf contact. The new touch ability owns only its own pointer; it does not cancel a second finger holding the sheep's mobile joystick, alter the camera, or spend gold.

Also includes the **v11.130 source fixes verified earlier but not independently deployed**: Android browser zoom is suppressed at the second single-finger starter-selection `touchstart` without blocking a true two-finger pinch; skill-button pointer movement and release no longer overwrite sheep-origin building previews. All original v11.129 and prior editor/Sheep Tag features remain intact, including the Clover model, startup gate, starter defaults, non-destructible walkways, player-build clearance, and all 68 bundled assets.

**[v11.130 sealed main preflight #40371349066](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40371349066) SUCCESS.** **[v11.131 full 163-patch CI #40372653251](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40372653251) SUCCESS**: rebuilt exact prior v11.130 seal, assembled 163 ordered patches, passed JavaScript syntax and automated Mirror ability tests for joystick-independent movement, drag direction, cooldown badge, short expiry, decoy-only material fade, tap use, no duplicate cast and original rule restrictions. Official new HTML: **6,679,918 bytes**, SHA-256 **`ae889b96eaeddf58d290a6214809463cf84930f88a02b5070cda83ae47080218`**, **163 patches, 68 assets**. Guarded production upload, live HTML/SOURCE audit and actual Android thumbstick/gesture acceptance are separate gates.

## §E v11.130 · Second-touch Android page zoom protection + true sheep-origin house preview (2026-10-26)

**Owner Android acceptance feedback:** §E v11.129 reduced browser magnification during rapid starter-project taps but **small browser PAGE zoom still reproduced**. This is not the 3D camera. The new `passive:false`, capture-phase `touchstart` guard observes a short stationary single-finger starter-card touch and prevents default on the **second** rapid single-finger touchstart within 670 ms, before mobile Chrome can decide to smart-zoom. Previous native `touch-action:manipulation` and post-click 420 ms handoff shield are retained as layered protection. Two-finger pinch, editable input interactions, long press, mouse/keyboard, viewport camera controls and general scrolling remain unaffected. This is a targeted browser-page control; no global viewport zoom restrictions are imposed.

**Owner also reproduced a construction regression:** tapping a Sheep Tag build skill still sometimes caused the house preview to spawn **at the skill icon**, despite v11.126 sheep-centered seeding. Root cause: the older v11.84 `stBuildInputAim(event)` unconditionally re-aimed the preview during **skill-button pointermove and pointerup**, overwriting the later sheep seed with the button's screen ray. v11.130 preserves native meadow pointer-down/aim/release but stops handling the skill-button finger as an aiming pointer. A skill tap simply selects the house tool and **re-seeds the preview at the controlled sheep** on release; only touching the meadow can aim or order a house. Native `stCanBuild`, collisions, unit relocation on valid build, resource costs, original joystick and safe lanes remain unchanged.

**[Full 162-patch source and DOM/native handler preflight #40370882999](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40370882999) PASS:** reconstructed exact v11.129 release; measured **6,672,532 bytes**, SHA-256 **`6156d4261621b38b570792f24acff2f126baaf2384b2f4f79acd5975a13b5a26`**; checked compiled module syntax. DOM tests confirmed rapid second `touchstart` cancellation, true pinch and editable-field exceptions, movement threshold, and actual extracted native skill-button `pointerup` handler re-seeding without ever aiming toward the button. Original **68 assets** and 161 earlier patches are preserved. Protected production deployment and owner real-device acceptance are separate checks.

## §E v11.129 · Live Android project-transition zoom guard verified (2026-10-26)

**Release:** [GitHub production Actions #40368794102](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40368794102) **SUCCESS**. Live Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` was **RUNNING**, revision `d77fbb1dec6a43c2e49edad774d897f78ace1d63`. First hosted audit checked exact HTML (**6,669,441 bytes**, SHA-256 `34caf41b05e3c404e12d0da122a79db61c8187aaea1692b2cd07c380a69a4f7f`), **161 source patches**, all **68 packaged assets**, and `SOURCE.json`. Browser page-zoom defense on project handoff deployed; preserve pinch zoom, native scene input and checkbox selection.

**Manual Android acceptance pending:** repeatedly tap project starters and test rapid taps around modal close; observe whether browser **page scale** changes versus the 3D camera. The synthetic event regression proves controls and transition shield behavior but does not reproduce the physical mobile browser gesture.

## §E v11.129 · Android project-switch page zoom protection (2026-10-26)

**Owner's reproduced bug:** repeatedly, immediately after selecting a starter project, the **entire browser page** enlarged—not the 3D camera—cutting off editor controls until manually zoomed back out. This occurred despite the pre-existing v11.122 root-page `touch-action:manipulation` rule.

The targeted fix applies `touch-action:manipulation` on **actual project cards, their default-project checkbox siblings, project picker, and editor workflow chrome** (preserving native scrolling and browser pinch accessibility). During a **touchscreen** starter-card selection only, a 420 ms transparent, non-focusable hit shield intercepts rapid second taps **after** the native Open click finishes, preventing a subsequent tap from landing on a newly exposed unrelated editor control or triggering double-tap page magnification across replaced DOM hit targets. Keyboard/mouse selection, checkbox-only changes, text editing/paste, the 3D viewport's original touch rules, game camera, model sculpt brushes, saved projects, and all prior engine behavior remain unchanged.

**[Feature full source and touch-DOM preflight #40368154931](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40368154931) PASS:** reconstructed the exact preceding v11.128 seal, verified full 161-patch source syntax and measured **6,669,441 HTML bytes**, SHA-256 **`34caf41b05e3c404e12d0da122a79db61c8187aaea1692b2cd07c380a69a4f7f`**. The jsdom harness verified keyboard/mouse taps unaffected, native starter click still fires, default checkbox not intercepted, touch selection adds the shield, double-click prevention, 420 ms cleanup, and no `#viewport`/viewport-scale restrictions. The engine still carries **68 original assets**. This does **not** prove Android browser acceptance; user real-device retest remains necessary.

## §E v11.128 · Persistent default starter checkbox (2026-10-26)

The owner requested an individual checkbox beside **every starter project** in the §E Projects picker so users can nominate one project to open by default on future visits. The real native template picker has **10 starter-card buttons**. Each card now has a sibling accessible, touch-sized **Load this project by default** checkbox (not nested inside its Open button). Selecting a checkbox records that template ID as the one default in browser-local storage `swyrl.engine.defaultStarter.v1`, clears other checkboxes and **does not open a project**. Unchecking the currently selected option removes the default and restores normal Dragon Den startup. Choosing a new starter remains a separate click on the existing card button.

At regular launch without an explicit URL project, the already-native startup router now uses the saved starter. Explicit `?project=` URLs take precedence without changing the saved choice. Specialist model links keep their existing project query handlers, and async default-project loading keeps the v11.127 boot overlay active until completion or its existing bounded fallback. Importantly, the preference is **independent of project data and autosaves**: setting/clearing a default does not delete, mutate or overwrite custom project JSON, the in-progress editor project, or the existing `swrlz-forge-v5-autosave` key. Browser storage being unavailable fails safely with UI feedback.

**[Full 160-patch source + real DOM interactions #40350416722](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40350416722) PASS**: prior 159-patch §E v11.127 verified unchanged, 160-patch HTML built and syntax checked; `jsdom` verified **10 card checkboxes**, native Open click remains usable, one-choice exclusivity, selection/clearing persistence, avoiding accidental project openings, old autosave preservation, normal and explicit-link launch precedence. Complete HTML: **6,666,214 bytes**, SHA-256 **`9bf9658db0592f6dccc4c9b57a6eec700c76de04461f542403e50cb6c2a49a2a`**. Earlier organic Clover Sheep Tag model and cute swurv gait, stable boot cover, permanent routes and earlier engine features remain as-is. This source test is not the protected live deployment or Android visual acceptance.

## §E v11.127 · Native Clover organic sheep + smoother editor startup (2026-10-26)

The owner requested that Sheep Tag reuse **Clover · Meadow Sheep**, the existing native Model Atelier organic sheep generator, and give the sheep a more lifelike gait with occasional small, cute pouncing swurvs. The runtime now builds that genuine authored organic geometry *once* at mobile-adjusted tessellation, preserving sculpted fleece, muzzle, face, ears and split hooves. Mesh resources are shared across Sheep Tag sheep; native actor ownership, collision radii, joystick/pathfinding, saves, capture/rescue, and distance-based leg gait remain unchanged. The visual-only pounce triggers occasionally **while moving**, applies small body hop, head tilt and slight sideways *appearance* then returns to walk. Disabled for captured, upper-route, falling and building sheep. Failure to build the organic model retains the existing fallback sheep.

The owner also documented a visible editor startup handoff: temporarily showing an old/default empty editor shell before the current project and toolbars finish restoring. v11.127 inserts the boot style into the document head, covering only the *intermediate visible shell* with a minimal loading surface while project and toolbar signals settle. It reveals the fully restored current editor (or uses an 11 s safety fallback) rather than showing stale controls and then snapping. Rendering/initialization continues unobstructed beneath the overlay; existing persisted projects/data are **not reset or overwritten**. Reduced-motion preference is honored.

**[Full source + real Three.js sheep regression #40348104741](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40348104741) PASS.** Exact previous v11.126 seal rebuilt; all 159 patches independently assembled; compiled HTML syntax passed. Genuine organic sheep generator created **28 parts / 29,332 triangles**, with shared geometry for two animals. Automated tests covered ears/fleece/hooves, four walk pivots, rare cosmetic pounce and no physics drift, old animation callback preservation, editor boot gate and no serialized Object3D metadata. Full build: **6,660,681 bytes**, SHA-256 **`a6dc826751d28b0385971cd32fbb41df47131ea2d2b1d2aeeee1f1aac45e584a`**, 159 patches, original 68 assets. Production deployment and owner's actual Android appearance/startup test remain separate gates.

## §E v11.126 · Live production verified (2026-10-26)

**Production confirmed:** [GitHub deployment Actions #40344188092](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40344188092) completed **SUCCESS** (deployment request `ce590802d9e9a2403bd359fc85cbec04ea5a67ae`). Hugging Face static Space `https://kamiloki-swrlz-forge-moba.static.hf.space/` reported **RUNNING**, revision `eb0fd0ecf3286501ae62faff0664e50416913b80`. Live verification attempt **1** matched the exact v11.126 compiled HTML SHA-256 `dbbc8d1ac954e3e93ec9f8feb74ed0371575c6378a9b27ef77c021c20dabcec5`, **6,651,868 bytes**, **158 patches**, all **68 bundled assets**, and the `SOURCE.json` receipt. This certifies production publishing/integrity, **not manual Android gameplay acceptance**.

**User acceptance next:** open a newly loaded canonical **Grand Moonbell Wildwood Sheep Tag starter** to see three indestructible prebuilt raised crossings; a previously saved personal map is deliberately not overwritten. Tap a house skill, verify its ghost starts on the controlled sheep, drag within the meadow and release to build. Verify the sheep can traverse both ramps/decks without jumping; Mirror ready at level 1 with a 12 s cooldown; Totem becomes usable after constructing one house, with 25 s repeats. Player-built structures remain demolishable. Preserve report of any Android-specific problem and exact game mode/map source.

## §E v11.126 · Sheep-centered building, permanent raised routes, faster sheep abilities (2026-10-26)

Owner-requested improvements extend the verified v11.125 safe house placement and local collision-gap indicators. On tapping a building skill, its **live green/red build preview starts exactly at the controlled sheep's position** instead of requiring a skill-button drag. Move it by dragging on the meadow, releasing to commit through the native build/placement pipeline. Dragging from the skill ring remains optional. Merely previewing never builds.

The authored **Grand Moonbell Wildwood Sheep Tag starter** gains three completed elevated crossings: Pinewatch (-52.5, -45), Moonflower (60, -52.5), and Amberglade (-52.5, 60). Each group has two functional 6 m ramps attached to a 6 m walkway: **nine baked pieces**, native upper navigation for sheep/wolves. These specifically identified *world routes* cannot be damaged or sold during gameplay. Player-built ramps, walkways and houses remain normally destructible; this does not overwrite custom/user-saved maps.

With the Archive sheep skills enabled, **Mirror / Illusive Split** unlocks at level 1, ready at match start, and repeats after **12 s** (was 30 s). **Totem** is reusable after **25 s** (was 120 s) as soon as an owned house is completed, rather than demanding nine houses. Totem still needs an actual completed house to convert. Explicitly disabled Classic abilities remain disabled.

**[Full 158-patch candidate and prior-source validation](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40343082708) PASS**: compiled original 157 patches without alteration, measured complete 158-patch source, verified JS syntax and regression tests for preview/no-auto-build, physical raised route joints, collision distance from spawns and obstacles, permanent-route protection, and both cooldowns. Final complete HTML: **6,651,868 bytes**, SHA-256 **`dbbc8d1ac954e3e93ec9f8feb74ed0371575c6378a9b27ef77c021c20dabcec5`**, existing **68 bundled assets**. Production deployment and owner's Android gameplay acceptance remain separate gates.

## §E v11.125 · Honest house clearances and safe builder relocation (2026-10-26)

The owner's actual Android v11.124 playthrough confirmed accurate house placement, but a measured **1.20 m gap** incorrectly appeared **BLOCKED** while the sheep could traverse it. The old label checked a lengthy approach beyond both facing walls; unrelated nearby houses could make a locally walkable corridor red. The v11.125 additive patch uses native swept collision **inside the facing walls** with the current sheep/wolf radii and nearby obstacles when a gap meets the safe snapping width. Cyan/Gold mean **local physically clear space**, not a guarantee of a connected whole-map route. Truly obstructed and historically unsafe 0.90 m gaps remain blocked.

Owner also requested placing houses under the standing sheep and moving the builder to the **closest safe outside position**. The assembled v11.124 native validator already exempts its builder but protects other units. The v11.90 opt-out disabled the existing nearest-safe-side ejection path. v11.125 restores only that previously implemented collision-tested path: if every side is blocked, reject the build without changing gold or structures. Original snapping, joystick movement, collision, structures, other-unit protection, HUD and 68 assets remain unchanged.

[Candidate CI #40278508544](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40278508544) **SUCCESS**: exact sealed v11.124 reconstruction, new patch, JavaScript syntax, earlier passage regression, blocked-gap and nearest-side exit CPU cases. **157 patches**, **68 assets**, **6,645,687 HTML bytes**, SHA-256 29a27f8a683abfbaf31ee0a3b02fc0dabb49168f302602f99c1361998621c1d8. This preflight is not the guarded production deployment or owner Android acceptance.

**Official full-chain v11.125 seal:** [GitHub Actions diagnostic #40279350924](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40279350924) reconstructed the complete 157-patch release and compared it with the candidate. The canonical build includes the newly preserved v11.124 release-notes history and sets the new release-notes version. Its **6,645,795 bytes**, SHA-256 `4b4e0a69a388083817b72e6600c7c7a8e3b6c08247d4714430aebf0717f416ac` supersede the candidate-only seal for production. No gameplay/source behavior was changed by this history reconciliation. Guarded production deployment and owner Android acceptance remain separate.

## §E v11.124 · Sheep Tag flush-or-passable house placement (2026-10-25)

Android owner test of v11.123 showed an existing **0.90 m “SHEEP ONLY” gap** that still trapped the sheep. The correction is **in building placement itself, not sheep movement**. Near existing structures, new houses now snap either visually flush (a 2 mm collision-safe epsilon) or one additional navigation grid interval farther out: **1.20 m at the default sheep radius**, dynamically enlarged for larger sheep. The authoritative placement validator rejects intermediate horizontal, vertical, and near-corner slits. For a new snapped passage, it also checks an actual swept sheep-collision segment through the opening against existing obstacles and the proposed house; if obstructed it rejects the placement rather than showing a passable preview. Old houses remain where the user placed them, but the clearance overlay marks their 0.90 m unsafe gap **BLOCKED** instead of SHEEP ONLY, and explains the new minimum safe spacing. Main menu, thumbstick, skills, collisions, movement speed and existing camera/nav paths remain unchanged.

Preflight [run 40270681386](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40270681386) verified official **156 ordered patches and 68 assets**, **6,643,360 bytes** source SHA-256 `8a45b889b2d48edc1101e423b05c97ebf68de55eaf6b158cd4c6fbc7914fa08c`, plus exact snap placement, third-party blockers, honest labels and earlier v11.123–v11.114 editor regressions. Real device passage acceptance remains for the owner to validate.

## §E v11.123 · Sheep-safe snap placement, Projects-first editor toolbar and inset mobile controls (2026-10-25)

User Android screenshot of Sheep Tag showed four small farms with misleading narrow clearances and the nearest gap explicitly labeled BLOCKED. Requested new house placements snap either directly against another house or with enough open passage for a sheep, instead of leaving no-man's-land slots. User also requested the native §E main header reorganized with Projects at the far left alongside Play/Pause/Simulate/Stop and slightly larger buttons, plus Sheep Tag skill icons and movement joystick shifted modestly inward.

**Implementation:** Existing Sheep Tag house placement now uses a 0.3-world-unit lattice instead of arbitrary 0.15 fine steps; when side-adjacent it magnetizes to visual flush contact (approximately 0.015 world units) or an unobstructed *width* of at least 0.9 world units (raised automatically for user-configured larger sheep collision radii). Existing polygon/rotated collision, sanctuary, resources, construction, navigation, and camera rules remain authoritative; the same validation runs on the preview and the actual build order, denying a narrow misleading slit. The native ground placement guide uses matching 0.3 grid. The native header's existing DOM buttons—not replacement controls—are reordered Projects, Play, Pause, Simulate, Stop before other tools, retaining handlers; mobile controls are gently enlarged. The right-side Sheep Tag ability/build icons shift approximately 18–28 CSS pixels toward center and movement stick is inset on the left without changing their touch gesture implementation.

**Verification:** targeted source-assembled tests [v11.123 preflight](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40249141658) passed grid-lane behavior, header reordering, HUD offsets and earlier gesture/inspector regressions. Full official seal tracks **155 patches, 68 assets, 6,637,490 HTML bytes**, SHA-256 `858c08fae2edd165aec884363672d41a5591db6456e8cb5389e25d73d2668376`. Neither mathematical clearance nor static tests prove a sheep can navigate every *connected* neighborhood if other walls or obstacles intervene. Release receipt and owner Android gameplay remain separate verification steps.

## §E v11.122 · Full-workspace mobile gesture boundaries (2026-10-25)

Owner feedback clarified that the Model Atelier-only v11.117 and v11.120 guards did **not** apply to the normal §E maker/editor page: double-tapping starter projects in the main workspace still triggered browser page zoom, and holding non-editable text/controls still opened Android/Chrome selection menus.

**Fix:** Apply document-level `touch-action:manipulation` to §E's HTML/body (not the Chrome application or unrelated websites) so rapid taps do not cause browser *page* zoom, while native browser pinch zoom and the editor's specialized touch/drawing/camera rules remain intact. Capture and cancel `contextmenu` and `selectstart` only on non-editable content across the full engine. Restore CSS callouts, caret, copy/paste and selection specifically for input, textarea, contenteditable and textbox surfaces, including those inside Model Atelier whose older styles blocked them. Do not cancel touchstart, pointerdown, pinch, dragging, scrolling or clicks.

**Evidence:** Chromium mobile-emulation smoke test (viewport scale remained 1× after two fast taps, noneditable menus prevented, editable fields allowed); §E scoped Node tests plus camera, gizmo, preview, inspector and earlier toolbars passed in [focused preflight](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40236170378). The Android owner still needs to verify actual Chrome/WebView behavior and any operating-system-controlled copy menus. Version **v11.122**, **154 ordered patches**, **68 assets**, **6,630,708 HTML bytes** SHA-256 `9e88c9b1c7cbf96f18d7e0720b02562812233ba664facb833368ce71f3a5b449`.

## §E v11.120 · Unobscured top menus, centered category buttons, and editor-only browser double-tap control (2026-10-25)

User Android v11.119 screenshot demonstrated toolbar collisions at the top of Model Atelier, a viewport mesh quickstrip partly hidden behind the header and reference toolbar, and bottom category buttons kept near a rail edge. Fast double-taps within the editor could also trigger Chrome's page zoom instead of a second tool tap. The user requested all three presentation fixes, retaining model operations and camera gestures.

**Implemented:** Explicit stacking order places the original Export and Views dropdown menus above surrounding header/viewport/display/reference controls, keeping their anchored buttons intact. The existing mesh quickstrip's calculated location receives a minimum vertical clearance measured against the *actual* complete top toolbar (including dynamic rows), while preserving its earlier native positioning and user dragging. The bottom tool rail uses safe centering when its content fits, retains touch-scroll and right-to-left thumb preferences when overflowing, and scrolls the currently selected category toward the visible center. The web-platform `touch-action: manipulation` is scoped to `#modelAtelierPanel` and its non-canvas chrome to prevent browser double-tap page zoom; editor-specific canvas orbit/pinch logic, one-finger mode selection, horizontal scrolling, text field selection and deliberate browser pinch-zoom remain available. No document-wide touch interception or viewport maximum-scale lockout is introduced. This cannot disable Android/Chrome gestures outside the §E page.

**Validation and release gates:** [targeted tests v11.120](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40227843968) PASSED new menu layer / safe-top / RTL-aware centering / double-tap policy assertions and previous v11.119 unified inspector, v11.118 taxonomy, v11.116 camera pinch, precision gizmos, preview selection and v11.117 context-menu regressions. Official final-source artifact: **152 ordered patches, 68 packaged assets, 6,626,204 HTML bytes**, SHA-256 `17d0920293dbc1ab80d34d6576d1ff91c627115db810785214839d360d862aaa`. Official sealed-source verification, separate guarded Hugging Face deployment and real Android touch/menu acceptance are distinct checks; simulated behavior is not owner-device acceptance.

## §E v11.119 · One draggable inspector, contextual mode rail, cleaner top chrome (2026-10-25)

Owner's screenshots of Android v11.118 demonstrated the conflict: clicking Sculpt launched a second full-width compact bottom workbench, while the correct native mesh inspector remained as a separate movable panel. The requested model-editor workflow is now one main category rail along the bottom, **one horizontal submode rail immediately above it** for categories with multiple operations, and **one mode-specific native inspector** in the existing draggable right-side tool dock.

**Architecture / exact changes:** The v11.61 context workbench and its real native-control proxies are embedded inside the original `#modelAtelierInspectorDock`, rather than creating a second bottom-sheet overlay. The v11.62 mobile takeover no longer hides the original inspector. Existing category buttons (Meshes, Sculpt, Lasso, Topology, Face, Appearance, Motion, References) select available submodes; for Sculpt these include Brush & falloff, Precision circle cut, Brush placement, Brush shape, Vertex editing and Sculpt resolution. Selecting a submode displays its registered settings and actions in the same draggable inspector. **More** returns to the original full native inspector. Mode-specific settings do not create new parallel geometry implementations. The bottom mode rail scrolls horizontally and is hidden when unnecessary. Resizing, dragging, hiding, preserving Undo/model data and the non-destructive cut preview remain native.

**Top controls:** Save model and Close remain available. Existing GLB, OBJ and PNG controls move to an anchored **Export** menu; existing view-direction presets and Center Pan move to an anchored **Views** menu; Render Mode, Target, display/wire/interior toggles and References remain available. Original DOM buttons are moved rather than cloned, retaining event listeners. Existing touch callout suppression remains in place. The Chrome bootstrap regression discovered v11.117's scope mismatch between the installed long-press helper and its bootstrap call; this forward-only patch exposes that existing helper through `window` without changing its behavior.

**Release evidence:** 151 ordered source patches, 68 bundled assets, **6,621,308 HTML bytes**, SHA-256 `62dfb014d58287c78281e9579565732ecd7366bcd26d178110cc6d6abadca510`. Targeted compiled UI and previous radius/camera/preview/long-hold regressions passed (see workflow logs). A separate experimental headless-Chrome test established that the engine module initializes but its isolated starter-scene path could not open a model; it **did not pass full live touchscreen UX acceptance** and is not used as positive acceptance evidence. Final source package verification, hosted integrity and **owner Android usability** remain distinct release gates.

## §E v11.118 · Modeling-editor-informed semantic tool organization (2026-10-25)

Owner request: audit the existing §E Model Atelier tool grouping and move relevant tools into relevant places. Compare the architecture with the published Blender workspaces manual (https://docs.blender.org/manual/en/latest/interface/window_system/workspaces.html), Autodesk Fusion toolbar/workspace documentation (https://help.autodesk.com/view/fusion360/ENU/?guid=GS-THE-FUSION-INTERFACE), and the Nomad Sculpt tool and topology manuals (https://nomadsculpt.com/manual/tools , https://nomadsculpt.com/manual/topology). The borrowed design *principle* is domain separation with context-appropriate operations; §E retains its own implementation and visual identity.

**Tool audit / implemented destinations:** Default thumb rail now follows **Meshes → Sculpt → Lasso → Topology → Face → Appearance → Motion → References → More**; original DOM buttons and event listeners are moved in-place, not cloned or replaced. **Meshes** owns object selection, transforms, shape identity and model export. **Sculpt** owns sculpting brushes, falloff, local vertex refinement and the complete precision circle cut (radius, depth, flat/rounded cap, radius/depth gizmos, Preview and Apply). **Lasso** owns masking, boundaries, region painting and deformations. **Topology** owns face/edge/vertex topology operations, UV mapping, LOD and mesh audits. **Face** owns portrait/anatomy, facial landmarks, profile and photographic cutout. **Appearance** now owns material, color and surface finish, not unrelated facial tools or precision cuts. **Motion** owns poses and animation; **References** holds photographs/comparison; **More** retains the original inspector and advanced native settings.

Contextual discovery now routes individual control IDs, including previously untracked nested fieldsets, rather than sending all unknown sections into Appearance. The existing source controls remain the only editor authority: contextual proxies only operate the real nodes; favorites, recent actions, presets, selection, saved scene formats, Undo, pinch/orbit, inspector drag/scroll and browser-long-press protection are preserved. Previously hidden/restricted features are not promoted as functioning commands. Tools are not cloned, removed or replaced, and no geometry transformations are changed.

**Evidence:** [targeted category and legacy gesture tests](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40218133774) PASSED on the exact v11.117 base plus v11.118 patch. The final source is 150 ordered patches, **6,608,292 HTML bytes**, SHA-256 `1c2e048831bcc21ebf2b19149e9ab44263cf66e096f4fae4470fb0978d4efa12`, preserving 68 packaged assets. Targeted unit results, official sealed source verification, live hosted file integrity and owner Android usability are separate gates.

## §E v11.117 · Suppress Android/Chrome long-press menus inside Model Atelier (2026-10-25)

The owner requested that holding a finger anywhere inside the editor should not trigger the browser's native popup/dropdown context menu. Add a **Model Atelier-scoped** forward-only gesture guard. While `#modelAtelierPanel` is open, capture `contextmenu` on the editor viewport, floating tool panels and other editor controls, including its detached `#seMobileNumberPad` modal. Suppress incidental text selection on **non-editable** editor chrome, while preserving text-input caret, selection and paste, plus the existing touch-action CSS, scrollable inspector, single-finger orbit, two-finger pan/pinch, sculpt and radius/depth gizmo interactions. Closing Model Atelier restores the browser's ordinary context-menu behavior outside the editor; unrelated project/app surfaces are not affected. Scoped `-webkit-touch-callout:none` CSS and the minimal `contextmenu`/`selectstart` handlers never intercept `pointerdown`, `pointermove`, `touchstart` or `touchmove`. This does not claim control over browser/OS chrome outside the page.

**Evidence and gates:** [targeted source preflight #40203921640](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40203921640) passed suppression/selection scoping, previous camera-touch and radius/depth regression, and JavaScript syntax on the 149-patch candidate. Official v11.117 final assembled source is **6,605,187 HTML bytes**, SHA-256 `0a7af4ccc8515cc0f12a827427b2fba71e0362e878d3c6f45f16bb74bfecaa84`, retaining all 68 bundled assets and prior history. Sealed-release CI, guarded Hugging Face deployment, hosted integrity and owner's Android long-hold acceptance remain independent gates.

## §E v11.116 · Precision radius touch and reliable camera gestures (2026-10-24)

The owner's Android screenshot showed an oversized/clipped white sphere during a radius-handle drag, simultaneously visible XYZ mesh arrows, and incorrect finger-camera behavior. Source inspection found that v11.76 allows the exterior camera to zoom to 0.16 units (inside a selected ball), and the v11.115 preview ghost tap stops propagation of pointerup before the camera's touch map is cleaned, leaving a phantom finger. The wide v11.114 ring touch hit target additionally competed with ordinary orbit movement.

This forward-only fix protects the existing native precision cutter instead of adding a bowling-ball-specific preset. In precision mode, pinch, wheel and zoom buttons respect a camera distance derived from the selected mesh's world-space bounding sphere; opt-in interior inspection retains close camera access. Tapping a ghost preview releases the corresponding camera pointer. Two fingers interrupt an active radius/depth drag safely, restore its uncommitted value, and transfer both pointers to camera pan/pinch; the remaining finger resumes orbit once its partner lifts. Touch grabs use a narrower ring with a separate larger grip target, and XYZ whole-mesh gizmos stay hidden while precision editing is active. Cancellation never saves a half-cut; explicit Apply/Undo remains the sole geometry commit path.

**Validation:** [v11.116 sealed source verification #40159277934](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40159277934) PASSED 148 sequential patches, 6,603,142 HTML bytes, SHA-256 `a779619854cc8fc0639ac5c3e4ca8555c37b09a7993be3db3ec11591ef06868c`, JavaScript syntax, v11.114 radius/depth and v11.115 preview/mesh-transform regressions, and new camera pointer handoff / ghost tap / safe zoom tests. All 68 bundled assets and prior projects are preserved. Official source packaging, gated Hugging Face deployment and owner Android UI acceptance remain separate evidence levels; green automated tests do **not** establish that the owner has visually accepted the gesture feel.

## §E v11.115 · Prevent detached precision-cut preview and accidental mesh moves (2026-10-24)

The owner photographed one Model Atelier sphere plus a separate apparently unselectable second ball with a carved hole while native Mesh tools were set to **Move Z**. The editor showed **1 individually editable meshes**: the holed sphere was actually an unsaved **precision-cut preview ghost** (rendered in `world`, not the selectable `modelRoot`), while the real source sphere moved independently beneath it. This version guards the lifecycle of that temporary render, not the geometry of the underlying cut. During an active ghost preview, block native Mesh Move/Rotate/Scale hit-handle starts and quick-strip +/- whole-mesh nudges, with an explanatory warning directing the user to amber Radius and violet Depth controls. A tap on the ghost proxy now reselects the corresponding editable source mesh safely, and native `renderParts()` selection/Undo/transform rebuilds clean up stale ghost geometry. Clearly mark the cut as **PREVIEW ONLY** until Apply; no preview change invokes `checkpoint()`, changes native mesh source or silently commits a cut. The original user-made precision cut remains fully editable once explicitly Applied. Targeted [preview-safety preflight #40153683396](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40153683396) tested ghost raycast proxy selection, direct transform hit blocking, nudge blocking, render invalidation and zero model checkpoints, alongside the prior sealed artifact + JavaScript syntax. All 68 assets, previous tools, meshes, and viewport radius/depth handles are preserved. [Full-source seal #40153853279](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40153853279) passed **147 ordered patches**, **6,600,621 HTML bytes** and SHA-256 `5cf410b40661f9c4a0a11089eceaca9a57a6ff1f6664d7a9a1e8cea8ed879f37`, preserving all **68 bundled assets**. Official release packaging, live host checks, and owner Android acceptance remain independent gates.

## §E v11.114 · Direct viewport radius/depth editing for Precision Circle Cut (2026-10-24)

Owner-requested phone-friendly modeling UX: numeric radius and depth should each have a **toggle** that exposes touch-draggable gizmos directly on the part in Model Atelier. v11.114 adds independent **yellow Radius handle** and **purple Depth handle** toggles inside existing Precision circle cut controls. The radius handle outlines the exact circular footprint on the curved sphere or flat source face; the depth guide reaches from selected surface down the bore's cut axis. The user can drag the colored ring or bead to resize width, or drag the purple grip to increase/decrease depth; the numeric fields stay synchronized. Front-on cameras switch automatically to vertical downward/upward depth adjustment when axial screen projection is too small. Touch interactions are captured only when a handle is hit; tapping elsewhere continues native selection/orbit. During drag only temporary helper geometry/fields change; on release the engine regenerates its validated non-destructive preview once, and only explicit Apply saves/calls Undo checkpoint. Gizmo overlays are editor-only and omitted from model JSON/export; turn both toggles off to restore an uncluttered viewport. Previous manual individually editable cut layout, flat-to-rounded bottoms, prior sculpt modes, Wireframe/X-Ray, histories, 68 assets and unrelated apps are preserved. **Targeted test #40137169712** passed simulated Android pointer drag (radius, straight-on depth, synchronous fields, preview on release with no checkpoint) and complete last-version patch integration. Sealed source [preflight #40137347856](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40137347856) passed 146 ordered patches and JavaScript syntax: **6,594,602 HTML bytes**, SHA-256 `7cd989c5973bb978725f0495ad9b20cf17328cbeaacc0954e0ebdf1b5717c22b`, with 68 preserved assets. Official release packaging, live hosted verification and owner Android UX acceptance are separate gates.

## §E v11.113 · General precision circle cut (2026-10-24)

Owner correctly rejected the bowling-ball-only feature framing. This additive release extends user-placed **Precision circle cut** into a reusable modeling tool, rather than automating preset hole arrangements. Pick each surface position manually, set cut radius and depth, choose a **flat (0) through rounded (1) bottom**, preview exact candidate geometry, and Apply with Undo. Reopen a prior cut's recipe to adjust its dimensions without inadvertently relocating it; relocation requires an explicit checkbox. Real closed indexed cavities now work on **native spheres**, **planar native box faces** and **flat native cylinder end caps**. Limits: initial surface orientation shared by cuts on a part; up to **3 on spheres**, **6 on one box face/cylinder cap** under native 9k-vertex/16k-triangle budget. Not a general Boolean solver for imported arbitrary meshes or curved cylinder sidewalls. Existing native project metadata, rendered previews, ordinary sculpt brush, JSON and geometry export, and 68 assets remain preserved. Targeted geometry [preflight #40135278226](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40135278226) passed seven live-indexed-mesh scenarios, including flat-bottom box cut and six box sockets, with zero open/nonmanifold/inverted/degenerate faces and valid replay. Full 145-patch source [seal #40135439020](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40135439020) passed: **6,579,505 HTML bytes**, SHA-256 `445a93e9a1b077aebba942524c54877bb709f8e73687d9b600432232a40194c8`, 68 preserved assets. Official package, hosted verification and owner Android UX acceptance remain separate.

## §E v11.112 · Manually place and edit every circle carve (2026-10-24)

Owner correction superseded the v11.111 automatic bowling-ball preset: **the user wants the fundamental precision tools to make each hole themselves**, not a three-hole generator. Replace the UI preset with a manual one-hole-at-a-time workflow in Sculpt: use existing **Pick center on mesh**, tap anywhere on the visible ball hemisphere, choose independent local circle radius, exact depth, and rounded-bottom cap profile (0.5–1.0), preview the changed indexed geometry, and deliberately Apply. `roundHolePlan` is validated native part metadata saved alongside each topology mesh; after a cut, pick another location or choose an earlier hole to modify and rebuild the same ball without losing earlier holes. First cut reconstructs the original procedural sphere, preserving Undo recovery; each subsequent cut remains editable, Undo and JSON saving remain supported. All bores share the first hole's drill axis (the initial lightweight/parallel-cavity limitation). Supports up to three user-positioned holes within the existing portable 9k vertex / 16k triangle cap; this does not claim general-purpose Boolean cutting of arbitrary meshes. A second spherical midpoint refinement pass corrects the crumpled, faceted exterior in the user's v11.111 Android screenshot. Owner selection of each hole is the crucial design requirement; no automatic placement remains in the UI. Targeted [preflight #40133868935](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40133868935) passed manual geometry replay (1/2/3 holes: 4674/6050/7426 verts, 9344/12096/14848 faces), manifold checks, persisted plan schema, curvature improvement, patch application and JavaScript syntax. Full versioned [seal #40134031269](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40134031269) passed with **144 ordered patches / 68 preserved assets / 6,576,477 generated HTML bytes**, SHA-256 `77d8da050f64d09ab611d33bf7b97685a99b24eb7ce81e5fa0d9df21be46d52c`. Hosted integrity and owner Android UX acceptance are independent gates.

## §E v11.111 · Actual drilled bowling-ball holes (2026-10-24)

Code audit confirmed that v11.110 sculpt Intrude pushes native vertices and cannot drill precise circular openings; face intrude is per-triangle, while Boolean lasso is only a selection mask. Instead of implementing broad CSG, a bounded `Round hole maker · bowling ball` is added inside Model Atelier Sculpt. On a selected procedural sphere it generates a **new native indexed topology mesh** with 1 or 3 circular openings, stitched cylindrical interior wall loops and hemispherical ends. Use picked mesh center to orient the group or default front, set finger radius/depth, Preview to temporarily display true edited geometry, then Apply to replace the original sphere; Undo restores the original. The original part's existing sculpt strokes will be replaced by a new clean round-hole mesh (explained beside the controls). The builder reuses the native `topologyMesh` schema, triangle budget, validation and audit; no new core mesh format, external CSG library or portable-format exception. The phone menu, existing sculpt brush, rendering modes, save/export and all 68 bundled assets remain intact. Targeted geometry regression [#40129504189](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40129504189) passed: 1-hole 2,114 vertices/4,224 faces; 3-hole 3,322 vertices/6,640 faces; no open edges, nonmanifold edges, winding conflicts or degenerate triangles. Targeted geometry regression [#40129504189](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40129504189) and full-source reconstruction [#40129688184](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40129688184) passed. **143 ordered patches, 68 preserved assets, 6,571,928 output bytes**, SHA-256 `eac0886d3fcfbf922979851044344794c9670ccc8feba358e06671d931f3845e`. Live-host verification and owner visual testing are distinct final gates.

## §E v11.110 · Displacement-accurate before-Apply sculpt preview (2026-10-24)

After owner Android acceptance of v11.109's rounded surface-following brush, a bounded audit found one misleading visual edge case: the translucent teal shader could still paint untouched source triangles, including when the submitted stroke would move zero vertices because of depth, snapping or selection. The v11.110 follow-up only improves temporary preview presentation: sample exact native stroke displacements on the already disposable preview geometry, multiply fragment alpha by interpolated movement, trim wireframe edges to moving regions, and explicitly report when no vertices will move. It preserves the existing yellow radius ring, green/cyan gizmo, lavender depth indicator, the stroke/apply operation, Wireframe/X-Ray, mobile menus, Undo, native exports, saved scenes and all 68 bundled assets. The owner remains the final mobile UX acceptance gate. Targeted source preflight [#40124895300](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40124895300) passed: **142 ordered patches, 68 retained assets, 6,559,449 HTML bytes**, SHA-256 `85570c8d83a2eb1e15ea4c0854d0571b590f6e9858925996c4458aa1ea187d41`. Release sealing, hosted integrity verification and owner acceptance remain separate.

## §E v11.109 · Round surface-following sculpt preview (2026-10-24)

Owner Android acceptance of v11.108 showed the teal before-Apply ghost had squared/polygonal outer edges even though the yellow radius ring was correct. Root cause: the old preview included entire displaced-vertex triangles and rendered their complete face edges. This forward-only patch retains the original native brush stroke and yellow ring, but masks the actual proposed temporary mesh with a radial alpha fade in unmodified object-local space and clips its teal wireframe edges to the brush radius. Unaffected surface faces near the footprint remain available for a smooth transition. Only the non-destructive ghost visualization changes: Undo, Apply, exported/saved meshes, mobile inspector, wireframe/X-Ray, source and 68 bundled assets stay intact. GitHub targeted full-source [preflight #40119683427](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40119683427) passed deterministic reconstruction, preview guards and JavaScript syntax: **141 ordered patches / 68 preserved assets / 6,558,232 generated HTML bytes**, SHA-256 `54f1a4f994a14db376868240a14c56442ed7dfd38c5ac84a3aee2cf1545a1aa4`. Dedicated deployment and hosted verification remain separate gates before claiming live status.

## §E v11.108 · Native sculpt ghost preview with classic amber radius ring (2026-10-24)

The owner's side-by-side Android screenshots establish the intended pre-Apply brush UX: keep the familiar yellow/amber radius ring and visible wireframe, then show a teal temporary deformation preview on the existing mesh. §E v11.108 uses the real native sculpt stroke evaluator on a disposable geometry clone for meshes up to 48,000 vertices, rendering affected wireframe faces, raised/recessed vertex positions and motion vectors before committing. Dense models use a bounded, explicitly labeled sampled push preview where supported; other high-density modes retain the radius/depth guide without misleading precision. The new "Show mesh preview before Apply" toggle starts enabled and reacts to changed brush controls. Preview overlays are editor-only, disposable, non-pickable by the model selector, and never stored in source geometry, Undo history, JSON or GLB. Existing v11.107 amber footprint/violet depth, v11.106 Wireframe/X-Ray safeguards, mobile menus, saved scenes and all 68 assets remain preserved. Targeted GitHub preflight [run 40116649201](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/40116649201) passed source reconstruction, exact patch anchors, JavaScript syntax and read-only preview checks; **140 ordered patches / 68 preserved assets / 6,555,286 generated HTML bytes**, SHA-256 `176ff6ec6baba39bffe123985ec1fecdd725b3002cf706f1a0c06950ebcf815b`. Code sealing and GitHub deployment are separate from actual Android aesthetic/gesture acceptance.

## §E v11.107 · Live radius footprint and depth guide before sculpt Apply (2026-10-24)

During owner testing of the new visible Pick center on mesh marker, the owner requested the marker to **match the brush radius** and show a **second layer preview for depth** before applying the edit. This new forward patch replaces the fixed-size helper ring with a brush-radius footprint and adds an inset ghost depth ring, tapered spokes and a center displacement axis (inward for intrude, outward for extrude). The preview updates as numeric inputs, mode and orientation change; it uses the native sculpt form's validated radius including screen-pixel to local conversion. It is an **illustrative planning guide**, not a Boolean cut or guaranteed precise deformed topology: the real stroke falloff and surface targeting still determine affected vertices. Editor helpers are non-pickable, are not saved or exported and leave brush history untouched. Preserve the v11.106 render-mode fix, menu sizes, touch scrolling, and drag behavior. Preflight assembled **139 ordered patches / 68 preserved assets / 6,545,909 HTML bytes**, SHA-256 `9aa81dd84b445e3cb51e84279a4141acd9a83069305332720753fea42f8946d0`. Production verification and actual Android visual/gesture acceptance are separate gates.

## §E v11.106 · Rebuild sculpt geometry without losing Wireframe/X-Ray (2026-10-24)

User's Android screenshot shows Render mode remains **Wireframe** but the actual sphere changes to a shaded solid immediately after pressing **Apply brush**. v11.105 targeted stroke Undo but did not enforce a viewport material invariant after *geometry edits*. §E v11.106 adds an after-render mesh/material consistency check for the global/selected viewport modes and explicitly requests an HD redraw whenever meshes or render display are rebuilt. It avoids extra geometry reconstruction and retains untouched the approved model window size/spacing/dragging, center marker, touch controls, assets, saved meshes and undo history. Source preflight measured **138 ordered patches, 68 preserved assets, 6,541,671 HTML bytes**, SHA-256 `18da40e3e728b97d0822494bb8038a6fe52a299603e11bebc6cd5aae8e4c3356`. Final hosted verification and Android Wireframe/X-Ray acceptance are still separate gates.

## §E v11.105 · Sculpt undo retains viewport mode; roomier floating menus (2026-10-24)

On Android v11.104 the owner confirmed surface-pick marker visibility but reported that clicking **Remove last stroke** while in X-Ray changes the render mode, and the right inspector remains cramped. Code inspection found the stroke-removal handler triggered `signalEdited()` **and** `select(p.id)`, redundantly rebuilding both geometry and view. The new forward patch eliminates the extra select/rebuild and independently preserves the global/per-part viewport display state and the All/Selected scope before refreshing mode UI; no sculpt geometry is altered. The panel becomes slightly wider, keeping 12px+ side trim, and increases vertical rhythm between labeled fields, paragraphs, sections and controls. Previously accepted v11.103 height, window dragging, scrolling gutters, touch-to-hold numeric pad, picked-point marker, 68 assets and all projects remain unchanged. Preflight measured **137 ordered patches, 68 preserved assets, 6,539,743 HTML bytes**, SHA-256 `d845e5ae1b064f4a6e1d7c41a654d1e561bfa8f4e1e02db227b5443ac9af5d3c`. The hosted-file verification and real Android X-Ray/Undo acceptance remain separate release gates.

## §E v11.104 · Visible sculpt pick marker and readable mobile menus (2026-10-24)

User Android screenshots show Pick center on mesh populating XYZ coordinates but no visible marker, and extremely cramped, difficult-to-read floating tool menus. This release adds a non-exporting, depth-test-disabled picked point ring/crosshair and outward surface-normal arrow aligned to the selected mesh, with an accessible XYZ status readout. On deselection or repick the marker is cleaned up. Native menu controls receive consistent typography, spacing, fieldsets, contrast, input alignment and touch-sized buttons while preserving the user-approved v11.103 window dimensions, dragging, scrolling gutters and 380ms hold-to-edit numeric keypad. Drilled cylindrical subtraction is **not** implied or added by this UI change; it requires a separate audited geometry feature. Preflight measured **136 ordered patches, 68 preserved assets, 6,535,811 HTML bytes**, SHA-256 `e205d04d8bd66d69994cbeca52b8a089468a6275146bfae59ba884bda6f443f1`. Live-host source verification and owner Android acceptance remain separate release gates.

## §E v11.103 · Double mobile inspector height only (2026-10-24)

After testing v11.102 on Android, the owner confirmed the floating Model Atelier window is better positioned and sized horizontally but asked to make the menu **twice as tall**. The new forward patch changes only mobile inspector height from 34dvh/350px to 68dvh/700px max, with an expanded state of 78dvh/800px max. The default 390px max width, original drag behavior, scrolling gutters, hold-to-edit keypad, 68 bundled assets, scenes and meshes are unchanged. Source preflight measured **135 patches, 68 preserved assets, 6,526,071 HTML bytes**, SHA-256 `7ce2d65c328d3c14f417062daaeb6f37f30b592c8f0b99f5cb305fd3bf1ee395`. Final hosted integrity verification and actual Android viewport acceptance remain separate gates.

## §E v11.102 · Balanced mobile size and real inspector dragging (2026-10-23)

Owner's next Android screenshot confirms the quarter-screen size in v11.101 is now too small and the inspector cannot be dragged. The existing v11.60 header pointer handler does calculate a new position, but later mobile CSS applies `top:auto!important`, `left:auto!important`, fixed `right` and `bottom`, so the script's inline top/left values never win. v11.102 retains that exact original pointer handler, preserves its model/tool behavior and translates its actual coordinates into scoped CSS variables which override mobile docking only after dragging. Default size is balanced at max 34dvh / 350 CSS px high, 390px wide; Expand reaches max 43dvh / 440px high and 440px wide. Side swipe gutters, hold-to-edit numeric pads, all scene geometry and exports remain untouched. Preflight measured **134 ordered patches, 68 preserved assets, 6,525,097 HTML bytes**, SHA-256 `fb2ec79211686c3aa4a69deaaa06570b83e8137abf9fb85b2d7a4869a2b1bb7c`. Production hosted verification and owner Android drag/scroll acceptance are separate gates.

## §E v11.101 · True quarter-screen compact mobile tools (2026-10-23)

Following real Android testing of v11.100, the owner reported that the supposedly compact tool panel still occupies roughly half the screen. The underlying 49dvh inspector default and 62dvh Expanded value caused that directly; an older mobile-adaptive inspector also carries higher-specificity !important sizing. The new additive release overrides both selectors: mobile inspector starts at no more than 26dvh / 255 CSS px, up to 320px wide, and Expand grows only to 38dvh / 385px and up to 375px wide. Context-sheet defaults are correspondingly reduced. All scroll gutters, deliberate number-field holds, brush controls and prior models remain unchanged. Compiled release measurement: **133 ordered patches / 68 preserved assets / 6,521,969 HTML bytes**, SHA-256 `011f44a659a6f0a76d482ba375476735b5f43c038082d3321f19f24bd2416162`. Full production verification and Android touch acceptance follow separately.

## §E v11.100 · Compact mobile panels, side swipe gutters and hold-to-edit (2026-10-23)

Owner Android screenshot confirms v11.99 panel scrolling but its full-width enlarged overlay covers too much of the modeling viewport. Owner asks for a near-original floating default size, a slightly larger optional expansion button, clear left/right scrolling gutters, and deliberate short press-and-hold to open numeric editing so scroll gestures never accidentally open the keypad. v11.100 is a presentation/input-only release. It restores compact floating sheets, adds a native Expand/Shrink button, widens internal scroll padding on both sides, and requires a stationary 380ms touch before the mobile numeric pad opens. Taps and moving touches do not open inputs. All existing mesh, brush, export, keypad Apply and saved-model logic is preserved. Package preflight measured **132 ordered patches / 68 preserved assets / 6,519,939 HTML bytes**, SHA-256 `aca02a1034c5ce79a70b024a2aa692344894493c9b4c79bc1d51b50d25a0eed1`. Independent hosted verification follows the separate deployment request; the actual Android press/scroll behavior still requires owner acceptance.

## §E v11.99 · Larger touch-scrollable Model Atelier menus (2026-10-23)

Owner Android testing confirmed the v11.98 keypad works, but scrolling the small floating sculpt panel is difficult and the other tool menus also feel undersized. Root cause candidates identified in the older floating dock are `pointer-events:none` over inspector background and a mobile supervisor width rule that can omit coarse-pointer/desktop-site phones. This mobile-only patch re-enables inspector touch hit testing, explicitly allows vertical panning on scroll surfaces, expands native inspector and context panels, and makes the horizontal tool rail larger. Existing modeling algorithms, the reliable v11.98 keypad, all 68 bundled assets and saved character geometry remain untouched. Preflight measured **131 ordered patches / 68 preserved assets / 6,513,741 HTML bytes**, SHA-256 `726cae0905ef5e2f8a381bebc109856b618451c68f7fa4afb5a0401332d2c783`. Production publication and owner-device swipe/scroll acceptance remain separate gates.

## §E v11.98 · Mobile number pad tap-through repair (2026-10-23)

On the user's Android browser, tapping a numeric field caused the new v11.97 in-editor keypad to appear and immediately disappear. The touch opened the keypad during `pointerdown`; the same gesture's following `click` could land on its Cancel backdrop. v11.98 gates pad click activation to controls that actually received the initiating pointer/touch press. Keyboard activation remains supported; original numeric change handlers, gesture controls, material editors and historical models are untouched. A mobile Chromium touchscreen simulation of the isolated dialog flow passed: opening does not close, numeric Apply reaches the native input, and a subsequent backdrop tap dismisses it. This test revealed that opening-tap click events can report `detail=0`, so v11.98 does not rely on `detail` alone for keyboard detection. Exact preflight measurement: **130 patches / 68 preserved assets / 6,509,696 HTML bytes**, SHA-256 `9b5033ee9bfcd3714ee4e52c0dd4dc46c2f06b78fb87eae441ffeac33aabe76d`. The separate manual deployment and owner touch acceptance are still required.

## §E v11.97 · Mobile viewport and focus-free number pad (2026-10-23)

Android owner screenshots confirm that §e v11.96's 16px numeric input style did not prevent browser page magnification. The actual document head contained one viewport tag with `maximum-scale=1` (two additional occurrences were inside historical runtime templates, not active document tags). The real head now uses `width=device-width, initial-scale=1` while preserving user pinch zoom and leaving historical templates untouched.

On coarse-pointer devices, tapping a Model Atelier numeric field opens a 44px-button in-engine number pad without focusing the browser input. The pad supports decimal, negative values, backspace, clear, validation against field bounds, Apply/Cancel and dispatches the original native change event. Desktop keyboard input remains unchanged. The v11.96 spherical blank starter stays uniform at `0.6/0.6/0.6`.

Preflight measured **129 patches / 68 preserved assets / 6,508,578 HTML bytes**, SHA-256 `9b3725919cce4c3cb135609dc815b449ceac8711658cc276afd6ba2a80882534`. Deployment and actual Android touch acceptance are separate release gates. Existing character geometry, history and stored assets are unchanged.

## §E v11.96 · Mobile input zoom and spherical blank model (2026-10-23)

New Model Project now opens with a uniformly scaled sphere (`0.6 / 0.6 / 0.6`) instead of the old nonuniform `0.5 / 0.6 / 0.8` blockout. On mobile/coarse-pointer layouts, Model Atelier number/text inputs, selects and text areas use at least 16px fonts to avoid the browser's small-field focus zoom. This changes only the new-model starter and editor input styling: all historical scenes, artwork and game models are preserved. Integrity preflight measured **128 patches / 68 preserved assets / 6,502,021 HTML bytes**, SHA-256 `c779e0889632a773341a78cbf0c3162932e5c7c9a6da17b20a60fc1166b3f3f9`. Model geometry and historical starter assets are unchanged; phone-browser focus behavior requires owner-device acceptance. Publication follows the separate final deployment request.

## §E v11.95 · Fitted festival skirt waist (2026-10-24)

The upper skirt now follows the existing waist and bodice more closely, then blends smoothly into the lower flare. Matching trim and the waist jewel follow the fitted surface. The lower skirt, knee-limit heights, opaque underlayer, smooth anatomy, soft portrait and original attached hair piñatas are preserved.

Release **127 patches / 68 assets**, **6,501,581 HTML bytes**, SHA-256 `a0d61bfac63c666ae7037edfb6b92f509abf8f7d4314615decb3b39bffa7ce8c`, marker `V11_95_FITTED_SKIRT_WAIST`. Targeted waist dimensions, coverage, native editing/save/export and immutable source lineage are recorded in [FITTED_SKIRT_WAIST_V11_95.md](projects/swrlz-forge-moba/reports/FITTED_SKIRT_WAIST_V11_95.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md), with ordinary source publication and a separate final deployment-request commit. Owner-device waist-fit acceptance follows the release.

## §E v11.94 · Full knee-length festival armor skirt and softer portrait (2026-10-24)

All nine existing lower armor panels now overlap around the hips and thighs as a continuous festival skirt, with matching piping, insets, stitches, brocade, baubles and tassels. Every lower costume piece ends above the kneecaps; the fitted opaque shorts retain crotch coverage. The nose has a softer bridge and rounded tip, and the head is subtly narrower with a smooth neck transition. Original hair piñatas, grips, sockets, rising amber eyes and smooth leg contours remain preserved.

Release **126 patches / 67 assets**, **6,495,464 HTML bytes**, SHA-256 `ede8f335dc9f9086d5d6f1ec6abf7d73711aa56bf3ea123c7494af2daac5d78c`, marker `V11_94_KNEE_SKIRT_SOFT_PORTRAIT`. The native model retains all **327 editable meshes / 1,755,616 triangles** and unchanged UV/index arrays. All **309** previous runtime/patch sources, **66** previous packaged assets and **117** companion meshes remain exact. Targeted validation and release evidence: [KNEE_SKIRT_SOFT_PORTRAIT_V11_94.md](projects/swrlz-forge-moba/reports/KNEE_SKIRT_SOFT_PORTRAIT_V11_94.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md), with a separate final deployment request after source publication; owner-device visual acceptance follows.

## §E v11.93 · Smooth anatomy, visible hair piñatas and fitted coverage (2026-10-23)

Both original hair-attached piñatas are visible in the normal opening/body view, with their original braid grips and sockets. Detail views retain the attached companions; the full-body camera fits their combined bounds. Eyes now rise clearly from lower corners near the nose to higher outer corners, with shallow round pupils and fitted lash wings. The face, cheeks, jaw and rounded chin use a continuous smooth skin contour. Exposed shoulder/arm muscles blend smoothly; thigh, knee, calf and ankle profiles remove the abrupt calf shoulder. A new Leg detail view makes that contour inspectable.

Compact hair locks leave the piñatas as the upper silhouette. More angular overlapping dress panels retain the longer festival tailoring. The existing under-skirt is replaced with fitted opaque shorts, and armor/cuff linings follow the actual finished skin to prevent poke-through and pelvis exposure. Saved originals, previous scenes, all piñata meshes and native socket data remain preserved. Release **125 patches/66 assets/6,477,235 HTML bytes**, SHA-256 `caad492d5e7ee95808c36102b47b24fcff816c340f242f9db1fc5d24a4316cf6`, marker `V11_93_SMOOTH_ANATOMY_PINATAS`. Source/editor/coverage/native-export checks passed; the separate final deployment request follows source publication. Source, editor, coverage and export evidence belongs to [SMOOTH_ANATOMY_PINATAS_V11_93.md](projects/swrlz-forge-moba/reports/SMOOTH_ANATOMY_PINATAS_V11_93.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md); local source completion does not claim production or owner-device acceptance.

## §E v11.92 · Reference face, swept hair and longer festival dress (2026-10-23)

The female Model Atelier starter follows the owner's festival references with amber almond eyes, finer arched brows, softer cheeks and a small rounded chin. The cyan/coral hair uses overlapping swept bangs, sculpted layers and cheek-framing locks. The layered teal, ivory and pale-cyan dress extends farther down; its yellow pointed tail reaches toward the knee. Native pleats, raised brocade, running stitches, pastel hem ornaments and a fine gold fringe add editable detail.

The connected skin mesh, original companions, 4K color/normal materials, native material editing/Undo, JSON save/import and textured GLB stay supported. The saved 283-part original and complete v11.91 scene remain packaged byte-exact. Release **124 patches / 65 assets**, **6,442,424 HTML bytes**, SHA-256 `eba0e3000950a95053dc7000bf9387d89e6fefa81e7d11cacdd722f765ddf6c5`, marker `V11_92_FESTIVAL_REFERENCE`. Local native/editor/save/export checks passed; canonical publication follows the separate final deployment request. This changes the existing authoring starter; it does not add skeletal rigging. Release details and validation: [FESTIVAL_REFERENCE_V11_92.md](projects/swrlz-forge-moba/reports/FESTIVAL_REFERENCE_V11_92.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md); owner-device visual acceptance follows the dedicated release.

## §E v11.91 · Saved Festival Girl and organic anime sculpt (2026-10-23)

The previous **283-part girl starter is preserved** as **Saved Festival Girl · v11.90** (`?project=festival-girl-saved`). The main Model Atelier card now opens **Prism · Organic Anime Girl** (`?project=organic-anime-girl`). Her complete skin is one closed, connected mesh from scalp and ears through the neck, torso, arms, ten fingers, legs and feet: **254,588 vertices / 509,172 triangles**. A more inward-tapering jaw ends in a narrow, rounded chin; shaped cheeks, orbital wells, a refined nose, fitted amber eyes tilted upward six degrees at the outer corners, and lips, hands with nail plates, knees, rear calves and Achilles transitions replace the old separate primitive anatomy.

The full sculpt has **353 editable topology meshes / 1,634,372 triangles**, including the asymmetric festival outfit, original paper-ferret companions and bunny. **72 tapered 3D hair filaments**, modeled stitches, knuckle folds and fitted closed sleeve/yoke shells add geometry detail. Dedicated **4096×4096 color and normal maps** provide skin, hair flow, weave, embroidery, leather, metal and radial iris detail. Body, face, hand and full-character views support close inspection; companion isolation changes the viewport only. Native material editing/Undo, JSON save/import and textured GLB retain the complete model. Detailed native import supports **256 MB**, and a part supports **300,000 vertices / 600,000 triangles**. This is a detailed authoring sculpt; skeletal weight painting has not been added.

Release **123 patches / 64 assets**, HTML **6,421,818 bytes**, SHA-256 `ba0105f62f2e7451d4e78148cae425f4ce5e3684093fc3954d3c1f0e1105b934`, marker `V11_91_ORGANIC_ANIME_GIRL`. All **294** prior runtime/patch sources and **60** prior packaged assets preserve exact bytes. Sheep Tag retains the v11.90 collision, controls and optimized game models. See [targeted verification](projects/swrlz-forge-moba/reports/ORGANIC_ANIME_GIRL_V11_91.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.90 · Solid house blockers, furred Astra and match performance (2026-10-23)

Houses stop sheep on contact. Holding the joystick first walks up to the blocker, then follows a cached, collision-checked route around it; releasing stops immediately. The previous nearest-side/lane-center pulling and construction ejection are retired. Placing a structure over its builder is rejected without moving the sheep or spending gold. Real narrow lanes, rotated houses, unit traffic and automatic ramp/walkway traversal retain native swept collision.

Astra now has flowing shoulder/ribcage/waist contours, **one connected skull-and-ear mesh**, inset velvet pinnae and **1,100 closed curved 3D fur locks** on its body, chest and limbs. The high-resolution wolf starter has **96 editable parts / 639,772 rendered triangles**, with all **37 original courier gear/comet-tail parts byte-exact** and the original **4096×4096 color and normal images**. Native rebuild, edit/Undo, JSON save/reload and textured GLB remain available; detailed native import supports 128 MB.

Sheep Tag uses a separate optimized copy: **69,471 triangles / 29 draw meshes per wolf**, compared with **274,980 / 106** previously. Compatible meshes are merged within each independently animated head/tail/leg joint, sharing cached geometry and materials. Broad-phase collision rejects distant houses before identical narrow-phase samples; footprints cache per navigation revision. Held-stick routes avoid repeated whole-map grid searches. On phones, full-rate run recording uses **10 Hz world snapshots**, preserving command/event captures and explicitly selected slower cadences. These changes target CPU, GPU and recording overhead; owner-device FPS still needs hands-on acceptance. Clover, compact corner controls, the 320×320 m map and seven-minute rounds remain.

Release **122 patches / 60 assets**, HTML **6,390,662 bytes**, SHA-256 `c76e61f6c4b8457ce1f49d3781c8aa0710d7e44adaf7176d17744fdbda5c663a`, marker `V11_90_SOLID_BLOCKERS_FURRED_ASTRA`. All **290** previous runtime/patch files and **58** previous assets preserve exact bytes. See [targeted validation](projects/swrlz-forge-moba/reports/SOLID_BLOCKERS_FURRED_ASTRA_V11_90.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.89 · Living Astra, Clover flock and compact corner controls (2026-10-23)

**Astra's full anatomy pass** replaces separate tube-like legs/toe pieces with four welded anatomical limb/paw meshes, including elbows, wrists, hocks, tendons and four toes per paw. The seated torso has shaped shoulders, ribs, pelvis and tucked belly; the ivory chest now tapers naturally and fits beneath the original harness. The face has orbital wells, a defined brow stop, tapered muzzle/lower jaw, canine pupils and nostrils. Closed cupped pinnae and curved fur surfaces replace the remaining biological primitive parts. All **24 original gear parts and 13 comet-tail/stardust parts** remain byte-exact. The native model contains **92 editable meshes / 547,676 rendered triangles**, retaining the original **4K color/normal atlases**. It remains rebuildable with the editor's organic volume/sweep tools and supports material editing, Undo, native JSON and textured GLB.

**Clover replaces the sheep in Sheep Tag**, including all eight starter sheep and reconstructed/spawned `st-sheep` actors. It uses the same 31 source parts, fleece/face/ears/hooves, native atlas bindings and shared **4096×4096** images as the new independent sheep model. A game copy made with Model Atelier's native mesh reducer uses **33,087 triangles**, while the original **275,872-triangle** authoring starter remains unchanged. Cached geometry/materials are shared across independently animated head, tail and four leg joints. Fleece width fits within the existing sheep collision diameter; routes, capture/wisps, construction and timer retain native logic.

**Controls corrected to the owner's screenshot:** at 926 px portrait width, the joystick and building/skill diameters are about **45% of v11.88**, with the joystick anchored **18 px from the left / 22 px from the bottom**. Separate compact right-side arcs retain spacing, readable labels and safe margins. Narrow screens keep a minimum 44 px ability target and 50 px building target. Landscape moves auxiliary actions beside the joystick to clear the minimap.

Release **121 patches / 58 assets**, HTML **4,557,192 bytes**, SHA-256 `a9f6b48036c852be5a75150f18ebc9e31633c43acaa28c3b08a79b1d67506ed0`, marker `V11_89_LIVING_ASTRA_CLOVER`. All **285** prior runtime/patch sources and **56** previous assets preserve exact bytes. See [targeted validation and anatomy references](projects/swrlz-forge-moba/reports/LIVING_ASTRA_CLOVER_V11_89.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.88 · Roomier passages, reachable controls and original Astra (2026-10-23)

Sheep prioritize alignment through nearby usable house lanes before steering around an outside corner. Short joystick targets refresh immediately, so previous corner routes cannot keep a sheep trapped. Existing 0.60 m lanes remain usable; new deliberate house-lane snapping leaves **0.75 m**, with native footprint, collision and traffic checks shared by preview and construction.

The joystick moves inward/up and scales to **65% of portrait viewport width**. Building buttons use **21%**, the main house **22%**, and abilities **18%**, with two separated arcs. At the 926 px screenshot width that means roughly **194–204 px building buttons**, about three times the previous size. Phone/landscape sizing and short-screen minimap clearance adapt to the available viewport.

The wolf starter again opens **Astra · Comet Courier**, retaining the original blue/ivory design, amber eyes, tall ears, cape, harness, satchel, compass, scroll, lantern and giant curled comet tail. All **37 original gear/tail parts** remain byte-exact. Three native welded anatomical surfaces add **134,348 triangles** across the torso/shoulders/haunches, skull/jaw and continuous muzzle; the original **4K color and normal maps** remain. Clover sheep stays available as its independent starter. Detailed native editing, material Undo, save/import and textured GLB export remain supported.

Release **120 patches / 56 assets**, HTML **3,371,397 bytes**, SHA-256 `6d4ce7a4f95c2c90fb988d99867ee240c7a505df13b43c7be4b2038f506e4c2e`, marker `V11_88_PASSAGES_CONTROLS_ORIGINAL_WOLF`. All **281** preceding runtime/patch sources and **55** assets preserve exact bytes. See [targeted validation](projects/swrlz-forge-moba/reports/PASSAGES_CONTROLS_ASTRA_V11_88.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.87 · Organic sheep and wolf model starters (2026-10-22)

**Clover · Meadow Sheep** is a new independent Model Atelier starter. **Fen · Wildwood Wolf** replaces the wolf model starter entry and the earlier `comet-courier` shortcut. The wolf is a natural quadruped with a fused ribcage/shoulder/neck/skull/muzzle surface, a tucked waist, bent hocks, four-toed paws, short alert ears and a low brush tail. The sheep has continuous fleece over shoulders/barrel/haunches, a tapered bare muzzle, folded pinnae, horizontal pupils, lower-leg tendons and split hooves. Visible parts are editable indexed organic meshes; there are no sphere, box, cylinder or cone model parts.

The native organic volume tool blends anatomy fields into a connected, welded surface. Model Atelier exposes `loadAnimal(species, {force, rebuild})` to rebuild with that tool, alongside the standard component, sculpt, group, undo, material and export controls. Both starters use a shared **4096×4096 color atlas and matching 4096×4096 normal map**. Native model import supports 64 MB detailed saves and meshes up to 65,536 vertices / 120,000 triangles per part; high detail remains authored data. Textured GLB export embeds the proper atlas, including mixed original/animal materials. Studio view opens with a clear silhouette and an Edit model button. Saved project payloads are compressed losslessly in `payload/organic-animals`; packaging emits the portable native JSON scenes.

Release **119 patches / 55 assets**, HTML **3,359,239 bytes**, SHA-256 `c2dda3de1cb7bf262e347a47c9dfde2f9c4af267ed1124fee068a804fb6cda40`, marker `V11_87_ORGANIC_ANIMAL_STARTERS`. All **277** previous runtime/patch sources and **51** assets preserve exact bytes. Sheep Tag retains v11.86 nearest-side house steering, 7-minute matches, large controls and the 320×320 m map. These model projects are independent authoring starters. See [targeted validation](projects/swrlz-forge-moba/reports/ORGANIC_ANIMALS_V11_87.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.86 · Sheep steer around houses (2026-10-22)

Holding the joystick into a house now steers a living sheep toward the **nearest clear side/corner**, then continues in the held direction. A blocked side falls back to the other clear side. Fully blocked exits stop safely. This uses the native swept movement and analog speed; it never relocates a sheep through a structure. Rotated houses, other creatures, narrow sheep-only gaps, joystick reversal and release are checked. Wolves, wisps and automatic ramp/deck movement keep their existing controls.

Release **118 patches / 51 assets**, HTML **3,340,927 bytes**, SHA-256 `01b695c06bc5636b762d87914d76e2511224345add0e80c93ce6a1e6f04eba0b`, marker `V11_86_SHEEP_HOUSE_SLIDE`. All **275** previous runtime/patch sources and **51** assets preserve exact bytes. The 320×320 m map, 4K textures, enlarged controls, 7-minute timer and versioned update history remain available. See [targeted validation](projects/swrlz-forge-moba/reports/SHEEP_HOUSE_SLIDE_V11_86.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.85 · Bigger controls and seven-minute matches (2026-10-22)

The portrait joystick grows from **156 to 224 px** and moves diagonally **up and right**. Compact portrait uses 192 px; landscape uses 208 px, or 176 px on a short phone. The knob and direction mark grow with it. Right-side buildings and abilities grow by roughly 12–23% in the main layouts, with adaptive compact sizes and the two separated arcs retained. Larger labels wrap within their circles. Landscape score, utility buttons and feedback shift to keep the enlarged controls accessible.

The default match lasts **7 minutes (420 seconds)**. The portable starter carries that duration, and saved maps using the previous 20-minute default migrate to seven minutes. Other explicitly tuned durations remain editable. The native countdown, head start, win conditions, movement, ramps and placement use their existing game clock and rules. The editor’s versioned update panel automatically lists this release.

Release **117 patches / 51 assets**, HTML **3,338,122 bytes**, SHA-256 `76ea088b19a441ed0e846ffdd4a02197eb131b45a3ea55255eeb032f7c5d13f4`, marker `V11_85_LARGE_CONTROLS_SEVEN_MINUTES`. All **272** earlier runtime/patch sources and **50** preceding assets preserve exact bytes; the additional asset is the seven-minute starter scene. See [targeted validation](projects/swrlz-forge-moba/reports/SHEEP_LARGE_CONTROLS_V11_85.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.84 · Reliable building, connected walkways and update history (2026-10-22)

- **Building recovery:** one placement pointer owner handles icon and meadow drags. Rejected/cancelled drops release capture, remove the ghost and clear the selected tool. Unaffordable buttons show a cost message without entering placement, so the free house remains available.
- **Automatic ramps:** joystick steering ascends and descends completed ramps directly, follows connected decks and stops at unsupported edges. The ground/upper-route and descent toggles are hidden. Species radii, traffic, wolf ramp permissions, capture and hunt-release restrictions remain native.
- **Connected extensions:** walkways and exit ramps snap to existing deck/ramp high edges and rotate toward the selected side. Straight extensions and side turns share physical seams and the native route graph. Sheep already on a connected deck can construct a nearby extension; normal costs, occupancy, sanctuary and completion rules still apply. Player-built side connections open a gap in the parent rail when complete.
- **Touch controls:** abilities occupy an inner arc beside the outer building arc. A larger joystick and separated compact layouts keep targets at least 44 px. Touch aim rises **128–180 px** above the finger, with top-readout clamping.
- **Larger map:** the new starter is **320 × 320 m**, 25% wider and 56.25% more area than the preceding 256 m meadow. Authored scenery, roads and the 4K ground scale with the layout; previous scene files remain unchanged.
- **Editor updates:** an automatic latest-update panel includes **107 previous versions**, grouping every previous patch. Its checkbox hides only this exact version; the next release appears again. The editor footer’s **Updates** button reopens it, and unchecking restores the popup. Future source versions derive notes and history automatically from the manifest and new patch summaries.

Release **116 patches / 50 assets**, HTML **3,333,468 bytes**, SHA-256 `82ae2d5fdac77f9a63cb4375aae2d93939c8cdf3338395f7120995f62d2bc411`, marker `V11_84_BUILD_RECOVERY_WALKWAYS`. All **264** preceding runtime/patch files and **49** prior assets preserve exact bytes. The additional asset is the larger native scene. See [targeted implementation and evidence](projects/swrlz-forge-moba/reports/SHEEP_RECOVERY_WALKWAYS_V11_84.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.83 · Drag houses to build, joystick movement and smooth fog (2026-10-22)

Manual movement now uses the **left joystick**, including the desktop pointer layout; ground clicks/taps no longer issue move orders. Drag a building skill icon onto the meadow, aim with the house **above your finger**, and release on a green footprint to order construction. A tap can also arm the building tool for a subsequent ground drag. Visible house/unit selection, wolf attack, rescue, camera pan and minimap camera navigation remain available. Construction retains its native approach, collision, footprint, cost and completion rules. Accepting a build releases held joystick ownership so the next frame cannot overwrite the construction order. Steering again deliberately replaces that order. Blocked/cancelled drops do not charge gold or build. The preview rechecks affordability and occupancy while held still, avoiding a stale red “Need gold” message after income arrives.

Fog uses **soft circular vision edges**, linear sampling and a 4× display mask (512×512 on the 256 m meadow), updated at most ten times per game second. The minimap shares that smooth display. Logical visibility, explored cells, enemy filtering, bot knowledge and pre-hunt restrictions remain native. All **262** preceding runtime/patch files and **49** assets retain exact bytes, including the 4K artwork.

Release: **115 patches / 49 assets**, HTML **3,288,058 bytes**, SHA-256 `41b34b31203777afffc242d42a83b32157e61442760fa9549960600ed27d7962`, marker `V11_83_DRAG_BUILD_SOFT_FOG`. See [targeted implementation and validation](projects/swrlz-forge-moba/reports/SHEEP_DRAG_V11_83.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.82 · Mobile building skills, joystick and clear touch placement (2026-10-22)

Sheep Tag now uses **round illustrated building skill buttons at the bottom right** on phones/tablets: house, income house, fortified house, wall and ramp. The existing native buttons retain their costs, availability, active state and build commands. A **left movement joystick** steers the actual sheep/wolf through native swept collisions and traffic, supports proportional speed, and stops on release/cancel/pause/blur. Captured wisps keep their slow crawl/leash; wolves remain immobile before release. The minimap moves to the top left. A compact **••• unit-actions drawer** keeps camera, upgrades, selling and archive controls accessible, while the editor footer returns after Stop. Desktop controls retain their original layout.

Touch building aim is **72–112 screen pixels above the finger**, with a dotted guide to the exact snapped footprint. Preview and release use the same native build target. Separate pointer owners let one thumb steer while another aims; two simultaneous placement fingers still cancel safely. Portrait, landscape and compact screen layouts keep touch controls at least 44 px. Camera following and normal frame updates keep the ghost aligned; resizing cancels held gestures.

Release **114 patches / 49 assets**, HTML **3,279,865 bytes**, SHA-256 `e0bfe63ddae1f5430cf0f80f7f17bd9745a5d0147d68fb96afbb441353d9b6c2`, marker `V11_82_TOUCH_BUILD_SKILLS`. All **259** preceding runtime/patch sources and all **49** bundled assets retain exact bytes, including the Astra and ground 4K textures. See [implementation and targeted evidence](projects/swrlz-forge-moba/reports/SHEEP_TOUCH_V11_82.md). Publication follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md): cohesive source, separate final deployment request and exact hosted-package confirmation.

## §E v11.81 · Building clearance, protected sanctuary and hidden hunters (2026-10-22)

House foundations and outlines now reach the real blocking footprint. Nearby face-to-face gaps show their measured width and a colored label: **red BLOCKED**, **cyan SHEEP ONLY**, or **gold BOTH**. Classification uses the native swept collision checks, surrounding visible structures and actual species radii. Exact lane entry points let sheep use fitting narrow passages even between navigation-grid lines. Default sheep need **0.54 m** and wolves **1.80 m**. The gold sanctuary boundary marks a **22 m no-build radius** on the default 256 m map; the whole structure must fit outside it. Both player placement and AI construction use this rule. Bots choose reachable outward bases instead of falling back to their central spawn.

Wolves are hidden and nonphysical during the countdown, with no perception, target memory, minimap markers or pre-release scent information. A waiting wolf role has no sheep/building vision. After release, bot hunting requires actual sightings; lost sheep leave only their last observed position. Default sheep speed rises from **5.4 to 6 m/s** and Astra hunters are **15.4% larger**, with collision radius increasing from **0.78 to 0.90 m**. The 106-mesh/274,980-triangle hunter and original 4K atlases remain. Captured-wisp crawl/leash/rescue behavior is retained.

Release **113 patches / 49 assets**, HTML **3,258,318 bytes**, SHA-256 `9fb46459d3ca870f766ff7c90c18a1649ffbfc68352da25c493bc5ffe284186c`, marker `V11_81_SHEEP_CLEARANCE`. All **257** previous patch/runtime sources and **49** assets preserve exact bytes. Details and targeted validation are in [the release report](projects/swrlz-forge-moba/reports/SHEEP_CLARITY_V11_81.md). Delivery follows [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md): cohesive source commit, separate final deploy request, terminal production success and exact hosted-source/asset confirmation.

## §E v11.80 · Vast Wildwood, central starts and captive wisps (2026-10-22)

The default map is now **256 × 256 m**, **4× the previous playable area**. All eight sheep start **9.5 m from the central respawn sanctuary**, rather than around the outer map. The existing four-region roads/ground/minimap and 4K Astra hunters remain. Fine **0.15 m** pathfinding now uses direct clear trips and cached local windows for most obstructed routes in large maps, with an unrestricted fallback for longer detours.

Captured wisps crawl at **0.35 m/s**. They may drift **2.5 m beyond each side of the pen**; crossing that leash teleports the still-captured wisp to its own capture spot and clears its movement/rescue progress. Reaching the leash never revives a sheep. The existing other-living-sheep rescue/hold/protection behavior remains the only revival path. Native move controls and help text describe this behavior.

Release **112 patches / 49 assets**, HTML **3,243,526 bytes**, SHA-256 `a4b58b9da3991fdd10fee42c4fd18648c65a79932b0af69ceea1a117ce5f151d`, marker `V11_80_VAST_WILDWOOD_WISPS`. The new native scene has 196 editable actors, eight central sheep, three Astra hunters and nine map layers. All 255 preceding patch/runtime sources and 48 previous assets retain exact bytes. Targeted CPU/browser checks and publication evidence are recorded in [the release report](projects/swrlz-forge-moba/reports/VAST_WISPS_V11_80.md). Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and terminal production run under current [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.79 · Moonbell Wildwood — larger Sheep Tag map (2026-10-22)

The default Sheep Tag starter is now **Moonbell Wildwood**, **128 × 128 m** versus the previous 80 × 80 m (**2.56× the area**). Four color-separated woodland regions — Pinewatch, Moonflower, Amberglade and Willowmere — surround open building glades, an octagonal road loop, cardinal/diagonal roads, four merchant plazas, four ponds and a central sanctuary with stone markers. Four genuine narrow stone passages admit sheep while hunters detour. The terrain and fog-respecting minimap share original **4096 × 4096 ground artwork**. There are **176 individually editable native actors** in nine map layers, retaining eight sheep and three 4K Astra hunters. Match timing, movement/combat rules and optional archive settings remain intact; the previous 80 m map is preserved as a separate source and remains loadable.

Release **111 patches / 48 assets**, HTML **3,222,398 bytes**, SHA-256 `f2d2c22aa4620f76407494767e27a4227c3d178af3f8a52f7fc736c6eb28e9ec`, marker `V11_79_MOONBELL_WILDWOOD`. All 253 preceding runtime/patch sources and 46 earlier assets retain exact bytes. Targeted desktop/phone-layout checks cover start validity, full map framing, all spawn/outer-road connectivity, four species-sized passages, native/portable save/load, generated floor scale, movement/construction outside the old boundary, terrain minimap and previous-map compatibility. Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and its terminal production receipt. See [map design and evidence](projects/swrlz-forge-moba/reports/SHEEP_WILDWOOD_V11_79.md); delivery follows current [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.78 · Astra hunters in Sheep Tag (2026-10-22)

Sheep Tag's `st-wolf` prefab now renders the complete **Astra · Comet Courier** model, with all 106 native meshes and the original 4096 × 4096 color/normal atlases. The three canonical hunters, newly spawned hunters and wolves reconstructed from older native project saves all use the same visual. Independent head, tail and four leg pivots connect the saved model to the existing walk and attack animations; geometry/materials and texture images are reused across instances. Logical wolf roles, IDs, names, teams, navigation/collision radii, combat, economy and map data are preserved. The independent editable Astra project remains available.

Release **110 patches / 46 assets**, HTML **3,152,424 bytes**, SHA-256 `234ddf6065f89438a3cabbcd9e3521d82fb08245830525131e3976d4f86b9ad4`, marker `V11_78_SHEEP_TAG_COURIER`. All 250 preceding runtime/patch files and 46 bundled assets are byte-preserved. Targeted local desktop/phone-layout checks cover loaded 4K maps, native spawn/save/reload, movement/four-leg gait, building attacks/head animation, sheep tagging and Stop/restart restoration. Deployment status and source commit resolve through the final separate `DEPLOY_REQUEST.json` and its terminal production run; owner device acceptance follows publication. See [integration evidence](projects/swrlz-forge-moba/reports/SHEEP_COURIER_V11_78.md). Delivery follows current [RELEASE_PROCESS.md](projects/swrlz-forge-moba/RELEASE_PROCESS.md).

## §E v11.77 · Astra, Comet Courier model project (2026-10-22)

New independent **Astra · Comet Courier** project and **New Model Project** starter. A celestial fox with sculpted ears/muzzle, four articulated legs, a flowing comet tail, travelling mantle, satchel and lantern is authored through native tools. Eight material regions use original 4096 × 4096 base-color and normal atlases. Saved atlas bindings support Undo; a textured GLB embeds real mesh/UV/material data and both 4K images. Six editable assemblies organise the model.

The existing 283-part festival model, all previous runtime/patch sources and 43 original assets are preserved. Release has 109 patches / 46 assets, marker `V11_77_COMET_COURIER_MODEL_PROJECT`. Exact bytes/SHA resolve through `source-manifest.json`; source/deploy commit and live status resolve through the final separate `DEPLOY_REQUEST.json` commit and terminal production receipt. Current delivery authority is `RELEASE_PROCESS.md` (§§§); targeted model checks precede direct-main source publication and the final dedicated deployment trigger. [Design and authoring](reports/COMET_COURIER_V11_77.md).

## 2026-10-21 · §E v11.76 — desktop modeling drag, scale, wire vertices and zoom

Owner PC gaming-monitor photos revealed four specific problems: gizmo drag would stop before available mouse/screen travel was exhausted, large piñata-related scaling appeared only after Undo triggered a procedural rebuild, dense whole-character wireframe washed out into nearly solid white rather than exposing vertex points, and scroll zoom had a hard minimum too far from the character. The v11.76 repair keeps §E's original **283 native Model Atelier parts, 43 original assets, existing object/assembly/component editors, geometry, history and full source lineage**.

- Desktop pointer-lock acquisition on a real mouse gizmo drag accumulates relative movement while the mouse cursor is locked; falling back to native pointer events when pointer lock is unavailable. Release or Esc exits lock. A native validity-bounded transform replaces the arbitrary *3× per-drag scale limit*. Preview amounts stop at safe mesh position/scale bounds rather than moving into invalid territory and reverting on release. Touch behavior remains intact. Real owner mouse acceptance remains outstanding.
- Scale commits trigger **one** post-commit procedural model redraw (not rebuild on every drag frame), ensuring native procedural hair and piñata structures update visibly without requiring an Undo event. The original Undo/Redo record is still the authority and correctly reverses and reapplies the scale.
- Global wireframe now draws muted low-opacity lines for all nonselected objects and a cyan outline for the selected object; users can control **Focus selected wire** and **Vertex points** within *Display, wire & interior*. Up to 2,000 actual sampled mesh vertices are drawn as contrasting yellow 5px points for the selected part. This is viewport-only and does **not** lower mesh topology or change materials in saved project. Open display controls are layered above movable gizmo panels, fixing an additional desktop click interception discovered during testing.
- The active mouse-wheel zoom, +/- buttons and touch pinch reach **0.16 model units** (previous min 1.2 framed / other historical higher floors), with close-range near clipping adjusted to **0.018**; preset camera views and original geometry are preserved.

[Real Chromium v11.76 test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39674744767) passed with 283 original mesh count; selected native Rear dyed lock scaled at a valid **9×** candidate, immediate scene transform update, Undo/Redo; **1,677** shown vertex markers on a wireframe mesh, contrasting selected/other wire opacity and toggle; 0.16 camera minimum with 0.018 near plane. No uncaught browser errors. Desktop pointer-lock ergonomics and piñata-specific real-device review remain for the owner. **108 ordered patches**, **3,091,496-byte** HTML, SHA-256 `ae0764bcdaef131a8d404b43ca20b4a3b6ed9bad66897709919b6f3f1bccf1ef`, marker `V11_76_DESKTOP_MODELING_REPAIR`. Maintain §§§ source → separate deployment request → exact hosted artifact verification.

## 2026-10-21 · §E v11.75 — Component Edit Foundations

Owner-approved mobile-first geometry editing update. Model Atelier adds **Mesh / Vertex / Edge / Face** mode buttons and keeps whole-object/group editing separate from component editing. Tappable vertex points, edge lines and tinted face selections; tap + independent component **Multi**, **Box** and **Lasso** tools; component count, Clear, and axis Move/Rotate/Scale with existing Fine↔Fast sensitivity and ± nudges around the selected component center. Transforms edit actual indexed positions of the selected native mesh with lightweight live WebGL preview. Edit offsets are saved using the preexisting bounded sculptVertexEdits project schema, retain Undo/Redo, native model JSON and OBJ geometry output. Weld-equivalent duplicated vertex slots move together. Editing is deliberately limited to one chosen mesh at a time and to stable (non-active-refinement) vertex indices; large selections obey existing 256-slot edit chunks, 64 history record and ±0.5 local-unit validation budgets. With a scaled character head, live drag now clamps **before preview** so no visually moved-but-invalid commit occurs. Performance protection raycasts the touched triangle for vertex/edge selection, caches topology per rendered geometry, samples dense overlays and avoids full mesh normal recomputation on each drag frame. The character's original **283 parts, individual materials**, old 2.5D/3D tools, v11.74 mesh groups and all **43 packaged assets** are retained.

[Real Chromium v11.75 component test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39664122664) **passed**: native indexed edit persisted, Undo/Redo restored it, both edge and face selection/nudges, component multiselect, box/lasso, live pointer drag changing geometry *while held* and saving on release, 390px phone controls with 44px targets, and no browser errors. Release seal: **107 ordered patches**, **3,083,471 bytes**, SHA-256 `910e4565727243256154adb8707bf0eaff9021338860b5b34146d04cc02474d1`, marker `V11_75_COMPONENT_EDIT_FOUNDATIONS`. Owner Android acceptance remains pending. Future extrude/inset/bevel/advanced loop tools remain deliberately out of this foundation release.

## 2026-10-21 · §E v11.74 — non-destructive mesh assemblies and mobile Multi-Select

Owner requested a mobile-friendly tap-to-toggle multi-selection mode and a reversible mesh group hierarchy, distinct from the existing destructive **Join selected** operation. v11.74 adds a permanent viewport Multi-Select control, selection counter, Select first 32, Clear and Done. With Multi on, tap meshes to add/remove them without Shift/Ctrl and tapping empty space retains the selection. The contextual Assemblies disclosure offers **Group selected**, **Edit group / Edit child**, **Update members**, **Remove child**, **Ungroup**, and an assembly picker. A flat assembly links the original part IDs using modelAtelier.meshGroups; meshes retain independent kind, topology, materials, color and source transforms, and group transforms reuse the existing smooth Move/Rotate/Scale gizmo around the common pivot. No geometry is flattened and the separately labeled native Join remains available. Group membership survives native project save and model JSON export/import; the preexisting whole-model Undo history, which also stores other original animation/socket and pose data, now captures membership edits without replacing those structures. One mesh belongs to at most one flat group, up to 32 parts/group, with up to 96 groups.

[Real Chromium full-workflow regression](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39631075995) **passed**: tap toggles and empty-tap retention, grouped selection, linked translations, independent child editing, membership updates, Undo/Redo for group creation and transforms, JSON round-trip, ungroup/Undo, and a 390px viewport with ~100×44px Multi button. It checked that all **283** original character parts, their materials and initial transforms remained identical after group creation. Sealed source **v11.74**, **106 ordered patches**, **3,056,562 HTML bytes**, SHA-256 `25ca54b95366258f3bc76912f90299aca42667c8f1938ea37a0a789da4399cc6`, marker `V11_74_NONDESTRUCTIVE_MESH_GROUPS`. The original 43 packaged assets remain unchanged. On-device owner testing remains required after deployment.

## 2026-10-21 · §E v11.73 — instant transform mode redraw and mobile-friendly rotation ruler grabs

Owner on Android observed Move/Rotate/Scale buttons did not visibly change handles until orbiting camera, plus arc lines were too small to grab. Source showed the contextual popup rebuilt the gizmo on button clicks but did not synchronously draw WebGL; curved rotation picking was limited to small slider beads. v11.73 explicitly paints a WebGL frame after mode/axis changes, without touching the camera, and adds thicker axis-colored 3D arc tubes, visibly larger slider beads, and screen-pixel curve hit testing for any position along a rotation arc. The user-chosen axis has precedence when projected rings overlap. Selecting a curve segment starts a native live rotation and moves the bead with the finger from the grabbed arc point. Native Undo/Redo, snap options, previous smooth drag behavior, geometry and materials remain unchanged.

The [real Chromium regression](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39617462205) passed after fixing a genuine X/Z projected-ring ambiguity found in the initial run. It verified immediate WebGL painting on each tool switch without camera movement, exactly one gizmo root, 3 thick Rotate arcs versus 0 for Move/Scale, off-bead Z-axis live rotation, and touch tolerance at 390px viewport. Release source **v11.73**, **105 ordered patches**, **3,040,330 HTML bytes**, SHA-256 `57998cfe4d71530e4f82fc0b0f0ec18c4bc858bc5f8f35d2d3ee5cdca7c56fe8`, marker `V11_73_INSTANT_GIZMO_ROTATION_TOUCH`. Preserve the canonical 283-part reference model and all 43 original assets. Owner's physical Android touch acceptance follows hosting verification.

## 2026-10-21 · §E v11.72 — rotation ruler alignment and accurate touch mapping

Owner Android screenshots of v11.71 showed rotation bands disproportionately large relative to the selected anatomical head, with overlapping axes and questionable rotation feel. Root cause: the original arc radius was camera-distance based, pointer-angle inference was an affine 2D ellipse approximation instead of an exact 3D angle, and the popup showed the previous gesture delta without labeling it as such. In v11.72 the arc radius is measured from the selected mesh's actual world-space bounding sphere with a minimum screen-size allowance for phone usability; the ring's plane is intersected with the camera ray to calculate angular movement, falling back to a tangent when the ring is seen edge-on. Each axis has its own colored ticks/bead; the selected axis is emphasized, inactive rings dim, and handle selection uses pixel distance instead of an oversized world-space collision sphere. The readout now labels live **Δ** and **Last Δ** separately rather than pretending to show absolute Euler orientation.

The [focused real Chromium test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39609712872) passed for X/Y/Z on the actual anatomical head, measured the head ring radius **0.573 vs 0.952** world units, confirmed the gizmo is centered, tested live mesh rotation and bead movement before pointer release for all three axes, verified saved changes, and checked Move/Scale remain distinct. Preserve the 283-part original model, 43 historical assets, native Undo/Redo, per-mode Fine/Fast and 5°/15° snapping. The rotation amount is a world-axis delta and can differ from individual Euler components after multiple-axis rotations; no mesh hierarchy or skeleton grouping was changed. Sealed v11.72: **104 patches**, **3,036,186 bytes**, SHA-256 `9b0d791a66bce68a28f21911d2de4bad703d9d676edd2076622c9b4060e0cae8`, marker `V11_72_ROTATION_ARC_ALIGNMENT`. Physical Android UX pending owner acceptance.

## 2026-10-21 · §E v11.71 — true curved 3-axis rotation rulers

Owner provided a screenshot reference showing overlapping colored curved rotation gizmo rings with ticked rulers and sliding points. v11.71 replaces the straight 3-axis handles *only in Rotate mode* with 3D X/Y/Z arcs in red/green/blue, 15° graduations and emphasized 30° ticks, plus large invisible touch targets on the draggable bead for each ring. A drag maps pointer position onto the corresponding world-space arc, uses the native XYZ quaternion transform path, and displays the mesh rotation and bead movement live before release; the per-mode Fine/Fast transform slider remains active. The nearby floating popup shows the current angle and optional Off/5°/15° snapping, saved as a local UI preference rather than model state. Move/Scale and source geometry remain untouched. The native Undo/Redo transaction persists transform edits.

[Focused real Chromium rotation test passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39605565651), including three visible rotation arcs, 12 live pointer updates/rendered frames, ~39.4° Z-axis rotation *before pointer release*, saved rotation, optional snap controls, and preserved Move/Scale. Original 283-part canonical model and 43 packaged assets remain preserved. Sealed source: **v11.71**, **103 patches**, **3,029,622 HTML bytes**, SHA-256 `44ae1de39f81874ccf2a06cfae8e067b06633053656283562523579850034c6b`, marker `V11_71_ARC_ROTATION_RULER`. Mobile touch usability remains subject to owner test after hosted deployment.

## 2026-10-21 · §E v11.70 — Fine/Fast gizmo sensitivity and responsive top tools

Owner accepted v11.69 live drag smoothness and requested a less cluttered top viewport control area and a fine-positioning slider in the selection gizmo popup. v11.70 groups the **Render mode / Target**, camera-direction presets and center-pan control, and an expandable **Display, wire & interior** section without recreating existing controls or handlers. The selection popup now offers **Fine ↔ Fast** sensitivity with ⅛×, ¼×, ½×, ¾×, 1×, 1½×, 2×, 3× and 4× for each of Move, Rotate and Scale independently, retained per device, affecting both drag gestures and plus/minus nudges. This does **not** adjust geometry subdivisions: the existing Grid U/V tool remains the dedicated vertex-count feature. Existing native bounded transforms, smooth live preview, Undo/Redo and original project data are preserved. [Focused real Chromium UI and drag test](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39602536277) passed, including 25px movement of ~0.180 units at 1× versus ~0.0225 units at ⅛×, saved sensitivity per mode, preserved camera buttons and 390px screen layout. An initial test failed with advanced settings open over the interaction area, and was corrected to test with the expandable panel closed during gizmo operation. 

Release seal: **v11.70**, **102 patches**, **3,019,798 HTML bytes**, SHA-256 `67a36e4efc75bf0a585463643b1e48ce70437add1b65087d9d1967df97204ca3`, marker `V11_70_PRECISION_GIZMO_TOOLBAR`. Original 283-part character and all 43 packaged assets remain unchanged. §§§: source commit directly to main, dedicated final deployment trigger, exact hosted/source audit, owner mobile acceptance.

## 2026-10-21 · §E v11.69 — proven in-browser drag feedback before pointer release

Owner reported that v11.68 mesh motion improved slightly but the selection gizmo and mesh still appeared static during touch-drag, then snapped to position on release. The v11.68 code updated Three.js transforms but repeatedly recalculated selected mesh world bounds on every pointer movement and depended on the ongoing render loop for visible paint. v11.69 uses the captured pivot and drag delta to update the existing selected part(s), native outline, and gizmo position directly without a geometry rebake or whole-model rebuild, and issues a WebGL render on active pointermove. Native Undo/Redo, full commit validation and previous selection optimizations are unchanged. A **real Chromium pointer interaction test** [passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39594806708): 9 movement events / 9 frames, selected mesh moved 0.45 units and handle followed **before pointerup**, with the saved position persisting after release. This is stronger than build-only validation; physical Android performance remains a separate owner test.

Sealed source: **v11.69**, **101 patches**, **3,012,114 bytes**, SHA-256 `6ed5ae18211945d86d2a73db45aadb173b377d656c57eeab6714105c26d8e471`, marker `V11_69_DRAG_PREVIEW_RENDER`; original 283-part starter and 43 packaged assets retained. This is an additive fix and does not change any other §wyrlz projects.

## 2026-10-20 · §E v11.68 — immediate native selection and live gizmo drag

Owner tested live v11.67 and confirmed that completed transforms landed correctly but the chosen mesh and gizmo did not visibly follow the finger during drag, and selecting an object had a small delay before its bounding outline appeared. The v11.68 additive patch retains the captured transform gizmo through pointer movement, applies candidate changes directly to existing Three.js mesh objects, refreshes the native selection BoxHelper and gizmo center on each live preview, and leaves v11.67 fast commit/Undo intact. Switching selection now re-targets the existing selection BoxHelper without `renderParts()` rebuilding the 283-part model. Native geometry-edit workflows remain unchanged. This is a scoped optimization, not a model reconstruction. **100 patches; 3,010,876 HTML bytes; SHA-256 `ddd1e5e5c7e09dc6635b6c32c2170c4c5f3d08e19f816530348667abc602ba93`; marker `V11_68_LIVE_MESH_GIZMO_FEEDBACK`.** Original 283-part canonical scene and 43 historical assets remain intact. [Targeted source assembly and syntax check passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39542983666); Android motion/selection responsiveness awaits owner test after deployment.

## 2026-10-20 · §E v11.67 — mobile mesh transform performance

Owner reproduced a pause after dragging one face/head mesh in live v11.66. The previous `atelierMeshCommit()` invoked `signalEdited()` to rebuild all 283 model parts on every valid Move/Rotate/Scale commit. v11.67 now stores the validated transform in native project data, uses the existing mesh and material in Three.js, updates selected-object helpers, inspector and Undo/Redo state, and preserves JSON/OBJ. Canceled or zero-motion drags restore the live transform without replacing geometry. Actual geometry edits still use their existing rebuild path. 99 ordered patches; 3,009,500 assembled HTML bytes; SHA-256 `a2122de3a296da3319de5d861875f7c3efd4663d714b31820d4e27acf5ca8017`; marker `V11_67_MESH_TRANSFORM_PERFORMANCE`. The original 283-part starter and 43 packaged assets remain intact. [Targeted build and syntax check passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39532595474). Live deployment and owner Android responsiveness checks are separate stages.

## 2026-10-20 · §E v11.66 — owner-reported selection gizmo & mobile popup repair

From owner screenshots on a physical Android phone: an extra yellow bounding helper appeared above the model, a face/part could be moved out of view, the floating toolbar obstructed the character, and Undo/Redo were hard to find. This version **removes the duplicate transformed selection outline** (native selection outline remains); **caps each touch/drag translation at 0.45 native world units** with fine camera-distance-scaled sensitivity; places **Undo / Redo / Frame mesh** directly in the floating selection strip; and makes its title bar **draggable with normalized on-device saved position**, maintained across viewport layout/orientation. Cybernetic cyan/indigo styling was added to the popup and scoped to existing Model Atelier tool windows; other projects are not restyled.

No model-source changes. Preserve the exact original 283-part canonical character and all 43 packaged assets. One targeted build and Node syntax check passed ([Actions run 39531500631](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39531500631)); physical-device gesture/position UX is explicitly awaiting owner acceptance. Release seal: **98 ordered patches**, **3,008,188 bytes**, SHA-256 `ab960990d91641c0a03c453181710ae2a6739c247a632e238e4aa1745e16e35f`, marker `V11_66_MESH_SELECTION_UX_REPAIR`. §§§ release: direct source commit to main, final independent deployment trigger, hosted source verification, then hands-on owner testing.

## 2026-10-20 · §E v11.65 — selected-mesh gizmos, group Join and vertex grid controls

Owner-requested modeling edit: select a native mesh and a nearby contextual strip exposes **Move / Rotate / Scale**, X/Y/Z gizmo handles plus step nudges; **＋ Add mesh** selects multiple parts for shared pivot transforms, **Join selected** bakes selected meshes into one editable `topologyMesh` within the supported budget (single material, first selected). Native Undo applies. **Show vertices** invokes the existing pickable source-vertex map and point gizmo, and **Grid U/V** adjusts actual procedural rows/columns with bounded budgets: sphere/loft use the native resampler, face sheets use their existing face-sheet grid, and box/cone/cylinder gain bounded parametric subdivisions. Changes to grid density clear indexed point edits after user confirmation; original part history is preserved through Undo and JSON/OBJ. Custom topology retains its dedicated native refinement tools instead of pretending it has rectangular U/V topology. The canonical **283-part starter** and all **43 packaged assets** remain byte-preserved.

Source seal: `§wyrl§ Engine v11.65`, **97 ordered patches**, **3,000,400 bytes**, SHA-256 `a7e1514e34261d115472e6e6db68b88da8277d4e73e4e31cc19f9f99a138f38f`, marker `V11_65_SELECTION_MESH_GIZMOS`. [Single focused source build and JS syntax check passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39529266779). Release follows §§§: commit coherent source directly to `main`, separate last `DEPLOY_REQUEST.json` trigger, confirm exact hosted source and assets, then owner device testing. No unrelated starter suites required. Do not claim physical-device UX acceptance from automated syntax/build validation.

## 2026-10-20 · §E v11.64 — §§§ minimal version/deployment timing test

Owner-directed version-only increment from v11.63 to v11.64, without changing Model Atelier, game or animation behavior. New additive patch `patches/v11_64_version_smoke.py` preserves the original 283-part character scene and 43 packaged assets. The rebuilt v11.64 HTML is **2,976,568 bytes** (96 ordered patches), SHA-256 `bd818ae35f08f5648c0a38ffce4d5bae620a46df8e56291dadba0b7cc53f6282`, marker `V11_64_VERSION_SMOKE_TEST`. A single targeted GitHub measurement run [39527720786](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39527720786) computed the seal. §§§ delivery: direct source commit to `main`, separate final deployment-request commit, one dedicated HF deploy workflow, then owner device acceptance. Never label v11.64 live without a successful hosted deploy receipt.

## 2026-10-20 · §E v11.63 — §§§ minimal version/deploy smoke test

This release changes **version metadata only** (v11.62 → v11.63), with no new modeling tools or changed game/animation behavior. `patches/v11_63_version_smoke.py` preserves the 283-part canonical model. `source-manifest.json` now seals **95 ordered patches**, **2,976,568 bytes**, SHA-256 `6adbda8d53e0b11fe6e98ae59605176362e0fc2b159c558e52087e96ed1274ec`, marker `V11_63_VERSION_SMOKE_TEST`, and the same 43 assets. This small release exercises the §§§ flow: build/version/manifest → commit to `main` → separate `DEPLOY_REQUEST.json` trigger → GitHub-to-Hugging-Face deploy → owner tests. Only the deployment's successful live receipt establishes hosted status. The v11.62 candidate paragraphs below are historical and superseded by this version.

## 2026-10-20 · §E v11.62 mobile adaptive tool sheet — SEALED SOURCE CANDIDATE (NOT LIVE)

This is a **source candidate only**; the publicly hosted §wyrl§ Engine remains verified v11.61 until the v11.62 release and hosted checks complete. The 94-patch candidate is byte-sealed at **2,976,576 bytes**, SHA-256 `215240cd453031834f76e90efd4d125466b6ecb1467dfe9941f3d69b8e08b931`, marker `V11_62_MOBILE_ADAPTIVE_TOOL_SHEET`. [Independent 94-patch measurement and source-preservation proof](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39511087814). The original 283-part anatomical model and 43 bundled historical assets are preserved.

**New editor layout (after release):** Model Atelier → bottom thumb-reachable category rail → choose Lasso, Sculpt, Topology, Face etc. → contextual phone sheet with real native properties, All/Quick/Recent operation discovery, favorites, Compact/Half/Expanded size and left/right-thumb layout; return to the original native inspector with **Original inspector**. Short landscape uses split operations/settings; desktop retains the movable original workbench. Repeated **More → References → More** now restores the original inspector while native-only More still toggles hide/reopen. The six-viewport browser regression for that fix passed at [39510184874](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39510184874).

**Source-of-truth owners:** `projects/swrlz-forge-moba/source-manifest.json` (94 patches and exact seal), `patches/v11_62_mobile_adaptive.py` (governed wrapper), `patches/v11_62_mobile_adaptive_preview.py` (tested presentation), `scripts/verify_v11_62_release.py` (signed build), `scripts/measure_v11_62_release.py` (independent measurement), `.github/workflows/verify-atelier-v11-62-production.yml` (browser/geometry integration), and `.github/workflows/deploy-swrlz-forge-moba.yml` (dedicated gated publication). [Stacked source release PR #283](https://github.com/kaministrator999-ui/Swrlzkamico/pull/283) derives from [preview #278](https://github.com/kaministrator999-ui/Swrlzkamico/pull/278).

**Required acceptance before LIVE:** exact sealed build, full applicable desktop/phone and cross-workspace regression matrix, verify no 283-part/43-asset changes, merge governed candidate into main, and make the **sole LAST release mutation** to `DEPLOY_REQUEST.json`. Observe terminal engine deploy and exact served HTML/SOURCE/all 43 assets plus hosted desktop/phone native editing. Owner on-physical-device UX acceptance remains separately unverified; other §E workspaces (Anime, Story Studio, Maul, Sheep Tag) do not acquire new contextual adapters in this release. Do not use the independent AI Chat/LALM deployment path or Vercel.

## 2026-10-20 · §E v11.62 phone tool-sheet continuity — STACKED PREVIEW (NOT LIVE)

**Authority:** production is verified **v11.61**, not the older v11.60 closeout or v11.61 candidate text retained below. [Engine deployment](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39452004741), [exact live v11.61 HTML and all bundled assets](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39452462102) and [live editor browser verification](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39452462260) passed; source commit `d17aaf3fdad799956c8e6224f5a7e0e6b3de2b82`, 93 patches, 43 assets, 2,958,383 bytes, SHA-256 `cd33b05e3e27304fe9d3e753e488d46fcb844841fd06e19b8058a81516e7d01e`.

**Current continuation:** [§E v11.62 preview #278](https://github.com/kaministrator999-ui/Swrlzkamico/pull/278), base/head source `5ef0df796ba0e68afb12158fd365d18393cee88c` for the 6-viewport preview success ([Actions receipt](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39466710392)). The v11.62 layout is **preview-only**, not included in production manifest or deployed HTML. It covers the native Model Atelier tool families; other game/animation workspaces require their own adapters.

**This follow-through slice:** on an isolated branch stacked onto #278, repair the native **More → References contextual sheet → More** repeat-selection edge case that could leave both tool surfaces closed. Preserve the v11.60 dock's original click handler and native controls; add a phone regression to the v11.62 six-viewport test rather than weakening its existing assertions. Revalidate the exact candidate through the v11.62 CI. The older standalone v11.60 preview job fails its *version-pinned manifest* assertion against v11.61, not a demonstrated defect in the v11.62 mobile UI; current v11.62 test independently exercises the inherited dock on desktop.

**Release boundary:** no change to source-manifest.json, protected 283-part scene, 43 assets or DEPLOY_REQUEST.json in this stacked preview. Before any production v11.62 release, reconcile and seal 94 patches, version/marker/hash, full required regression matrix, merge, final dedicated deploy trigger, hosted exact-source/all-assets audit and owner physical-device UX signoff separately. Original historical notes remain below.

## 2026-10-20 · §E v11.61 contextual native tool workbench — GOVERNED RELEASE CANDIDATE

**Not production live until final verified deploy.** Source adds an optional second split floating tool window. To find it: **Model Atelier → ⠿ Move tools → ◫ Context**. Pick a family in the right rail, a relevant operation on the left, and its native inputs/actions on the right. **Save my values / Apply saved values** are explicit per-operation presets. All original controls and projects remain accessible, with unchanged 283-part canonical model and 43 media assets.

Eight native Model Atelier category families: Meshes, Sculpt, Lasso, Face, Topology, References, Motion, Appearance; only existing compatible controls are exposed. No other §E editor (Anime, timeline, game builders) adapter is yet implemented. 93 patches, v11.61 marker `V11_61_ADAPTIVE_CONTEXT_TOOL_WORKBENCH`, exact generated **2,958,383 bytes / SHA-256 `cd33b05e3e27304fe9d3e753e488d46fcb844841fd06e19b8058a81516e7d01e`**. [Desktop & Android browser preview PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39435151694) and [independent seal measurement PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39435615603). [Feature controls and location guide](https://github.com/kaministrator999-ui/Swrlzkamico/blob/feature/se-adaptive-context-workbench-v11-61/projects/swrlz-forge-moba/reports/CONTEXT_WORKBENCH_V11_61_PREVIEW.md).

Release gates remaining: full production CI/regressions, merge, sole final `DEPLOY_REQUEST.json` trigger, terminal hosted deploy, 43-asset live audit, hosted desktop/Android tests. Historical v11.60 receipts below remain valid for that previous version.

## 2026-10-20 · v11.60 LIVE PRODUCTION CLOSEOUT (post-release)

**Current release: §wyrl§ Engine v11.60 is live.** This verified post-release receipt supersedes the historical *release candidate / not live until* status below; those original checkpoints remain intact.

- Source commit: [`67f835019f850788cc4b4eddf9ca57729e1c11ac`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/67f835019f850788cc4b4eddf9ca57729e1c11ac), containing 92 ordered patches, preserved original 283-part character and 43 bundled assets.
- Final dedicated `DEPLOY_REQUEST.json` trigger: [`e8cad46238e735135012a4c87319f5fe692d4639`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/e8cad46238e735135012a4c87319f5fe692d4639). [Production deployment 39369014929](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369014929): **SUCCESS**.
- [Independent hosted source/all-43-assets audit 39369120445](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369120445): **SUCCESS**, matched `SOURCE.json` and exact served normalized HTML **2,933,954 bytes**, SHA-256 `fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V11_60_FLOATING_MODEL_ATELIER_DOCK`.
- [Live desktop and Android-browser character editor verification 39369120456](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369120456): **SUCCESS**. Automated browser evidence is not owner signoff on a physical phone.
- [Open §wyrl§ Engine](https://kamiloki-swrlz-forge-moba.static.hf.space/) → **Model Atelier**. The persistent **right-side vertical category rail** offers **Meshes / Sculpt / Lasso / Face / Topology / More**. Tap a category to show the floating inspector; drag its **⠿ Move tools** handle to reposition; use **✕ Hide** and a rail button to close/reopen. Original Model Atelier edit handlers and saved model state remain preserved.
- Scope: shipped floating dock, not automatic photograph-to-head reconstruction, high-end QEM retopology, physical-device GPU profiling, or subjective likeness approval. Those are separate, unfinished acceptances.

**This closeout is documentation-only; no engine binary, source-manifest, 283-part scene, release version, hosted content or deploy-trigger mutation is requested.**

## v11.60 · draggable vertical Model Atelier tool dock — governed release candidate (2026-10-19)

Owner requested the precision tools leave the bottom mobile viewport and become immediately discoverable. The v11.60 candidate adds a persistent slim vertical category rail and draggable, collapsible scrollable inspector overlay, **without changing** original 283-part model or all 43 asset files. The cumulative editor includes all v11.59 precision tools; `patches/v11_60_floating_tool_dock.py` is the additive 92nd patch. Exact source seal: **2,933,954 bytes**, SHA-256 `fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f`, marker `V11_60_FLOATING_MODEL_ATELIER_DOCK`. The separate [v11.60 acceptance report](projects/swrlz-forge-moba/reports/FLOATING_TOOL_DOCK_V11_60_RELEASE.md) retains CI and release lineage. **Not live until merge, final dedicated deploy request, successful terminal deployment, exact hosted 43-asset receipt and desktop/mobile UI acceptance.** Older v11.59 source and preview records are retained as history.

## v11.59 · precision Model Atelier production release candidate (2026-10-19)

Owner-directed promotion of the fully **preview-verified** cumulative §E Model Atelier toolset from **v11.21–v11.59** into the governed release pipeline. The additive `patches/v11_59_precision_model_atelier.py` reproduces all previously tested precision tools on the sealed v11.20 anatomical starter, preserving its **283 editable parts** and the original **43 bundled assets**. Highlights: vertex/face sculpting and Undo; camera occlusion + geodesic surface targeting; pixel-radius and editable falloff; lasso geometry, painted Add/Erase masks and native grouped gizmos; multi-image floating reference windows; manually traced feathered photographic cutouts; face landmarks/profile depth/extrusion; native topology, conservative UV island-safe LOD and mesh audit/export.

**Scope and acceptance:** These are implemented modeling tools, *not* automatic human head photogrammetry, curvature-QEM professional retopology, universal 3D pin manipulators, or measured performance on physical Android hardware. Owner requested the production upgrade; appearance/likeness signoff for actual reconstructed faces remains separate.

**Release seal:** `SWYRL_ENGINE_DEPLOY_MARKER: V11_59_PRECISION_MODEL_ATELIER`, **91** ordered patches, **43** original packaged assets, **2,927,005** HTML bytes, SHA-256 `f4d72c72a5fc4ee90c921198d7086b5898b89941de3efadd7f52c063d3dab0b3`. Release-source QA and full browser/legacy compatibility are distinct from the earlier isolated [v11.59 preview success](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39271247522). Dedicated DEPLOY_REQUEST.json trigger must remain the very **last GitHub release mutation** after PR merge and full production validation; live status requires terminal deployment, served exact HTML/43 assets and hosted desktop/Android acceptance. [v11.59 governed release plan](projects/swrlz-forge-moba/reports/PRECISION_MODEL_ATELIER_V11_59_RELEASE.md).

## §E v11.47 verified preview and unfinished original spec — 2026-10-18

[Open v11.47 precision preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-47/index.html?project=model-atelier). [CI 39186091212 SUCCESS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39186091212) at code SHA `d27cc62a73c1cedd911753b3f5654a5da95d36c3` across full six-part desktop/Android browser matrix and CPU geometry; exact served HTML (2,852,736 bytes; SHA256 `5a49c4886db81403a516d18fdf69dbed0ebba6ad8e6355fd9d0db606b9ef76f7`), SOURCE.json and original 283-part anatomy scene verified. Scope adds [PR #256](https://github.com/kaministrator999-ui/Swrlzkamico/pull/256) adaptive local topology/UV stitching and [stacked PR #257](https://github.com/kaministrator999-ui/Swrlzkamico/pull/257) owner-calibrated profile photograph feature-depth maps; no automatic anatomy/perspective claims. The [private owner-spec acceptance tracker](projects/swrlz-forge-moba/reports/MODEL_ATELIER_OWNER_SPEC_ACCEPTANCE_V11_47.md) lists outstanding §2–§12 feature and dense mobile/art QA requirements. Both PRs draft, no production main merge, production sealed v11.20 original remains intact, DEPLOY_REQUEST stays the LAST authorized gate. **The complete modeling document is NOT finished.** Prioritize true ray-visible selection, on-canvas pin gizmos/painted lasso and full actual photographic head/neck reconstruction separately with evidence and owner visual approval.

## §E v11.42 published precision preview handoff — NOT MAIN ROOT PRODUCTION (2026-10-18)

[Open v11.42 verified preview](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-42/index.html?project=model-atelier). [CI run 39178855114 terminal SUCCESS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178855114), second attempt same code revision `10101d16a6ed65ba63875b2d742bd11e756c00c6`; all four cumulative desktop/Android browser groups and native geometry schema passed. Final actual hosted HTML + SOURCE + original anatomy scene SHA matched; first simultaneous publication attempt was correctly blocked due to overlapping source receipts, rerun in isolation succeeded. See [v11.42 acceptance](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_42.md). Stacked draft [#250](https://github.com/kaministrator999-ui/Swrlzkamico/pull/250), [#251](https://github.com/kaministrator999-ui/Swrlzkamico/pull/251), [#252](https://github.com/kaministrator999-ui/Swrlzkamico/pull/252) remain unmerged. Original v11.20 production and 283 parts are **untouched**. Unimplemented milestone A–C remainder: automatic runtime LOD, high-quality remeshing/manifold repair, freehand image clipping and alpha, calibrated multi-camera skull/neck, true camera-space brush occlusion, full 3D gizmos and dense-device QA. Do not declare full spec complete; keep deploy request last after gated promotion and owner visual approval.

## §E v11.42 precision editing handoff — additive draft, production not replaced (2026-10-18)

Current owner Milestones A–C continuation: [v11.42 acceptance addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_42.md) → [PR #252](https://github.com/kaministrator999-ui/Swrlzkamico/pull/252) stacked on [#251](https://github.com/kaministrator999-ui/Swrlzkamico/pull/251) on [#250](https://github.com/kaministrator999-ui/Swrlzkamico/pull/250) and prior v11.39 preview. Dedicated CPU and desktop/Android gates passed for explicit indexed edge split/vertex translate/face remove, authored radial image silhouette and opt-in reference image tap → true saved UV facial landmarks. Full integrated [v11.42 verification/preview workflow](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39178855114) must pass before sharing any new v11.42 hosted URL. **No stable main merge, source-manifest rewrite or DEPLOY_REQUEST mutation for these drafts.** Open gaps: manifold-sound arbitrary edge/bevel/retopo and QEM decimation; runtime distance-switched LOD/thresholds; freehand mask silhouettes and transparent alpha repair; calibrated front/profile matching into skull/neck; true camera-space occlusion, brush-painted lasso, graphical rotate/scale gizmos and dense mobile performance gates. Continue with explicit user-approved design scope and actual visual acceptance.

## CURRENT §E v11.39 precision modeling continuation (2026-10-18)

Two **verified preview-only** owner-priority slices: (1) [PR #248](https://github.com/kaministrator999-ui/Swrlzkamico/pull/248) actual indexed low-poly topology copy + UV OBJ LOD authoring and (2) stacked [PR #249](https://github.com/kaministrator999-ui/Swrlzkamico/pull/249) manual photo-UV face landmark displacement; source of truth [v11.39 acceptance addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_39.md). Cumulative [CI 39174642704 PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39174642704) across geometry and desktop/Android preview UI; [exact v11.39 hosted review candidate](https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-precision-v11-39/index.html?project=model-atelier). It retains the prior v11.37 tools in [PR #247](https://github.com/kaministrator999-ui/Swrlzkamico/pull/247). **No main merge / production deployment or full owner-spec completeness.** Keep original 283-part v11.20 figure and references unchanged; develop feature-preserving decimation, robust arbitrary edge/face operations and automatic LOD separately from photo silhouette and calibrated front/side head/neck construction. Owner artistic acceptance, full source-version sync and governed release remain gates; `DEPLOY_REQUEST.json` is the last release mutation, never touched for preview.

## CURRENT §E precision Model Atelier — v11.36 DRAFT continuation, not production (2026-10-18)

Continue development from [v11.36 acceptance addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_36.md) and stacked [PR #246](https://github.com/kaministrator999-ui/Swrlzkamico/pull/246) → #245 → #243 → #241 → #240/#238/#235/#234/#233/#232/#231/#230/#229/#219. Earlier [v11.32](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_32.md) and [v11.29](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md) documents preserve original history. Recent tested candidate tools: CI exact 90-sealed-patch routing, actual named-region Add/Subtract/Intersect selection across sculpt and local refinement, separately rounded boundary interpolation, and single-edge surface-constrained lasso grow/shrink. Each has a passing dedicated CPU + desktop/Android browser Actions receipt.

**DO NOT** conflate the drafts with merged/deployed §E or a finished character likeness. The original v11.20 283-part anatomical head and source seal remain canonical. Unfinished: true camera occlusion, painted masks, arbitrary retopology/decimation and exported runtime LOD, visual pin rotate/scale handles, multi-view photo-to-skull manual modeling, full integrated mobile/source/artistic release acceptance. Keep unrelated source and personal reference images untouched. Full release requires governed version/manifest sync, owner visual approval, exact integration tests and `DEPLOY_REQUEST.json` as the **last release mutation** after merging validated code. Continue in isolated slices; don't press deploy for an incomplete feature candidate.

## Current precision-editor handoff — v11.32 DRAFT continuation (2026-10-18)

Source of truth: [v11.30–v11.32 verified addendum](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_ADDENDUM_V11_32.md) and [v11.29 baseline acceptance ledger](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md). Current stacked draft PR [#240](https://github.com/kaministrator999-ui/Swrlzkamico/pull/240) → #238 → #235 → #234/#233/#232/#231/#230/#229/#219. New native editor tools verified on desktop/Android: bounded group surface-pin transform, lock and disabled duplication of detail layers, user-sized and pinned floating references. **The full design, full Codex-operated character sculpt, artistic likeness, production merge and deployment are NOT complete.** Preserve original v11.20 283-part anatomical scene and independent project boundaries. Continue true camera occlusion, lasso booleans, real decimation/runtime LOD, visual rotate/scale gizmos, multi-view face modeling and cross-tool testing in small evidence-backed slices. Govern version/release and press `DEPLOY_REQUEST.json` only as the last mutation after total release acceptance.

## Current §E precision-sculpt handoff — v11.29 stacked DRAFT ONLY (2026-10-18)

**Continue from** [v11.29 implementation and acceptance ledger](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_ACCEPTANCE_LEDGER_V11_29.md) and current development PR [#234](https://github.com/kaministrator999-ui/Swrlzkamico/pull/234), stacked on #233 → #232 → #231 → #230 → #229 → #219. The v11.20 original 283-part, eleven-section anatomical scene and sealed source manifest remain production truth. This is **not** a finished spec, merged release, deployed preview or completed character sculpt.

Verified tested candidate additions since v11.23: freehand surface 📌 lasso; interior camera and deliberate opposite-normal sculpt; measured local triangle preview; smooth/flatten/inflate/pinch/translate and mirrored-X brush (base asymmetry remains); parametric sphere/loft sampling presets with true-generator vertex/triangle previews (not exported LODs); opt-in nearest-facing projected-depth safeguard (not accurate camera visibility). See the ledger for exact terminal CI receipts, corrected failures and remaining design requirements. Continue with source-of-truth-first small slices and real device/geometry tests. Do not merge/deploy this draft or press `DEPLOY_REQUEST.json` until full release gates, owner visual review and original v11.20 character protection are satisfied.

## Draft v11.23 precision Model Atelier — Codex operator entry (preview only)

The owner requested **Codex to operate the actual §E Model Atelier controls** for reference-matched character sculpting, not to instruct the owner to manually edit the mesh. The stable release is still **v11.20**; do not merge this draft, overwrite production, or replace the original eleven-section anatomical head/283-part scene.

**Interactive preview:** https://kamiloki-swrlz-forge-moba.static.hf.space/atelier-sculpt-preview/index.html?project=model-atelier

**Read before editing:** [Precision Editor Codex Readiness & Operating Contract](projects/swrlz-forge-moba/reports/PRECISION_ATELIER_CODEX_READINESS_V11_22.md). It enumerates the actual inspector control IDs and bounded workflow for native surface brushes (front/connected/through), vertex matrix and numeric group transforms, lasso boundary pins, conforming local-refinement layers, floating references, UV face-sheet/explicit oval head closure, distortion visualization, Undo and Save/Reload. The original references and sculpt must remain separate assets.

**Acceptance:** the new modules are reviewed by dedicated CPU and desktop/mobile browser tests; exact hosted-preview digest is checked. Test green ≠ artistic likeness approved or a completed Codex modeling session. The advanced freehand cutout, arbitrary decimation/LOD, fully generalized layer stack and automatic reconstruction are not represented as finished.

## v11.20 · anatomical head reconstruction

The owner rejected the round head foundation. A new native surface builds the skull, temples, cheekbones, jaw angles and chin from eleven editable sections, with a flatter facial mask, eye sockets and an integrated nasal profile. Facial contours are refitted and the neck extends into the jaw underside; the corrected legs and remaining body retain their prior data. Saved Apply/Undo and bounded JSON import support the new anatomy controls.

The native starter is `scenes/model-atelier-festival-anatomy-v11-20.swyrl.json`; 90 patches / 43 assets, marker `V11_20_ANATOMICAL_HEAD`. All 179 predecessor patch/runtime sources and 42 assets remain byte-preserved. Exact integrity is recorded in the manifest. Source/deploy commit and live status resolve through the final dedicated deploy request and terminal deployment/audit/native receipts. [Workflow and geometry evidence](reports/ANATOMICAL_HEAD_V11_20.md).

## v11.19 · portrait and body polish

The supplied portrait/body references guide a shorter, softer chin, integrated nose-tip relief and skin warmth, finer eyes/lashes, surface-fitted lips and brows, a smoother neck/shoulder transition and shaped upper arms. Saved native **Portrait finish** and **Fit facial contour** tools support Apply, Undo and validated imports. The existing calf, ankle, foot and independent creature data remain unchanged.

The new starter is `scenes/model-atelier-festival-polish-v11-19.swyrl.json`. The release appends one patch/runtime and one asset, preserving all 177 predecessor patch/runtime files and 41 assets. Package: 89 patches/42 assets. Marker: `V11_19_PORTRAIT_BODY_POLISH`. Exact source integrity is in `source-manifest.json`; publication authority resolves through the final dedicated `DEPLOY_REQUEST.json`, terminal deployment, hosted all-assets audit and desktop/phone native checks. Owner visual acceptance remains separate.

[Native portrait/body workflow](reports/PORTRAIT_BODY_POLISH_V11_19.md). Sealed HTML: 2,614,804 bytes / SHA-256 `d3f8ddb34a964a3955bc1546b7b83db74d29da86ea92f45beb0dbcb998317e72`.

# Current v11.18 · corrected legs and reference portrait

The supplied side-view screenshot identified a knee depth reversal. Both native leg splines now use a gradual hip–knee–ankle profile with actual posterior calf volume, restrained shin contours and an Achilles taper, while preserving ankle endpoints and all foot placements. The new close-up guides warmer amber eyes, finer lids/lashes/lips, swept fringe, a grooved crown, open knotted hair wraps, a fitted collar and refined coral/ivory neckline. All changes remain individually editable and save through native Model Atelier JSON.

New native leg anatomy, crown/wrap finishes and saved iris pigment controls include undo and validated import. The saved starter is `scenes/model-atelier-festival-reference-v11-18.swyrl.json`. All 175 predecessor patch/runtime sources and 40 assets are preserved; the new package has 88 patches and 41 assets. Version/marker: **v11.18 / V11_18_LEG_REFERENCE_CORRECTION**. Sealed HTML: **2,594,314 bytes**, SHA-256 `82f833c7a7771d167e582f381b655e01b5a63e5f6d50a3abb5e2f604467b234b`. Exact source integrity is recorded by the manifest; source/deploy commits and publication authority resolve through the final dedicated deployment request and terminal hosted receipts.

[Correction workflow and evidence](projects/swrlz-forge-moba/reports/LEG_REFERENCE_CORRECTION_V11_18.md). Full native replay, all 18 desktop/phone compatibility suites, merge, dedicated deployment and exact hosted checks are separate gates. Owner visual review remains separate.

## v11.17 · HD character sculpt and native studio finish (2026-10-16)

The owner requested unrestricted high-definition quality. The new native starter refines the continuous portrait surface, integrated iris/pupil fibers and corneal highlights, thin eyelids and smiling lips, transported hair sweeps with a harmonious split-dye fringe, black woven pigtail wraps, embroidered curved garment panels, ribbed draped socks, welted leather shoes and pinched satin bows. Each ferret plume now has a continuous core beneath genuinely creased, overlapping paper leaves with cut edge thickness. Floating cheek/nose decorations and stacked sock-fold primitives were replaced with continuous surfaces.

Native **HD surface finish**, relief, compatible matching-spline application, **Fit trim to cloth**, and saved sampling controls are editable, undoable and validated during import. Physical materials, ACES studio lighting and clean **Render PNG · 2k** support close-up review. The HD starter has **283 editable meshes**, **1,619,108 measured triangles** in the complete set, **1,335,220 in the heroine** and **48,768 in the head**. These are generated buffer measurements, not a quality score or a device-performance claim. The lighter preview and standard detail presets remain available; HD is the saved default.

The saved scene was authored and reimported through real Model Atelier controls. All **173 predecessor patch/runtime files and 39 historical assets** remain byte-preserved. The current package has **87 ordered patches and 40 assets**. Sealed HTML: **2,582,080 bytes**, SHA-256 `623283cc9589fa166ea00f985350f55092606818ab6be4188302f256a0fdb854`. Native geometry checks, desktop/phone editor tests, the full compatibility matrix, merge, final dedicated deployment, exact hosted digest/all-assets audit and hosted editor workflow are separate release gates. Owner visual acceptance remains separate; UV texture painting and weighted skeletal skinning are still outside this release.

Repeatable authoring, measured evidence and art-review limits: [HD character workflow](projects/swrlz-forge-moba/reports/HD_CHARACTER_SCULPT_V11_17.md).

## v11.16 · facial contours and adjustable native mesh detail (2026-10-16)

Owner requested a much more detailed face and asked to verify the proposed 20k mobile triangle budget against UE4 guidance. The current heroine uses **92,028 triangles**, including **12,096 in the continuous head surface** (previously 77,444 and 1,944 respectively). Native nose bridge, eye socket and cheek controls shape the actual head vertices. Smooth jaw transitions remove the hard chin/cheek sampling discontinuity exposed by denser topology. Spline body surfaces, eyes, hair and garment panels have saved sampling controls, with a triangle-edge preview and exact selected/heroine/whole-set counts.

The optional mobile preset is **26,908 heroine triangles**, including **6,016 in the head**. The two independent paper ferrets and bunny retain **32,112 triangles** across both presets, so the complete sets are **124,140 close-up / 59,020 mobile**. The high detail preset is the saved starter. This is selectable native authoring detail; it is not automatic distance LOD or a measured physical-device FPS guarantee. Mesh sampling and continuous facial forms are independently editable, undoable and retained by native JSON/OBJ export.

Epic's [UE4.27 mobile performance guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-guidelines-for-mobile-devices?application_version=4.27) discusses about 500k triangles for the entire view on older iPad targets, rather than a 20k per-character rule. Its [optimization guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/optimization-and-development-best-practices-for-mobile?application_version=4.27) emphasizes profiling target hardware and material/draw-call costs. Preset budgets here are project choices, not Epic character limits.

Native asset: `scenes/model-atelier-festival-detail-v11-16.swyrl.json`, saved and reimported through real Model Atelier controls; **301 editable meshes**, with all 85 prior patches/runtime sources and 38 historical assets preserved. The independent audit's asset list now includes the v11.15 and v11.16 native scenes. Seal: **2,501,987 HTML bytes**, SHA-256 `fd9deed8f22f5b111eadcb59501d47b00061bd4bd219bae6e8e894c82138c97a`, **86 patches and 39 assets**. Native desktop/phone, full compatibility CI, validated merge, the final dedicated deployment and exact hosted verification remain separate gates; owner visual acceptance remains separate.

Recipe and evidence details: [Native detail workflow](projects/swrlz-forge-moba/reports/CHARACTER_DETAIL_V11_16.md).

## v11.15 · native portrait, cloth and ferret surface study (2026-10-16)

The owner requested continued native-editor work against the supplied Honor of Kings Scorchet turnaround. The new starter is the actual model saved and reimported through Model Atelier after **80 native inspector operations**: shorter facial proportions and smiling lip contours, subtler brows/blush, a continuous cyan/coral crown, clearer tapered ferret muzzles and exposed ears/masks, paper bodies swept behind the face in profile, flatter fitted skirt panels with matching borders, a broader coral wrap and corrected rear shoulder layering.

Reusable native tools add portrait jaw taper, tapered muzzle and split-dye crown surfaces, a second dye color, cloth curvature/fold depth and **Frame selected** with detail zoom. New parameters are bounded on import, retained by model JSON and whole-model Undo/Redo, and drive the rendered geometry. The independent ferret sockets, flex, model motion keys, detach/reattach, bunny and native JSON/OBJ exports remain available. Historical defaults retain their old geometry when the new surface fields are absent. Repeated model import now accepts the empty neutral pose emitted by native save/load while retaining validation of actual pose frames.

Native asset: `scenes/model-atelier-festival-surface-v11-15.swyrl.json`; **301 editable parts and 109,556 measured triangles**. [Native authoring and multiview evidence](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38956922273) comes from the real CI browser operating the editor, saving/reimporting JSON and capturing front, three-quarter, profile, rear, portrait, ferret and cloth views plus a phone view. Authoring source: `b411aa3b9592d1ec9d9b3fb1d5f3ebe28f354d02`.

Source seal: **2,487,712 bytes**, SHA-256 `c4c7356c35827eeaea2f24ca943c0dd431c65f5898dbcd325440f0821fc10a3a`, **85 patches and 38 packaged assets**. All 84 predecessor patches/runtime sources and 37 assets are preserved. Full independent compatibility CI, merge, the final dedicated deploy request, exact hosted digest/all-asset audit and native hosted phone/desktop controls are distinct release gates. Source/deploy commits and current publication authority are recorded by `DEPLOY_REQUEST.json`, its final trigger commit and the dedicated deployment/audit receipts; this source note does not substitute for those receipts. Owner visual acceptance remains separate. UV painting and weighted skeletal skinning are outside this release.

Details and repeatable editor authoring: [Native surface workflow](projects/swrlz-forge-moba/reports/NATIVE_SURFACE_STUDY_V11_15.md).

# §wyrl§ Engine · current v11.14 reference refinement

## v11.14 · portrait, silhouette and cloth refinement

The owner requested a closer match to the festival turnaround after reviewing v11.13. This pass refines swept cyan/coral hair into closed elliptical ribbon locks, narrows the round sclera, improves ferret muzzle/eye/ear readability, varies paper edges and color, opens the relaxed A stance, reshapes sock folds and shoes, adds inset garment stitching, and gives the skirt real curved side panels with an opaque fitted underlayer. The separate bunny is moved clear of the wider shoe stance. Front, three-quarter, back and profile views are required; a front-only screenshot cannot reveal missing side cloth.

New native asset: `scenes/model-atelier-festival-refined-v11-14.swyrl.json`; **301 editable parts and 108,260 measured triangles**. Native editor Save model JSON retains the authored result. All three creatures keep independent motion, sockets, detach/reattach, transform keys and exports. The new geometry uses deterministic variation so save/load and OBJ exports reproduce the same surfaces.

Candidate seal: **2,482,877 bytes**, SHA-256 `1154b86d8a8c027fc3b94a39254ff77d5d136a0fcc8283061ef1d0b6d6fe1803`, 84 patches and 37 assets. All 83 predecessor patches/runtime sources and 36 assets remain preserved. Baseline v11.13 was verified live at `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8` before this work. Branch `feature/model-reference-refinement`. Full compatibility CI, the final dedicated deploy request, hosted digest/asset audit and live native controls are release gates; owner visual acceptance remains separate. This is an editable original geometric study, with UV painting and skeletal weight painting still outside the implemented tools.

# §wyrl§ Engine · current v11.13 reference sculpt update

## v11.13 · native reference sculpt and independent living piñatas

Measured candidate seal: **2,467,619 HTML bytes**, SHA-256 `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8`; 83 ordered patches and 36 assets. Native model-save authoring, twenty focused desktop/phone cases and twelve phone/desktop-site/multiview framing checks passed; full independent release CI remains required.

The owner-provided festival turnaround now drives a new 275-part native starter: sculpted facial planes and almond eyes, swept dyed hair, asymmetric layered outfit, bare anatomical legs and socks, two three-dimensional tissue-paper ferrets attached to actual hair sockets, and a separate paper bunny. The living-model inspector provides reversible attach/detach, per-model flex, saved transform keys, a six-second transformation preview, independent model JSON exports and actual rendered OBJ export. Whole model history, native save/load and the measured geometry profiler remain available. Default generated geometry is approximately 82,396 triangles, measured from the buffers rather than guessed from mesh count.

Candidate branch `feature/model-reference-sockets`; source and hosted baseline `43dd6db` / v11.12, 2,352,463 bytes, SHA-256 `76051c90fda3b9f32fef582977fb8af872edc14de44781e253f90ed3f0f9bc6f`. The new release appends patch 83 and native asset 36. All 82 predecessor patches/runtime modules and 35 packaged assets are preserved. The exact earlier v11.12 default remains independently loadable for its full regression.

Research, native format, controls and limitations: [Festival reference workflow](projects/swrlz-forge-moba/reports/FESTIVAL_REFERENCE_WORKFLOW.md). This is an original editable geometric study; production retopology, UV painting and skeletal skin weights are not implemented. Full desktop/phone compatibility, final dedicated deploy, exact hosted audit and the owner's visual response are separate gates. This candidate section does not claim publication before those checks pass.

# §tart §E — §wyrl§ Engine Build & Deploy Router

## v11.12 grounded pose correction — validated and merged; deploy pending (2026-10-15)

**Owner rejection:** three-quarter, profile and rear phone screenshots of live v11.11 reveal visible “banana/rubber legs” and unnatural apparent knee pain when Idle/Victory is applied. The v11.11 pose algorithm displaced most leg spline knots with a bell-shaped depth weight while fixing both hips and ankles; a clean knee hinge and believable weight-bearing stance did not result. Earlier numerical tests rewarded **more bend**, so green CI was not visual acceptance.

**Implementation:** append-only `patches/v11_12_grounded_stance_poses.py` replaces only the inlined v11.11 built-in pose handlers, preserving saved-frame schema, face refinement, ferret-piñatas and older scene assets. For each six-knot continuous anatomical leg, interpolate each interior point along either a hip–knee or knee–ankle segment with restrained depth displacement. Give one leg a stable near-straight support posture and let the other leg relax to a modest step; translate the whole sock/shoe/toe/sole assembly with its ankle in X/Z while preserving every foot's Y-ground contact. Avoid moving the face independently of torso and ferret sockets. `Neutral`, `Relaxed idle`, `Victory` and `Victory B` remain reversible/editable.

**Validated merge:** [PR #194](https://github.com/kaministrator999-ui/Swrlzkamico/pull/194) merged as `f2fa861fe65742f7a3dce1b60db358a6e6472368` from validated head `6ab1a126ffcc73b904436d6603a51c1428bc59aa`. **17/17 desktop/mobile browser suites and all nine applicable workflows passed** including the new grounded-joint, anchored-sole and neutral-restoration assertions. Source seal 2,352,463 bytes / SHA-256 `76051c90fda3b9f32fef582977fb8af872edc14de44781e253f90ed3f0f9bc6f`. Hosted release and owner visual acceptance remain separate.\n\n**Acceptance gates:** exact source SHA and 82-patch/35-asset seal; 811-part source preservation; native geometry CPU test validates near-straight thigh/shin, maximum knee angle, both anchored soles, idempotent pose application and neutral restoration; desktop/mobile screenshot/UI test rejects support-leg banana deformation and airborne footwear; all historic game/rig browser suites must pass. Once merged, update only `DEPLOY_REQUEST.json` as the last main mutation; independent hosted digest/asset audit and owner's subsequent multi-angle screenshot review remain mandatory. This is **still not** a skin-weighted skeleton or authored animation.


## v11.11 facial + native pose/frame studio — validated and merged; deployment gate pending (2026-10-15)

The owner's mobile front/rear/side screenshots of live v11.10 showed a too-stiff straight-legged standing pose and overly flat face. A new append-only `patches/v11_11_face_pose_frame_studio.py` changes **only the generated canonical starter** to subtly soften the jaw, eyes, brow, cheeks, nose and smile while preserving the original v11.9 811-part scene asset. The new in-viewport collapsible Pose & camera frames panel supports **Neutral, Relaxed idle, Victory, Victory B** and front/back/left/right/three-quarter camera choices. Leg poses are actual edits to existing native smooth loft knee spline knots (not animation bones), remain undoable, and preserve all 811 editable parts. Eight named custom pose+camera frames can be saved, restored, renamed through save-overwrite, deleted and carried in validated native project JSON / Save Project. Original ferret bodies remain distinct; no commercial game asset is extracted.

**Technical boundary:** No skeletal skinning, pose interpolation, animation timeline, imported animation libraries or guaranteed facial likeness in this release. Do not claim visual approval without comparing new front, rear and profile screenshots to the provided references.

**Validated PR:** [#193](https://github.com/kaministrator999-ui/Swrlzkamico/pull/193), head `ccca615f79960f7cb0ec65a76daa466d6b178b3e`, squash merge `16faf1b8a7b42f15e9e01b56da010b100ac6dc6b`. All 17 desktop/mobile browser acceptance jobs passed and all eight related §E source/audit workflows reached terminal success. This is validated merged source, **not** hosted release or owner visual approval.\n\n**Sealed candidate:** 81 ordered patches, 35 unchanged historical packaged native assets; independently reconstructed **2,350,741 bytes**, SHA-256 `e89ea40f0b7609d0b5cf376666aaba4a58971a3a294c3225ad303ce9f6ef4792`. Source syntax + controlled knee spline CPU acceptance passed. Full package/browser CI, merge, dedicated deploy request as last `main` source mutation, successful Hugging Face delivery and independent hosted SHA/assets audit are required before calling v11.11 live.


## v11.10 measured model statistics — merged source, release gate pending (2026-10-15)

Owner-directed Modeling Engineering Brief implementation slice: [PR #190](https://github.com/kaministrator999-ui/Swrlzkamico/pull/190) merged with source commit `7e38e623ed24801becd6afd738519652d79d9909` after all seven §E CI workflows and all 17 independent desktop/mobile browser jobs passed on validated head `4e89457c990e654e96e80bec8138148b25637dcf`. New append-only `patches/v11_10_model_geometry_profiler.py` adds measured generated BufferGeometry triangles, buffer vertices, CPU geometry memory, grouped component breakdown and native JSON statistics export with a mobile-friendly collapsed inspector. No source character meshes were replaced: the 811-part v11.9 original native scene and all 35 historical game/media assets remain preserved. Source seal: **2,339,787 HTML bytes, SHA-256 `e8b2ca7b4e12d9981475a861d40eabf513f5d26a40c8f6627d393b93d03dddf6`, 80 patches, 35 assets**. See `projects/swrlz-forge-moba/reports/MODEL_ATELIER_ASSET_PIPELINE_2026_10_15.md` for scoped next slices: reversible independent creature sockets, character identity and skins, skeletal rigging, animation, material/LOD tools, VFX and chat orchestration. These later systems are **planned, not implemented** in v11.10. Do not mistake reported buffer vertices for welded topology or estimated meshes for actual GPU draw calls.

**Release authority:** this merged source remains only a candidate until the deliberately changed `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` triggers the dedicated HF pipeline, that workflow reaches terminal success, and an independent hosted SHA/asset audit confirms serving the new digest. Human owner front/side/back visual acceptance remains separate. Never deploy via §wyrlz AI Chat or weaken historical game/browser checks.


## Active v11.9 model starter candidate — owner-approved ferret-and-figure refinement (2026-10-15)

Owner reference is the primary cyan/coral carnival mage and approved character turnaround; other skins are anatomy/material context, not replacements. The two ferret-piñatas are independent native creature bodies gripping separate dyed hair at the head, each with a 36-tier faceted editable loft and a narrow root (r=.115), broad midbody (peak r=.77) and tapered far end (r=.20). The default candidate adds a continuous sculpted neck/torso, refined human arms/legs/hands/shoes, eight actual editable cloth panels and a separate paper bunny. The prior 253/303/539/653/733/749-part scenes are preserved. Branch `feature/engine-v119-figure-ferret-silhouette`, PR #187, 811 current editable parts, 79 governed patches, 35 native assets. Exact source candidate: 2,335,886 HTML bytes, SHA-256 `987f074e111420126715142da652d4907c7d1a0e493215ee9784e35da48966dd`. Full CI, merge, dedicated deploy trigger, independent hosted SHA/assets audit and owner's multi-angle likeness review remain distinct gates. This is procedural unrigged original geometry, **not** skeletal skinning or animation; do not call it visually accepted without owner screenshots.

## Active v11.8 · approved model sheet → functional sculpt, not primitive inflation

Owner-approved character correction for this release: giant paper ferrets originate behind the heroine's head, sweep back in 3D and twist forward along opposed broken-S paths; the girl becomes taller, with continuous loft-shaped arms/legs and no discrete bead knees/elbows. Native spline controls must edit twist, depth profile, smoothing, X-mirror and paper fringe, while smooth anatomical loft creation remains available. The implementation uses a procedural native loft tool; **rigged skinning, invisible armatures, bone weights, UV painting and volumetric sculpt brushes are still future tools** and must not be claimed as implemented. Meshes and material colors alone are not proof of quality: inspect actual front/side/back output against owner-approved concept sheet. Only merged, validated, deployed, independently audited artifacts may be called live.


## Current §E v11.7 model fidelity gate — owner corrective screenshots

The live v11.6 reference study failed the visual acceptance gate. The owner identified smooth boomerang/sausage loop geometry, fake detail inflation, insufficient piñata construction, flat rear treatment, blockout facial/garment anatomy and inconsistent mobile presentation. **When this is reported, implement the authorized code changes immediately rather than responding with another plan or menu of options.**

**Current construction contract:** The two ferret bodies must be distinct, visibly stepped chains of **36 capped truncated-pyramid disk slices each**, with angular flat-shaded faces, interlayer recesses, torn paper edges and colored overlaps on the front, sides, underside and rear. There must be actual gripped dyed hair braids, prominent elongated ferret muzzles, jaw/brow/eyes/ears, and sculpted front/rear apparel, hair and footwear. This is structural geometry, not tiny box inflation. Loft control paths and radii must remain editable, and each historical scene must remain loadable.

**Proof, not assertion:** Native 3D object data, shader/geometry flags, model counts, front/side/back screenshots, mobile and desktop interaction, import/export and full regression must be tested. Passing a source seal or adding hundreds of objects does not establish visual quality. Record unsatisfied art-direction differences and keep iterating on observed defects. Group fixes and test expectation updates into atomic commits to avoid needless CI churn. Gate merging and the dedicated last-main-mutation deployment trigger on independently returned CI results, then confirm production served digest and owner visual response.

**Release candidate:** v11.7 — faceted tiered piñata spine surfaces, 733 editable pieces (474 old wafer decorations retired; 554 structurally placed additions), 77 governed patches and 33 native assets, pending measured artifact seal, complete browser tests and hosted audit. Production remains v11.6 until independently verified.


## Active owner workflow contract — §E (2026-10-15)

**Entry rule:** When owner reports a defect, supplies screenshots, or approves work, do the authorized scoped change in this session where tools permit. Do not stop after a plan, handoff, diagnosis, or recommendation. Read this router and the governed source manifest; identify actual code/artifact and live deployment state. Repeat tool calls as needed within available limits, and report genuine connector limits rather than pretending a build deployed.

**Completion loop:** observe → isolate → modify narrowly → test targeted code and visual behavior → run necessary regression suite → merge validated work → edit only the dedicated `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` as the **last main mutation** → wait for terminal deploy result → independently audit exact served HTML hash, native asset list, and production behavior → review owner's front/side/back screenshots and continue corrections if acceptance fails. A green workflow, branch commit, merged PR, or mesh count alone is *never* equivalent to visual or live acceptance.

**Release efficiency:** batch logically related changes; avoid a new PR or tiny CI-triggering commit for every discovery. Centralize version/patch/asset expectations. Use branch-level concurrency cancellation for superseded *validation* only; never cancel a production release. Run cheap syntax, scene schema and editor checks before expensive browser matrix. Reuse built artifacts and cached browser dependencies where safely feasible. Keep full release regression coverage before deployment; do not delete or weaken tests to manufacture green checks.

**Model acceptance:** assess silhouette, depth, readable head and muzzle anatomy, actual hair gripped by two separately modeled living piñata-ferrets, paper fringe on front *and back*, face/garment proportions, and front/side/rear evidence. Added parts must produce noticeable improvements, not merely a higher counter. Preserve historical native scenes and provenance; do not extract commercial models.

**Mobile acceptance:** prioritize practical viewport height, sensible camera framing, touch controls, compact accessible inspector, independently scrollable object list, and no giant unused screen space; check both actual mobile browser viewport and desktop-site mobile mode. The owner's screenshots are first-class regression evidence.

**Truth and release status:** distinguish requested, source edited, tests pass, merged, deploy triggered, deploy succeeded, independently audited live, and visually accepted. If a blocker remains, name the failing gate and continue working when tools allow; do not claim finished early.


## Current project: §wyrl§ Engine v11.6 — visual/mobile candidate (not deployed)

Owner screenshots of **live v11.5** established the correct 539-mesh release but exposed flat piñata reverse surfaces, thin angular loft silhouette, underdeveloped face/back detail, tiny default model framing and excessive empty mobile workspace. The **separate v11.6 candidate** includes native 653-editable-part festival scene and a compact mobile viewport/inspector stylesheet. Its measured source seal is **2,279,438 bytes / SHA-256 `d5f8dce1cbaf221a9f03719f99d53a10b26c6a68fc980ccd38359c4cbbb3a6d0`** with 76 governed patches and 32 native assets. Test and screenshot review are required; do not call v11.6 live until dedicated deploy succeeds and independently hosted audit confirms exact source. Historical v11.5 source verification notes below must not override this current release state.

## Historical v11.5 candidate · now deployed successfully 2026-10-15

The new 539-part original festival character variant keeps historical 253- and 303-part editable native scenes intact. The 75th governed patch adds editable loft path/radius control, raises the Model Atelier capacity to 1,200 parts and JSON import allowance to 8 MB; the new native variant is packaged independently. The exact candidate rebuilt in GitHub Actions [#38747495949](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38747495949) at 2,253,004 HTML bytes, SHA-256 `325f286e0dd3166e34bff57b1e721a6e244089a02cc01d33f8bc3025bace324a`, marker `V11_5_FESTIVAL_LOFT_ATELIER`. **This is source candidate evidence, not a hosted v11.5 deployment confirmation.** Full legacy browser CI, integration review, final §E manual trigger, independent hosted audit and owner visual acceptance are distinct gates. Previous v11.4 production receipts below remain historical evidence.


## Current verified live v11.4 · Prism Jester ferret-piñata fidelity

**Owner direction:** stay on the original cyan/coral **carnival mage** concept. The apparent oversized pigtails are **two living ferret-like paper piñatas biting/holding the real pigtails**—separate muzzle, ears, eyes, paws, and gracefully arched paper bodies—not just curved hair tubes. Other skins are material/render references only.

A separate native **303-part** model variant at `scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json` replaces only the default Model Atelier sample at Projects; the original 253-part v11.3 scene remains packaged for historical import. Append-only `patches/v11_4_prism_ferret_fidelity.py` adds two smooth variable-radius editable `loft` meshes with paper fringe, improved facial layers and costume detail; engine runtime defaults and existing Maul/Sheep/anime starter saves remain preserved. `reports/PRISM_JESTER_FERRET_ART_DIRECTION.md` contains the comparison criteria, implementation notes, official Blender/Three.js learning references and limitations.

**Verified live v11.4 (2026-10-15 CDT):** [PR #171](https://github.com/kaministrator999-ui/Swrlzkamico/pull/171) merged at `0540cfbfc29129548941881f659f26a767038ed3`. [All 17 desktop/phone browser suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364328) with all five candidate source workflows green. [Guarded production deploy #38729222214](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729222214) and [independent hosted audit #38729291039](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729291039) both SUCCESS from release trigger `2dba7e6da30fef16c8bb1f4a35f979bcfbffb9b4`. Published Hugging Face Space revision `f88b57b39893f556e380cef7c279d93860800a95`, marker `V11_4_PRISM_FERRET_FIDELITY`, 74 patches, 30 assets, 2,197,108 HTML bytes, SHA-256 `40d1e985bd3754b7a2996e6be14056be9c22164995d83b84ad253b4ae7a24658`; independent hosted audit reported `HOSTED_AUDIT_SCOPE=current-requested-release` and `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`. Original 253-part scene remains available historically. This is a procedural fidelity study, not an exact extracted game mesh or advanced sculpt/UV/rig/animation toolset.

## Current verified live v11.3 · Native 3D Model Atelier and Prism Jester

The new **Projects → Model Atelier · Prism Jester** starter is a separate, editable native `scenes/model-atelier-prism-jester.swyrl.json`, not an overwrite of the 30-wave Frostveil or existing Animation Studio. Its original scene contains **253 individually editable meshes**: layered hat/hair, face details, costume, limbs, and two sweeping segmented coral/cyan forms, inspired by owner-provided reference screenshots. It is an original approximation, **not extracted proprietary game geometry or a pixel-exact replica**.

Model Atelier adds a dedicated responsive WebGL viewport, orbit/touch camera, raycast part selection, XYZ position/rotation/scale editing, shape/color/material controls, adding/duplicating/removing meshes, bounded local undo/redo, validated JSON import/export, and triangulated OBJ export. Its data is stored under `project.modelAtelier` in the standard §E native save envelope. The Scene/project launcher and historical native assets remain preserved. Advanced vertex sculpting, texture painting/UV mapping, bone-rigging, mesh deformation and animation have not been implemented.

**Verified live v11.3 (2026-10-14 CDT):** [PR #167](https://github.com/kaministrator999-ui/Swrlzkamico/pull/167) merged as `abfe8a495b3a7c166f2bebe9151887b2cef6b807`. [All 17 desktop/phone browser suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608237) and five candidate §E validations passed. [Dedicated deploy #38677061503](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677061503) and [independent hosted audit #38677099743](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677099743) both completed SUCCESS on source trigger `44a594f534c92c723079adcb33d8a80962bc7e0f`. Host audit scope `current-requested-release` reported `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`; published `V11_3_MODEL_ATELIER_PRISM_JESTER`, 73 patches, 29 assets, 2,175,921 HTML bytes, SHA-256 `a2ec94f418f294ea5ebd50363833d37025a6e6cc804732116a7cb927d0b069db`. This verifies production integrity, not personal human gameplay acceptance or advanced vertex sculpt/UV painting/rigging.

**Starter-pack source of truth (verified live v11.2):** The default **Projects → Frostveil Maul** tile now opens the independently authored `scenes/maul-frostveil-flight.swyrl.json` (78 actors, nine builders, 30 rounds) directly, instead of relying on hidden mutations to the older grouped starter. It saves `maulConstruction: walk-v1`, `maulSpawnProtection: full-pad-v1`, `maulBuilderFlight: hover-v1`, and `maulVisualStyle: glacial-v2` inside the native project. Its own package asset is shipped beside the older `scenes/maul-frostveil-groups.swyrl.json` and classic Maul files, never overwriting the earlier scenes. Browser CI must verify that the editor’s default starter is identical in critical profile and builder identity to the downloadable native pack. The v11.2 release passed candidate CI, dedicated deployment, and independent hosted audit.

## Current verified v11.2 · Hover construction and glacial battlefield polish

New canonical Frostveil starter opts into `maulBuilderFlight: hover-v1` and `maulVisualStyle: glacial-v2`. Each sector's winged builder flies directly across terrain and existing towers at **15 world units/second**, hovers approximately **3.25 units above the ground**, and constructs the tower directly underneath its position after travel and the existing route/gold/footprint rechecks. Manual flight remains inside its assigned territory; build placement still forbids protected entrances, gates, exits and occupied ground. Moving cancels a pending build, pause suspends movement, and legacy walk-v1 imported projects keep their original ground pathing and side-cell construction.

The native visual update adds bounded, cached, original procedural 256px snow/ice and harbor-water textures, layered cliff/ice accents, highlighted entrances, pine snow, and lightweight animated builder wings. These are visual-only: no Maul route/wave schema or project asset is overwritten. The baseline 30-wave co-op and earlier Sheep Tag/anime/Den releases remain intact.

**Status:** completed [PR #159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159), ordered 72nd patch `patches/v11_2_maul_flight_glacial_art.py`. **Verified live v11.2 (2026-10-14 CDT):** [PR #159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159) merged as `b3ef6130f0d9685018debb06fcdd4ef2912d9f6e`. Six candidate Forge workflows and all 16 native desktop/phone suites succeeded on `716a2bc81b01c79b65ed7771eb3dc794248ce55b`. [Dedicated deploy #38668840620](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668840620) and [independent hosted audit #38668893410](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668893410) both completed SUCCESS on trigger `e47c027816fa5029f0c27ac273e040ae62fd1a5f`. Space revision: `ef8f325b2d8d45cf67da2c54bc4f8e3455df263e`. Published binary: **72 patches, 28 assets, 2,097,069 HTML bytes**, SHA-256 `1fab5e61f2065c02a56658c6e8e8ef999eb525ac16c373b310826ca970e10e59`, marker `V11_2_MAUL_FLIGHT_GLACIAL_ART`. Exact served HTML, SOURCE receipt, and all 28 assets matched. Owner gameplay acceptance remains separate.

**Next separate engineering slices:** physical creep spacing and congested-lane traffic; legal blocked-route response with tower aggression; distinct enemy fast/stealth/detection/typed immunity/teleport/heal/Hydra/Infernal archetypes with counters; adjustable wave mixes and recorder events; optional endless and two-team automatically synchronized Mirror Survival (no player-sent monsters); neutral-balanced thematic builder sets; and a native Maul-specific map/route/wave creator. None of these remaining systems is claimed implemented by v11.2.

**Frostveil implementation ledger:** [Wintermaul v11.1 shipped-versus-planned minion waves and gameplay](projects/swrlz-forge-moba/reports/WINTERMAUL_DESIGN_ARCHITECTURE.md#verified-v111-minion-wave-status-2026-10-14). Three grouped arrival batches, flying/boss rounds and walk-to-build are live; collision/congestion, stealth, immunity, teleport, split/Hydra/Infernal and healer archetypes, endless and Mirror Survival remain planned. The report's acceptance gates govern future claims of completion.

## Historical verified v11.1 · Physical builders, tower mazes, protected entrances

The v11.1 **Frostveil Maul** starter (not historical imported maps) introduced **walk-to-build**: tower placement queues the chosen sector builder to path to a clear adjacent cell; the tower only exists after the builder arrives, when the game rechecks the route, footprint and available gold. Pausing freezes the walk. Moving a builder deliberately cancels their pending construction; changing sectors does not. Building in an entrance pad, gate, or exit is forbidden, and the spawn pads are visibly outlined. Standalone maze walls are hidden from the current build menu; the four combat tower families still physically obstruct ground routes and form staggered, jagged mazes. Historical saved walls are not deleted, and old Maul imports preserve legacy rules.

This is the **first playable delivery** against the larger Wintermaul specification, not a claim that every discussed feature exists. Remaining distinct design/engineering work includes physical crowding/no overlap, completely blocked-path creep aggression against towers, stealth/detection, speed and immunity variations, teleport, hydra/infernal splits, healing creeps, themed balanced builders, Mirror Survival (identical automatic waves for both teams; no player-sent waves), endless scaling/rewards and the dedicated in-editor Maul creator. Keep both player territory independence and team-shared survival. Extend in separate validated slices rather than silently enabling unimplemented mechanics. Older 30-wave rules, animated story projects, Sheep Tag and recorder formats are preserved.

Release: **71 governed patches**, **27 assets**; final patch `patches/v11_1_maul_walk_builder.py`. The exact source, CI, full desktop/phone native acceptance matrix, deployed revision, and independent hosted audit were verified.


**Verified live v11.1 release (2026-10-14):** Merged source [`bbe56716867e`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/bbe56716867e046d3a4f887aa2f5829f25709cd1) includes recorder PR #154 and walked-builder PR #156 through reviewed PR #157. The exact candidate passed [all six Forge workflows and 16 native desktop/phone browser suites](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38643766910). Dedicated [Forge deployment #38646048742](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38646048742) and independent [hosted artifact/asset audit #38646122359](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38646122359) both completed **SUCCESS** for the existing `kamiloki/swrlz-forge-moba` Space. Published v11.1 contains **71 patches, 27 assets, 2,027,727 HTML bytes**, SHA-256 `c96e5fea45bd316750e2fcc60ff1cbd96feadd6a90a56a5667dddad0aaf21121`; Space revision `70a5a943fa302668a2b46bf5c5765f7bfa5349cf`. Published source and all bundled assets were matched independently; future owner gameplay feedback remains separate from these CI/hosted receipts.


## Included v11.0 contribution · Compressed recordings and clear Maul spectator

Frostveil Maul Play-run review now renders recorded snowfields, water, cliffs, tower families, maze walls, builders, creeps and the exit as distinct visual layers, with camera framing adjusted to the actual Maul map dimensions. The original Sheep Tag recorder presentation and recording schema remain intact. A new **Export compressed (.json.gz)** control uses lossless browser-native gzip; the recorder also imports these gzip files with format validation and a bounded 256 MiB decompressed limit. Existing raw JSON, text, HTML spectator, camera, timelines, events and saved projects continue to work.

This v11.0 source contribution added the seventieth governed patch and retained **27 packaged assets**. It was integrated into the cumulative, verified v11.1 publication; v11.0 was not released separately.


## Previous v10.9 candidate · Story actions and an animated first episode

Open **Projects → Ghosts in Different Forms**, or `?project=anime-ghosts-ep01`, then use **Play** or **Watch Episode 01**. Kami and §wyrlz now act through the story: greeting and reaching, recoiling and bracing, casting, writing, stepping, hovering and recovering. Their arm chains, attached full-length staff, heads and costume depth pieces move together. Short dialogue windows leave room for a character to listen and react between lines. Kami's first attempt to burn a doorway nearly erases the library and makes §wyrlz fade. They recover by joining Kami's light with §wyrlz's written names, build a doorway that remembers them and step toward a world that answers, ‘Welcome back.’

The native **Animation Studio** adds **Story Actions** and **Story effects**. Saved action clips control character, action, time, duration, strength and side; effect cues control page motion, bursts, ink and a portal. Preview Frame, editor Play and Watch sample the same saved story time, including reverse and fast playback. Disabling an overlay leaves the underlying limb, face and scenery keys available. Native Undo/Redo and Save/Load retain the clips and cues separately from those keys.

The current native export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`. It retains **70 actors, 11 layers, eight contiguous story beats, nine stage/camera tracks, 134 seconds**, the 12-second book opening and the fitted full staff/socket/relief settings. Its native save contains 175 stage/camera keys, 468 limb/face keys, 383 scenery keys, 36 action clips and 11 effect cues. `project.animePerformance` uses `anime-performance-v1`; `project.animeStoryEffects` uses `anime-story-effects-v1`. The previous full-staff scene and every earlier project/artwork asset remain packaged unchanged for import.

Publication appends `patches/v10_9_episode_story_actions.py`, for **69 governed patches and 27 assets**. All 68 published patches, previous runtime modules, 26 predecessor assets and payload chunks remain byte-identical. Artifact: `swyrl_engine_v10_9.html`; marker: `SWYRL_ENGINE_DEPLOY_MARKER: V10_9_EPISODE_STORY_ACTIONS`. The starter count remains **seven**.

Acceptance requires all **six engine workflows**, **sixteen desktop/phone browser suites**, thirteen sealed Sheep Tag geometry cases, seventeen preserved Maul CPU cases, twelve classic-layout CPU cases and fifteen grouped-spawn CPU cases. The new episode suite checks the saved action/effect data and actual native authoring, Preview/Play/Watch movement, playback controls and lifecycle on both layouts. Completion requires the final dedicated `DEPLOY_REQUEST.json`, terminal successful deployment and exact hosted HTML/SOURCE/all-asset audit. Candidate documentation does not assert publication before those checks pass.

## Historical verified v10.8 · Grouped Maul rounds and visible phone placement

The v10.8 release is verified live: merged source `d371df09a37d44d40d9b05425e01f977eabfa62a`, final trigger `507d11b93e7af81359614e6d56d98a35adbf0b6b`, [deployment 38567626510](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38567626510) and [hosted audit 38567696344](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38567696344). It seals **68 patches, 26 assets and 1,905,846 bytes**, SHA-256 `775d7dfab363da120c2c779b5d8d129d7c75ee6a9681911958bdb9cef3fa1e3e`. All six engine workflows, fifteen desktop/phone browser suites and the four sealed CPU suites passed, followed by native live desktop and phone gameplay and recorder exports. Marker: `V10_8_MAUL_BATCH_PLACEMENT`; artifact: `swyrl_engine_v10_8.html`.

Each cooperative Maul round releases three scattered groups at 0, 2.5 and 5 seconds. The saved `classic-v2` map adds `maulSpawnStyle: "grouped-v1"`; its native `scenes/maul-frostveil-groups.swyrl.json` starts with no authored towers. Phone placement lifts the complete ghost and footprint 140 CSS pixels above the finger. These receipts certify v10.8; the story-action revision requires its own deployment and exact hosted audit.

## Historical verified v10.7 · Classic Maul map layout

The v10.7 release is verified live: merged source `c80e0b98e33ad2c68943415d8c767f836f849f0f`, final trigger `c26630d0f8fce2ba5f3c10c2edfec6e92cf5b109`, [deployment 38513639622](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38513639622) and [hosted audit 38513700470](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38513700470). It seals **67 patches, 25 assets and 1,833,206 bytes**, SHA-256 `c3f24f05ba745a5e834e964d7e06f0637b57b1115fe242bc86d7920738984ddc`. All six engine workflows, fourteen desktop/phone browser suites, twelve classic-layout CPU cases, seventeen preserved Maul CPU cases and thirteen Sheep Tag geometry cases passed, followed by native live desktop and phone gameplay and actual recorder exports. Marker: `V10_7_CLASSIC_MAUL_MAP`; artifact: `swyrl_engine_v10_7.html`.

This release established three long northern snowy bays, a broad crossbar, winding lower defense lanes, editable route turns and one shared ship exit. Its original `scenes/maul-frostveil-classic.swyrl.json` remains packaged unchanged for import. These receipts certify v10.7; the grouped-spawn and placement revision requires its own deployment and exact hosted audit.

## Historical verified v10.6 · Frostveil Maul tower defense

The v10.6 release is verified live: merged source `52862f6a2f8a869d21a03103888b4a094ad19969`, final trigger `6200148fcc7c4ba83bfe76883b4fd49c7d20c53f`, [deployment 38434348748](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38434348748) and [hosted audit 38434414319](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38434414319). It seals **66 patches, 24 assets and 1,748,442 bytes**, SHA-256 `01d7fff6e2a943a326e4582670640d60eec78475c75ab12e16d92c12ee2a9843`. All six engine workflows, thirteen desktop/phone browser suites, 17 Maul CPU cases and 13 Sheep Tag geometry CPU cases passed, followed by native live tower placement/selection, waves, Pause/Stop and actual recorder exports on desktop and phone. Marker: `V10_6_MAUL_TOWER_DEFENSE`; artifact: `swyrl_engine_v10_6.html`.

The cooperative starter introduced nine linked sectors, thirty waves, shared lives, tower mazes, upgrades, air/boss rounds, optional support and native rules authoring. Its original `scenes/maul-frostveil.swyrl.json` remains packaged unchanged. These receipts certify v10.6; the revised classic map requires its own deployment and exact hosted audit.

## Historical verified v10.5 · Editor play-run recorder

The v10.5 release is verified live: merged source `6da367913c0eecc89c67a4976c3db407d851da15`, final trigger `e3b252b6850dfd84824563d1209333930321b268`, [deployment 38344147035](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38344147035) and [hosted audit 38344188938](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38344188938). It seals **65 patches, 23 assets and 1,594,471 bytes**, SHA-256 `cd3b50f06d3a802c025b3e530e743446d284633961bff0dacd46a656eb7e8ace`. All six engine workflows, twelve desktop/phone browser suites and 13 geometry CPU scenarios passed, followed by native live recorder downloads on desktop and phone. Marker: `V10_5_SHEEP_RUN_RECORDER`; artifact: `swyrl_engine_v10_5.html`.

The opt-in recorder introduced by v10.5 works across native starters and custom projects. Full capture records each observed Play update; 10 Hz and 2 Hz settings offer smaller state logs while retaining timed commands/events. It retains the starting map, actual seed, hierarchical object/limb poses, camera, input, health/lifecycle and game state. After Stop, the latest three runs can be scrubbed through a spectator schematic, object-follow view or recorded camera and exported as JSON, text or offline HTML. Simulate creates no recordings. Exports preserve a run beyond the current tab; the viewer reconstructs captured states rather than rerunning gameplay or exporting a rendered video.

## Historical verified v10.4 · House lanes and physical creature traffic

The v10.4 release is verified live: merged source `6d04109c27dfcd7e732e2550f3184db82755e999`, final trigger `04ba3ef018d4715cd51fd56ff51b1f96d8530bc6`, [deployment 38317704872](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38317704872) and [hosted audit 38317774602](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38317774602). It seals **64 patches, 23 assets and 1,520,413 bytes**, SHA-256 `f2c2eeb2a28d91239b3cb7afd48c0d189373a260bd12a851e3aaa8fd92524a2d`. All six engine workflows, eleven desktop/phone browser suites and 13 continuous-geometry CPU scenarios passed, followed by 17 live controls cases per layout and exact hosted source/assets. Marker: `V10_4_SHEEP_LANES`; artifact: `swyrl_engine_v10_4.html`.

Sheep can build at their feet, moving to the nearest clear side; blocked construction rejects without moving the builder or charging gold. Houses remain **2.4 × 2.4** and snap flush together or with a **0.6-unit lane**, with preview and collision using the same placement. Wolves retain **0.78-unit** default bodies and approximately 15% larger artwork; sheep retain **0.27**. Wolf bots prioritize reachable visible sheep over buildings. Physical creatures do not overlap on the same floor: blocked ground traffic replans or backs out; raised-route traffic waits. Wisps and decoys stay intangible, rescue chooses a free landing, and native preflight rejects overlapping same-species starts.

## Historical verified v10.3 · Placement above the finger

The v10.3 release is verified live: merged source `de24b04c95e13993313b0abd3496b6fb2602c9be`, final trigger `d0442216bf82ee82fb9df0aaefc8aa345d3f36c0`, [deployment 38312154843](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38312154843) and [hosted audit 38312197696](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38312197696). It seals **63 patches, 23 assets and 1,501,714 bytes**, SHA-256 `6b0f2f461ea2bb1595e0be2ef4dbc58a114ecb39bd8e1828ac745cd0b7ed2653`. All six workflows and eleven desktop/phone suites passed, followed by 13 live controls cases per layout and exact hosted source/assets. Marker: `V10_3_SHEEP_TOUCH_OFFSET`; artifact: `swyrl_engine_v10_3.html`. Touch previews remain above the finger and release builds at that displayed footprint.

## Historical verified v10.2 · Sheep selection and ground placement

The v10.2 release is verified live: merged source `0144031ae3b35630de1eb969fd05f7c0efbade74`, final trigger `3bf7004e716c3bea29f3f3e683d33c0700ef8669`, [deployment 38273428696](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38273428696) and [hosted audit 38273499402](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38273499402). It seals **62 patches, 23 assets and 1,487,394 bytes**, SHA-256 `2c0d10636bda9cf6062e6ec49d8173a77a104fa208c841d6eda4d48409a9ba35`. All six workflows and eleven desktop/phone suites passed, followed by eleven live controls cases on each layout and normal Projects/Play checks. Sheep use deliberate double taps to select buildings; single taps keep movement available. A terrain-following grid, filled footprint and green/red boundary show full house, wall and ramp extent. Marker: `V10_2_SHEEP_TOUCH_PLACEMENT`; artifact: `swyrl_engine_v10_2.html`.

## Historical verified v10.1 · Sheep Tag Design Archive

The v10.1 release is verified live: merged source `86aa05b494db007d9aebc073f0c7242756376447`, final trigger `1779223f8b92024f2625e68046ad9582ca80f594`, [deployment 38223924840](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38223924840) and [hosted audit 38224004659](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38224004659). It seals **61 patches, 23 assets and 1,464,129 bytes**, SHA-256 `ef72eb9177a81537c5f6f56f65d620ac9593b4e08da6eae4f1bc4e34b5c9b8f1`. All six engine CI workflows and ten desktop/phone browser suites passed, followed by nineteen live archive cases on each layout. Marker: `V10_1_SHEEP_TAG_ARCHIVE`; artifact: `swyrl_engine_v10_1.html`. These receipts certify v10.1.

The player's **SE_Sheep_Tag_Complete_Design_Archive.docx**, prepared 11 October 2026, guides this starter. Choose **Sheep Tag · Moonbell Meadow** in **Projects** or use `?project=sheep-tag-meadow`; `scenes/sheep-tag-moonbell-archive.swyrl.json` retains **92 baked actors, six populated layers, eight sheep and three wolves**, with twelve thorns, two no-build zones, the central wisp pen and four merchants. The default **Archive** preset enables thorn sensing, nine-house totem conversion, connected raised routes and Illusive Split; events remain off. **Classic** independently retains survival, construction, wolf demolition and wisp rescue. Values remain provisional and adjustable.

**Map Creator** provides terrain painting, hazards, landmarks, spawns, no-build zones, species path previews, independent map Save/Load and native Play/Stop revision. The released 66-actor meadow and all prior media remain preserved. Pond cleansing, advanced illusion tiers, automatic structural collapse and a future multi-game hub remain outside this release's scope.

## Historical verified v10.0 · Sheep Tag Starter

The v10.0 release is verified live: [PR #106](https://github.com/kaministrator999-ui/Swrlzkamico/pull/106) merged engine source `a06c89ed9e6cd65737de111efc11cac268519449`; [deployment 38174454216](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174454216) and [hosted audit 38174501776](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174501776) succeeded on final trigger `87b6a4be9319be30ac22b99212d773a289d2b199`. It seals **60 patches, 1,290,101 bytes**, SHA-256 `abcab023bbec0b5cacc72d7b845096060feb56418ab12b9eacee62bf9b7bf8c4`, and 22 assets. All six engine CI workflows and all nine desktop/phone browser suites passed, followed by fourteen live gameplay cases on each layout. The native Save Project map retains 66 actors in four populated layers, six sheep, two wolves, one pen and four merchants. Editor validation reported zero issues and warnings. Marker: `V10_0_SHEEP_TAG_STARTER`; artifact: `swyrl_engine_v10_0.html`. These receipts certify the released v10.0 starter.

## Historical verified v9.9 · Episode Shuttle Controls

The v9.9 release is verified live: [deployment 38150826816](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150826816) and [hosted audit 38150874160](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150874160) succeeded on final trigger `a382b4ea577c0a72f0223ef2aa4aad650121a5bf`. Merged engine source `4eb6021976e999bb84b9b915d2a9546cdb569a18` seals **59 patches, 1,139,928 bytes**, SHA-256 `60dfa8da434eaa6cfe578f441a93be1fb9139676933e985a19919c13938b60c9`, and the unchanged 21 media assets. All eight desktop/phone browser suites and six engine checks passed. Watch Episode Rewind/Fast forward buttons cycle **2× → 4× → 8× → normal 1×** beside the chapter skips. Pause, scrubbing and chapter changes preserve signed speed; boundaries pause at normal speed, and Replay/Stop/Explore/close/new screening restore 1×. Player speed remains session data. Marker: `V9_9_EPISODE_SHUTTLE_CONTROLS`; artifact: `swyrl_engine_v9_9.html`. These receipts certify v9.9; v10.0 requires its own validation and final deployment.

## Historical verified v9.8 · Full-length Mage Staff

The v9.8 release is verified live: [deployment 38115297536](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38115297536) and [hosted audit 38115324306](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38115324306) succeeded on final trigger `6cd814f925a79759a8b65b11af46895ce14014a2`. Merged source `35936a688fe14eeb06a4db90d1c3d8a5a1a8fb70` seals **58 patches, 1,133,438 bytes**, SHA-256 `d486985beb2e92ba9ad237ea6e5313dcffb7f53e9b5e69c3b54aca24e4a9b5b8`, and 21 assets. Its flaming skull crown, uninterrupted black-and-gold shaft, fitted hand grip and pointed foot stay connected during poses and the opening from the book. The saved `staffArt: "painted-full-v1"` profile and **Use full-length staff** preset retain native fitting, Undo/Redo and Save/Load; original/custom atlases retain their artwork. All seven desktop/phone browser suites and hosted native Play/Watch, Reset, Undo/Redo and Save/Load passed. Marker: `V9_8_FULL_LENGTH_MAGE_STAFF`; artifact: `swyrl_engine_v9_8.html`. These receipts certify v9.8; v10.0 requires its own final deployment and hosted audit.

## Historical verified v9.7 · Ornate Mage Staff

The v9.7 release is verified live: [deployment 38099380535](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38099380535) and [hosted audit 38099404177](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38099404177) both succeeded on final trigger `a5366aaf269ee3ad248dc380855ef440cdc67358`. Merged source `63d5924557598706f79703324a5eac0ad0114a7b` seals **57 patches, 1,111,978 bytes**, SHA-256 `0e1d8a7cbf90e956714245364d923107d7c8d0e8ab8476aa7b81e0fcbad43ac3`, and nineteen assets. It added ebony grain, gold inlay, slim rounded bands and fitted end caps to the existing round pole while preserving the natural grip. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_7_ORNATE_MAGE_STAFF`; artifact: `swyrl_engine_v9_7.html`. Its short painted staff-head cutout remained separate from that long core; v9.8 replaces that cutout with full-length painted artwork. These receipts certify v9.7; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.6 · Natural Staff and Painted Faces

The v9.6 release is verified live: [deployment 38071280266](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38071280266) and [hosted audit 38071311391](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38071311391) passed on final trigger `f164ccd37ce8ffd28cbc28ce4dea9b4f64ed7178`. Merged source `b21f0dd3072ada0f157e4f75b041c008d861a8cb` seals **56 patches, 1,099,583 bytes**, SHA-256 `d78dedc68ae0fe7bcbd368ee949bb2926c6f9bf321586e5254ad3fb97c1f07bd`, and nineteen assets. It introduced the saved natural-grip profile, continuous round shaft, fitted crest, larger painted facial features, exact face-cache inputs, consistent Canvas rasterization, opacity-preserving mouth blending and deterministic staff motes. All seven desktop/phone browser suites passed before deployment; hosted native Play and Watch passed on desktop and phone. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_6_NATURAL_STAFF_PAINTED_FACES`; artifact: `swyrl_engine_v9_6.html`. These receipts certify v9.6; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.5 · Fitted Staff and Character Relief

The v9.5 release is the previous verified checkpoint: [deployment 38013962412](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013962412) and [hosted audit 38013986565](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013986565) passed. Source `49b82022de841a26a4692359751395ca792efc9f`, final trigger `dcab50950603fb4160615e0d6bf5e0ec8558b06e`, seals 55 patches, 1,075,201 bytes, SHA-256 `bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb`, and 16 assets. It introduced the saved staff mount and per-piece character relief. These receipts certify v9.5; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v10.0 candidate requires its own final deployment and hosted verification.


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

### Atomic starter-pack draft & engine-upgrade handoff (v215 source guidance)

For user-owned §E work that derives a native project seed into an eventual editor starter or new game mode, read [`docs/engineering/SWRLZ_ENGINE_PACK_AUTHORING_V215.md`](docs/engineering/SWRLZ_ENGINE_PACK_AUTHORING_V215.md) alongside the v214 ladder. This describes the current two-file **unregistered data draft** and the separate steps for Projects registration, per-game controls, mode-specific rules, deterministic ordered engine patching, desktop/phone tests, PR review and dedicated §E release. A plain scene clone or descriptor must never be reported as a playable mode, and no AI Chat Hugging Face deployment may publish engine work. This documentation has no deployment authority.

### GitHub/AI editor-and-starter development ladder (source-only)

For a §wyrlz AI session that aims to edit this §E editor, derive native starter packs, build new playable modes or update engine internals, consult `docs/engineering/SWRLZ_ENGINE_AGENT_V214_BUILD_LADDER.md` after this start router. It distinguishes real current GitHub tool capabilities (verified source mapping, planned work, approval-gated scene draft and draft PR) from not-yet-supported multi-file patch generation, automatic starter registration, engine release, or verified live gameplay. The specialized §E build and dedicated deploy rules in this document remain authoritative. Reading this reference is non-deploying.

### Coder education cross-reference (conditional, non-deploying)

When teaching a coding model about §wyrl§ Engine source, Three.js, Python ordered patches, animation data, character sockets or Forge build validation, also read `training/coder/PROJECT_STACK_ARCHITECTURE_V1.md` and its public practice exercises `training/coder/project_stack_architecture_v1.json`. If a *new language* or platform integration is specifically being studied (Kotlin/Java/TypeScript/Rust), also inspect `training/coder/CROSS_LANGUAGE_CURRICULUM_V2.md` as **non-executable education**; it does not convert this engine to another toolchain or change the governed engine build. Post-discovery task-size coaching is continued in `training/coder/MODEL_MATURITY_DISCOVERY_V4.md` (only optional educational examples; no engine/runtime activation or release authority). Model task-size and verification coaching is separately taught by `training/coder/MODEL_MATURITY_EFFORT_V3.md`; this reference cannot activate the v182 opt-in classifier or touch the dedicated §E release gate. Those exercises are **ungraded**, do not train model weights, and do not replace this router's mandatory engine source-manifest/build/deploy rules. Chat/LALM model-route instruction remains owned by the separate Programming LALM Runtime Architecture. This curriculum link itself is documentation-only and must not trigger an engine deployment.

## Supported book opening and limb sockets

The existing coordinated opening brings Kami, §wyrlz, architecture, props, effects and the three star-depth shells out of the pages before they reach their saved stage positions. Preview Frame, Play and Watch use the same saved opening. Persistent limb sockets keep snapped children attached while their pose keys rotate around the connection.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`; the full-staff export remains preserved for import. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Saved per-character rest layouts, 468 limb/face keys, 383 scenery keys and the action/effect overlays remain independent. The v9.6 natural-grip, v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all eleven artwork PNGs and the historical episode HTML.

The 54th and 55th patches retain the staff mount and per-piece relief. The 56th, `patches/v9_6_natural_staff_painted_faces.py`, retains the compact grip and painted facial features; the 57th, `patches/v9_7_ornate_staff.py`, retains socket-attached shaft ornament. The 58th, `patches/v9_8_full_length_staff.py`, integrates the full painted staff and native preset; artifact `swyrl_engine_v9_8.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_8_FULL_LENGTH_MAGE_STAFF`. The 59th, `patches/v9_9_episode_shuttle.py`, adds signed episode shuttle playback; v9.9 artifact `swyrl_engine_v9_9.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_9_EPISODE_SHUTTLE_CONTROLS`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging contains nine episode scene JSON exports, the historical episode HTML and eleven PNGs, for twenty-one media assets. The 60th patch, `patches/v10_0_sheep_tag.py`, adds the separate native Sheep Tag starter; v10.0 artifact `swyrl_engine_v10_0.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V10_0_SHEEP_TAG_STARTER`. The native meadow map raised the v10.0 package to 22 assets. The 61st patch, `patches/v10_1_sheep_tag_archive.py`, adds the verified archive rules and creator. The 62nd, `patches/v10_2_sheep_touch_placement.py`, adds double-tap sheep building selection and ground placement guides; `swyrl_engine_v10_2.html` and `V10_2_SHEEP_TOUCH_PLACEMENT` identify the historical v10.2 release with the same 23 assets. The 63rd patch retains touch aim above the finger, the 64th retains house lanes and physical creature traffic, and the 65th adds the opt-in Play-run recorder and post-Stop review. The 66th adds the separate Frostveil Maul tower-defense starter, with its native scene as the 24th packaged asset. The 67th reshapes that starter around the classic upper bays, crossbar and shared ship funnel, with a new native scene as the 25th asset. The 68th adds scattered grouped arrivals, visible phone placement and an empty default build area; its separate native map is the 26th asset. The 69th adds the animated story and native action/effect editors; the new performance export is the 27th asset.

The verified v10.8 source and production receipts are recorded above. The current v10.9 candidate requires its own sixteen-suite desktop/phone browser matrix, six engine workflows, all four sealed CPU suites, final dedicated deployment and exact hosted package audit.

## Historical verified v9.3 · Connected Character Pieces

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v10.0 requires its own final deployment and hosted audit.

## Historical verified v9.2 · Layered Scenery and Fitted Faces

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`; the v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

The 51st governed patch is `patches/v9_2_depth_theatre.py`; artifact `swyrl_engine_v9_2.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_2_LAYERED_SCENERY_FACES`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging includes four episode scene JSON exports, the historical episode HTML, and eight PNGs including the new transparent `assets/anime/scenery-parts.png` atlas.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

## Historical verified v9.1 · Articulated Paper Rigs

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

The project keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Limb and face tracks live separately under `project.animeRigs` (`anime-character-rigs-v1`), so posing one mage does not overwrite the other mage or the existing shot timeline. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json`; the v9.0 storybook export and original 62-actor production scene remain bundled.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

The 50th governed patch is `patches/v9_1_character_rigs.py`; artifact `swyrl_engine_v9_1.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_1_ARTICULATED_PAPER_RIGS`. Exact bytes and SHA-256 come from the final sealed manifest and generated receipt. The package includes the new rigged scene and `assets/anime/kami-rig.png` / `swyrlz-rig.png`, while preserving all previous artwork, scenes, and screening assets.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

## Historical v9.0 · Native Animation Studio and Paper Theatre

The **Ghosts in Different Forms · The Page That Remembered** starter is now authored and saved through the native editor. Its 134 second episode has eight story beats and nine independent tracks: Camera, Kami, §wyrlz, Background, Atmosphere, Midground, Effects, Foreground, and Book. Kami is the larger horn-hooded mage; §wyrlz is the smaller hovering skull mage. Newly generated transparent character artwork and independent scenery plates follow the supplied gothic amber/gold references.

The exported `projects/swrlz-forge-moba/scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json` contains **70 actors and 11 editor layers**. Eight new saved paper actors each own a layer; the original 62 production set actors, three production layers, eight workstations, and eight destinations are preserved. Native `animeCel` and `animeBook` actors persist through Save/Load, with the timeline under `project.animeTimeline`.

**Animation Studio** edits camera position/target/FOV, individual cast/scenery/book keys, numeric transforms, easing, visibility, opacity, unfolding, episode title, and timed dialogue. Preview Frame and the editor Play button use the same native renderer. Timeline and artwork changes use native Undo/Redo and Save Project; PNG, WebP, and JPEG artwork can replace a saved layer. The **Capture Actor Pose** workflow copies a track's native Inspector pose into a keyframe.

Reusable engine implementation lives in `runtime/anime_timeline.js`, `runtime/anime_stage.js`, `runtime/anime_editor.js`, their CSS, and the 49th governed patch `patches/v9_0_animation_studio.py`. Physical mesh cards unfold around bottom-edge hinges, with protective scenery depth, a low foreground/book, and adaptive portrait framing. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_0_AUTHORED_PAPER_THEATRE`; artifact: `swyrl_engine_v9_0.html`. Exact integrity is recorded in the sealed manifest/build receipt.

Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Production authority is recorded in the final `DEPLOY_REQUEST.json`, the dedicated deployment receipt, and the exact hosted-release audit. Live completion requires terminal deployment success and exact served source/artwork verification. The original **Watch Episode 01** remains the historical 2D screening; native Play runs the saved paper theatre. Skeletal posing, lip sync, audio authoring, and MP4 export remain unimplemented. See `ANIMATION_STUDIO.md` and `VERIFICATION.md` in the engine project.

Direct starter: https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01 .

## Historical verified v8.9 · Camera-safe Pop-Up Storybook

Android playback revealed the v8.8 set/desk card and book obscuring the actors. Source patch `projects/swrlz-forge-moba/patches/v8_9_cinematic_staging.py` lowers the animated book, makes the foreground a thin bottom border with transparent upper pixels, and enforces behind-the-cast architecture and effects. Tests check first/later scene occlusion geometry at phone and desktop sizes. v8.9 source: **48 patches**, `swyrl_engine_v8_9.html`, **647,639 bytes**, SHA-256 `da9f48941543c81062a232417ed8897e8c82e912852474cf2154e209c12ddf37`, marker `SWYRL_ENGINE_DEPLOY_MARKER: V8_9_CINEMATIC_STAGING_SAFE`. [Desktop/mobile Play/Save acceptance passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728474772); [production deployment passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728665723) and [independent hosted source+both media asset audit passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728754278). v8.9 is an earlier verified camera-safety checkpoint; its exact receipts and the older source remain preserved.

## Historical v8.8 candidate · 3D Pop-Up Storybook Video Creator

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

The Anime Studio starter joins Embervault and Starforge as an independent project. Current v10.9 authoring uses 70 actors, 11 editor layers, nine stage animation tracks, independent limb/face/scenery keys and saved story action/effect overlays in the native Animation Studio editor. The 134 second paper theatre runs through Preview Frame and Play. Watch Episode opens the pop-up cinema using the same native scene and chapter controls; its original static HTML media asset remains bundled. See the current v10.9 contract above.

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

### Historical v8.4 release receipt contract

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

Sealed HTML: **2,621,375 bytes**, SHA-256 `d0db24152221ea1dfd4ecc284f65686af71f74c770d4c7c15134979d98b77494`. Local native authoring completed 14 recorded edit groups, exact Save/reimport and eight review views. The 283-part set retains 1,623,252 measured triangles (heroine 1,339,364; head 48,768). The focused phone Apply/Undo, invalid-section/import and surface-cleanup/Undo checks passed.
