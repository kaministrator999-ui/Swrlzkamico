CI efficiency (2026-10-17): split the four slowest browser suites by desktop/phone while preserving all18suites and36viewport runs; remove duplicate native UI scroll waits, supersede obsolete validation, install only the headless browser, and keep final exports while omitting redundant intermediate OBJ upload copies. Measured timing baseline and validation: [Engine CI timing](reports/ENGINE_CI_SPEED_2026_10_17.md). Engine artifact/model data are unchanged.

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

## v11.15 · native portrait, cloth and ferret surface study (2026-10-16)

The owner requested continued native-editor work against the supplied Honor of Kings Scorchet turnaround. The new starter is the actual model saved and reimported through Model Atelier after **80 native inspector operations**: shorter facial proportions and smiling lip contours, subtler brows/blush, a continuous cyan/coral crown, clearer tapered ferret muzzles and exposed ears/masks, paper bodies swept behind the face in profile, flatter fitted skirt panels with matching borders, a broader coral wrap and corrected rear shoulder layering.

Reusable native tools add portrait jaw taper, tapered muzzle and split-dye crown surfaces, a second dye color, cloth curvature/fold depth and **Frame selected** with detail zoom. New parameters are bounded on import, retained by model JSON and whole-model Undo/Redo, and drive the rendered geometry. The independent ferret sockets, flex, model motion keys, detach/reattach, bunny and native JSON/OBJ exports remain available. Historical defaults retain their old geometry when the new surface fields are absent. Repeated model import now accepts the empty neutral pose emitted by native save/load while retaining validation of actual pose frames.

Native asset: `scenes/model-atelier-festival-surface-v11-15.swyrl.json`; **301 editable parts and 109,556 measured triangles**. [Native authoring and multiview evidence](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38956922273) comes from the real CI browser operating the editor, saving/reimporting JSON and capturing front, three-quarter, profile, rear, portrait, ferret and cloth views plus a phone view. Authoring source: `b411aa3b9592d1ec9d9b3fb1d5f3ebe28f354d02`.

Source seal: **2,487,712 bytes**, SHA-256 `c4c7356c35827eeaea2f24ca943c0dd431c65f5898dbcd325440f0821fc10a3a`, **85 patches and 38 packaged assets**. All 84 predecessor patches/runtime sources and 37 assets are preserved. Full independent compatibility CI, merge, the final dedicated deploy request, exact hosted digest/all-asset audit and native hosted phone/desktop controls are distinct release gates. Source/deploy commits and current publication authority are recorded by `DEPLOY_REQUEST.json`, its final trigger commit and the dedicated deployment/audit receipts; this source note does not substitute for those receipts. Owner visual acceptance remains separate. UV painting and weighted skeletal skinning are outside this release.

Details and repeatable editor authoring: [Native surface workflow](reports/NATIVE_SURFACE_STUDY_V11_15.md).

# §wyrl§ Engine · Roadmap

## v11.13 · native reference sculpt and independent living piñatas

Measured candidate seal: **2,467,619 HTML bytes**, SHA-256 `25b33e64c5211d47dde7bb8cb77e0f58d1917d5c55971938bf732c2d1371b9d8`; 83 ordered patches and 36 assets. Native model-save authoring, twenty focused desktop/phone cases and twelve phone/desktop-site/multiview framing checks passed; full independent release CI remains required.

The owner-provided festival turnaround now drives a new 275-part native starter: sculpted facial planes and almond eyes, swept dyed hair, asymmetric layered outfit, bare anatomical legs and socks, two three-dimensional tissue-paper ferrets attached to actual hair sockets, and a separate paper bunny. The living-model inspector provides reversible attach/detach, per-model flex, saved transform keys, a six-second transformation preview, independent model JSON exports and actual rendered OBJ export. Whole model history, native save/load and the measured geometry profiler remain available. Default generated geometry is approximately 82,396 triangles, measured from the buffers rather than guessed from mesh count.

Candidate branch `feature/model-reference-sockets`; source and hosted baseline `43dd6db` / v11.12, 2,352,463 bytes, SHA-256 `76051c90fda3b9f32fef582977fb8af872edc14de44781e253f90ed3f0f9bc6f`. The new release appends patch 83 and native asset 36. All 82 predecessor patches/runtime modules and 35 packaged assets are preserved. The exact earlier v11.12 default remains independently loadable for its full regression.

Research, native format, controls and limitations: [Festival reference workflow](reports/FESTIVAL_REFERENCE_WORKFLOW.md). This is an original editable geometric study; production retopology, UV painting and skeletal skin weights are not implemented. Full desktop/phone compatibility, final dedicated deploy, exact hosted audit and the owner's visual response are separate gates. This candidate section does not claim publication before those checks pass.

## UPDATE STARTED — v11.9 original festival model and model-first touch viewport

Owner's approved character sheet and original skin screenshots govern the proportions. Current work adds an independently authored 811-part native scene (without overwriting older scene assets), separate 36-tier editable paper-ferret bodies with narrow→bulky→tapered radius profiles, modeled scalp/hair grips, continuous neck/torso/limb form, eight editable draped fabric panels, detailed hands/boots, a native piñata pet, and a larger mobile 3D canvas with local inspector scrolling. Native cloth-panels remain actual editable loft splines, not painted image proxies. Source seal 2,335,886 bytes / SHA-256 `987f074e111420126715142da652d4907c7d1a0e493215ee9784e35da48966dd`; 79 patches / 35 bundled assets. Branch: `feature/engine-v119-figure-ferret-silhouette`, PR #187. This is a **candidate**, not deployed or owner visually accepted until full CI, merge, dedicated release and independent host audit complete. Hair companions are structurally separate but do not yet have skeletal rigs or animations.

