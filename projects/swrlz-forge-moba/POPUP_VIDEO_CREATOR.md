# Video Creator Starter · Articulated Pop-Up Book · v9.4 candidate

The v9.4 source candidate gives the episode a coordinated book opening: Kami, §wyrlz, architecture, props, effects and the three star-depth shells emerge from the pages before reaching their saved stage positions. The opening uses the same renderer and saved project data in Preview Frame, Play and Watch. Character limbs have persistent connection sockets; snapped children stay attached while their pose keys rotate around the socket. Kami’s visible staff grip and staff placement are repaired within the articulated paper rig.

In **Animation Studio → Book Opening · unfold from the pages**, enable **Expand from book** and set **Opening duration (s)**. Choose an **Opening layer**, adjust **Start delay (s)** and **Expansion time (s)**, then use **Apply Book Opening**. Preview the first seconds and use Play to inspect the expansion. Changing the overall duration scales the other layers’ timings; every layer must finish within the opening. Native Undo/Redo and Save/Load preserve the opening separately from the stage, limb, face and scenery keys.

To connect and pose a limb, select **Kami** or **§wyrlz** in Animation Studio and expand **Character Rig · limbs and face → Limb Sockets · snap and rotate**. Choose a **Socket body piece** and its incoming attachment or a named outgoing socket. **Socket X/Y/Z** use the painted piece’s centre: incoming **attach** defines the rotation pivot, while an outgoing socket places its attached child. Use **Apply Socket** to place the connection. **Detach Piece** releases the selected child; **Snap to Socket** reconnects it to its anatomical parent. Animate the snapped limb with the existing pose controls. **Show joint sockets** displays editor guides; Running Play and Watch hide those guides. **Reset Piece Sockets** restores the selected connections while preserving pose keys. Snapped pieces stay connected through shoulder, elbow, wrist, hip, knee and ankle motion; each hand has a prop grip.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The current native Save Project export is `scenes/ghosts-in-different-forms-ep01-sockets.swyrl.json`. Each character has 19 socket-bearing parts and 18 anatomical connections. Connections belong to `project.animeSockets` (`anime-rig-sockets-v1`) and the opening to `project.animeEmergence` (`anime-book-emergence-v1`). Existing per-character rest layouts, 425 limb/face keys and 341 scenery keys remain independent. The v9.3 positioned, v9.2 depth, v9.1 rigged, v9.0 storybook and original production exports remain bundled, together with all eight artwork PNGs and the historical episode HTML.

The 53rd governed patch is `patches/v9_4_socket_book_emergence.py`; artifact `swyrl_engine_v9_4.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_4_SOCKET_PUPPETS_BOOK_EMERGENCE`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging includes six episode scene JSON exports, the historical episode HTML and eight PNGs, for fifteen media assets.

v9.4 is a source candidate. Desktop/phone socket connection and book-emergence acceptance, all existing native Play/Studio/rig/depth/body-fit regressions, exact sealed reconstruction, and remote engine CI must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all fifteen media assets.

## Historical verified v9.3 · Connected Character Pieces

The previous **v9.3 Connected Character Pieces** release is verified live: [deployment 37893678594](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893678594) and [exact hosted audit 37893722231](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37893722231) passed. Source [`84d8966f4240`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/84d8966f4240cef8ebe037dbc03baac43099c06e) seals 52 patches, **980,767 bytes**, SHA-256 `caba518b67524567899d93a74308bc894cf40413fd69b330b8f7f5f7b6c042be`, with all fourteen media assets. These receipts certify v9.3; v9.4 requires its own final deployment and hosted audit.

