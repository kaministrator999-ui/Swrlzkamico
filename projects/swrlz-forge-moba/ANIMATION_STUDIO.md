# Animation Studio · v9.0

**Ghosts in Different Forms · The Page That Remembered** is a 134 second, eight beat pop-up book starter authored in the native editor. Kami is the main horn-hooded mage; §wyrlz is the small hovering skull mage with a grimoire. Their independent illustrated character layers use newly generated transparent PNG artwork based on the supplied gothic anime references.

Choose **Ghosts in Different Forms** in **Projects**, or open the [direct starter URL](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01). Native desktop and phone authoring/Play acceptance [passed in GitHub](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37797022555). Production authority is recorded in the final `DEPLOY_REQUEST.json`, the dedicated deployment receipt, and the exact hosted-release audit.

## The saved starter

The native **Save Project** export is [ghosts-in-different-forms-ep01-storybook.swyrl.json](scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json). It contains the episode title, timed dialogue, camera and layer keyframes, artwork bindings, and eight new paper stage actors, each in its own saved editor layer. Seven actors are `animeCel` objects; the physical book is an `animeBook` object. The original 62 production set actors and eight workstations remain in the project, giving the export 70 actors and 11 editor layers in total.

| Time | Story beat |
| --- | --- |
| 0–14 s | The Sleeping Book |
| 14–30 s | A Ghost in the Margins |
| 30–46 s | The Library Unfolds |
| 46–66 s | The Page with No Door |
| 66–84 s | A Door Made of Light |
| 84–103 s | The Memory We Carry |
| 103–121 s | Two Mages, One World |
| 121–134 s | The First Step |

The nine animation tracks are Camera, Kami, §wyrlz, Background, Atmosphere, Midground, Effects, Foreground, and Book. Camera has its own position, look-at target, and field of view keys. The cast, scenery, and book can each move independently. The story and shot data belong to the project rather than being fixed inside the player.

## Edit and play

1. Open **Animation Studio**, choose a track, and scrub the playhead or select a keyframe. **Preview Frame** renders the chosen time in the native engine viewport.
2. Edit position, depth, scale, rotation, opacity, visibility, or unfold values where the selected track supports them. Camera exposes its position, target, and field of view instead. Choose Linear, Smooth, or Hold easing, then use **Add Keyframe** or **Update Keyframe**. **Delete Keyframe** removes an interior key; the first and last keys retain the track's complete duration.
3. Select a story beat, edit its title and dialogue cues, and use **Save Story Beat**. A cue can be entered as `14 | §wyrlz: Did that page just whisper?`, with the time in seconds from the start of the episode. Cues must fall within the selected beat. The episode title has its own **Save Title** control.
4. Use the editor's **Play** button or Animation Studio's **Play** to run the same native renderer used by Preview Frame. Pause to make changes, scrub to inspect the shot, then play again to assess movement and timing. Stop returns to the editor camera.
5. Use native **Undo** and **Redo** for timeline and artwork changes. **Save Project** keeps a portable `.swyrl.json` copy; loading that copy restores its timeline, actors, layers, and artwork bindings.

**Build Book Stage** creates the eight saved paper actors and their layers if they are missing. It keeps existing paper actors. Select a character or scenery track to **Replace layer artwork** with a PNG, WebP, or JPEG up to 8 MiB. Imported artwork is included in the saved project; transparency preserves the character and scenery cutout edges.

**Capture Actor Pose** connects the native Inspector to timeline authoring. Stop playback and close the frame preview, select the saved paper actor in the Outliner, and set its position, scale, and rotation in the Inspector. Return to Animation Studio, choose that actor's track and the intended playhead time, then capture the pose to create or update the keyframe. Timeline keys control playback after capture. Capture uses the native transaction history and preserves the other character's track.

## Depth and camera behavior

The cast uses separate textured paper meshes. Characters and scenery rotate around bottom-edge hinges as the book opens. Background arches, workshop scenery, mist, and magic occupy different depths, so camera movement produces parallax. Folding changes the actual surface orientation.

The renderer keeps background and effects surfaces behind both characters and folds scenery away from the camera. It measures the foreground image's visible ink and keeps that ink below whichever characters are visible; fully opaque replacement images receive full-height protection. The physical book has independent visibility and scale and remains below the character area. These protective limits also apply to edited keys. Portrait screens increase camera distance to retain both mages in the shot. The camera's keyed position, target, and field of view guide the scene within those framing limits.

The supplied art is bundled in [assets/anime](assets/anime). Kami and §wyrlz have separate PNGs; cathedral, workshop, and foreground art are separate plates. Mist and rune textures are drawn by the engine. Playback does not call a paid image generation service.

The original **Watch Episode 01** button still opens the historical procedural 2D screening. Native **Play** and **Preview Frame** use the saved v9.0 paper theatre timeline described here.

## Reusable engine tools and design sources

[anime_timeline.js](runtime/anime_timeline.js) owns the validated saved timeline, interpolation, edits, and transaction integration. [anime_stage.js](runtime/anime_stage.js) owns the paper actor types, textures, hinges, staging, shared Preview/Play renderer, and camera restoration. [anime_editor.js](runtime/anime_editor.js), [anime_editor.css](runtime/anime_editor.css), and [anime_stage.css](runtime/anime_stage.css) provide the native authoring controls and layout. [v9_0_animation_studio.py](patches/v9_0_animation_studio.py) integrates these reusable tools and the exported starter into the governed engine build.

The browser APIs `SWYRL_ENGINE_ANIMATION` and `SWYRL_ENGINE_STORYBOARD` expose the same timeline editing, sampling, stage construction, artwork binding, preview, and serialization used by the native UI. The episode package was authored through those native APIs and editor controls, then exported with Save Project.

The following Internet references informed concrete implementation choices:

- [Three.js transparency guidance](https://threejs.org/manual/pages/transparency.html) and [Material documentation](https://threejs.org/docs/pages/Material.html): transparent texture edges, alpha testing, double-sided paper surfaces, and depth behavior.
- [Three.js Object3D documentation](https://threejs.org/docs/pages/Object3D.html): separate object groups, transforms, camera targeting, and parented paper hinges.
- [Robert Sabuda's beginner castle pop-up](https://www.robertsabuda.com/castle-beginner.html): a physical fold-and-rise staging reference for the book and scenery cards.
- [Blender timeline documentation](https://docs.blender.org/manual/en/latest/editors/timeline.html): familiar playhead, scrubbing, keyframe selection, and playback controls for the editor workflow.

This starter animates illustrated cutouts, layered scenery, a physical book, camera shots, and timed text. Skeletal posing, lip sync, audio authoring, and MP4 export are not implemented.
