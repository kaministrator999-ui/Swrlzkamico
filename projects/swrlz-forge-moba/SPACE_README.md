---
title: §wyrl§ Engine v9.5
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Jointed anime paper theatre, Dragon Den and Starforge.
---

# §wyrl§ Engine · Maker v9.5

## Current v9.5 candidate · Fitted Staff and Character Relief

Kami’s gripping hand wraps from the viewer’s left toward the right around the upright staff. The staff head’s opaque painted gold stem now joins the long pole at a saved **Staff → shaft** socket, with the brass collar behind the artwork. Fitting the staff’s width and height updates this mount in the same native Undo action. In **Animation Studio → Character Rig → Limb Sockets**, choose **Staff** and **Outgoing · shaft**, then use **Apply Socket** to adjust the join.

Every body piece of Kami and §wyrlz has three separately editable depth sections. Raised armor and folds give the painted pieces volume, while cloth and armor flex with the character’s saved motion. Connection points stay pinned to their limb sockets; expressions follow the head’s relief. These settings belong to each character and body piece, so editing one piece preserves the other mage and all pose, face and scenery keys. Preview Frame, native Play and Watch render the same geometry; native Undo/Redo and Save/Load retain the section settings.

In **Animation Studio**, select **Kami** or **§wyrlz** and expand **Character Rig → Character Piece Depth Sections**. Choose a **Depth body piece**, adjust **Depth Left**, **Depth Centre**, **Depth Right**, **Paper thickness** and **Costume Flex**, then use **Apply Piece Depth**. **Reset Piece Depth** restores that piece’s defaults. Pause playback before authoring, and use Preview Frame or Play to inspect how the robe and armor follow the pose. A flex value of 0 keeps the piece rigid.

The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json`. The starter retains its 12-second book opening, 70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, 425 limb/face keys and 341 scenery keys. The v9.4 sockets export and all earlier exports remain bundled. The candidate has **55 governed patches and 16 media assets**: seven scene JSON files, eight unchanged PNGs and the historical episode HTML. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_5_FITTED_STAFF_CHARACTER_RELIEF`; artifact: `swyrl_engine_v9_5.html`.

Validation and hosted deployment are pending. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Production authority belongs to the final `DEPLOY_REQUEST.json`, its exact dedicated deployment run and the hosted audit of the normalized HTML, `SOURCE.json` and all sixteen assets.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v9.5 candidate requires its own final deployment and hosted verification.


**Embervault Atelier** is a three-tier Dragon Den with six project stations, walkable ramps, and eight named destinations. **Starforge Observatory** is a separate floating-island workspace with physical bridges and ramps, six stations, and seven destinations beneath a constellation sky.

## Socket puppets and book emergence

The existing coordinated opening brings Kami, §wyrlz, architecture, props, effects and the three star-depth shells out of the pages before they reach their saved stage positions. Preview Frame, Play and Watch use the same saved opening. Persistent limb sockets keep snapped children attached while their pose keys rotate around the connection.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json`. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Existing per-character rest layouts, 425 limb/face keys and 341 scenery keys remain independent. The v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all eight artwork PNGs and the historical episode HTML.

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json`; the v9.2 depth, v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

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

Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_5_FITTED_STAFF_CHARACTER_RELIEF`


### Release verification

v9.5 is a source candidate. Desktop/phone acceptance must verify the painted staff-to-pole join, the right-facing grip, each piece’s section depth and motion, socket connections, native Undo/Redo and Save/Load. All existing native Play/Studio/rig/scenery/body-fit/book-opening regressions, exact sealed reconstruction and remote engine CI must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all sixteen media assets.

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v9.5 requires its own final deployment and hosted audit.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2. Earlier releases and their receipts remain in the source roadmap and verification document.