## Historical verified v9.2 · Layered Scenery and Fitted Faces

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`; the v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

The 51st governed patch is `patches/v9_2_depth_theatre.py`; artifact `swyrl_engine_v9_2.html`; marker `SWYRL_ENGINE_DEPLOY_MARKER: V9_2_LAYERED_SCENERY_FACES`. Exact bytes and SHA-256 belong to the final sealed manifest and generated receipt. Packaging includes four episode scene JSON exports, the historical episode HTML, and eight PNGs including the new transparent `assets/anime/scenery-parts.png` atlas.

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

The project keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Limb and face tracks live separately under `project.animeRigs` (`anime-character-rigs-v1`), so posing one mage does not overwrite the other mage or the existing shot timeline. The prior v9.1 native rig export is `scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json`; it remains bundled with the v9.0 storybook export and original 62-actor production scene.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

Layered scenery, independent book controls, camera tracks, captions, and protective foreground/background staging continue through the same Preview Frame and editor Play renderer. Paper joints add local depth and articulation inside each independent character layer.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify the historical v9.2 release.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

See [ANIMATION_STUDIO.md](ANIMATION_STUDIO.md) for controls and [VERIFICATION.md](VERIFICATION.md) for evidence. [Open the starter](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01).

## Historical v9.0 · Native Pop-Up Storybook

**Ghosts in Different Forms · The Page That Remembered** is a 134 second, eight beat episode authored and exported through the native editor. Its 70 actors and 11 layers preserve the original 62 production set actors and three layers while adding eight independently saved paper actors/layers. The camera and each cast/scenery/book layer have their own timeline track, for nine tracks in total.

Generated transparent PNGs give Kami, the larger horn-hooded mage, and §wyrlz, the little hovering skull mage, separate detailed gothic anime silhouettes. Background cathedral, workshop, and foreground plates are separate assets; mist and runes are generated by the engine. The physical book has opening page geometry, and scenery meshes fold around bottom-edge hinges. Playback uses bundled assets without a paid generation service.

Open **Animation Studio** to scrub and preview, add/update/delete keys, edit camera position/target/FOV, individual transforms, easing, visibility, opacity, unfolding, titles, and timed dialogue. Native Undo/Redo and Save/Load preserve changes. PNG/WebP/JPEG imports replace one selected artwork layer. **Capture Actor Pose** workflow copies a saved layer actor's native Inspector pose into the playhead's keyframe. **Preview Frame** and editor **Play** use the same native renderer.

Protective scenery depth keeps architecture and magic behind both characters. The foreground paints a low strip and the book stays below the cast; fold direction moves scenery away from the camera. Portrait framing increases camera distance to retain both mages. These safeguards apply to edited timeline values. Pause, seek, Layers, Stop, and Explore Set remain available. The separate Watch Episode 01 button preserves the historical procedural 2D screening.

Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Production authority is recorded in the final `DEPLOY_REQUEST.json`, the dedicated deployment receipt, and the exact hosted-release audit. Skeletal posing, lip sync, audio authoring, and MP4 export remain unimplemented. See [ANIMATION_STUDIO.md](ANIMATION_STUDIO.md) for controls and [VERIFICATION.md](VERIFICATION.md) for evidence. [Open the starter](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01).

## Historical v8.8 implementation · Procedural Pop-Up Storybook

This is an extension of the existing **Ghosts in Different Forms** Anime Studio starter in §wyrl§ Engine, not a separate game, new app, or image.

## Historical v8.8 · Art direction

The staged episode is a dark-fantasy **book theatre**, following the user's wizard sketches and the two-character concept-art direction.

- **Kami:** larger horn-hooded fantasy wizard with layered robes, broad hair coverage, ornamental belts, burning-skull staff and rune details.
- **§wyrlz:** separate smaller hovering skeletal wizard, deliberate pointed mage hat and floating grimoire.
- **Scenery:** hand-rendered CanvasTexture cutout plates for a moonlit distant city, magical atmospheric flourishes, gothic cathedral archways, workshop shelves, painted runes, desk props, and a *real Three.js page-thickness book model*.
- **No extra mascot character** in the cinematic. The original canonical guardian object stays in the editor starter so older dialogue/stations and exploratory project content are not deleted.
- **No external images, generation service or remote asset provider** required at runtime. The artwork is procedural/vector-style; it is a dark-fantasy interpretation of the reference concept, not a pixel-perfect recreation of the earlier illustration.

## Historical v8.9 · Camera-safe pop-up scenery staging

Real Android screenshots of v8.8 showed the large opaque desk/foreground panel and animated book rising *in front of the camera and character cels*. Corrective engine patch `patches/v8_9_cinematic_staging.py` keeps the physical book below the wizard cutouts, replaces the opaque foreground panel with a thin transparent-trim plate that only paints its bottom portion, and clamps cathedral/sky/magic scenery behind both independent wizard cels. The effect still uses actual Three.js depth/perspective and independent hinges. Older saved `animePopUp` Director values remain serialized, but scenery render staging enforces a safe maximum so dangerous near-camera cards cannot obscure the cast. Runtime `popUpStatus().stageSafety` exposes book height, foreground painted boundary, actors and architecture Z values, and camera gap. Desktop and mobile automated regressions check first/later scene layouts against those boundaries.

This release is **not** verified live until exact rebuilt source and hosted assets pass production receipt checks.

## Historical v8.8 · Engine behavior

At each of the existing eight episode acts, the physical open book and scenery **unfold from the page** on independent Three.js pivots. Every cutout is an individual depth plane with separate parallax and unfold delay. The perspective camera can travel past those planes without flattening them into a single backdrop.

The Pop-Up Director is available while the Anime Studio starter is loaded. Each layer can separately configure:

| Setting | Range | Stored |
|---|---:|---|
| Z depth | -28 to +6 | Yes |
| Side position | -4 to +4 | Yes |
| Parallax factor | 0 to 1.5 | Yes |
| Unfold delay | 0 to 4 sec | Yes |
| Unfold time | 0.25 to 4 sec | Yes |

**Kami** and **§wyrlz** are individually adjustable character cels rather than a single flattened character image. The older aggregate Characters layer remains as a compatibility visibility toggle. The six historical background/atmosphere/midground/characters/effects/foreground layers remain, with new individual Kami, §wyrlz and Guardian visibility entries.

On phone-width views, **Pop-Up Director → Save Project** explicitly invokes the normal editor's project export, even if the original Save toolbar item is out of view.

Save Project exports all Director values under `project.animePopUp` with schema `anime-popup-v1`. On Load Project, finite numeric values are sanitized and clamped to safe ranges. Project export does not require localStorage, internet or a paid runtime. This setting applies **only** to the Anime Studio starter. The original §E Dragon Den, Starforge and other starter projects retain their Play behavior.

The in-editor Play HUD still provides seek, Pause, next/previous scene, Layers, Stop and Explore Set. Scene script captions remain in the existing editable act workstations.

## Historical v8.8 · Capability boundaries

The cel artwork is still authored procedurally in the engine source, not yet an SVG/PNG asset-import or skeletal rig/puppet editor. Director supports basic depth/parallax/position/unfold animation parameters, not arbitrary timelines and bone posing. No claim of finished video export, lip sync or full character animation.

## Acceptance tests

- Reconstruct source from every governed patch; verify SHA, bytes and generated module syntax.
- Desktop Chromium and mobile-sized Chromium load Anime Studio and start native Play.
- Eight scripted scenes, physical popup book, at least five distinct hinged scenery plates, separate Kami/§wyrlz cels and ordered Z depth.
- Director UI changes each wizard independently; Save Project downloaded JSON retains parameters.
- Layer visibility toggles, caption bounds, seek, Pause, Explore Set, Stop and original actor restoration.
- No uncaught browser errors; no regression to Embervault and Starforge.
- Deploy only using the repository's governed `DEPLOY_REQUEST.json`; verify the exact HTML/asset receipt from the served dedicated HF Space.
