# §wyrl§ Engine · current v11.13 reference sculpt update

## v11.13 · native reference sculpt and independent living piñatas

Measured candidate seal: **2,464,667 HTML bytes**, SHA-256 `d53fd7990d85ad0444d245016ae6d61c91e2894a3adb8982756bc24f3903aaf5`; 83 ordered patches and 36 assets. Native model-save authoring and twenty focused desktop/phone cases passed; full independent release CI remains required.

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
