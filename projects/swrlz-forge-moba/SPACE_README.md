---
title: §wyrl§ Engine v9.7
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Jointed anime paper theatre, Dragon Den and Starforge.
---

# §wyrl§ Engine · Maker v9.7

## Current v9.7 candidate · Ornate Mage Staff

The candidate refines Kami’s existing staff with painted-style shaft detail and fitted brass ornament. The continuous round wooden pole, compact rear palm/cuff and separate front fingers/thumb remain connected through the existing wrist and **Staff → shaft** sockets. The painted skull/flame crest retains its proportions above the hand. The ornament belongs to the same staff assembly, so it follows fitted poses, animated rotations and book emergence in Preview Frame, Play and Watch.

The refinement applies only to Kami’s saved `gripStyle: "natural-v1"` profile with the bundled `assets/anime/kami-rig.png` artwork. Older original-grip projects and imported character atlases retain their existing artwork, body fit and prop sockets. No pose keys, socket coordinates or project schemas change. Native Undo/Redo and Save/Load retain the saved character profile and fitting.

The larger painted facial features, exact sampled expression/blink/mouth/gaze controls and opacity-preserving mouth blending from v9.6 remain available. Each character piece retains separate **Depth Left**, **Depth Centre**, **Depth Right**, **Paper thickness** and **Costume Flex** settings. Cloth and armor follow the saved body movement while limb sockets stay connected. The layered scenery, three star-depth shells and authored camera continue to provide perspective depth around the mages.

Small gold motes follow the painted staff head through wrist and staff motion. Their positions and brightness derive from story time, so scrubbing, Preview Frame, Play and Watch reproduce the same effect at the same time. The bounded effect follows the existing **Effects** layer’s visibility and opacity.

The current native Save Project export remains `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`. The starter retains its 12-second book opening, 70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, 425 limb/face keys, 341 scenery keys and 134-second episode. The candidate has **57 governed patches and the same 19 media assets**: eight scene JSON exports, ten PNGs and the historical episode HTML. No new artwork or scene export replaces the preserved package. Patch: `patches/v9_7_ornate_staff.py`; runtime: `runtime/anime_staff_ornament.js`; marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_7_ORNATE_MAGE_STAFF`; artifact: `swyrl_engine_v9_7.html`.

Validation and hosted deployment are pending. Desktop/phone acceptance must inspect the staff fittings, continuous shaft, compact grip, socket alignment and shared Preview/Play/Watch rendering. All seven existing browser suites, exact sealed reconstruction and six remote engine CI checks remain required. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Production authority belongs to the final `DEPLOY_REQUEST.json`, its exact dedicated deployment run and the hosted audit of the normalized HTML, `SOURCE.json` and all nineteen assets.

## Historical verified v9.6 · Natural Staff and Painted Faces

The v9.6 release is verified live: [deployment 38071280266](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38071280266) and [hosted audit 38071311391](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38071311391) passed on final trigger `f164ccd37ce8ffd28cbc28ce4dea9b4f64ed7178`. Merged source `b21f0dd3072ada0f157e4f75b041c008d861a8cb` seals **56 patches, 1,099,583 bytes**, SHA-256 `d78dedc68ae0fe7bcbd368ee949bb2926c6f9bf321586e5254ad3fb97c1f07bd`, and nineteen assets. It introduced the saved natural-grip profile, continuous round shaft, fitted crest, larger painted facial features, exact face-cache inputs, consistent Canvas rasterization, opacity-preserving mouth blending and deterministic staff motes. All seven desktop/phone browser suites passed before deployment; hosted native Play and Watch passed on desktop and phone. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_6_NATURAL_STAFF_PAINTED_FACES`; artifact: `swyrl_engine_v9_6.html`. These receipts certify v9.6; the v9.7 candidate requires its own final deployment and hosted verification.

## Historical verified v9.5 · Fitted Staff and Character Relief

The v9.5 release is the previous verified checkpoint: [deployment 38013962412](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013962412) and [hosted audit 38013986565](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013986565) passed. Source `49b82022de841a26a4692359751395ca792efc9f`, final trigger `dcab50950603fb4160615e0d6bf5e0ec8558b06e`, seals 55 patches, 1,075,201 bytes, SHA-256 `bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb`, and 16 assets. It introduced the saved staff mount and per-piece character relief. These receipts certify v9.5; the v9.7 candidate requires its own final deployment and hosted verification.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v9.7 candidate requires its own final deployment and hosted verification.


