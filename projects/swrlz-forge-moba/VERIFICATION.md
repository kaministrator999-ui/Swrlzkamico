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

## §E v11.91 · Saved Festival Girl and organic anime sculpt (2026-10-23)

The previous **283-part girl starter is preserved** as **Saved Festival Girl · v11.90** (`?project=festival-girl-saved`). The main Model Atelier card now opens **Prism · Organic Anime Girl** (`?project=organic-anime-girl`). Her complete skin is one closed, connected mesh from scalp and ears through the neck, torso, arms, ten fingers, legs and feet: **254,588 vertices / 509,172 triangles**. A more inward-tapering jaw ends in a narrow, rounded chin; shaped cheeks, orbital wells, a refined nose, fitted amber eyes tilted upward six degrees at the outer corners, and lips, hands with nail plates, knees, rear calves and Achilles transitions replace the old separate primitive anatomy.

The full sculpt has **353 editable topology meshes / 1,634,372 triangles**, including the asymmetric festival outfit, original paper-ferret companions and bunny. **72 tapered 3D hair filaments**, modeled stitches, knuckle folds and fitted closed sleeve/yoke shells add geometry detail. Dedicated **4096×4096 color and normal maps** provide skin, hair flow, weave, embroidery, leather, metal and radial iris detail. Body, face, hand and full-character views support close inspection; companion isolation changes the viewport only. Native material editing/Undo, JSON save/import and textured GLB retain the complete model. Detailed native import supports **256 MB**, and a part supports **300,000 vertices / 600,000 triangles**. This is a detailed authoring sculpt; skeletal weight painting has not been added.

