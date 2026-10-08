# Anime Studio starter · Ghosts in Different Forms · v9.0 candidate

## Starter contract

The §wyrl§ Engine Projects hub offers **Ghosts in Different Forms · The Page That Remembered**, a 134 second pop-up book episode authored in the native editor. It is an independent selectable project alongside Embervault and Starforge. Generated transparent artwork places Kami, the larger horn-hooded mage, and §wyrlz, the small hovering skull mage, on their own layers amid gothic amber/gold scenery.

Canonical project ID: `ghosts-different-forms-ep01`
Project selector key: `anime-ghosts-ep01`. [Direct starter URL](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01).

- 70 uniquely identified actors and 11 editor layers
- Eight new saved paper actors, each owning a layer, alongside the original 62 production set actors and three layers
- Eight story beats and nine independent camera/cast/scenery/book tracks spanning 134 seconds
- Eight preserved production stages, travel zones, and editable workstations, with the original guardian and visitor
- Native **Animation Studio** keyframe, title, and timed dialogue editing, Preview Frame, native Undo/Redo, and Save/Load
- PNG/WebP/JPEG layer artwork replacement; separate bundled character and scenery PNGs
- Candidate **Capture Actor Pose** workflow transfers a saved actor's native Inspector transforms to a timeline keyframe
- Native editor **Play** runs the same paper theatre renderer as Preview Frame; **Explore Set** returns to ordinary walking Play/T-zone mode
- **Watch Episode 01** opens the separate historical procedural 2D screening
- Bundled artwork and screening assets require no paid generation service during playback

## Animation behavior and boundaries

The saved `anime-timeline-v1` timeline animates camera position, target, and field of view; separate Kami and §wyrlz transforms; layered scenery; and book opening. Animation Studio exposes add/update/delete keys, Linear/Smooth/Hold easing, opacity, visibility, unfolding, titles, and dialogue cues. Native **Preview Frame** and **Play** share the renderer, while physical scenery planes fold around bottom-edge hinges at distinct depths. Protective background depth, a low foreground/book, and adaptive portrait framing prevent scenery from filling the central camera corridor.

The episode uses illustrated cutout motion. Skeletal posing, lip sync, audio authoring, and MP4 export are unimplemented. The separate **Watch Episode 01** player retains its historical canvas screening. Local desktop/phone-sized Chromium authoring and Play acceptance has been exercised; final source sealing, remote CI, dedicated deployment, and exact hosted v9.0 receipts remain pending at documentation time.

## Source files

- Current native Save Project export: `scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json`
- Preserved original production scene: `scenes/ghosts-in-different-forms-ep01.swyrl.json`
- Independent artwork: `assets/anime/`
- Screened episode: `episodes/ghosts-in-different-forms-ep01.html`
- Reusable timeline, stage, and UI: `runtime/anime_timeline.js`, `runtime/anime_stage.js`, `runtime/anime_editor.js`, and their CSS
- Current integration: `patches/v9_0_animation_studio.py`; historical starter integration remains in the governed chain
- Governed build packaging: `build_space.py`

## Acceptance tests

1. Projects hub shows Anime Studio alongside Embervault and Starforge; pressing Play starts native cinematic, not an unexplained first-person aerial view.
2. Opening Anime Studio loads 70 actors, 11 layers, eight stations, eight destinations, and the saved 134 second/nine track/eight beat episode.
3. Native keyframe/title/dialogue edits, Undo/Redo, artwork replacement, and Save/Load preserve independent project data. Capture Actor Pose must preserve the selected native Inspector pose in the intended track keyframe.
4. Preview and editor Play use the saved camera/cast/scenery/book keys, advance time, display dialogue, and accept Pause/scrub/next. Desktop and portrait shots retain both mages with safe scenery depths; Stop restores the editor camera. Explore Set returns to first-person Play > T with eight destinations.
5. The separate Watch button opens the original 2D Episode 01 in a modal without navigating away or overwriting editor data.
6. Close screening disposes the iframe source and returns focus.
7. Direct `?project=anime-ghosts-ep01` boots the same starter.
8. Starting a different project hides the screening control. Returning to Anime Studio restores it.
9. Existing Embervault and Starforge remain unchanged.
10. Engine reconstruction, native module syntax, bundled-screening integrity, and served-host hashes must pass before claiming production success.

## Future capability probes

- Skeletal character posing and reusable pose clips
- Lip sync and audio recording/import
- Exportable video capture and reproducible render settings

See [ANIMATION_STUDIO.md](ANIMATION_STUDIO.md) for the authoring workflow and [VERIFICATION.md](VERIFICATION.md) for current and historical evidence.

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
