---
title: §wyrl§ Engine v9.3
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Jointed anime paper theatre, Dragon Den and Starforge.
---

# §wyrl§ Engine · Maker v9.3

**Embervault Atelier** is a three-tier Dragon Den with six project stations, walkable ramps, and eight named destinations. **Starforge Observatory** is a separate floating-island workspace with physical bridges and ramps, six stations, and seven destinations beneath a constellation sky.

## Connected character pieces

v9.3 fits each mage’s body pieces to its own painted silhouette: shoulders, elbows, wrists, hips, knees, ankles and the head use corrected attachment placement and overlap. Staff, quill and grimoire placement follows the owning hand. Kami and §wyrlz retain separate eighteen-piece paper rigs, fitted facial controls and independent animation tracks. The engine samples the bundled transparent artwork directly; no flattened replacement character is introduced.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json`. Per-character rest layouts belong to `project.animeRigs.characters[character].layout`, alongside the independent limb/face keys. The saved performance retains 425 limb/face keys and 341 scenery keys. The v9.2 depth, v9.1 rigged, v9.0 storybook and original production scene exports remain bundled, together with all eight artwork PNGs and the historical episode HTML.

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json`; the v9.2 depth, v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

**Ghosts in Different Forms · The Page That Remembered** is the third selectable Projects starter: a 134 second, eight beat anime pop-up book episode with 70 actors, 11 editor layers, and nine independent saved animation tracks. Eight new paper actors/layers join the preserved original 62 production set actors, three layers, eight destinations, and eight workstations. Generated transparent artwork depicts **Kami**, the larger horn-hooded mage, and **§wyrlz**, the smaller hovering skull mage, with separate layered gothic scenery.

Open [Anime Studio directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01) or use Projects. **Animation Studio** edits camera position/target/FOV, character/scenery/book keyframes, easing, opacity, visibility, unfolding, titles, and timed dialogue. Scrub, **Preview Frame**, and the editor **Play** button use the same native renderer. PNG/WebP/JPEG imports replace individual artwork; native Undo/Redo and Save/Load preserve edits. **Capture Actor Pose** workflow copies native Inspector transforms to the selected track keyframe.

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

Physical mesh scenery folds around hinges, and protective background depth, a low foreground/book, and adaptive portrait framing keep the mages clear. Pause, seek, Stop, and **Explore Set** remain available. Pose data is saved under `project.animeRigs`. These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history. Playback uses bundled art without a paid generation service.

Use WASD/arrows and mouse look in Play. Press **T** or **Zones** to travel, and approach a station then press **E** / **Open** to edit files and notes. Download files, transfer workspace JSON, or **Save Project** to preserve the scene, destinations, environment, and station work. Chat stations open the existing §wyrlz LALM chat in a new tab.

Choose Starforge in Projects or [open it directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=starforge-observatory). The native editor provides reusable architecture and island assets, grouped transforms, project-owned layers, signs, workstations, and editable teleport zones. Enable **Show destination markers** for optional landing rings and heading arrows; the device preference starts off by default, and **Frame Destination** keeps the current orthographic viewing axis. These helpers stay in the editor and are excluded from collision and saved scenes. Travel validates supported, clear landings and restores the prior pause state; Starforge can return a fallen visitor to Arrival.

The den arrival directory and Starforge Garden guide sit beside circulation routes, keeping project pads and paths open.

**Graphics & Performance** provides Auto/Low/Medium/High/Custom presets, render scale, shadows, frame caps, and separate Editor/Play diagnostics. Preferences persist locally.

Desktop first-person verification is recorded with the source. Headset VR, VR controller input, in-room AI conversation, and executing project code are future integrations.

Source: https://github.com/kaministrator999-ui/Swrlzkamico/tree/main/projects/swrlz-forge-moba

Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_3_CONNECTED_CHARACTER_PIECES`


### Release verification

v9.3 is a source candidate. Desktop/phone connected-part fitting and authoring acceptance, the existing native Play/Studio/rig/depth regressions, exact sealed reconstruction, and remote engine CI must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all fourteen media assets.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify v9.2; v9.3 needs its own final deployment and hosted audit.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2. Earlier releases and their receipts remain in the source roadmap and verification document.
