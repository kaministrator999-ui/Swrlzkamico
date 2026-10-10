# Anime Studio starter · Ghosts in Different Forms · v9.6 candidate

## Current v9.6 candidate · Natural Staff and Painted Faces

The candidate replaces Kami’s stretched staff grip with a compact painted fist. Rear palm/cuff and front curled fingers/thumb sit on opposite sides of one continuous round shaft. The larger skull/flame crest sits above a visible upper shaft; its narrow join follows the saved **Staff → shaft** socket. The grip is part of the articulated hand, so the fingers, cuff and prop follow the same wrist movement. Kami’s fitted native forearm and wrist form a raised, bent casting pose while the existing timed joint keys retain their movement.

The natural grip belongs to the v9.6 starter’s saved `gripStyle: "natural-v1"` profile. Older projects keep their original painted glove, saved body fit, wrist rotation and grip/staff sockets. Native Save/Load and Undo/Redo retain the selected profile; sharing the bundled body atlas does not opt an older project into the new hand layout.

Both mages use a shared original painted-feature atlas to improve facial readability and match the amber, sepia and bone tones of their robes, armor and skull. The existing expression, blink, mouth, gaze and saved-dialogue controls remain available. Kami’s larger amber irises sit inside shaped eyelids, and §wyrlz’s round skull sockets retain the painted bone shading around the eyes. The head’s raised paper surface carries the animated features through pose and relief changes. Native Preview Frame, Play and Watch share the character renderer.

Facial rendering uses the exact sampled expression, blink, mouth, smile, brow and gaze values when deciding whether to redraw the face texture. A nearby playback sample cannot keep a stale face after Undo, seeking or a fresh Load at the same story time. Face canvases request the same Canvas2D mode when created, keeping Undo/Load rebuilds consistent with heavily inspected previews.

Small gold motes follow the painted staff head through wrist and staff motion. Their positions and brightness derive from story time, so scrubbing, Preview Frame, Play and Watch reproduce the same effect at the same time. The fixed particle pool stays close to the crest and follows the existing **Effects** layer’s visibility and opacity.

Every body piece retains independent **Depth Left**, **Depth Centre**, **Depth Right**, **Paper thickness** and **Costume Flex** settings in **Animation Studio → Character Rig → Character Piece Depth Sections**. Cloth and armor follow saved body movement while limb sockets stay connected. Native Undo/Redo and Save/Load preserve the piece settings, body fits, pose tracks and scenery separately.

The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`. The starter retains its 12-second book opening, 70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, 425 limb/face keys and 341 scenery keys. The candidate has **56 governed patches and 19 media assets**: eight scene JSON exports, ten PNGs and the historical episode HTML. The new artwork is `assets/anime/kami-grip-layers.png` and `assets/anime/mage-faces-painted.png`; all eight earlier PNGs and seven earlier scene exports remain bundled. Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V9_6_NATURAL_STAFF_PAINTED_FACES`; artifact: `swyrl_engine_v9_6.html`.

Validation and hosted deployment are pending. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Production authority belongs to the final `DEPLOY_REQUEST.json`, its exact dedicated deployment run and the hosted audit of the normalized HTML, `SOURCE.json` and all nineteen assets.

## Historical verified v9.5 · Fitted Staff and Character Relief

The v9.5 release is the previous verified checkpoint: [deployment 38013962412](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013962412) and [hosted audit 38013986565](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38013986565) passed. Source `49b82022de841a26a4692359751395ca792efc9f`, final trigger `dcab50950603fb4160615e0d6bf5e0ec8558b06e`, seals 55 patches, 1,075,201 bytes, SHA-256 `bbfee8886ae48164b8bda7864a6d5ae773994a91cd953bea0f1d7820a44ccedb`, and 16 assets. It introduced the saved staff mount and per-piece character relief. These receipts certify v9.5; the v9.6 candidate requires its own final deployment and hosted verification.

## Historical verified v9.4