**Embervault Atelier** is a three-tier Dragon Den with six project stations, walkable ramps, and eight named destinations. **Starforge Observatory** is a separate floating-island workspace with physical bridges and ramps, six stations, and seven destinations beneath a constellation sky.

## Socket puppets and book emergence

The existing coordinated opening brings Kami, §wyrlz, architecture, props, effects and the three star-depth shells out of the pages before they reach their saved stage positions. Preview Frame, Play and Watch use the same saved opening. Persistent limb sockets keep snapped children attached while their pose keys rotate around the connection.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Existing per-character rest layouts, 425 limb/face keys and 341 scenery keys remain independent. The v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all ten artwork PNGs and the historical episode HTML.

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`; the v9.2 depth, v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

**Ghosts in Different Forms · The Page That Remembered** is the third selectable Projects starter: a 134 second, eight beat anime pop-up book episode with 70 actors, 11 editor layers, and nine independent saved animation tracks. Eight new paper actors/layers join the preserved original 62 production set actors, three layers, eight destinations, and eight workstations. Generated transparent artwork depicts **Kami**, the larger horn-hooded mage, and **§wyrlz**, the smaller hovering skull mage, with separate layered gothic scenery.

Open [Anime Studio directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01) or use Projects. **Animation Studio** edits camera position/target/FOV, character/scenery/book keyframes, easing, opacity, visibility, unfolding, titles, and timed dialogue. Scrub, **Preview Frame**, and the editor **Play** button use the same native renderer. PNG/WebP/JPEG imports replace individual artwork; native Undo/Redo and Save/Load preserve edits. **Capture Actor Pose** workflow copies native Inspector transforms to the selected track keyframe.

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

Physical mesh scenery folds around hinges, and protective background depth, a low foreground/book, and adaptive portrait framing keep the mages clear. Pause, seek, Stop, and **Explore Set** remain available. Pose data is saved under `project.animeRigs`. These are jointed 2.5D paper characters with overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history. Playback uses bundled art without a paid generation service.

Use WASD/arrows and mouse look in Play. Press **T** or **Zones** to travel, and approach a station then press **E** / **Open** to edit files and notes. Download files, transfer workspace JSON, or **Save Project** to preserve the scene, destinations, environment, and station work. Chat stations open the existing §wyrlz LALM chat in a new tab.

Choose Starforge in Projects or [open it directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=starforge-observatory). The native editor provides reusable architecture and island assets, grouped transforms, project-owned layers, signs, workstations, and editable teleport zones. Enable **Show destination markers** for optional landing rings and heading arrows; the device preference starts off by default, and **Frame Destination** keeps the current orthographic viewing axis. These helpers stay in the editor and are excluded from collision and saved scenes. Travel validates supported, clear landings and restores the prior pause state; Starforge can return a fallen visitor to Arrival.

The den arrival directory and Starforge Garden guide sit beside circulation routes, keeping project pads and paths open.

**Graphics & Performance** provides Auto/Low/Medium/High/Custom presets, render scale, shadows, frame caps, and separate Editor/Play diagnostics. Preferences persist locally.

Desktop first-person verification is recorded with the source. Headset VR, VR controller input, in-room AI conversation, and executing project code are future integrations.

Source: https://github.com/kaministrator999-ui/Swrlzkamico/tree/main/projects/swrlz-forge-moba

Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_7_ORNATE_MAGE_STAFF`


### Release verification

v9.7 is a source candidate. Desktop/phone acceptance must inspect the fitted staff ornament, continuous round shaft and crest proportions, compact grip, painted facial features, expression motion, piece depth and connected sockets in native Play and Watch. All seven existing native cinematic, Studio, rig, scenery, body-fit, book-opening and relief suites, exact sealed reconstruction and six remote engine CI checks must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all nineteen media assets.

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v9.7 requires its own final deployment and hosted audit.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2. Earlier releases and their receipts remain in the source roadmap and verification document.
