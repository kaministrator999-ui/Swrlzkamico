---
title: §wyrl§ Engine v9.1
emoji: 🐉
colorFrom: purple
colorTo: blue
sdk: static
app_file: index.html
fullWidth: true
header: mini
short_description: Dragon Den, Starforge and Anime Studio workspaces.
---

# §wyrl§ Engine · Maker v9.1

**Embervault Atelier** is a three-tier Dragon Den with six project stations, walkable ramps, and eight named destinations. **Starforge Observatory** is a separate floating-island workspace with physical bridges and ramps, six stations, and seven destinations beneath a constellation sky.

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

Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_1_ARTICULATED_PAPER_RIGS`


### Release verification

v9.1 is a source candidate. Rig-specific desktop/phone authoring and Play checks, the sealed build, and production deployment receipts must be completed before this revision is called verified live. The previous v9.0 native authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555); its proof remains historical. Production authority is recorded in the final `DEPLOY_REQUEST.json`, dedicated deployment receipt, and exact hosted-release audit. Earlier releases and their receipts remain in the source roadmap and verification document.