The previous v9.4 Socket Puppets and Book Emergence release is verified live: [deployment 37942614513](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942614513) and [hosted audit 37942679834](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37942679834) passed. Source `511668bf024b1c225ff3280ef14837152e4602a2`, final trigger `fd1b3812a5445ee335328da7e6a34e1e7c0e1c1d`, seals 53 patches, 1,044,257 bytes, SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`, and 15 assets. These receipts certify v9.4; the v9.6 candidate requires its own final deployment and hosted verification.


## Starter contract

The §wyrl§ Engine Projects hub offers **Ghosts in Different Forms · The Page That Remembered**, a 134 second pop-up book episode authored in the native editor. It is an independent selectable project alongside Embervault and Starforge. Generated transparent artwork places Kami, the larger horn-hooded mage, and §wyrlz, the small hovering skull mage, on their own layers amid gothic amber/gold scenery.

Canonical project ID: `ghosts-different-forms-ep01`
Project selector key: `anime-ghosts-ep01`. [Direct starter URL](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01).

- 70 uniquely identified actors and 11 editor layers
- Eight new saved paper actors, each owning a layer, alongside the original 62 production set actors and three layers
- Eight story beats and nine independent camera/cast/scenery/book tracks spanning 134 seconds
- Eight preserved production stages, travel zones, and editable workstations, with the original guardian and visitor
- Independent jointed Kami/§wyrlz paper rigs with thickness, pop-out depth, body-part X/Y/Z rotation/depth keys, and facial expression/blink/mouth/gaze keys saved under `project.animeRigs`
- Native **Animation Studio** keyframe, title, and timed dialogue editing, Preview Frame, native Undo/Redo, and Save/Load
- PNG/WebP/JPEG layer artwork replacement; separate bundled character and scenery PNGs
- **Capture Actor Pose** workflow transfers a saved actor's native Inspector transforms to a timeline keyframe
- Native editor **Play** runs the same paper theatre renderer as Preview Frame; **Explore Set** returns to ordinary walking Play/T-zone mode
- **Watch Episode 01** opens a pop-up cinema with the same native 2.5D scene and chapter controls; the original procedural episode HTML remains bundled
- Bundled artwork and screening assets require no paid generation service during playback

## Socket puppets and book emergence

The existing coordinated opening brings Kami, §wyrlz, architecture, props, effects and the three star-depth shells out of the pages before they reach their saved stage positions. Preview Frame, Play and Watch use the same saved opening. Persistent limb sockets keep snapped children attached while their pose keys rotate around the connection.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Existing per-character rest layouts, 425 limb/face keys and 341 scenery keys remain independent. The v9.5 staff-grip, v9.4 sockets, v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all ten artwork PNGs and the historical episode HTML.

## Layered scenery and fitted faces

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`; the v9.2 depth, v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

## Animation behavior and boundaries

The saved `anime-timeline-v1` timeline animates camera position, target, and field of view; separate Kami and §wyrlz transforms; layered scenery; and book opening. Animation Studio exposes add/update/delete keys, Linear/Smooth/Hold easing, opacity, visibility, unfolding, titles, and dialogue cues. Native **Preview Frame** and **Play** share the renderer, while physical scenery planes fold around bottom-edge hinges at distinct depths. Protective background depth, a low foreground/book, and adaptive portrait framing prevent scenery from filling the central camera corridor.

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

These are jointed 2.5D paper characters with overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

v9.6 is a source candidate. Desktop/phone acceptance must inspect the compact grip, continuous round shaft and crest proportions, larger painted facial features, expression motion, piece depth and connected sockets in native Play and Watch. All seven existing native cinematic, Studio, rig, scenery, body-fit, book-opening and relief suites, exact sealed reconstruction and six remote engine CI checks must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all nineteen media assets.

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v9.6 requires its own final deployment and hosted audit.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

## Source files

- Current native Save Project export: `scenes/ghosts-in-different-forms-ep01-natural-grip.swyrl.json`
- Preserved v9.5 native export: `scenes/ghosts-in-different-forms-ep01-staff-grip.swyrl.json`
- Preserved v9.4 native export: `scenes/ghosts-in-different-forms-ep01-sockets.swyrl.json`
- Preserved v9.3 native export: `scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json`
- Preserved v9.2 native export: `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`
- Preserved v9.1 native export: `scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json`
- Preserved v9.0 native export: `scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json`
- Preserved original production scene: `scenes/ghosts-in-different-forms-ep01.swyrl.json`
- Independent artwork: `assets/anime/`, including separate `kami-rig.png` and `swyrlz-rig.png` body-part atlases and `scenery-parts.png` scenery atlas
- Historical episode media: `episodes/ghosts-in-different-forms-ep01.html`
- Native pop-up cinema: `runtime/anime_screening.js` and `runtime/anime_screening.css`
- Reusable timeline, stage, and UI: `runtime/anime_timeline.js`, `runtime/anime_stage.js`, `runtime/anime_editor.js`, and their CSS
- Saved character poses, cutout renderer, and rig UI: `runtime/anime_rig_model.js`, `runtime/anime_rig_renderer.js`, `runtime/anime_rig_editor.js`, and `runtime/anime_rig_editor.css`
- Saved scenery model, layered renderer and object-key UI: `runtime/anime_scenery_model.js`, `runtime/anime_scenery_renderer.js`, `runtime/anime_scenery_editor.js`, and `runtime/anime_scenery_editor.css`
- Saved per-piece section relief and costume motion: `runtime/anime_relief_model.js`, `runtime/anime_relief_renderer.js`, `runtime/anime_relief_editor.js` and `runtime/anime_relief_editor.css`
- Current integration: `patches/v9_6_natural_staff_painted_faces.py`; the v9.5 staff mount and per-piece relief remain in `patches/v9_5_staff_grip_fit.py` and `patches/v9_5_character_depth_sections.py`; the v9.4 sockets/opening, v9.3 fitting, v9.2 scenery, v9.1 rigs, v9.0 Studio and historical starter integrations remain in the governed chain
- Governed build packaging: `build_space.py`

## Acceptance tests