Release **123 patches / 64 assets**, HTML **6,421,818 bytes**, SHA-256 `ba0105f62f2e7451d4e78148cae425f4ce5e3684093fc3954d3c1f0e1105b934`, marker `V11_91_ORGANIC_ANIME_GIRL`. All **294** prior runtime/patch sources and **60** prior packaged assets preserve exact bytes. Sheep Tag retains the v11.90 collision, controls and optimized game models. See [targeted verification](reports/ORGANIC_ANIME_GIRL_V11_91.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.90 · Solid house blockers, furred Astra and match performance (2026-10-23)

Houses stop sheep on contact. Holding the joystick first walks up to the blocker, then follows a cached, collision-checked route around it; releasing stops immediately. The previous nearest-side/lane-center pulling and construction ejection are retired. Placing a structure over its builder is rejected without moving the sheep or spending gold. Real narrow lanes, rotated houses, unit traffic and automatic ramp/walkway traversal retain native swept collision.

Astra now has flowing shoulder/ribcage/waist contours, **one connected skull-and-ear mesh**, inset velvet pinnae and **1,100 closed curved 3D fur locks** on its body, chest and limbs. The high-resolution wolf starter has **96 editable parts / 639,772 rendered triangles**, with all **37 original courier gear/comet-tail parts byte-exact** and the original **4096×4096 color and normal images**. Native rebuild, edit/Undo, JSON save/reload and textured GLB remain available; detailed native import supports 128 MB.

Sheep Tag uses a separate optimized copy: **69,471 triangles / 29 draw meshes per wolf**, compared with **274,980 / 106** previously. Compatible meshes are merged within each independently animated head/tail/leg joint, sharing cached geometry and materials. Broad-phase collision rejects distant houses before identical narrow-phase samples; footprints cache per navigation revision. Held-stick routes avoid repeated whole-map grid searches. On phones, full-rate run recording uses **10 Hz world snapshots**, preserving command/event captures and explicitly selected slower cadences. These changes target CPU, GPU and recording overhead; owner-device FPS still needs hands-on acceptance. Clover, compact corner controls, the 320×320 m map and seven-minute rounds remain.

Release **122 patches / 60 assets**, HTML **6,390,662 bytes**, SHA-256 `c76e61f6c4b8457ce1f49d3781c8aa0710d7e44adaf7176d17744fdbda5c663a`, marker `V11_90_SOLID_BLOCKERS_FURRED_ASTRA`. All **290** previous runtime/patch files and **58** previous assets preserve exact bytes. See [targeted validation](reports/SOLID_BLOCKERS_FURRED_ASTRA_V11_90.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.89 · Living Astra, Clover flock and compact corner controls (2026-10-23)

**Astra's full anatomy pass** replaces separate tube-like legs/toe pieces with four welded anatomical limb/paw meshes, including elbows, wrists, hocks, tendons and four toes per paw. The seated torso has shaped shoulders, ribs, pelvis and tucked belly; the ivory chest now tapers naturally and fits beneath the original harness. The face has orbital wells, a defined brow stop, tapered muzzle/lower jaw, canine pupils and nostrils. Closed cupped pinnae and curved fur surfaces replace the remaining biological primitive parts. All **24 original gear parts and 13 comet-tail/stardust parts** remain byte-exact. The native model contains **92 editable meshes / 547,676 rendered triangles**, retaining the original **4K color/normal atlases**. It remains rebuildable with the editor's organic volume/sweep tools and supports material editing, Undo, native JSON and textured GLB.

**Clover replaces the sheep in Sheep Tag**, including all eight starter sheep and reconstructed/spawned `st-sheep` actors. It uses the same 31 source parts, fleece/face/ears/hooves, native atlas bindings and shared **4096×4096** images as the new independent sheep model. A game copy made with Model Atelier's native mesh reducer uses **33,087 triangles**, while the original **275,872-triangle** authoring starter remains unchanged. Cached geometry/materials are shared across independently animated head, tail and four leg joints. Fleece width fits within the existing sheep collision diameter; routes, capture/wisps, construction and timer retain native logic.

**Controls corrected to the owner's screenshot:** at 926 px portrait width, the joystick and building/skill diameters are about **45% of v11.88**, with the joystick anchored **18 px from the left / 22 px from the bottom**. Separate compact right-side arcs retain spacing, readable labels and safe margins. Narrow screens keep a minimum 44 px ability target and 50 px building target. Landscape moves auxiliary actions beside the joystick to clear the minimap.

Release **121 patches / 58 assets**, HTML **4,557,192 bytes**, SHA-256 `a9f6b48036c852be5a75150f18ebc9e31633c43acaa28c3b08a79b1d67506ed0`, marker `V11_89_LIVING_ASTRA_CLOVER`. All **285** prior runtime/patch sources and **56** previous assets preserve exact bytes. See [targeted validation and anatomy references](reports/LIVING_ASTRA_CLOVER_V11_89.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.87 · Organic sheep and wolf model starters (2026-10-22)

**Clover · Meadow Sheep** is a new independent Model Atelier starter. **Fen · Wildwood Wolf** replaces the wolf model starter entry and the earlier `comet-courier` shortcut. The wolf is a natural quadruped with a fused ribcage/shoulder/neck/skull/muzzle surface, a tucked waist, bent hocks, four-toed paws, short alert ears and a low brush tail. The sheep has continuous fleece over shoulders/barrel/haunches, a tapered bare muzzle, folded pinnae, horizontal pupils, lower-leg tendons and split hooves. Visible parts are editable indexed organic meshes; there are no sphere, box, cylinder or cone model parts.

The native organic volume tool blends anatomy fields into a connected, welded surface. Model Atelier exposes `loadAnimal(species, {force, rebuild})` to rebuild with that tool, alongside the standard component, sculpt, group, undo, material and export controls. Both starters use a shared **4096×4096 color atlas and matching 4096×4096 normal map**. Native model import supports 64 MB detailed saves and meshes up to 65,536 vertices / 120,000 triangles per part; high detail remains authored data. Textured GLB export embeds the proper atlas, including mixed original/animal materials. Studio view opens with a clear silhouette and an Edit model button. Saved project payloads are compressed losslessly in `payload/organic-animals`; packaging emits the portable native JSON scenes.

Release **119 patches / 55 assets**, HTML **3,359,239 bytes**, SHA-256 `c2dda3de1cb7bf262e347a47c9dfde2f9c4af267ed1124fee068a804fb6cda40`, marker `V11_87_ORGANIC_ANIMAL_STARTERS`. All **277** previous runtime/patch sources and **51** assets preserve exact bytes. Sheep Tag retains v11.86 nearest-side house steering, 7-minute matches, large controls and the 320×320 m map. These model projects are independent authoring starters. See [targeted validation](reports/ORGANIC_ANIMALS_V11_87.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.86 · Sheep steer around houses (2026-10-22)

Holding the joystick into a house now steers a living sheep toward the **nearest clear side/corner**, then continues in the held direction. A blocked side falls back to the other clear side. Fully blocked exits stop safely. This uses the native swept movement and analog speed; it never relocates a sheep through a structure. Rotated houses, other creatures, narrow sheep-only gaps, joystick reversal and release are checked. Wolves, wisps and automatic ramp/deck movement keep their existing controls.

Release **118 patches / 51 assets**, HTML **3,340,927 bytes**, SHA-256 `01b695c06bc5636b762d87914d76e2511224345add0e80c93ce6a1e6f04eba0b`, marker `V11_86_SHEEP_HOUSE_SLIDE`. All **275** previous runtime/patch sources and **51** assets preserve exact bytes. The 320×320 m map, 4K textures, enlarged controls, 7-minute timer and versioned update history remain available. See [targeted validation](reports/SHEEP_HOUSE_SLIDE_V11_86.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.85 · Bigger controls and seven-minute matches (2026-10-22)

The portrait joystick grows from **156 to 224 px** and moves diagonally **up and right**. Compact portrait uses 192 px; landscape uses 208 px, or 176 px on a short phone. The knob and direction mark grow with it. Right-side buildings and abilities grow by roughly 12–23% in the main layouts, with adaptive compact sizes and the two separated arcs retained. Larger labels wrap within their circles. Landscape score, utility buttons and feedback shift to keep the enlarged controls accessible.

The default match lasts **7 minutes (420 seconds)**. The portable starter carries that duration, and saved maps using the previous 20-minute default migrate to seven minutes. Other explicitly tuned durations remain editable. The native countdown, head start, win conditions, movement, ramps and placement use their existing game clock and rules. The editor’s versioned update panel automatically lists this release.

Release **117 patches / 51 assets**, HTML **3,338,122 bytes**, SHA-256 `76ea088b19a441ed0e846ffdd4a02197eb131b45a3ea55255eeb032f7c5d13f4`, marker `V11_85_LARGE_CONTROLS_SEVEN_MINUTES`. All **272** earlier runtime/patch sources and **50** preceding assets preserve exact bytes; the additional asset is the seven-minute starter scene. See [targeted validation](reports/SHEEP_LARGE_CONTROLS_V11_85.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.84 · Reliable building, connected walkways and update history (2026-10-22)

- **Building recovery:** one placement pointer owner handles icon and meadow drags. Rejected/cancelled drops release capture, remove the ghost and clear the selected tool. Unaffordable buttons show a cost message without entering placement, so the free house remains available.
- **Automatic ramps:** joystick steering ascends and descends completed ramps directly, follows connected decks and stops at unsupported edges. The ground/upper-route and descent toggles are hidden. Species radii, traffic, wolf ramp permissions, capture and hunt-release restrictions remain native.
- **Connected extensions:** walkways and exit ramps snap to existing deck/ramp high edges and rotate toward the selected side. Straight extensions and side turns share physical seams and the native route graph. Sheep already on a connected deck can construct a nearby extension; normal costs, occupancy, sanctuary and completion rules still apply. Player-built side connections open a gap in the parent rail when complete.
- **Touch controls:** abilities occupy an inner arc beside the outer building arc. A larger joystick and separated compact layouts keep targets at least 44 px. Touch aim rises **128–180 px** above the finger, with top-readout clamping.
- **Larger map:** the new starter is **320 × 320 m**, 25% wider and 56.25% more area than the preceding 256 m meadow. Authored scenery, roads and the 4K ground scale with the layout; previous scene files remain unchanged.
- **Editor updates:** an automatic latest-update panel includes **107 previous versions**, grouping every previous patch. Its checkbox hides only this exact version; the next release appears again. The editor footer’s **Updates** button reopens it, and unchecking restores the popup. Future source versions derive notes and history automatically from the manifest and new patch summaries.

Release **116 patches / 50 assets**, HTML **3,333,468 bytes**, SHA-256 `82ae2d5fdac77f9a63cb4375aae2d93939c8cdf3338395f7120995f62d2bc411`, marker `V11_84_BUILD_RECOVERY_WALKWAYS`. All **264** preceding runtime/patch files and **49** prior assets preserve exact bytes. The additional asset is the larger native scene. See [targeted implementation and evidence](reports/SHEEP_RECOVERY_WALKWAYS_V11_84.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.83 · Drag houses to build, joystick movement and smooth fog (2026-10-22)

Manual movement now uses the **left joystick**, including the desktop pointer layout; ground clicks/taps no longer issue move orders. Drag a building skill icon onto the meadow, aim with the house **above your finger**, and release on a green footprint to order construction. A tap can also arm the building tool for a subsequent ground drag. Visible house/unit selection, wolf attack, rescue, camera pan and minimap camera navigation remain available. Construction retains its native approach, collision, footprint, cost and completion rules. Accepting a build releases held joystick ownership so the next frame cannot overwrite the construction order. Steering again deliberately replaces that order. Blocked/cancelled drops do not charge gold or build. The preview rechecks affordability and occupancy while held still, avoiding a stale red “Need gold” message after income arrives.

Fog uses **soft circular vision edges**, linear sampling and a 4× display mask (512×512 on the 256 m meadow), updated at most ten times per game second. The minimap shares that smooth display. Logical visibility, explored cells, enemy filtering, bot knowledge and pre-hunt restrictions remain native. All **262** preceding runtime/patch files and **49** assets retain exact bytes, including the 4K artwork.

Release: **115 patches / 49 assets**, HTML **3,288,058 bytes**, SHA-256 `41b34b31203777afffc242d42a83b32157e61442760fa9549960600ed27d7962`, marker `V11_83_DRAG_BUILD_SOFT_FOG`. See [targeted implementation and validation](reports/SHEEP_DRAG_V11_83.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.82 · Mobile building skills, joystick and clear touch placement (2026-10-22)

Sheep Tag now uses **round illustrated building skill buttons at the bottom right** on phones/tablets: house, income house, fortified house, wall and ramp. The existing native buttons retain their costs, availability, active state and build commands. A **left movement joystick** steers the actual sheep/wolf through native swept collisions and traffic, supports proportional speed, and stops on release/cancel/pause/blur. Captured wisps keep their slow crawl/leash; wolves remain immobile before release. The minimap moves to the top left. A compact **••• unit-actions drawer** keeps camera, upgrades, selling and archive controls accessible, while the editor footer returns after Stop. Desktop controls retain their original layout.

Touch building aim is **72–112 screen pixels above the finger**, with a dotted guide to the exact snapped footprint. Preview and release use the same native build target. Separate pointer owners let one thumb steer while another aims; two simultaneous placement fingers still cancel safely. Portrait, landscape and compact screen layouts keep touch controls at least 44 px. Camera following and normal frame updates keep the ghost aligned; resizing cancels held gestures.

Release **114 patches / 49 assets**, HTML **3,279,865 bytes**, SHA-256 `e0bfe63ddae1f5430cf0f80f7f17bd9745a5d0147d68fb96afbb441353d9b6c2`, marker `V11_82_TOUCH_BUILD_SKILLS`. All **259** preceding runtime/patch sources and all **49** bundled assets retain exact bytes, including the Astra and ground 4K textures. See [implementation and targeted evidence](reports/SHEEP_TOUCH_V11_82.md). Publication follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md): cohesive source, separate final deployment request and exact hosted-package confirmation.

## §E v11.81 · Building clearance, protected sanctuary and hidden hunters (2026-10-22)

House foundations and outlines now reach the real blocking footprint. Nearby face-to-face gaps show their measured width and a colored label: **red BLOCKED**, **cyan SHEEP ONLY**, or **gold BOTH**. Classification uses the native swept collision checks, surrounding visible structures and actual species radii. Exact lane entry points let sheep use fitting narrow passages even between navigation-grid lines. Default sheep need **0.54 m** and wolves **1.80 m**. The gold sanctuary boundary marks a **22 m no-build radius** on the default 256 m map; the whole structure must fit outside it. Both player placement and AI construction use this rule. Bots choose reachable outward bases instead of falling back to their central spawn.

Wolves are hidden and nonphysical during the countdown, with no perception, target memory, minimap markers or pre-release scent information. A waiting wolf role has no sheep/building vision. After release, bot hunting requires actual sightings; lost sheep leave only their last observed position. Default sheep speed rises from **5.4 to 6 m/s** and Astra hunters are **15.4% larger**, with collision radius increasing from **0.78 to 0.90 m**. The 106-mesh/274,980-triangle hunter and original 4K atlases remain. Captured-wisp crawl/leash/rescue behavior is retained.

Release **113 patches / 49 assets**, HTML **3,258,318 bytes**, SHA-256 `9fb46459d3ca870f766ff7c90c18a1649ffbfc68352da25c493bc5ffe284186c`, marker `V11_81_SHEEP_CLEARANCE`. All **257** previous patch/runtime sources and **49** assets preserve exact bytes. Details and targeted validation are in [the release report](reports/SHEEP_CLARITY_V11_81.md). Delivery follows [RELEASE_PROCESS.md](RELEASE_PROCESS.md): cohesive source commit, separate final deploy request, terminal production success and exact hosted-source/asset confirmation.

## §E v11.80 · Vast Wildwood, central starts and captive wisps (2026-10-22)

The default map is now **256 × 256 m**, **4× the previous playable area**. All eight sheep start **9.5 m from the central respawn sanctuary**, rather than around the outer map. The existing four-region roads/ground/minimap and 4K Astra hunters remain. Fine **0.15 m** pathfinding now uses direct clear trips and cached local windows for most obstructed routes in large maps, with an unrestricted fallback for longer detours.

Captured wisps crawl at **0.35 m/s**. They may drift **2.5 m beyond each side of the pen**; crossing that leash teleports the still-captured wisp to its own capture spot and clears its movement/rescue progress. Reaching the leash never revives a sheep. The existing other-living-sheep rescue/hold/protection behavior remains the only revival path. Native move controls and help text describe this behavior.

Release **112 patches / 49 assets**, HTML **3,243,526 bytes**, SHA-256 `a4b58b9da3991fdd10fee42c4fd18648c65a79932b0af69ceea1a117ce5f151d`, marker `V11_80_VAST_WILDWOOD_WISPS`. The new native scene has 196 editable actors, eight central sheep, three Astra hunters and nine map layers. All 255 preceding patch/runtime sources and 48 previous assets retain exact bytes. Targeted CPU/browser checks and publication evidence are recorded in [the release report](reports/VAST_WISPS_V11_80.md). Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and terminal production run under current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.79 · Moonbell Wildwood — larger Sheep Tag map (2026-10-22)

The default Sheep Tag starter is now **Moonbell Wildwood**, **128 × 128 m** versus the previous 80 × 80 m (**2.56× the area**). Four color-separated woodland regions — Pinewatch, Moonflower, Amberglade and Willowmere — surround open building glades, an octagonal road loop, cardinal/diagonal roads, four merchant plazas, four ponds and a central sanctuary with stone markers. Four genuine narrow stone passages admit sheep while hunters detour. The terrain and fog-respecting minimap share original **4096 × 4096 ground artwork**. There are **176 individually editable native actors** in nine map layers, retaining eight sheep and three 4K Astra hunters. Match timing, movement/combat rules and optional archive settings remain intact; the previous 80 m map is preserved as a separate source and remains loadable.

Release **111 patches / 48 assets**, HTML **3,222,398 bytes**, SHA-256 `f2d2c22aa4620f76407494767e27a4227c3d178af3f8a52f7fc736c6eb28e9ec`, marker `V11_79_MOONBELL_WILDWOOD`. All 253 preceding runtime/patch sources and 46 earlier assets retain exact bytes. Targeted desktop/phone-layout checks cover start validity, full map framing, all spawn/outer-road connectivity, four species-sized passages, native/portable save/load, generated floor scale, movement/construction outside the old boundary, terrain minimap and previous-map compatibility. Source/deploy status resolves through the final separate `DEPLOY_REQUEST.json` and its terminal production receipt. See [map design and evidence](reports/SHEEP_WILDWOOD_V11_79.md); delivery follows current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.78 · Astra hunters in Sheep Tag (2026-10-22)

Sheep Tag's `st-wolf` prefab now renders the complete **Astra · Comet Courier** model, with all 106 native meshes and the original 4096 × 4096 color/normal atlases. The three canonical hunters, newly spawned hunters and wolves reconstructed from older native project saves all use the same visual. Independent head, tail and four leg pivots connect the saved model to the existing walk and attack animations; geometry/materials and texture images are reused across instances. Logical wolf roles, IDs, names, teams, navigation/collision radii, combat, economy and map data are preserved. The independent editable Astra project remains available.

Release **110 patches / 46 assets**, HTML **3,152,424 bytes**, SHA-256 `234ddf6065f89438a3cabbcd9e3521d82fb08245830525131e3976d4f86b9ad4`, marker `V11_78_SHEEP_TAG_COURIER`. All 250 preceding runtime/patch files and 46 bundled assets are byte-preserved. Targeted local desktop/phone-layout checks cover loaded 4K maps, native spawn/save/reload, movement/four-leg gait, building attacks/head animation, sheep tagging and Stop/restart restoration. Deployment status and source commit resolve through the final separate `DEPLOY_REQUEST.json` and its terminal production run; owner device acceptance follows publication. See [integration evidence](reports/SHEEP_COURIER_V11_78.md). Delivery follows current [RELEASE_PROCESS.md](RELEASE_PROCESS.md).

## §E v11.77 · Astra, Comet Courier model project (2026-10-22)

New independent **Astra · Comet Courier** project and **New Model Project** starter. A celestial fox with sculpted ears/muzzle, four articulated legs, a flowing comet tail, travelling mantle, satchel and lantern is authored through native tools. Eight material regions use original 4096 × 4096 base-color and normal atlases. Saved atlas bindings support Undo; a textured GLB embeds real mesh/UV/material data and both 4K images. Six editable assemblies organise the model.

The existing 283-part festival model, all previous runtime/patch sources and 43 original assets are preserved. Release has 109 patches / 46 assets, marker `V11_77_COMET_COURIER_MODEL_PROJECT`. Exact bytes/SHA resolve through `source-manifest.json`; source/deploy commit and live status resolve through the final separate `DEPLOY_REQUEST.json` commit and terminal production receipt. Current delivery authority is `RELEASE_PROCESS.md` (§§§); targeted model checks precede direct-main source publication and the final dedicated deployment trigger. [Design and authoring](reports/COMET_COURIER_V11_77.md).

## v11.20 · anatomical head reconstruction

The owner rejected the round head foundation. A new native surface builds the skull, temples, cheekbones, jaw angles and chin from eleven editable sections, with a flatter facial mask, eye sockets and an integrated nasal profile. Facial contours are refitted and the neck extends into the jaw underside; the corrected legs and remaining body retain their prior data. Saved Apply/Undo and bounded JSON import support the new anatomy controls.

The native starter is `scenes/model-atelier-festival-anatomy-v11-20.swyrl.json`; 90 patches / 43 assets, marker `V11_20_ANATOMICAL_HEAD`. All 179 predecessor patch/runtime sources and 42 assets remain byte-preserved. Exact integrity is recorded in the manifest. Source/deploy commit and live status resolve through the final dedicated deploy request and terminal deployment/audit/native receipts. [Workflow and geometry evidence](reports/ANATOMICAL_HEAD_V11_20.md).

## v11.19 portrait/body gates

Reconstruct the exact 89-patch/42-asset source. Run both historical HD and corrected-calf CPU checks plus `model_portrait_polish_cpu.mjs` against the built HTML. Verify actual chin/nose geometry, warmth colors, historical defaults, fitted facial contour contact, invalid-fit rejection, neck contact, anchored wrists and unchanged calf/foot/creature data. Native UI acceptance includes portrait Apply/Undo, invalid imports and actual facial-curve fit/Undo/rejection. The full native recipe must reproduce the saved starter exactly. All 18 browser suites on both viewports remain required; the final dedicated deploy request follows validated merge, then exact hosted audit and native desktop/phone acceptance.

## v11.18 correction release gates

Rebuild the exact 88-patch/41-asset package, verify preservation of 175 predecessor patch/runtime files and 40 assets, then run `model_hd_geometry_cpu.mjs` and `model_reference_correction_cpu.mjs` against the built HTML. The latter checks the reported knee reversal, posterior calf placement, anterior shin restraint, Achilles taper, unchanged knee/ankle rings, real finite crown/wrap geometry, open wrap centers, sampling and saved iris colors with historical defaults. Repeat the native v11.18 recipe and require exact saved-model equality plus real save/reimport and desktop/phone multiview evidence.

The full 18-suite compatibility matrix retains36 suite/viewport pairs in 22 jobs. Native character checks include pigment Apply/Undo/rejected import and idle-to-neutral grounded-leg restoration. After merge, the final dedicated deploy request must reach terminal success; audit the exact served HTML/SOURCE and all 41 assets, then require both hosted desktop and phone native jobs to pass. [Workflow](reports/LEG_REFERENCE_CORRECTION_V11_18.md).

Workflow timing and retained coverage: [Engine CI timing](reports/ENGINE_CI_SPEED_2026_10_17.md). The long suites and hosted editor checks run desktop/phone independently; all viewport cases and final exports remain required.

HD motion clock correction: dense frames now advance by actual elapsed seconds, preserving pause/resume and the six-second end time. The earlier 80 ms-per-frame clamp stretched playback on software rendering and failed the animation completion gate; the HD clock now has a deterministic long-frame regression check as well as the unchanged native playback test. Historical unannotated scenes keep their existing clock behavior.

## v11.17 · HD character sculpt and native studio finish (2026-10-16)

The owner requested unrestricted high-definition quality. The new native starter refines the continuous portrait surface, integrated iris/pupil fibers and corneal highlights, thin eyelids and smiling lips, transported hair sweeps with a harmonious split-dye fringe, black woven pigtail wraps, embroidered curved garment panels, ribbed draped socks, welted leather shoes and pinched satin bows. Each ferret plume now has a continuous core beneath genuinely creased, overlapping paper leaves with cut edge thickness. Floating cheek/nose decorations and stacked sock-fold primitives were replaced with continuous surfaces.

Native **HD surface finish**, relief, compatible matching-spline application, **Fit trim to cloth**, and saved sampling controls are editable, undoable and validated during import. Physical materials, ACES studio lighting and clean **Render PNG · 2k** support close-up review. The HD starter has **283 editable meshes**, **1,619,108 measured triangles** in the complete set, **1,335,220 in the heroine** and **48,768 in the head**. These are generated buffer measurements, not a quality score or a device-performance claim. The lighter preview and standard detail presets remain available; HD is the saved default.

The saved scene was authored and reimported through real Model Atelier controls. All **173 predecessor patch/runtime files and 39 historical assets** remain byte-preserved. The current package has **87 ordered patches and 40 assets**. Sealed HTML: **2,582,080 bytes**, SHA-256 `623283cc9589fa166ea00f985350f55092606818ab6be4188302f256a0fdb854`. Native geometry checks, desktop/phone editor tests, the full compatibility matrix, merge, final dedicated deployment, exact hosted digest/all-assets audit and hosted editor workflow are separate release gates. Owner visual acceptance remains separate; UV texture painting and weighted skeletal skinning are still outside this release.

Repeatable authoring, measured evidence and art-review limits: [HD character workflow](reports/HD_CHARACTER_SCULPT_V11_17.md).

## v11.16 · facial contours and adjustable native mesh detail (2026-10-16)

Owner requested a much more detailed face and asked to verify the proposed 20k mobile triangle budget against UE4 guidance. The current heroine uses **92,028 triangles**, including **12,096 in the continuous head surface** (previously 77,444 and 1,944 respectively). Native nose bridge, eye socket and cheek controls shape the actual head vertices. Smooth jaw transitions remove the hard chin/cheek sampling discontinuity exposed by denser topology. Spline body surfaces, eyes, hair and garment panels have saved sampling controls, with a triangle-edge preview and exact selected/heroine/whole-set counts.

The optional mobile preset is **26,908 heroine triangles**, including **6,016 in the head**. The two independent paper ferrets and bunny retain **32,112 triangles** across both presets, so the complete sets are **124,140 close-up / 59,020 mobile**. The high detail preset is the saved starter. This is selectable native authoring detail; it is not automatic distance LOD or a measured physical-device FPS guarantee. Mesh sampling and continuous facial forms are independently editable, undoable and retained by native JSON/OBJ export.

Epic's [UE4.27 mobile performance guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-guidelines-for-mobile-devices?application_version=4.27) discusses about 500k triangles for the entire view on older iPad targets, rather than a 20k per-character rule. Its [optimization guide](https://dev.epicgames.com/documentation/en-us/unreal-engine/optimization-and-development-best-practices-for-mobile?application_version=4.27) emphasizes profiling target hardware and material/draw-call costs. Preset budgets here are project choices, not Epic character limits.

Native asset: `scenes/model-atelier-festival-detail-v11-16.swyrl.json`, saved and reimported through real Model Atelier controls; **301 editable meshes**, with all 85 prior patches/runtime sources and 38 historical assets preserved. The independent audit's asset list now includes the v11.15 and v11.16 native scenes. Seal: **2,501,987 HTML bytes**, SHA-256 `fd9deed8f22f5b111eadcb59501d47b00061bd4bd219bae6e8e894c82138c97a`, **86 patches and 39 assets**. Native desktop/phone, full compatibility CI, validated merge, the final dedicated deployment and exact hosted verification remain separate gates; owner visual acceptance remains separate.

Recipe and evidence details: [Native detail workflow](reports/CHARACTER_DETAIL_V11_16.md).

# §E v11.4 Prism Jester ferret fidelity · verified production (2026-10-15 CDT)

## v11.13 · native reference sculpt and independent living piñatas

Measured candidate seal: **2,467,619 HTML bytes**, SHA-256 `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8`; 83 ordered patches and 36 assets. Native model-save authoring, twenty focused desktop/phone cases and twelve phone/desktop-site/multiview framing checks passed; full independent release CI remains required.

The owner-provided festival turnaround now drives a new 275-part native starter: sculpted facial planes and almond eyes, swept dyed hair, asymmetric layered outfit, bare anatomical legs and socks, two three-dimensional tissue-paper ferrets attached to actual hair sockets, and a separate paper bunny. The living-model inspector provides reversible attach/detach, per-model flex, saved transform keys, a six-second transformation preview, independent model JSON exports and actual rendered OBJ export. Whole model history, native save/load and the measured geometry profiler remain available. Default generated geometry is approximately 82,396 triangles, measured from the buffers rather than guessed from mesh count.

Candidate branch `feature/model-reference-sockets`; source and hosted baseline `43dd6db` / v11.12, 2,352,463 bytes, SHA-256 `76051c90fda3b9f32fef582977fb8af872edc14de44781e253f90ed3f0f9bc6f`. The new release appends patch 83 and native asset 36. All 82 predecessor patches/runtime modules and 35 packaged assets are preserved. The exact earlier v11.12 default remains independently loadable for its full regression.

Research, native format, controls and limitations: [Festival reference workflow](reports/FESTIVAL_REFERENCE_WORKFLOW.md). This is an original editable geometric study; production retopology, UV painting and skeletal skin weights are not implemented. Full desktop/phone compatibility, final dedicated deploy, exact hosted audit and the owner's visual response are separate gates. This candidate section does not claim publication before those checks pass.

> **v11.7 candidate (not yet live):** Replaces unconvincing continuous piñata tubes with 36 capped, faceted layered discs per ferret, direct grip onto the heroine's dyed braids, more explicit facial/garment/rear volumes. Full CI, deployment receipt and owner front/side/back evidence required. Prior v11.6 receipts below are historical.

## v11.5 candidate · Festival Model Atelier — release pending

The new 539-part original festival character variant keeps historical 253- and 303-part editable native scenes intact. The 75th governed patch adds editable loft path/radius control, raises the Model Atelier capacity to 1,200 parts and JSON import allowance to 8 MB; the new native variant is packaged independently. The exact candidate rebuilt in GitHub Actions [#38747495949](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38747495949) at 2,253,004 HTML bytes, SHA-256 `325f286e0dd3166e34bff57b1e721a6e244089a02cc01d33f8bc3025bace324a`, marker `V11_5_FESTIVAL_LOFT_ATELIER`. **This is source candidate evidence, not a hosted v11.5 deployment confirmation.** Full legacy browser CI, integration review, final §E manual trigger, independent hosted audit and owner visual acceptance are distinct gates. Previous v11.4 production receipts below remain historical evidence.


- [x] [PR #171 merged](https://github.com/kaministrator999-ui/Swrlzkamico/pull/171) at `0540cfbfc29129548941881f659f26a767038ed3`.
- [x] [17/17 native desktop/phone browser tests passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364328), including 303 editable objects, 2 organic loft bodies, two ferret heads, save/load and original Maul/Sheep/anime regressions.
- [x] All five source workflows passed: [authored anime](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364335), [native cinematic](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364400), [cel layers](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364349), [story staging](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364326), and browser matrix above.
- [x] Sealed `V11_4_PRISM_FERRET_FIDELITY`, 74 patches, 30 packaged assets (including original 253-part v11.3 scene), **2,197,108 HTML bytes**, SHA-256 `40d1e985bd3754b7a2996e6be14056be9c22164995d83b84ad253b4ae7a24658`.
- [x] [Dedicated guarded deployment #38729222214](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729222214) **SUCCESS** on source trigger `2dba7e6da30fef16c8bb1f4a35f979bcfbffb9b4`, Space revision `f88b57b39893f556e380cef7c279d93860800a95`.
- [x] [Independent hosted audit #38729291039](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729291039) **SUCCESS** (`HOSTED_AUDIT_SCOPE=current-requested-release`, `PUBLISHED_VERSION=v11.4`, `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`) proving the exact 2,197,108-byte HTML and all 30 packaged assets.
- [ ] Human owner visual acceptance and advanced sculpt/UV/rig/animation remain outstanding.

---

# §E v11.3 Model Atelier · verified production (2026-10-14 CDT)

- [x] [PR #167](https://github.com/kaministrator999-ui/Swrlzkamico/pull/167) merged at `abfe8a495b3a7c166f2bebe9151887b2cef6b807`.
- [x] [17 of 17 real browser suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608237), each using native desktop and phone layouts, including Model Atelier viewport, edits, save/load, OBJ/JSON export, re-open touch hit-target, and all historical scene regressions.
- [x] Five additional candidate workflows passed: [authored source](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608236), [cinematic source](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608235), [camera staging](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608243), [cel layers](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608277), and browser matrix above.
- [x] Sealed 73-patch / 29-asset artifact, 2,175,921 bytes, SHA-256 `a2ec94f418f294ea5ebd50363833d37025a6e6cc804732116a7cb927d0b069db`. Native 253-part original Prism Jester model remains authorable; no extracted game files or claims of exact likeness.
- [x] [Guarded production deployment #38677061503](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677061503) **SUCCESS** on final request SHA `44a594f534c92c723079adcb33d8a80962bc7e0f`.
- [x] [Independent hosted audit #38677099743](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677099743) **SUCCESS**: source SHA-256 `a2ec94f418f294ea5ebd50363833d37025a6e6cc804732116a7cb927d0b069db` and all 29 asset bytes independently matched, `HOSTED_AUDIT_SCOPE=current-requested-release`, `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`.
- [ ] Optional future advanced sculpting, UV texture painting, rigging, and animations are not implemented.

---

# Verified v11.2 Frostveil flying-builder release

**Verified live v11.2 (2026-10-14 CDT):** [PR #159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159) merged as `b3ef6130f0d9685018debb06fcdd4ef2912d9f6e`. Six candidate Forge workflows and all 16 native desktop/phone suites succeeded on `716a2bc81b01c79b65ed7771eb3dc794248ce55b`. [Dedicated deploy #38668840620](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668840620) and [independent hosted audit #38668893410](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668893410) both completed SUCCESS on trigger `e47c027816fa5029f0c27ac273e040ae62fd1a5f`. Space revision: `ef8f325b2d8d45cf67da2c54bc4f8e3455df263e`. Published binary: **72 patches, 28 assets, 2,097,069 HTML bytes**, SHA-256 `1fab5e61f2065c02a56658c6e8e8ef999eb525ac16c373b310826ca970e10e59`, marker `V11_2_MAUL_FLIGHT_GLACIAL_ART`. Exact served HTML, SOURCE receipt, and all 28 assets matched. Owner gameplay acceptance remains separate.

- Projects → Frostveil Maul selects independent native `scenes/maul-frostveil-flight.swyrl.json` with nine builders and preserved 30-wave layout; scene launch and downloadable pack are checked for matching profile and builder identities.
- Flight movement uses 15 world units/s, 3.25 hover altitude, crosses terrain/towers, then builds underneath after legal footprint, route, territory and gold rechecks; legacy walk-v1 imports remain unchanged.
- Glacial procedural art is non-destructive; preserve earlier native games, recorder and scene packages. Physical congested creeps, special units, endless mode, Mirror Survival, themed builders, and native Maul creator remain unimplemented backlog.
- Separate signed-in human gameplay acceptance is not claimed by the automated release evidence.

---

# Historical verified v11.1 Maul walk-to-build acceptance

- Default grouped Frostveil starter must show no wall construction option.
- A tower command must queue the selected sector builder, move across actual traversable cells and complete only upon reaching an adjacent footprint.
- Gold must not be deducted while the order is pending. Revalidate gold, occupancy and shared routes upon completion.
- Fully reserved enemy entrance pads, every gate and the shared exit must reject construction.
- Cancel/replace movement orders and Pause/Stop must not produce phantom towers.
- Earlier Maul saved project variants, Sheep Tag, recording import/export and the other §E projects remain compatible.
- Seal 71 patches, 27 unchanged assets, all six checks, desktop and phone gameplay, then exact hosted audit before claiming deployment.

**Release acceptance received:** [six-workflow exact-source candidate validation](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38643766910) (all sixteen native desktop/phone browser suites SUCCESS); [dedicated Forge deployment #38646048742](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38646048742) and [independent live-source/all-27-asset audit #38646122359](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38646122359) both terminal SUCCESS. Integrated source `bbe56716867e046d3a4f887aa2f5829f25709cd1`, published `v11.1`, sealed HTML 2,027,727 bytes, SHA-256 `c96e5fea45bd316750e2fcc60ff1cbd96feadd6a90a56a5667dddad0aaf21121`. Historical imports and earlier starters passed automated regressions. Independent owner manual/gameplay acceptance remains unclaimed.

---

## Current v11.0 candidate · Compressed recordings and clear Maul spectator

Frostveil Maul Play-run review now renders recorded snowfields, water, cliffs, tower families, maze walls, builders, creeps and the exit as distinct visual layers, with camera framing adjusted to the actual Maul map dimensions. The original Sheep Tag recorder presentation and recording schema remain intact. A new **Export compressed (.json.gz)** control uses lossless browser-native gzip; the recorder also imports these gzip files with format validation and a bounded 256 MiB decompressed limit. Existing raw JSON, text, HTML spectator, camera, timelines, events and saved projects continue to work.

The add-only release brings the engine to **70 governed patches** and keeps **27 packaged assets**. All 69 predecessor patches and their runtime files are unchanged. Candidate code requires package, browser, CPU and exact hosted release verification; these notes are not publication evidence.

# §wyrl§ Engine v10.9 candidate · Story action and effect acceptance

## Current v10.9 candidate · Story actions and an animated first episode

Open **Projects → Ghosts in Different Forms**, or `?project=anime-ghosts-ep01`, then use **Play** or **Watch Episode 01**. Kami and §wyrlz now act through the story: greeting and reaching, recoiling and bracing, casting, writing, stepping, hovering and recovering. Their arm chains, attached full-length staff, heads and costume depth pieces move together. Short dialogue windows leave room for a character to listen and react between lines. Kami's first attempt to burn a doorway nearly erases the library and makes §wyrlz fade. They recover by joining Kami's light with §wyrlz's written names, build a doorway that remembers them and step toward a world that answers, ‘Welcome back.’

The native **Animation Studio** adds **Story Actions** and **Story effects**. Saved action clips control character, action, time, duration, strength and side; effect cues control page motion, bursts, ink and a portal. Preview Frame, editor Play and Watch sample the same saved story time, including reverse and fast playback. Disabling an overlay leaves the underlying limb, face and scenery keys available. Native Undo/Redo and Save/Load retain the clips and cues separately from those keys.

The current native export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`. It retains **70 actors, 11 layers, eight contiguous story beats, nine stage/camera tracks, 134 seconds**, the 12-second book opening and the fitted full staff/socket/relief settings. Its native save contains 175 stage/camera keys, 468 limb/face keys, 383 scenery keys, 36 action clips and 11 effect cues. `project.animePerformance` uses `anime-performance-v1`; `project.animeStoryEffects` uses `anime-story-effects-v1`. The previous full-staff scene and every earlier project/artwork asset remain packaged unchanged for import.

Publication appends `patches/v10_9_episode_story_actions.py`, for **69 governed patches and 27 assets**. All 68 published patches, previous runtime modules, 26 predecessor assets and payload chunks remain byte-identical. Artifact: `swyrl_engine_v10_9.html`; marker: `SWYRL_ENGINE_DEPLOY_MARKER: V10_9_EPISODE_STORY_ACTIONS`. The starter count remains **seven**.

Acceptance requires all **six engine workflows**, **sixteen desktop/phone browser suites**, thirteen sealed Sheep Tag geometry cases, seventeen preserved Maul CPU cases, twelve classic-layout CPU cases and fifteen grouped-spawn CPU cases. The new episode suite checks the saved action/effect data and actual native authoring, Preview/Play/Watch movement, playback controls and lifecycle on both layouts. Completion requires the final dedicated `DEPLOY_REQUEST.json`, terminal successful deployment and exact hosted HTML/SOURCE/all-asset audit. Candidate documentation does not assert publication before those checks pass.

## Episode performance acceptance

`tests/episode_performance_package.py` verifies the saved native 70-actor/11-layer project, contiguous eight-beat story, all 175 stage/camera keys, 468 rig keys and 383 scenery keys, 36 action clips and 11 effect cues. It requires both mages, all eight action kinds, all four effect kinds and finite timing/transforms. Character and scenery actor definitions, editor layers, socket connections, full-staff/rest fitting, relief and the 12-second opening match the preserved full-staff export. Every one of the 26 published media assets is checked against its v10.8 byte count and SHA-256.

`tests/episode_performance_playwright.mjs` must emit each committed unique `EPISODE_PERFORMANCE_CASE_PASSED desktop|mobile <case>` line, one `EPISODE_PERFORMANCE_SOURCE_SHA256 <layout> <sealed SHA>` per layout, and `EPISODE_PERFORMANCE_DESKTOP_PASS`, `EPISODE_PERFORMANCE_MOBILE_PASS`, `EPISODE_PERFORMANCE_ALL_VIEWPORTS_PASS`. Exact source reconstruction, real native controls and both viewport completions remain required. Echoed commands and static screenshots do not replace actual playback/authoring checks.

## Historical verified v10.8 · Grouped Maul rounds and visible phone placement

The v10.8 release is verified live: merged source `d371df09a37d44d40d9b05425e01f977eabfa62a`, final trigger `507d11b93e7af81359614e6d56d98a35adbf0b6b`, [deployment 38567626510](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38567626510) and [hosted audit 38567696344](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38567696344). It seals **68 patches, 26 assets and 1,905,846 bytes**, SHA-256 `775d7dfab363da120c2c779b5d8d129d7c75ee6a9681911958bdb9cef3fa1e3e`. All six engine workflows, fifteen desktop/phone browser suites and the four sealed CPU suites passed, followed by native live desktop and phone gameplay and recorder exports. Marker: `V10_8_MAUL_BATCH_PLACEMENT`; artifact: `swyrl_engine_v10_8.html`.

Each cooperative Maul round releases three scattered groups at 0, 2.5 and 5 seconds. The saved `classic-v2` map adds `maulSpawnStyle: "grouped-v1"`; its native `scenes/maul-frostveil-groups.swyrl.json` starts with no authored towers. Phone placement lifts the complete ghost and footprint 140 CSS pixels above the finger. These receipts certify v10.8; the story-action revision requires its own deployment and exact hosted audit.

## Historical verified v10.7 · Classic Maul map layout

The v10.7 release is verified live: merged source `c80e0b98e33ad2c68943415d8c767f836f849f0f`, final trigger `c26630d0f8fce2ba5f3c10c2edfec6e92cf5b109`, [deployment 38513639622](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38513639622) and [hosted audit 38513700470](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38513700470). It seals **67 patches, 25 assets and 1,833,206 bytes**, SHA-256 `c3f24f05ba745a5e834e964d7e06f0637b57b1115fe242bc86d7920738984ddc`. All six engine workflows, fourteen desktop/phone browser suites, twelve classic-layout CPU cases, seventeen preserved Maul CPU cases and thirteen Sheep Tag geometry cases passed, followed by native live desktop and phone gameplay and actual recorder exports. Marker: `V10_7_CLASSIC_MAUL_MAP`; artifact: `swyrl_engine_v10_7.html`.

This release established three long northern snowy bays, a broad crossbar, winding lower defense lanes, editable route turns and one shared ship exit. Its original `scenes/maul-frostveil-classic.swyrl.json` remains packaged unchanged for import. These receipts certify v10.7; the grouped-spawn and placement revision requires its own deployment and exact hosted audit.

## Grouped Maul round and placement acceptance scope

`tests/maul_batch_playwright.mjs` is the fifteenth browser suite. It must use native Projects, Play, wave controls, physical canvas taps/drags and actual recorder downloads in both desktop and phone layouts. Required evidence covers the grouped default and empty defender starts, native Save/Load of its profile, whole-group scatter and delayed arrivals, protected entrance placement without a charge, visible touch placement with release at the displayed footprint, cancelled gestures, camera stability, Pause/Stop restoration and captured group state/events in offline review.

Each committed browser case prints actual `MAUL_BATCH_CASE_PASSED desktop|mobile <case>` stdout, bounded by `MAUL_BATCH_SOURCE_SHA256 desktop|mobile <sealed HTML hash>` and `MAUL_BATCH_DESKTOP_PASS`, `MAUL_BATCH_MOBILE_PASS`, `MAUL_BATCH_ALL_VIEWPORTS_PASS`. `tests/maul_batch_cpu.mjs` extracts the grouped helper and its dependencies from the sealed HTML through `SWYRL_MAUL_BATCH_HTML`; it must print the exact committed case set between `MAUL_BATCH_CPU_SOURCE_SHA256 <hash>` and `MAUL_BATCH_CPU_ALL_CASES_PASS <count>`. Required scenarios include timed groups, preserved campaign totals/combat, seeded scatter, clear reserved entrance cells, authored-tower avoidance, atomic retry on congestion, valid route stages, runtime restoration and legacy unflagged behavior. Echoed commands are not proof.

`tests/maul_batch_package.py` independently validates the 68-patch/26-asset package, the grouped native profile, all nine defender/spawn/gate connections, six editable route turns, shared exit, six populated layers and empty initial tower spaces. Every reconstruction/package workflow runs this check. The hosted audit validates the exact served grouped scene against its committed source as well as all preserved assets.

## Preserved v10.7 classic Maul layout acceptance scope

`tests/maul_layout_playwright.mjs` is the fourteenth browser suite, with **16 distinct cases per layout**. It uses the actual sealed editor and native visible controls on desktop and phone. Required evidence covers the Projects/direct route, upper bays and connected lower funnel, nine builders, one shared exit, native rules and Save/Load, real ground placement and above-finger preview, cliff/protected/occupied/closed-route rejection without charge, actual tower-surface selection, range/priority/upgrade/sell, linked ground routes, air bypass, waves and leaks, frozen Pause, terminal outcomes, Stop restoration and actual recorder exports. Stopped authored fixtures are allowed; runtime, renderer, economy, AI and combat remain native.

`tests/maul_layout_cpu.mjs` extracts the actual `MAUL_LAYOUT_CORE` from reconstructed sealed HTML through `SWYRL_MAUL_LAYOUT_HTML`. Scenarios cover the classic map geometry, ordered upstream/crossbar/funnel routes, legal maze detours, protected/blocked/active-enemy route preservation, air bypass, malformed layouts, legacy map compatibility and native campaign outcomes. CPU runs against an unsealed module alone establish development evidence rather than release proof.

Every unique committed layout browser case must appear as actual `MAUL_LAYOUT_CASE_PASSED desktop|mobile <case>` stdout, with `MAUL_LAYOUT_SOURCE_SHA256 desktop|mobile <sealed HTML hash>`, followed by `MAUL_LAYOUT_DESKTOP_PASS`, `MAUL_LAYOUT_MOBILE_PASS` and `MAUL_LAYOUT_ALL_VIEWPORTS_PASS`. Every unique CPU case must appear as `MAUL_LAYOUT_CPU_CASE_PASS <case>`, bounded by `MAUL_LAYOUT_CPU_SOURCE_SHA256 <sealed HTML hash>` and `MAUL_LAYOUT_CPU_ALL_CASES_PASS <count>`. Decoded CI receipts require the committed exact case sets on the tested source head alongside all predecessor suites and all four CPU suites. Echoed command text is not pass evidence.

`tests/maul_layout_package.py` independently checks the current 68-patch/26-asset package and the unchanged v10.7 fixture and native scene semantics: nine distinct builder/spawn/waypoint connections, six distinct editable lower-funnel route turns, one exit, snowfield and shore-water actors, raised cliffs, seven populated native layers and finite transforms. Every engine verification workflow retains this check, including semantic validation of the exact served classic map asset during the hosted audit.

## Preserved v10.6 Maul regression scope

`tests/maul_playwright.mjs` is the thirteenth browser suite. It must exercise the actual sealed editor and its native controls in desktop and phone layouts. Required evidence covers the Projects entry followed by native import of the preserved v10.6 fixture, native authored map and settings Save/Load, real ground placement and above-finger preview, footprint/closed-route rejection without a charge, selected tower range/targeting/upgrade/sell, all-sector camera/builders, native wave combat and leaks, frozen Pause, Stop restoration, and Maul state/events in actual recorder downloads and offline review. Test fixtures may author a stopped project; runtime state, combat, economy, AI and renderer must remain native.

`tests/maul_cpu.mjs` must extract the actual `MAUL_CORE` from the reconstructed sealed HTML through `SWYRL_MAUL_HTML`. Its required scenarios cover linked entrance/gate/exit routes, blocked and reserved footprints, existing-enemy route preservation, successful maze detours, deterministic waves, air bypass, tower capabilities and target priorities, upgrades/refunds, support, natural wins/losses and malformed map/rule preflight. CPU acceptance against a separate unsealed source file does not establish release proof.

Every unique committed Maul browser case must appear as actual `MAUL_CASE_PASSED desktop|mobile <case>` stdout, followed by `MAUL_DESKTOP_PASS`, `MAUL_MOBILE_PASS` and `MAUL_ALL_VIEWPORTS_PASS`. Every committed CPU case must appear as `MAUL_CPU_CASE_PASS <case>`, bounded by `MAUL_CPU_SOURCE_SHA256 <sealed HTML hash>` and `MAUL_CPU_ALL_CASES_PASS <count>`. The final decoded receipt requires those exact case sets on the tested source head, in addition to all twelve predecessor browser suites and all thirteen Sheep Tag geometry cases.

## Historical verified v10.6 · Frostveil Maul tower defense

The v10.6 release is verified live: merged source `52862f6a2f8a869d21a03103888b4a094ad19969`, final trigger `6200148fcc7c4ba83bfe76883b4fd49c7d20c53f`, [deployment 38434348748](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38434348748) and [hosted audit 38434414319](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38434414319). It seals **66 patches, 24 assets and 1,748,442 bytes**, SHA-256 `01d7fff6e2a943a326e4582670640d60eec78475c75ab12e16d92c12ee2a9843`. All six engine workflows, thirteen desktop/phone browser suites, 17 Maul CPU cases and 13 Sheep Tag geometry CPU cases passed, followed by native live tower placement/selection, waves, Pause/Stop and actual recorder exports on desktop and phone. Marker: `V10_6_MAUL_TOWER_DEFENSE`; artifact: `swyrl_engine_v10_6.html`.

The cooperative starter introduced nine linked sectors, thirty waves, shared lives, tower mazes, upgrades, air/boss rounds, optional support and native rules authoring. Its original `scenes/maul-frostveil.swyrl.json` remains packaged unchanged. These receipts certify v10.6; the revised classic map requires its own deployment and exact hosted audit.

## Historical verified v10.5 · Editor play-run recorder

The v10.5 release is verified live: merged source `6da367913c0eecc89c67a4976c3db407d851da15`, final trigger `e3b252b6850dfd84824563d1209333930321b268`, [deployment 38344147035](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38344147035) and [hosted audit 38344188938](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38344188938). It seals **65 patches, 23 assets and 1,594,471 bytes**, SHA-256 `cd3b50f06d3a802c025b3e530e743446d284633961bff0dacd46a656eb7e8ace`. All six engine workflows, twelve desktop/phone browser suites and 13 geometry CPU scenarios passed, followed by native live recorder downloads on desktop and phone. Marker: `V10_5_SHEEP_RUN_RECORDER`; artifact: `swyrl_engine_v10_5.html`.

The opt-in recorder introduced by v10.5 works across native starters and custom projects. Full capture records each observed Play update; 10 Hz and 2 Hz settings offer smaller state logs while retaining timed commands/events. It retains the starting map, actual seed, hierarchical object/limb poses, camera, input, health/lifecycle and game state. After Stop, the latest three runs can be scrubbed through a spectator schematic, object-follow view or recorded camera and exported as JSON, text or offline HTML. Simulate creates no recordings. Exports preserve a run beyond the current tab; the viewer reconstructs captured states rather than rerunning gameplay or exporting a rendered video.

## Existing recorder regression scope

`tests/sheep_run_playwright.mjs` is the twelfth browser suite. It must pass these **16 distinct cases** in both desktop and phone layouts against the sealed artifact. This is the required scope; passed results come from actual suite stdout and its `receipt.json`.

| Case | Required behavior |
|---|---|
| `v10_9_source_native_starter_and_default_off_checkbox` | Current marker/source and native starter load; recording starts disabled. |
| `disabled_logging_creates_no_run_and_preserves_native_map` | Native Play without recording creates no run and preserves the authored map. |
| `editor_run_preferences_are_excluded_from_native_and_portable_maps` | Settings remain device preferences outside both project formats. |
| `play_locks_review_and_settings_and_keeps_hidden_wolves_out_of_player_hud` | Active Play blocks review/settings and retains player fog. |
| `real_canvas_move_records_world_pose_limbs_camera_and_original_geometry` | Actual canvas movement captures spatial state, poses, camera and object catalog. |
| `real_build_at_feet_records_runtime_house_economy_and_rejected_command` | Native self-construction and rejected commands retain their outcomes and economy. |
| `pause_freezes_log_time_and_resume_keeps_the_same_run` | Pause freezes simulation time; resume continues the same recording. |
| `stop_seals_full_final_world_before_restoring_authored_native_map` | Stop preserves the final runtime world before native restoration. |
| `native_json_spatial_text_and_escaped_self_contained_offline_html_downloads` | Actual JSON/text/HTML downloads retain evidence; escaped HTML works offline. |
| `restart_allocates_a_new_run_and_retains_prior_completed_history` | Restart creates a separate identity and retains finished history. |
| `native_win_finalizes_once_and_keeps_the_winning_final_state` | Native victory finalizes once and retains the winning state. |
| `json_import_history_and_native_scrubber_review_without_editor_mutation` | Imported/history review and timeline seeking preserve the editor map. |
| `seeded_actual_gameplay_has_identical_logging_on_and_off_results` | The recorder does not change seeded native gameplay results. |
| `full_tenth_and_half_second_cadence_controls_and_final_native_restoration` | All three cadence settings work and Stop restores native state. |
| `all_seven_native_project_builders_support_recording_toggle_pause_stop_and_review` | Every native starter supports enable/disable, Play, frozen Pause, Stop and spectator review. |
| `imported_custom_projects_use_the_same_engine_recorder` | Imported custom projects capture and finalize through the same native Play lifecycle. |

Acceptance stdout must include each unique `SHEEP_RUN_CASE_PASSED desktop|mobile <case>` line and `SHEEP_RUN_DESKTOP_PASS`, `SHEEP_RUN_MOBILE_PASS`, `SHEEP_RUN_ALL_VIEWPORTS_PASS`. The receipt must contain two passing viewport records with these same 16 cases. Echoed commands are not pass evidence.

The fifteen other browser suites and `tests/sheep_lanes_cpu.mjs` remain required. All **13 actual sealed-source geometry cases** continue to cover builder ejection on four sides and all five construction kinds, blocked/no-exit rejection, flush or sheep-only house lanes, following/head-on sheep traffic, wolf body separation, reachable-sheep priority on ground and raised routes, free rescue landings, and overlapping-start preflight. Older runtime modules, all 68 older patches and all 26 predecessor assets must remain byte-identical.

Production acceptance still requires the exact final-trigger dedicated Actions run to succeed, followed by matching live `SOURCE.json`, current marker, normalized complete HTML and every packaged asset. The current v10.9 candidate requires its own deployment and exact hosted audit.

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

Historical v10.1 source evidence also includes native Save Project authoring with zero editor validation issues or warnings and 32 portable-creator CPU checks covering transforms, clean exports, malformed imports, blocked spawns and pen boundaries. v10.2 requires fresh acceptance against its own sealed source.

## Historical verified v10.0 · Sheep Tag Starter

The v10.0 release is verified live: [PR #106](https://github.com/kaministrator999-ui/Swrlzkamico/pull/106) merged engine source `a06c89ed9e6cd65737de111efc11cac268519449`; [deployment 38174454216](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174454216) and [hosted audit 38174501776](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174501776) succeeded on final trigger `87b6a4be9319be30ac22b99212d773a289d2b199`. It seals **60 patches, 1,290,101 bytes**, SHA-256 `abcab023bbec0b5cacc72d7b845096060feb56418ab12b9eacee62bf9b7bf8c4`, and 22 assets. All six engine CI workflows and all nine desktop/phone browser suites passed, followed by fourteen live gameplay cases on each layout. The native Save Project map retains 66 actors in four populated layers, six sheep, two wolves, one pen and four merchants. Editor validation reported zero issues and warnings. Marker: `V10_0_SHEEP_TAG_STARTER`; artifact: `swyrl_engine_v10_0.html`. These receipts certify the released v10.0 starter.

## Historical verified v9.9 · Episode Shuttle Controls

The v9.9 release is verified live: [deployment 38150826816](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150826816) and [hosted audit 38150874160](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150874160) succeeded on final trigger `a382b4ea577c0a72f0223ef2aa4aad650121a5bf`. Merged engine source `4eb6021976e999bb84b9b915d2a9546cdb569a18` seals **59 patches, 1,139,928 bytes**, SHA-256 `60dfa8da434eaa6cfe578f441a93be1fb9139676933e985a19919c13938b60c9`, and the unchanged 21 media assets. All eight desktop/phone browser suites and six engine checks passed. Watch Episode Rewind/Fast forward buttons cycle **2× → 4× → 8× → normal 1×** beside the chapter skips. Pause, scrubbing and chapter changes preserve signed speed; boundaries pause at normal speed, and Replay/Stop/Explore/close/new screening restore 1×. Player speed remains session data. Marker: `V9_9_EPISODE_SHUTTLE_CONTROLS`; artifact: `swyrl_engine_v9_9.html`. These receipts certify v9.9; v10.0 requires its own validation and final deployment.

## Episode shuttle acceptance

`tests/episode_transport_playwright.mjs` is the eighth desktop/phone browser suite. It uses the actual player buttons and independently measured story-time/frame changes. Verify both directional cycles and their visible/accessible speed state; pause/start/end behavior; scrubbing and chapter changes; Stop, Explore Set and close/reopen; normal editor Play; unchanged project/history data; and shared camera, character, scenery, opening and caption frames while seeking backward. The seven historical suites retain their existing assertions and tolerances.

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


The 54th and 55th patches retain the staff mount and per-piece relief. The 56th, `patches/v9_6_natural_staff_painted_faces.py`, retains the compact grip and painted facial features; the 57th, `patches/v9_7_ornate_staff.py`, retains socket-attached shaft ornament. The 58th, `patches/v9_8_full_length_staff.py`, integrates the full painted staff and native preset; artifact `swyrl_engine_v9_8.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_8_FULL_LENGTH_MAGE_STAFF`. The 59th, `patches/v9_9_episode_shuttle.py`, adds signed episode shuttle playback; v9.9 artifact `swyrl_engine_v9_9.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_9_EPISODE_SHUTTLE_CONTROLS`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging contains nine episode scene JSON exports, the historical episode HTML and eleven PNGs, for twenty-one media assets. The 60th patch, `patches/v10_0_sheep_tag.py`, adds the separate native Sheep Tag starter; v10.0 artifact `swyrl_engine_v10_0.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V10_0_SHEEP_TAG_STARTER`. The native meadow map raised the v10.0 package to 22 assets. The 61st patch, `patches/v10_1_sheep_tag_archive.py`, adds the verified archive rules and creator. The 62nd, `patches/v10_2_sheep_touch_placement.py`, adds double-tap sheep building selection and ground placement guides; `swyrl_engine_v10_2.html` and `V10_2_SHEEP_TOUCH_PLACEMENT` identify the historical v10.2 release with the same 23 assets. The 63rd patch retains touch aim above the finger, the 64th retains house lanes and physical creature traffic, and the 65th adds the opt-in Play-run recorder and post-Stop review. The 66th adds the separate Frostveil Maul tower-defense starter, with its native scene as the 24th packaged asset. The 67th reshapes that starter around the classic upper bays, crossbar and shared ship funnel, with a new native scene as the 25th asset. The 68th adds scattered grouped arrivals, visible phone placement and an empty default build area; its separate native map is the 26th asset. The 69th adds the animated story and native action/effect editors; the new performance export is the 27th asset.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`; the full-staff export remains preserved for import. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Saved per-character rest layouts, 468 limb/face keys, 383 scenery keys and the action/effect overlays remain independent. The v9.6 natural-grip, v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all eleven artwork PNGs and the historical episode HTML.

`tests/character_relief_playwright.mjs` adds desktop/phone acceptance for all piece sections, actual front/back/edge depth, pose-driven cloth and armor motion, anchored sockets and facial surfaces, native controls, Undo/Redo and fresh-context Save/Load. `tests/socket_emergence_playwright.mjs` adds desktop/phone acceptance for page-emergence progress, snapped socket contact during rotation, the visible staff hand, native connection authoring, Undo/Redo, Save/Load and shared Play/Watch rendering. The existing native cinematic, storybook authoring, character rig, depth theatre and character alignment suites remain required. Reconstruction checks all 59 governed patches; packaging compares all twenty-one media assets against committed source bytes and SHA-256.

`tests/character_relief_playwright.mjs` owns full-staff acceptance: independent PNG pixel and geometry checks, uninterrupted painted crest-to-foot continuity, hand-wrap depth, saved rotations and body/socket fitting. It must exercise **Use full-length staff**, one-transaction Undo/Redo, native Save/Load and shared Preview/Play/Watch rendering, and retain the original/custom-atlas fallback. The unchanged socket/emergence suite continues to check the actual cylinder, mounted staff pixels and sockets through resizing and Undo. The v9.7 geometry/ornament checks remain applicable to historical natural-grip projects. The existing seven suites remain required alongside the new episode transport suite.

Pose, grip and effects references: [PoseMyArt’s male casting-spell pose](https://posemy.art/magic-poses/male-casting-spell-pose/2396/) informs the staff silhouette and bent elbow; [Clip Studio Tips](https://tips.clip-studio.com/en-us/articles/8226) informs the opposing thumb and curled fingers; [Riot’s VFX style guide](https://nexus.leagueoflegends.com/en-us/2017/10/dev-leagues-vfx-style-guide/) informs the clear silhouette and restrained effects. The native fitted rig, painted atlases and particle renderer use original project content.

- [ ] Inspect the full painted staff on desktop and phone, including its uninterrupted crest-to-foot artwork, connected grip, depth ordering and attachment through poses, native Play and Watch.
- [ ] Use the native full-staff preset, edit Staff artwork/socket fitting, then verify one-transaction Undo/Redo and native Save/Load.
- [ ] Verify original-grip and imported-atlas projects retain their saved hand/body fitting and prop sockets.
- [ ] Complete desktop/phone full-staff proportions, natural grip, painted-face and per-piece section-depth acceptance with visual inspection.
- [ ] Compare actual face pixels at one fixed story time and camera before editing and after Undo; also cover direct seeks, rebuilt rigs and fresh-context Save/Load.
- [ ] Load the preserved v9.5 staff-grip and v9.6 natural-grip exports, then a v9.8 native Save Project export; verify each retains its own grip/staff-art profile, fitted pose and prop socket alignment.
- [ ] Verify finite, bounded staff-head motes, exact-time seek determinism, shared Play/Watch attachment, and hiding/fading through the Effects layer.
- [ ] Complete all five existing native cinematic, Studio, rig, scenery and body-fit regressions.
- [ ] Seal the generated artifact and pass Node/Python syntax plus remote engine CI.
- [ ] Follow the exact final source/trigger deployment to terminal success.
- [ ] Verify the current marker, normalized served HTML, SOURCE receipt, all fourteen scene exports, screening HTML and all eleven PNGs against committed source.

The verified v10.8 source and production receipts are recorded above. The current v10.9 candidate requires its own sixteen-suite desktop/phone browser matrix, six engine workflows, all four sealed CPU suites, final dedicated deployment and exact hosted package audit.


---

# Historical verified §wyrl§ Engine v9.3 · Connected Character Pieces

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v10.0 requires its own final deployment and hosted audit.

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

Historical v9.0 candidate: `patches/v9_0_animation_studio.py`, 49 governed patches, artifact `swyrl_engine_v9_0.html`, marker `V9_0_AUTHORED_PAPER_THEATRE`. Sealed HTML: **746,616 bytes**, SHA-256 `6a0a9d24e2c888991afbe051d2ae5eba65f38a034c590013e447ca129962d157`. Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Production authority is recorded in the final `DEPLOY_REQUEST.json`, the dedicated deployment receipt, and the exact hosted-release audit.

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
