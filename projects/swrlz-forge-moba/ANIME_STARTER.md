# Anime Studio starter · Ghosts in Different Forms · v9.2 candidate

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

## Layered scenery and fitted faces

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

The episode keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. Independent scenery pieces live beneath the saved scenery actors; their keys belong to `project.animeScenery` (`anime-scenery-v1`), alongside the existing `project.animeRigs` and `project.animeTimeline`. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`; the v9.1 rigged, v9.0 storybook and original production scene exports remain bundled.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

## Animation behavior and boundaries

The saved `anime-timeline-v1` timeline animates camera position, target, and field of view; separate Kami and §wyrlz transforms; layered scenery; and book opening. Animation Studio exposes add/update/delete keys, Linear/Smooth/Hold easing, opacity, visibility, unfolding, titles, and dialogue cues. Native **Preview Frame** and **Play** share the renderer, while physical scenery planes fold around bottom-edge hinges at distinct depths. Protective background depth, a low foreground/book, and adaptive portrait framing prevent scenery from filling the central camera corridor.

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

v9.2 is a source candidate. Desktop/phone depth and face acceptance, native authoring/Play regressions, exact sealed reconstruction, and remote engine CI must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all thirteen media assets.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

## Source files

- Current native Save Project export: `scenes/ghosts-in-different-forms-ep01-depth.swyrl.json`
- Preserved v9.1 native export: `scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json`
- Preserved v9.0 native export: `scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json`
- Preserved original production scene: `scenes/ghosts-in-different-forms-ep01.swyrl.json`
- Independent artwork: `assets/anime/`, including separate `kami-rig.png` and `swyrlz-rig.png` body-part atlases and `scenery-parts.png` scenery atlas
- Historical episode media: `episodes/ghosts-in-different-forms-ep01.html`
- Native pop-up cinema: `runtime/anime_screening.js` and `runtime/anime_screening.css`
- Reusable timeline, stage, and UI: `runtime/anime_timeline.js`, `runtime/anime_stage.js`, `runtime/anime_editor.js`, and their CSS
- Saved character poses, cutout renderer, and rig UI: `runtime/anime_rig_model.js`, `runtime/anime_rig_renderer.js`, `runtime/anime_rig_editor.js`, and `runtime/anime_rig_editor.css`
- Saved scenery model, layered renderer and object-key UI: `runtime/anime_scenery_model.js`, `runtime/anime_scenery_renderer.js`, `runtime/anime_scenery_editor.js`, and `runtime/anime_scenery_editor.css`
- Current integration: `patches/v9_2_depth_theatre.py`; the v9.1 rigs, v9.0 Studio and historical starter integrations remain in the governed chain
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
10. Engine reconstruction, native module syntax, bundled-screening integrity, and served-host hashes must pass before claiming production success.

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