1. Projects hub shows Anime Studio alongside Embervault and Starforge; pressing Play starts native cinematic, not an unexplained first-person aerial view.
2. Opening Anime Studio loads 70 actors, 11 layers, eight stations, eight destinations, and the saved 134 second/nine track/eight beat episode.
3. Native keyframe/title/dialogue and limb/face/depth edits, Undo/Redo, artwork replacement, and Save/Load preserve independent project data. Joint rotation must visibly move the selected body part in depth while leaving the companion's tracks unchanged; expression/blink/mouth keys must render in Preview and Play. Capture Actor Pose must preserve the selected native Inspector pose in the intended stage track keyframe.
4. Preview and editor Play use the saved camera/cast/scenery/book keys, advance time, display dialogue, and accept Pause/scrub/next. Desktop and portrait shots retain both mages with safe scenery depths; Stop restores the editor camera. Explore Set returns to first-person Play > T with eight destinations.
5. Watch Episode opens the pop-up cinema using the same authored native scene, canvas, chapter navigation, and transport HUD without navigating away or overwriting editor data.
6. Closing the cinema stops its runtime, restores the canvas and editor camera to the workspace, and returns focus.
7. Direct `?project=anime-ghosts-ep01` boots the same starter.
8. Starting a different project hides the screening control. Returning to Anime Studio restores it.
9. Existing Embervault and Starforge remain unchanged.
10. Every character piece retains left/centre/right depth, thickness and costume flex through native edits, Undo/Redo and Save/Load. Actual surface geometry must follow animated body motion without separating limb sockets or facial features.
11. Engine reconstruction, native module syntax, bundled-screening integrity, and served-host hashes must pass before claiming production success.

## Future capability probes

- Reusable pose clips and full sculpted/skinned character rigs
- Lip sync and audio recording/import
- Exportable video capture and reproducible render settings

See [ANIMATION_STUDIO.md](ANIMATION_STUDIO.md) for the authoring workflow and [VERIFICATION.md](VERIFICATION.md) for current and historical evidence.

## Historical v9.0 authoring checkpoint

The previous native storybook export is [ghosts-in-different-forms-ep01-storybook.swyrl.json](scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json). Its separate whole-character/scenery/camera timeline authoring and desktop/phone Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555), before joint and face tracks were introduced. The source and older release receipts remain preserved.

## Historical v8.8 · Animated Storybook Video Creator starter

The native anime project now stages a book-shaped Three.js prop with page thickness, two opening page halves and multiple scenery cards that **unfold from the book** at separately editable times. The illustrated wizard art is redrawn in source code from the dark-fantasy sketch direction: Kami is the larger horn-hooded staff wizard, and §wyrlz is the smaller floating, book-holding skeletal mage. They are **different cels and different toggleable layers** (rather than a shared image).

The in-editor **✦ Pop-Up Director** gives each background, atmosphere, cathedral/workshop, Kami, §wyrlz, effects and foreground layer independently saved Z depth, side position, parallax, unfold delay and duration. Save Project includes `project.animePopUp`. All visuals use CanvasTexture, not paid generative image requests. This is a procedural dark-fantasy rendition, not a pixel-perfect extraction of earlier artwork. See [POPUP_VIDEO_CREATOR.md](POPUP_VIDEO_CREATOR.md).

## v8.7 · 2D anime cels with 3D parallax (historical)

The Anime Studio **Play** cinematic now uses a layered **2.5D cel compositor**, responding to real phone screenshots from v8.6:

- Six independently visible native render layers: **background sky**, **atmosphere**, **midground architecture**, **character cels**, **magic effects**, and **foreground framing**.
- Flat, thick-outlined anime-style characters are original procedural canvas textures mapped to perspective-aware `THREE.Sprite` cels. They are not photorealistic 3D avatars or external static screenshots.
- Each layer is positioned at a different camera depth; camera movement gives genuine parallax. **Layers** control in the cinematic HUD toggles each layer while inspecting the result.
- Existing saved level actors, signs, workstations, archways, and the guardian are **temporarily hidden while watching**, so no giant in-world signs cross the screen. Stop/Explore Set restores every actor's previous visibility.
- Subtitle overlay wraps and stays within the mobile viewport instead of competing with in-world signage.
- Editor stage, workspace scripts, teleport destinations, asset/source lineage, and normal Play for other templates are preserved.

**Limit:** Layer visibility is a runtime inspection tool in v8.7, not yet a fully editable timeline/rig/cel sequence editor; the illustrated cels and shot choreography are generated by the engine patch. This is precisely the next starter-pack limit to exercise.

## Native cinematic acceptance · v8.6

The [Chromium browser run](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407234) passed both 1280×800 desktop and 390×844 phone layouts. It clicks Play, checks continuous clock and moving camera, rendered HUD/dialogue, seeks to the dragon shot, pauses, selects Explore Set, and stops with no uncaught page errors. The [full 45-patch candidate reconstruction](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37719407233) passed module/Python syntax checks. Live host receipt remains a separate production gate.