## Current v11.8 candidate — procedural twisted piñata and continuous anime limbs (not deployed)

The approved visual study is being revised with two editable rear-origin broken-S frustum sweeps; native twist/depth/smoothing/mirror/fringe editing; four continuous anatomical limb lofts replacing bead joints; and retained historical scenes. The owner still judges front/side/rear visual quality. A passing test matrix is not equivalent to rigging or textured sculpting, which remain future editor capabilities. Follow §tart_§E.md's gated deployment and independent audit.


> **v11.7 sculpt candidate:** 36 discretely capped faceted piñata slices per creature; 733 native-editable parts; face/hair/clothes/rear structural details; historic variants preserved. Not published until full CI and independent hosted audit; art-direction judgment requires new front/side/back screenshots.

## UPDATE STARTED — v11.5 original festival model detail and spline authoring (2026-10-15 CDT)

**Owner input:** supplied current 253/303-mesh screenshots and multi-angle carnival mage reference. Asked for real starter/model improvements and any necessary engine modeling capabilities, not a written brief. The requested primary target is an original expressive cyan/coral two-ferret-piñata carnival mage study; alternate character skins are visual-quality references only.

**Isolated candidate:** `feature/forge-model-atelier-spline-fidelity-v11-5` adds distinct `scenes/model-atelier-prism-jester-festival-v11-5.swyrl.json` (539 independently selectable meshes versus v11.4's 303), with extra layered paper tissue vanes, hanging fringe, face framing and costume trims. The historical 253- and 303-part authored starter assets remain unmodified. Append-only `patches/v11_5_festival_loft_atelier.py` replaces only the canonical default on rebuild and adds native inspector control-point/radii JSON editing for the existing loft mesh type, with validation, edit history, import, and existing OBJ export behavior retained. Native part ceiling rises from 400 to 1,200; JSON import file bound rises from 2 to 8 MB.

**Release status: CANDIDATE ONLY — NOT DEPLOYED.** The updated manifest intentionally omits finalBytes/finalSha256 until the *actual generated candidate* can be built and sealed. Do not merge, press `DEPLOY_REQUEST.json`, or claim production success until the new complete build has been reconstructed, JS/HTML syntax and source integrity checked, native desktop/phone editor/loft/save/OBJ tests and preserved Maul/Sheep/anime suites passed, manifest digest sealed, README/Space version/verification surfaces synchronized, PR reviewed, and dedicated final deploy and independent hosted audit completed. This change has no authorization to mutate the separate AI Chat Space.


## UPDATE FINISHED — v11.4 ferret-piñata refinement published (2026-10-15 CDT)

**Production complete:** [PR #171](https://github.com/kaministrator999-ui/Swrlzkamico/pull/171) merged at `0540cfbfc29129548941881f659f26a767038ed3`; 17/17 desktop/phone acceptance suites passed [browser run #38680364328](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364328) plus five candidate source workflows. [Dedicated deployed release #38729222214](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729222214) SUCCESS on `2dba7e6da30fef16c8bb1f4a35f979bcfbffb9b4`; [independent hosted audit #38729291039](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38729291039) SUCCESS with `HOSTED_AUDIT_SCOPE=current-requested-release`, `PUBLISHED_VERSION=v11.4`, and `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`. Hosted HF revision `f88b57b39893f556e380cef7c279d93860800a95`.

**Exact published sealed artifact:** `V11_4_PRISM_FERRET_FIDELITY`, 74 patches, 30 assets, 2,197,108 HTML bytes, SHA-256 `40d1e985bd3754b7a2996e6be14056be9c22164995d83b84ad253b4ae7a24658`. The Model Atelier Projects tile now opens the newer 303-part original model variant including two tapered organic lofts and ferret heads, eyes, ears, muzzles, paws, paper fringe and facial detail; the 253-part v11.3 scene remains packaged for import. Full editor save/transform/OBJ/mobile acceptance is browser-verified, and other game starter assets remain preserved. **No human-owner visual acceptance or claim of exact skin/model likeness, sculpting, UV editing, rigging or animation.**

**Governance:** synchronized `§tart_§E.md`, project README, Space README, and `VERIFICATION.md` to verified v11.4 hosted status after first successful audit. Their commits are documentation-only; source manifest and authored scenes remain unchanged. The final dedicated `DEPLOY_REQUEST.json` write must be last, followed by a new terminal deploy and independent audit to close this documentation-only continuation. Retain preceding UPDATE STARTED and CONTINUATION STARTED entries unmodified as provenance.

## UPDATE CONTINUATION STARTED — v11.4 production deployment and audit (2026-10-15 CDT)

**Source and acceptance closure:** [PR #171](https://github.com/kaministrator999-ui/Swrlzkamico/pull/171) merged at `0540cfbfc29129548941881f659f26a767038ed3` on latest main, preserving earlier patch and native model assets. [Full 17/17 browser matrix](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38680364328) and all five source/cinematic/cel/staging candidate validations completed SUCCESS against exact sealed candidate `b6d43100279232ea4c660df8c1cf0e6781a1437d`.

**Identity/integrity:** `§wyrl§ Engine v11.4`, `V11_4_PRISM_FERRET_FIDELITY`, 74 ordered patches, 30 bundled assets, 2,197,108 bytes, SHA-256 `40d1e985bd3754b7a2996e6be14056be9c22164995d83b84ad253b4ae7a24658`. The default Model Atelier native sample now opens 303 selectable parts and two tapered ferret-piñata bodies with separated heads, while the previous 253-part version remains packaged. Not a pixel-perfect game asset nor advanced sculpt/UV/rigging/animation claim.

**Final release boundary:** docs `§tart_§E.md`, Engine README, Space README, verification ledger, and this roadmap synchronized to **source merged / deployment pending**. Change only the dedicated `DEPLOY_REQUEST.json` last on main, await terminal dedicated deploy SUCCESS and separately triggered independent hosted verification SUCCESS before calling new v11.4 live. After publication, reconcile source/host receipts and if required use the final dedicated documentation-close deploy button again. Preserve all historical game starters and do not trigger Chat Space deployment.

## UPDATE STARTED — v11.4 Prism Jester ferret-piñata fidelity (2026-10-14 CDT)

**Observed owner feedback:** the published v11.3 screenshot is recognizable but too primitive/round, and the apparent large pigtails are **two ferret-like piñata creatures physically gripping the pigtails**, not rigid hair tubes. The owner provided additional screenshots but explicitly kept the original cyan/coral carnival skin as the main target; other skins serve only as material/face-quality examples.

**Source baseline:** v11.3 verified release at main `c8836ea681821ebb303024372c4803aa67b6f8a0`, 73 patches, 29 assets, live hosted audit verified. All previous shipped original scene assets and patch files are immutable for this slice.

**v11.4 implemented on isolated branch:** `feature/forge-prism-jester-ferret-v11-4`. Additive 74th patch `patches/v11_4_prism_ferret_fidelity.py`, a distinct `scenes/model-atelier-prism-jester-ferret-v11-4.swyrl.json` containing 303 editable parts, 2 organically tapered lofts, preserved legacy project identity, paper fringe, facial refinement, pigtail attachment points, dark ferret muzzles/eyes/ears/paws, safe bounded loft validation and existing JSON/OBJ authoring compatibility. New engine patch modifies the generated latest code only, preserving published v11.3 source files. Art direction and grounded modeling references: `reports/PRISM_JESTER_FERRET_ART_DIRECTION.md`.

**Acceptance required before delivery:** build and seal exact 74-patch / 30-asset HTML; source and JS syntax; model anatomy schema/native package regression; updated desktop/mobile browser matrix including model edit/save/reopen and original authored project; previous Maul/Sheep Tag/anime cases; five source workflows; reviewed PR; explicit final dedicated `DEPLOY_REQUEST.json` after merge; terminal successful deployment and independent hosted full-asset audit. No claims of pixel-exact hero likeness, vertex-sculpt tools, glTF import, UV editor, skinning, or animation in this slice.

## UPDATE FINISHED — v11.3 Model Atelier merged, deployed and independently audited (2026-10-14 CDT)

**Production result:** [PR #167](https://github.com/kaministrator999-ui/Swrlzkamico/pull/167) merged at `abfe8a495b3a7c166f2bebe9151887b2cef6b807`, after [all 17 of 17 desktop/mobile browser suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608237) and every §E candidate source workflow. [Dedicated Engine deploy #38677061503](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677061503) ended SUCCESS from explicit request commit `44a594f534c92c723079adcb33d8a80962bc7e0f` and [independent hosted audit #38677099743](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38677099743) ended SUCCESS for the exact same release authority. Hosted audit reported `HOSTED_AUDIT_SCOPE=current-requested-release`, `PUBLISHED_VERSION=v11.3`, and `LIVE_SOURCE_AND_ALL_ASSETS_VERIFIED`.

**Exact published bytes:** `V11_3_MODEL_ATELIER_PRISM_JESTER`, 73 patch chain, 29 assets, 2,175,921-byte HTML, SHA-256 `a2ec94f418f294ea5ebd50363833d37025a6e6cc804732116a7cb927d0b069db`. A distinct new Projects template opens 253 individual meshes within a real WebGL editor; controls for selection, transforms, colors/materials, duplicate/delete, undo/redo, native JSON round-trip, and OBJ export passed desktop and phone automation. Original themed study, not a proprietary extracted replica; advanced sculpt/UV/rigging/animation and human artistic sign-off remain future work.

**Governance completion:** the §E router, engine README, Space README, and verification register were synchronized after the first successful terminal host audit. The source manifest, original/native scene meshes, older releases, and separate Chat Space deployment remain unchanged. The dedicated `DEPLOY_REQUEST.json` is the **final** publication button for this documentation-closure continuation; wait for its fresh terminal deployment and independent audit before claiming the latest deploy pass complete. Retain the earlier continuation and initial UPDATE STARTED entries below as exact lineage.

## UPDATE CONTINUATION STARTED — v11.3 final governed production deployment (2026-10-14 CDT)

**Latest merged source:** [PR #167](https://github.com/kaministrator999-ui/Swrlzkamico/pull/167) merged at `abfe8a495b3a7c166f2bebe9151887b2cef6b807`. All [17 desktop/phone Playwright suites passed](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608237) on candidate SHA `23b458b4bb7e165a759f5cab7419dfed51083df5`; additional [source](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608236), [cinematic](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608235), [camera](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608243), [cel](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38674608277) checks PASS. The source-only v11.3 import/export, inspector editing and original 253-part scene are independently validated, alongside historical project regression cases.

**Sealed integrity:** `V11_3_MODEL_ATELIER_PRISM_JESTER` · 73 ordered patches · 29 bundled assets · 2,175,921 exact HTML bytes · SHA-256 `a2ec94f418f294ea5ebd50363833d37025a6e6cc804732116a7cb927d0b069db`. No source runtime changes made for documentation closure. The original `UPDATE STARTED` retained underneath.

**Final handoff:** source and docs are synced on main. Next write `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` **last** on latest main to trigger the dedicated Engine release workflow, then wait for terminal deploy and independent hosted audit. Do not report live until both succeed; archive those exact receipts in this roadmap and the §E router. Maintain separation from the concurrent Chat Space deployment, and preserve all native older scenes intact. No artist-level sculpt/UV/rigger/animation claim is made.

## UPDATE STARTED — v11.3 editable 3D Model Atelier and original character test (2026-10-14 CDT)

**Owner/design intent:** a separate §E native Projects tile for an actual editable character-modeling workspace. Four user-provided Honor of Kings Scorchette screenshots establish shape/color/detail targets only, not source meshes or licensed game assets. First authored sample is an **original visual approximation** (two oversized cyan/coral segmented ribbon forms, colorful jester/mage attire, hands, face, hair, layered details). Never represent it as extracted game geometry or pixel-exact copyrighted asset.

**Isolation:** `feature/forge-model-atelier-v11-3` from main `dca38449f01def470a47ea3c643072a69b3d9af7`; scope confined to `projects/swrlz-forge-moba/`. Keep 72 published v11.2 patches and all existing native starters byte-identical. Preserve independent `kamiloki/Swyrlz` Chat deployment path. Canonical engine pieces: new ordered patch, scoped model-atelier runtime and stylesheet, model-atelier native scene/serialized part data, registration in project launcher, build-time packaged project asset, model-edit acceptance tests. No duplicated engine shell, backend or third-party cloud runtime.

**Implementation acceptance:** a fully registered Projects starter opens a live 3D viewport on desktop/phone; tap/raycast chooses parts; editable transform/material, add/duplicate/delete, undo/redo, orbit/zoom, native-model JSON import/export and geometry export preserve distinctions; loading old projects is unaffected. The reference model is controllable geometry rather than a flat screenshot, with visible layered forms. Bounded loading, disposal, non-executable imports and safe inspector controls. Test exact native package against launcher identity, browser interactions on both viewports, static and JS syntax, prior full §E suites and exact hosted release.

**Release policy:** source-only draft until candidate manifest SHA sealed, reviewer/integration gates complete; after exact source validation, merge on newest main, change the dedicated `DEPLOY_REQUEST.json` **last**, wait for dedicated terminal workflow plus independent hosted asset audit. Do not claim full sculpting, a true game-model replica, rigging/animation, or live release without their own evidence.

## UPDATE FINISHED — v11.2 publication and documentation closure (2026-10-14 CDT)

**Outcome:** Release implementation and terminal proof are complete: [source PR #159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159) merged as `b3ef6130f0d9685018debb06fcdd4ef2912d9f6e`; original six Forge CI workflows and all 16 desktop/phone suites passed on `716a2bc81b01c79b65ed7771eb3dc794248ce55b`. Last final production release trigger `e47c027816fa5029f0c27ac273e040ae62fd1a5f` has [successful dedicated deployment 38668840620](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668840620) and [successful independent hosted audit 38668893410](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668893410). Its exact hosted normalized HTML and SOURCE receipt and all 28 assets matched. Published HF revision `ef8f325b2d8d45cf67da2c54bc4f8e3455df263e`. **v11.2 / V11_2_MAUL_FLIGHT_GLACIAL_ART**, 72 ordered patches, 28 bundled assets, 2,097,069 bytes, SHA-256 `1fab5e61f2065c02a56658c6e8e8ef999eb525ac16c373b310826ca970e10e59`.

**Governance-only continuation:** synchronized `§tart_§E.md`, engine `README.md`, `SPACE_README.md`, and `VERIFICATION.md` from stale v11.2 candidate claims to exact source/deployment/audit receipts. Commit lineage: router `06ce84e984b5771233ba6bf8ab2fab58a1b4e6c1`, README `1e93ebc927dd147edfba53d92ab7ec035114d8be`, Space README `41024bc550ce23f6315067da3c6fc08da04ccba5`, verification `59e7cbbc901362572fd34a86ca328c15bc2ef412`. No changes to manifest, authored scene, runtime modules, package assets, model, Chat Space, or engine binary; no new version assigned. Following §E's final-deploy-button rule, this documentation-only closure must finish with a fresh explicit `DEPLOY_REQUEST.json` handoff, then its own terminal workflow+hosted check, before reporting the documentation update's deployment as complete. Existing v11.2 release is verified; the fresh redeploy remains a distinct subsequent observation.

**Acceptance separation:** native CI and hosted integrity are verified; independent owner playthrough/UI judgement has not been performed here. Missing advanced Wintermaul creep systems, adjustable waves, endless/Mirror Survival, thematic builders and native creator remain planned. The original UPDATE STARTED and CONTINUATION STARTED entries are retained verbatim below as lineage. No unrelated AI Chat deployment was invoked by these §E documentation commits.

## UPDATE CONTINUATION STARTED — v11.2 release receipt / documentation closure (2026-10-14 CDT)

**Reconstructed baseline:** `main` contains merged PR #159 at `b3ef6130f0d9685018debb06fcdd4ef2912d9f6e`. The final v11.2 deploy request `e47c027816fa5029f0c27ac273e040ae62fd1a5f` passed [dedicated deployment 38668840620](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668840620), followed by [independent hosted audit 38668893410](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668893410), both SUCCESS. Hosting revision `ef8f325b2d8d45cf67da2c54bc4f8e3455df263e`; sealed HTML **2,097,069 bytes**, SHA-256 `1fab5e61f2065c02a56658c6e8e8ef999eb525ac16c373b310826ca970e10e59`; 72 patches/28 assets. All six original candidate workflows/16 browser suites passed. A later main-branch `sheep_archive` rerun remains in progress at this checkpoint; do not replace the original six-workflow receipt with an unverified claim.

**Already completed:** source implementation, merger, source validation, guarded deployment and hosted full-asset verification. The primary v11.2 UPDATE STARTED entry remains preserved below. **Current deficiency:** top-of-file router/readme/SPACE docs and release ledger still state 'candidate/unreleased' and original UPDATE STARTED has no terminal marker.

**Continuation scope:** governance-only correction of `§tart_§E.md`, engine `README.md`, `SPACE_README.md`, `VERIFICATION.md`, and this Roadmap. Preserve binary/manifest, authored scene, all historical evidence, and separate Chat Space. Validate documents and re-check release identity; use the repository's dedicated deploy-button contract if required by the mandated §E update protocol. Do not claim owner-playtest acceptance or future enemy/wave modes as implemented. No engine feature or patch change planned.

**v11.2 audit compatibility repair before final re-deploy:** The first guarded trigger `2723c49cb5f327ae6d4e93f5bfa59f26d42495a7` produced successful deployment [run 38668615711](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668615711), with exact hosted HTML/SOURCE and **all 28 live assets matched**. The secondary independent audit [run 38668682992](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38668682992) failed solely because its hand-maintained expected file set lacked the added `scenes/maul-frostveil-flight.swyrl.json`. Fixed in `.github/workflows/verify-swrlz-v8-9-live-receipt.yml` (commit `4ff55dd2d535eb0282ae9c6463c1a95d6f8240b8`), which now also validates the live native flight/glacial/protected construction profiles. The governed v11.2 binary, sealed SHA-256 and native scene are unchanged; a new **last-mutation release trigger** and fully green independent terminal audit are required for final closure. The other pending Wintermaul features remain backlog, not part of v11.2.

**v11.2 merger and release gate · October 14–15, 2026:** PR [#159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159) merged into `main` at `b3ef6130f0d9685018debb06fcdd4ef2912d9f6e` after **six successful Forge workflows** on source head `716a2bc81b01c79b65ed7771eb3dc794248ce55b`, including **all 16 desktop/phone native browser suites** (the Maul starter, layout, and legacy recorder among them). Final source candidate: **v11.2**, 72 patches, **28 assets**, **2,097,069 bytes**, SHA-256 `1fab5e61f2065c02a56658c6e8e8ef999eb525ac16c373b310826ca970e10e59`; deploy marker `V11_2_MAUL_FLIGHT_GLACIAL_ART`. The Projects → Frostveil Maul starter now loads the independent flight-native scene, tested against the downloadable packed version. Next release gate is the **final dedicated `DEPLOY_REQUEST.json` mutation**, then terminal Hugging Face deployment and exact hosted asset audit; until that terminal receipt, v11.1 is the last confirmed live release. No remaining Wintermaul backlog is declared completed here.

**Starter-pack integration correction:** A standalone v11.2 authored native map, `scenes/maul-frostveil-flight.swyrl.json`, is now the exact Projects → Frostveil Maul starting scene. It contains 78 native actors (nine builders, no free towers), keeps the 30-round co-op layout, stores `hover-v1` flight, `glacial-v2` textures, `walk-v1` gated construction and `full-pad-v1` protection in the file, and is included as the **28th published asset** without overwriting prior maps. The native browser test fetches this actual asset and asserts project settings and builder identity match the project launcher. Unverified candidate only; it is not a released v11.2 promise.

## UPDATE STARTED — v11.2 Frostveil hover-builders and glacial map art (source candidate)

**Scope/owner:** dedicated §E source on isolated branch `feature/forge-frostveil-flight-art-v11-2`, based on main `fc9d94da315af1c559fcbc6bfb16af343f194fe0`; PR [#159](https://github.com/kaministrator999-ui/Swrlzkamico/pull/159). The new current Frostveil profile gains direct airborne 15-unit/s movement over towers and cliffs, flight height 3.25, same-cell delayed construction, hover-wing visuals and cached original procedurally textured glacial map pieces. Previous v11.1 71-patch release and legacy imports are preserved.

**Candidate manifest:** 72 governed patches; `patches/v11_2_maul_flight_glacial_art.py` appends `runtime/maul_flight_core.js`, `runtime/maul_flight_integration.js` and `runtime/maul_frostveil_art.js`. Pure deterministic flight CPU acceptance and all prior Maul/Sheep Tag/anime tests, original assets, package hash and desktop/mobile Play are release gates. This STARTED entry is neither FINISHED nor deployed. Keep the live version at **v11.1** until final manifest sealing, all engine CI suites, reviewed merge, dedicated final `DEPLOY_REQUEST.json` trigger and independent hosted audit. A failing CI gate belongs to the implementing agent to diagnose and repair.

**Remaining Wintermaul scope (separate source slices):** no-overlap creep lane congestion, blocked route aggression, special fast/stealth/detection/immunity/teleport/Heal/Hydra/Infernal units, balanced wave roster/rewards, endless and two-team synchronized automatic-wave Mirror Survival, independent themed builders, and native Maul creator; none claimed implemented. Source-of-truth feature ledger: `reports/WINTERMAUL_DESIGN_ARCHITECTURE.md`.

## Historical v10.9 candidate · Story actions and an animated first episode

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

Pose, grip and effects references preserved from v9.6: [PoseMyArt’s male casting-spell pose](https://posemy.art/magic-poses/male-casting-spell-pose/2396/), [Clip Studio Tips](https://tips.clip-studio.com/en-us/articles/8226), and [Riot’s VFX style guide](https://nexus.leagueoflegends.com/en-us/2017/10/dev-leagues-vfx-style-guide/). The fitted rig, painted atlases and staff rendering use original project content.

## Historical verified v9.5 · Fitted Staff and Character Relief

The v9.5 release is the previous verified checkpoint: [deployment 38013962412](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013962412) and [hosted audit 38013986565](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013986565) passed. Source `49b82022de841a26a4692359751395ca792efc9f`, final trigger `dcab50950603fb4160615e0d6bf5e0ec8558b06e`, seals 55 patches, 1,075,201 bytes, SHA-256 `bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb`, and 16 assets. It introduced the saved staff mount and per-piece character relief. These receipts certify v9.5; the v10.0 candidate requires its own final deployment and hosted verification.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v10.0 candidate requires its own final deployment and hosted verification.


Canonical lane: §E / §wyrl§ Engine
History audited through: **2026-10-14**
Current candidate: **v11.2 flying builders + glacial art (72 patches, source-only)**; current independently audited **live release v11.1 (71 patches)**. The manifest, the final DEPLOY_REQUEST and served-source audit are separate authorities. Historical releases remain preserved.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

This roadmap is the mandatory release lineage for governed §E GitHub updates. Root `§tart_§E.md` defines the deployment contract.

## Supported book opening and limb sockets

The existing coordinated opening brings Kami, §wyrlz, architecture, props, effects and the three star-depth shells out of the pages before they reach their saved stage positions. Preview Frame, Play and Watch use the same saved opening. Persistent limb sockets keep snapped children attached while their pose keys rotate around the connection. Camera target bounds now include the low book pages, allowing the saved opening shot to focus on the book before pulling back to the expanded cast.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-performance.swyrl.json`; the full-staff export remains preserved for import. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Saved per-character rest layouts, 468 limb/face keys, 383 scenery keys and the action/effect overlays remain independent. The v9.6 natural-grip, v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all eleven artwork PNGs and the historical episode HTML.

The 54th and 55th patches retain the staff mount and per-piece relief. The 56th, `patches/v9_6_natural_staff_painted_faces.py`, retains the compact grip and painted facial features; the 57th, `patches/v9_7_ornate_staff.py`, retains socket-attached shaft ornament. The 58th, `patches/v9_8_full_length_staff.py`, integrates the full painted staff and native preset; artifact `swyrl_engine_v9_8.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_8_FULL_LENGTH_MAGE_STAFF`. The 59th, `patches/v9_9_episode_shuttle.py`, adds signed episode shuttle playback; v9.9 artifact `swyrl_engine_v9_9.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_9_EPISODE_SHUTTLE_CONTROLS`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging contains nine episode scene JSON exports, the historical episode HTML and eleven PNGs, for twenty-one media assets. The 60th patch, `patches/v10_0_sheep_tag.py`, adds the separate native Sheep Tag starter; v10.0 artifact `swyrl_engine_v10_0.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V10_0_SHEEP_TAG_STARTER`. The native meadow map raised the v10.0 package to 22 assets. The 61st patch, `patches/v10_1_sheep_tag_archive.py`, adds the verified archive rules and creator. The 62nd, `patches/v10_2_sheep_touch_placement.py`, adds double-tap sheep building selection and ground placement guides; `swyrl_engine_v10_2.html` and `V10_2_SHEEP_TOUCH_PLACEMENT` identify the historical v10.2 release with the same 23 assets. The 63rd patch retains touch aim above the finger, the 64th retains house lanes and physical creature traffic, and the 65th adds the opt-in Play-run recorder and post-Stop review. The 66th adds the separate Frostveil Maul tower-defense starter, with its native scene as the 24th packaged asset. The 67th reshapes that starter around the classic upper bays, crossbar and shared ship funnel, with a new native scene as the 25th asset.

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

These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

**Validation:** The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

## Historical v9.0 · Native Animation Studio and Paper Theatre

The native 2.5D Watch player was deployed from [source `9c19b537f111`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/9c19b537f11144811c9c1509e90430d9adaccf13). Its served-source authority is 758,245 bytes, SHA-256 `20e1ed3d3697d4a199e34ae812e7b30a3bbc7c2503da3223bf54ddb8915e3236`. This later v9.0 cinema checkpoint preserves the earlier whole-cel authoring acceptance below.

**Ghosts in Different Forms · The Page That Remembered** is a native editor export with 70 actors, 11 editor layers, eight story beats, nine independent animation tracks, and 134 seconds of playback. It adds eight saved paper actors/layers while preserving the original 62 production set actors, three production layers, eight stations, and eight destinations. Generated transparent Kami and §wyrlz artwork and separate cathedral, workshop, and foreground plates follow the user's reference direction.

Reusable `runtime/anime_timeline.js`, `anime_stage.js`, `anime_editor.js`, and associated CSS are integrated by `patches/v9_0_animation_studio.py`. Animation Studio edits camera position/target/FOV, character and scenery transforms, easing, visibility, opacity, unfolding, titles, and timed dialogue. Preview Frame and editor Play use the same renderer; native Undo/Redo and Save/Load preserve changes. PNG/WebP/JPEG replacement binds artwork to an individual saved actor. Capture Actor Pose connects native Inspector transforms to the selected timeline keyframe.

Physical scenery meshes rotate at hinges. Protective background depth, a low foreground/book, and adaptive portrait framing keep the central cast readable. The historical Watch Episode 01 screening remains separate. Skeletal posing, lip sync, audio authoring, and MP4 export are not implemented.

**Validation:** Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Sealed source reconstruction and every engine CI gate passed. Artifact `swyrl_engine_v9_0.html`; marker `V9_0_AUTHORED_PAPER_THEATRE`. Exact integrity and source/deploy commit references will be supplied by the sealed manifest and final trigger receipt. The dedicated `DEPLOY_REQUEST.json` procedure and exact served HTML, scene, episode, and artwork verification are required before v9.0 is called live. Direct starter: https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01 .

## v8.5 candidate · Anime Studio starter

Source integration introduces a third independently selectable project, `Ghosts in Different Forms · Episode 01`, using `patches/v8_5_anime_starter.py`. The original 62-actor native scene, eight act zones, three layers, and eight per-scene production workstations are embedded in the governed composite. The animated HTML episode is also distributed as a static asset, screened inside the editor rather than in the 3D runtime. A separate candidate workflow verifies the reconstructed hash and JavaScript syntax before the deploy request.

**Status:** Source candidate; exact artifact, deployment, and live runtime verification are tracked independently. This entry does not redefine or erase the v8.4 checkpoint.

## Historical v8.6 native Anime Studio Play

Dedicated [deployment 37719877533](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719877533) and exact served HTML plus both episode/scene asset SHA-256 verification passed. Earlier v8.3 receipts remain in historical sections.

The Anime Studio starter now begins a real-time native Three.js cinematic when Play is pressed. Eight scripted camera shots, temporary procedural performers, guardian-dragon animation, motes/lighting, and captions driven by each stage's editable `script.md` form an approximately 134-second episode preview. A transport HUD provides Pause/Resume, seek, previous/next shot, Stop, and **Explore Set** to switch to the prior first-person world mode. Other §E starter projects keep their original Play behavior.

Source: `patches/v8_6_native_anime_cinematic.py`; final SHA-256 `1468357c5ce082b71548de983fd11f818cf4eeccb34eca3df92a0f15e3e94dc0`, 611,675 bytes, 45 patches. [Headless Chromium desktop/mobile test run 37719407234](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234) and [candidate compiler run 37719407233](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233) passed. Native authoring of cinematic keyframes, lip-sync and exportable video remain future capabilities.

## v8.9 candidate · Camera-safe pop-up scenery staging

Real Android screenshots of v8.8 showed the large opaque desk/foreground panel and animated book rising *in front of the camera and character cels*. Corrective engine patch `patches/v8_9_cinematic_staging.py` keeps the physical book below the wizard cutouts, replaces the opaque foreground panel with a thin transparent-trim plate that only paints its bottom portion, and clamps cathedral/sky/magic scenery behind both independent wizard cels. The effect still uses actual Three.js depth/perspective and independent hinges. Older saved `animePopUp` Director values remain serialized, but scenery render staging enforces a safe maximum so dangerous near-camera cards cannot obscure the cast. Runtime `popUpStatus().stageSafety` exposes book height, foreground painted boundary, actors and architecture Z values, and camera gap. Desktop and mobile automated regressions check first/later scene layouts against those boundaries.

Verified browser acceptance: [Actions 37728474772](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728474772). Full artifact **647,639 bytes**, SHA-256 `da9f48941543c81062a232417ed8897e8c82e912852474cf2154e209c12ddf37`; production receipt **passed**: [deployment 37728665723](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728665723) and [independent live audit 37728754278](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37728754278).

## v8.8 candidate · Pop-Up Storybook Video Creator

Upgrade the existing Anime Studio starter rather than creating another image or application. Native Three.js book geometry opens under the scene; independent painted book/card/cathedral/workshop/foreground plates rise on animated hinges with perspective parallax. Kami and §wyrlz become separately rendered dark-fantasy wizard cels, echoing the user's two-wizard artwork direction. **Pop-Up Director** saves per-layer depth, parallax, horizontal offset, unfold delay/duration as part of project JSON. The original eight acts, subtitles, Explore/Stop, and unrelated project templates are preserved. Exact 644,951-byte candidate SHA-256 `06c55a0d090bd6ffa9383ff44f914b922a841de7dc03284a50955cb4036478cd` and browser acceptance [Actions 37726896000](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37726896000). See [POPUP_VIDEO_CREATOR.md](POPUP_VIDEO_CREATOR.md) for explicit feature and remaining limits.

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
| v8.8 (historical candidate) | 2026-10-08 | Physical pop-up book, individual hinged scenery, separate wizard cels, and saved Pop-Up Director controls. |
| v8.9 (verified hosted checkpoint) | 2026-10-08 | Low book/foreground and behind-cast scenery limits repair Android camera occlusion; desktop/mobile and hosted integrity receipts passed. |
| v9.0 (historical checkpoint) | 2026-10-08 | Native Animation Studio, generated separate artwork, saved paper actors, nine authorable tracks, editor Preview/Play, and a native 134 second storybook export with 70 actors/11 layers; later native Watch cinema deployed. |
| v9.1 (verified hosted checkpoint) | 2026-10-08 | Independent jointed eighteen-piece paper rigs, saved body/face keys and native pose authoring. |
| v9.2 (verified hosted checkpoint) | 2026-10-09 | Fitted faces, 34 independently keyed scenery objects, three star-depth shells and camera-safe folds. |
| v9.3 (verified) | 2026-10-09 | Connected character pieces, character-specific rest layouts and native part-fitting controls; exact deployment 37893678594 and audit 37893722231 passed. |
| v9.4 (verified) | 2026-10-09 | Saved limb sockets, snapped articulation and coordinated page emergence for cast/scenery/stars; deployment 37942614513 and audit 37942679834 passed. |
| v9.5 (verified) | 2026-10-10 | Saved staff mount and individual character relief sections, paper thickness and costume flex; deployment 38013962412 and audit 38013986565 passed. |
| v9.6 (verified) | 2026-10-10 | Compact painted staff grip with a saved legacy-compatible profile, continuous shaft and crest proportions, matching animated painted facial features and deterministic gold staff motes; deployment 38071280266 and audit 38071311391 passed. |
| v9.7 (verified) | 2026-10-11 | Socket-attached ebony grain, gold inlay and fitted staff ornament, preserving the natural grip and nineteen assets; deployment 38099380535 and hosted audit 38099404177 succeeded. |
| v9.8 (verified) | 2026-10-11 | Full-length painted staff, fitted grip and pointed foot; 58 patches, 21 assets. Deployment 38115297536 and hosted audit 38115324306 passed on trigger 6cd814f925a7; source 35936a688fe1. |
| v9.9 (verified) | 2026-10-11 | Native episode Rewind/Fast forward 2×/4×/8×; 59 patches and 21 assets. Deployment 38150826816 and hosted audit 38150874160 passed on trigger a382b4ea577c; source 4eb6021976e9. |
| v10.0 (verified) | 2026-10-11 | Separate native Sheep Tag · Moonbell Meadow starter, construction/economy, AI wolves and wisp rescue; 60 patches and 22 assets. Six engine workflows, nine desktop/phone suites and fourteen live gameplay cases per layout passed. Source a06c89ed9e6c, trigger 87b6a4be9319, deployment 38174454216 and hosted audit 38174501776 succeeded. |
| v10.1 (verified) | 2026-10-12 | Archive rules, purposeful AI, fog, optional territory/upper-route/split experiments and native Map Creator; 92 actors, 61 patches and 23 assets. Six engine workflows, ten desktop/phone suites and nineteen live archive cases per layout passed. Source 86aa05b494db, trigger 1779223f8b92, deployment 38223924840 and hosted audit 38224004659 succeeded. |
| v10.2 (verified) | 2026-10-12 | Double-tap building selection and ground footprint grid. All six engine workflows and eleven desktop/phone suites passed, plus eleven live cases per layout. Source 0144031ae3b3, trigger 3bf7004e716c, deployment 38273428696 and hosted audit 38273499402 succeeded. |
| v10.3 (verified) | 2026-10-12 | Touch previews above the finger. Source de24b04c95e1, trigger d0442216bf82, deployment 38312154843 and audit 38312197696 passed. |
| v10.4 (verified) | 2026-10-13 | Self-construction ejection, flush/sheep-only house lanes, larger wolves and physical creature traffic. Source 6d04109c27df, trigger 04ba3ef018d4, deployment 38317704872 and audit 38317774602 passed. |
| v10.5 (verified) | 2026-10-13 | Optional Play-run recording for every starter/custom project; source 6da367913c0e, trigger e3b252b6850d, deployment 38344147035 and audit 38344188938 passed. |
| v10.6 (verified) | 2026-10-13 | Cooperative Frostveil Maul campaign; 66 patches, 24 assets, thirteen browser suites, 17 Maul and 13 geometry CPU cases; deployment 38434348748 and audit 38434414319 passed. |
| v10.7 (verified) | 2026-10-14 | Classic Maul upper bays, crossbar and lower shared-ship funnel; 67 patches, 25 assets and fourteen browser suites; source c80e0b98e33a, trigger c26630d0f8fc, deployment 38513639622 and audit 38513700470 passed. |
| v10.8 (candidate) | 2026-10-14 | Three scattered arrival groups per round, empty Player 1 building area, 140-pixel phone placement lift and visible structure footprint; seven starter modes, 68 patches, 26 assets and fifteen browser suites. Source commit and final dedicated deploy/audit receipts pending validation. |

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
| v9.5 (verified) | swyrl_engine_v9_5.html | 1075201 | bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb |
| v9.6 (verified) | swyrl_engine_v9_6.html | 1099583 | d78dedc68ae0fe7bcbd368ee949bb2926c6f9bf321586e5254ad3fb97c1f07bd |
| v9.7 (verified) | swyrl_engine_v9_7.html | 1111978 | 0e1d8a7cbf90e956714245364d923107d7c8d0e8ab8476aa7b81e0fcbad43ac3 |
| v9.8 (verified) | swyrl_engine_v9_8.html | 1133438 | d486985beb2e92ba9ad237ea6e5313dcffb7f53e9b5e69c3b54aca24e4a9b5b8 |
| v9.9 (verified) | swyrl_engine_v9_9.html | 1139928 | 60dfa8da434eaa6cfe578f441a93be1fb9139676933e985a19919c13938b60c9 |
| v10.0 (verified) | swyrl_engine_v10_0.html | 1290101 | abcab023bbec0b5cacc72d7b845096060feb56418ab12b9eacee62bf9b7bf8c4 |
| v10.1 (verified) | swyrl_engine_v10_1.html | 1464129 | ef72eb9177a81537c5f6f56f65d620ac9593b4e08da6eae4f1bc4e34b5c9b8f1 |
| v10.2 (verified) | swyrl_engine_v10_2.html | 1487394 | 2c0d10636bda9cf6062e6ec49d8173a77a104fa208c841d6eda4d48409a9ba35 |
| v10.3 (verified) | swyrl_engine_v10_3.html | 1501714 | 6b0f2f461ea2bb1595e0be2ef4dbc58a114ecb39bd8e1828ac745cd0b7ed2653 |
| v10.4 (verified) | swyrl_engine_v10_4.html | 1520413 | f2c2eeb2a28d91239b3cb7afd48c0d189373a260bd12a851e3aaa8fd92524a2d |
| v10.5 (verified) | swyrl_engine_v10_5.html | 1594471 | cd3b50f06d3a802c025b3e530e743446d284633961bff0dacd46a656eb7e8ace |
| v10.6 (verified) | swyrl_engine_v10_6.html | 1748442 | 01d7fff6e2a943a326e4582670640d60eec78475c75ab12e16d92c12ee2a9843 |
| v10.7 (verified) | swyrl_engine_v10_7.html | 1833206 | c3f24f05ba745a5e834e964d7e06f0637b57b1115fe242bc86d7920738984ddc |
| v10.8 (candidate) | swyrl_engine_v10_8.html | Final sealed manifest | Final sealed manifest |

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
