# Animation Studio · v9.3 candidate

**Ghosts in Different Forms · The Page That Remembered** is a 134 second, eight beat pop-up book starter authored in the native editor. Kami is the main horn-hooded mage; §wyrlz is the small hovering skull mage with a grimoire. Their independent illustrated character layers use jointed paper puppets with new transparent body-part atlases based on the supplied gothic anime references.

Choose **Ghosts in Different Forms** in **Projects**, or open the [direct starter URL](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01). v9.3 is a source candidate. Desktop/phone connected-part fitting and authoring acceptance, the existing native Play/Studio/rig/depth regressions, exact sealed reconstruction, and remote engine CI must pass before deployment. Production authority comes from the final `DEPLOY_REQUEST.json`, the exact dedicated deployment run, and the hosted audit of the current marker, normalized HTML, `SOURCE.json`, and all fourteen media assets.

The previous **v9.2 Layered Scenery and Fitted Faces** release is verified live: [deployment 37871463769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871463769) and [exact hosted audit 37871508796](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37871508796) passed. Source [`7f664a2c967a`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/7f664a2c967a0bff63d6d1a5c0eb1e8acc472a01) seals 51 patches, **965,788 bytes**, SHA-256 `b952e375be6a2cfb88014714cccbe80285e70d4b76821763bc68ada46e2dcbc4`, with all thirteen media assets, 425 rig keys and 341 scenery keys. These receipts certify v9.2; v9.3 needs its own final deployment and hosted audit.

The previous **v9.1 Articulated Paper Rigs** release is verified live: [deployment 37838083241](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838083241) and [exact hosted audit 37838137243](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/37838137243) passed. Source [`d3e7dc4d6a06`](https://github.com/kaministrator999-ui/Swrlzkamico/commit/d3e7dc4d6a0633995210a7217943753d4de28e29) seals 50 patches, **857,746 bytes**, SHA-256 `7b6f3806c666b991a07e0c6bf162286b09dd70862f7de9acc9bf0ea3d214473f`, with all eleven bundled media assets and 425 character pose/face keys. These receipts are historical authority for v9.1; they do not certify v9.2.

## Connected character pieces

v9.3 fits each mage’s body pieces to its own painted silhouette: shoulders, elbows, wrists, hips, knees, ankles and the head use corrected attachment placement and overlap. Staff, quill and grimoire placement follows the owning hand. Kami and §wyrlz retain separate eighteen-piece paper rigs, fitted facial controls and independent animation tracks. The engine samples the bundled transparent artwork directly; no flattened replacement character is introduced.

In **Animation Studio**, select **Kami** or **§wyrlz**, expand **Character Rig · limbs and face**, choose a body part, then use **Fit Body Piece**. **Joint X/Y** place its pivot; **Artwork X/Y** position its painted cutout; **Piece width/height** and **Rest angle (°)** fit the silhouette. Use **Apply Body Piece Fit**, preview the shared playhead, and use Play to inspect the attached chain through motion. **Reset Piece Fit** restores that piece’s default fit. Fitting is saved separately from timed rotation/depth keys; native Undo/Redo and Save/Load preserve it without changing the companion’s rig or scenery keys. Pause running playback before editing.

The starter keeps **70 actors, 11 editor layers, eight story beats, nine stage/camera tracks, and 134 seconds**. The native Save Project export is `scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json`. Per-character rest layouts belong to `project.animeRigs.characters[character].layout`, alongside the independent limb/face keys. The saved performance retains 425 limb/face keys and 341 scenery keys. The v9.2 depth, v9.1 rigged, v9.0 storybook and original production scene exports remain bundled, together with all eight artwork PNGs and the historical episode HTML.

## Layered scenery and fitted faces

The screenshot exposed misaligned facial features and a library rendered as broad flat plates. v9.2 fits Kami’s eyes, brows and mouth inside the painted face and keeps §wyrlz’s expressions aligned with the skull. Existing blink, mouth, gaze and expression keys remain editable. The background becomes a paper depth theatre: a distant sky and three star shells sit behind independent windows, arches, shelves, banners, lanterns and props. Each cutout has its own transform/opacity/visibility/unfold keys, so perspective-camera motion produces real parallax between the pieces.

Open **Animation Studio**, select **Background**, **Midground**, **Atmosphere**, or **Effects**, then expand **Scenery Depth · individual cutouts**. Choose a **Scenery piece**, set its depth and pose at the shared playhead, and use **Add/Update Scenery Key**. **Layered scenery**, **Pop-out depth**, and **Apply Scenery Depth** control the depth assembly. Preview Frame, editor Play and the native Watch cinema use the same saved renderer; native Undo/Redo and Save/Load retain each piece’s edits. Pause running Play before authoring. Camera protection keeps the background behind the mages and the foreground/book below their face and body corridor.

The depth model contains **34 independent scenery objects**: left/center/right arches and distant castles; paired windows, pillars, bookcases, banners, lanterns, chains, candelabra, books, mist and flames; a bridge, moon, crystal, floating pages and star ornament; and the three far/middle/near constellation shells. The three star shells use individual star points at separate depths. These are textured paper cutouts and point stars in a perspective scene. Their internal hierarchies preserve the saved 70-actor/11-layer native project.

Scenery keys expose **Position X/Y**, **Depth Z**, **Lean X**, **Turn Y**, **Turn Z**, **Scale**, **Opacity**, **Unfold**, and **Visible**. Depth is negative relative to the parent scenery layer; angles display degrees and save radians. Choose Smooth, Linear, or Hold in **Easing to next scenery key**. Tap a saved scenery key to preview it, use **Add/Update Scenery Key** to save the current controls, or **Delete Scenery Key** to remove an interior key. Whole-layer track controls still move the complete background/midground assembly, while these controls move one cutout.

## The saved starter

The native **Save Project** export is [ghosts-in-different-forms-ep01-positioned.swyrl.json](scenes/ghosts-in-different-forms-ep01-positioned.swyrl.json). The [v9.2 layered-depth export](scenes/ghosts-in-different-forms-ep01-depth.swyrl.json) remains bundled. It contains the episode title, timed dialogue, camera and layer keyframes, artwork bindings, and eight new paper stage actors, each in its own saved editor layer. Seven actors are `animeCel` objects; the physical book is an `animeBook` object. The original 62 production set actors and eight workstations remain in the project, giving the export 70 actors and 11 editor layers in total. The [v9.1 articulated rig export](scenes/ghosts-in-different-forms-ep01-rigged.swyrl.json), original production scene and [v9.0 whole-cel storybook export](scenes/ghosts-in-different-forms-ep01-storybook.swyrl.json) remain bundled. Individual scenery object keys are saved under `project.animeScenery` (`anime-scenery-v1`); joint and face pose keys are saved under `project.animeRigs`; they do not add scene actors or replace the nine stage tracks.

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

## Pose limbs and expressions

Kami and §wyrlz now use separate articulated paper rigs. Each mage has independently jointed torso, pelvis, head, cape, upper/lower arms, hands, upper/lower legs, and feet, plus character-specific staff/quill or grimoire props. Joint keys save real X/Y/Z rotations and part depth; per-character paper thickness and pop-out depth give the limbs room in front of the scenery. Faces save Neutral, Happy, Determined, Surprised, or Sad expressions together with blink, mouth openness, smile, brow, gaze, and optional mouth motion driven by saved dialogue cues.

Open **Animation Studio**, select **Kami** or **§wyrlz**, then expand **Character Rig · limbs and face**. Use **Apply Character Depth** to save thickness/pop-out settings. Choose a body part and edit **Lean X**, **Turn Y**, **Bend Z**, or **Part depth**, then **Add Pose Key** / **Update Pose Key** at the shared playhead. **Face & Expression** exposes expression, blink and mouth; **Gaze, smile and dialogue motion** adds smile, brow, gaze and saved-dialogue mouth movement. Pose and face keys use Linear/Smooth/Hold easing, Preview Frame, native Play/Pause, Undo/Redo, and Save/Load.

Angles are shown in degrees and saved as radians. Positive **Part depth** moves the selected part toward the camera within bounded limits. A part's joint hierarchy keeps hands attached to forearms and forearms attached to upper arms; the same principle applies to legs and the head. Whole-character movement remains on the Kami/§wyrlz stage tracks above, while local limb and face keys share that timeline's duration and playhead. Each character retains its own keys and depth settings.

**Move mouth with saved dialogue** adds procedural mouth movement when that character's text cue is active. It uses saved cue timing; it does not analyze or synthesize audio. Direct mouth/blink/gaze values and expression keys remain editable. Pause playback before changing a pose, preview that frame, then Play to inspect the interpolation.

The transparent `kami-rig.png` and `swyrlz-rig.png` atlases hold separate body-part/face artwork. Choosing ordinary replacement layer artwork switches that character to whole-cel rendering; arbitrary images are not automatically separated into body parts. The rig's enabled control selects the articulated puppet when its compatible atlas is available.

## Depth and camera behavior

The cast uses separate hierarchies of rigid, overlapping textured paper parts with silhouette side walls and local depth. Faces use their own canvas textures for blink, mouth, brow, and gaze changes. Characters and scenery rotate around bottom-edge hinges as the book opens. Background arches, workshop scenery, mist, and magic occupy different depths, so camera movement produces parallax. Folding changes the actual surface orientation.

The renderer keeps background and effects surfaces behind both characters and folds scenery away from the camera. It measures the foreground image's visible ink and keeps that ink below whichever characters are visible; fully opaque replacement images receive full-height protection. The physical book has independent visibility and scale and remains below the character area. These protective limits also apply to edited keys. Portrait screens increase camera distance to retain both mages in the shot. The camera's keyed position, target, and field of view guide the scene within those framing limits.

The supplied art is bundled in [assets/anime](assets/anime). Kami and §wyrlz have separate original whole-cel PNGs and separate rig atlases; cathedral, workshop, and foreground art are separate plates. Mist and rune textures are drawn by the engine. Playback does not call a paid image generation service.

**Watch Episode 01** opens the pop-up cinema with the real engine canvas, chapter buttons, and native transport HUD. It uses the same saved stage, individual scenery and character-pose timelines as **Play** and **Preview Frame**. Closing the cinema restores the editor viewport; the original procedural episode HTML remains bundled as a historical media asset.

## Reusable engine tools and design sources

[v9_3_character_alignment.py](patches/v9_3_character_alignment.py) adds connected character rest layouts and fitting controls without replacing timed joint or face tracks. `SWYRL_ENGINE_RIG.fitPart(character,part,layout)` and `resetPartFit(character,part)` back the native fitting controls; `model(character).layout` exposes saved fits and `layoutBounds` exposes their finite bounds. Fit angles display degrees and save radians. Joint/artwork X/Y, width, height and rest angle apply throughout the episode, while the existing pose keys retain their own time and easing.

[anime_timeline.js](runtime/anime_timeline.js) owns the validated saved timeline, interpolation, edits, and transaction integration. [anime_stage.js](runtime/anime_stage.js) owns the paper actor types, textures, hinges, staging, shared Preview/Play renderer, and camera restoration. [anime_editor.js](runtime/anime_editor.js), [anime_editor.css](runtime/anime_editor.css), and [anime_stage.css](runtime/anime_stage.css) provide the native authoring controls and layout. [v9_0_animation_studio.py](patches/v9_0_animation_studio.py) preserves the Studio integration; [v9_1_character_rigs.py](patches/v9_1_character_rigs.py) adds the saved character pose model, rig controls, and rigged starter. [anime_rig_model.js](runtime/anime_rig_model.js) validates/interpolates `project.animeRigs`, [anime_rig_renderer.js](runtime/anime_rig_renderer.js) builds hierarchical textured cutouts with silhouette side walls and a separate facial canvas texture, and [anime_rig_editor.js](runtime/anime_rig_editor.js) / [anime_rig_editor.css](runtime/anime_rig_editor.css) add native part/face editing.

[v9_2_depth_theatre.py](patches/v9_2_depth_theatre.py) adds fitted facial placement and independently keyed paper scenery. [anime_scenery_model.js](runtime/anime_scenery_model.js) validates/interpolates `project.animeScenery`, [anime_scenery_renderer.js](runtime/anime_scenery_renderer.js) renders independent cutouts and star shells at separated depths, and [anime_scenery_editor.js](runtime/anime_scenery_editor.js) / [anime_scenery_editor.css](runtime/anime_scenery_editor.css) provide native object-key controls.

`SWYRL_ENGINE_SCENERY.model()` returns the saved scenery configuration; `sample(id,time)`, `upsertKey(id,key)`, `removeKey(id,time)`, and `configure({enabled,depth})` back the native object-key controls. Keys store local positions, X/Y/Z rotation in radians, scale, opacity, unfold, visibility, easing and time. Object track endpoints cover the complete episode duration; changing the episode duration rescales stage, rig and scenery keys together in one Undo transaction.

The browser APIs `SWYRL_ENGINE_ANIMATION`, `SWYRL_ENGINE_STORYBOARD`, `SWYRL_ENGINE_RIG`, and `SWYRL_ENGINE_SCENERY` expose the same timeline/pose editing, sampling, stage construction, artwork binding, preview, and serialization used by the native UI. The episode package was authored through those native APIs and editor controls, then exported with Save Project.

The following Internet references informed concrete implementation choices:

- [Three.js transparency guidance](https://threejs.org/manual/pages/transparency.html) and [Material documentation](https://threejs.org/docs/pages/Material.html): transparent texture edges, alpha testing, double-sided paper surfaces, and depth behavior.
- [Three.js Object3D documentation](https://threejs.org/docs/pages/Object3D.html): separate object groups, transforms, camera targeting, and parented paper hinges.
- [Robert Sabuda's beginner castle pop-up](https://www.robertsabuda.com/castle-beginner.html): a physical fold-and-rise staging reference for the book and scenery cards.
- [Blender timeline documentation](https://docs.blender.org/manual/en/latest/editors/timeline.html): familiar playhead, scrubbing, keyframe selection, and playback controls for the editor workflow.

This starter animates articulated paper cutouts, facial controls, layered scenery, a physical book, camera shots, and timed text. These are jointed 2.5D paper characters with rigid overlapping cutouts, silhouette side walls, and separated depth. Full sculpted/skinned 3D characters, audio-driven lip synchronization, audio authoring, and MP4 export remain future work. **Watch Episode 01** preserves the pop-up cinema experience and plays the same native authored 2.5D scene, with chapter buttons and transport controls. The original procedural episode HTML remains bundled for history.

## Character artwork and design references

The saved performance contains 217 Kami pose/face keys and 208 §wyrlz pose/face keys. Each mage renders eighteen separate paper pieces, including its props, with front, back, and silhouette-edge geometry. Imported whole-character artwork keeps the existing flat-cel workflow: replacing Kami or §wyrlz artwork disables that character’s puppet, and Undo restores it. Rig atlases use twenty row-major slots; the bundled Kami atlas uses the measured source rectangle `[0,75,1122,1320]`. The engine samples these immutable images directly with UV coordinates.

The overlap and pivot design follows [Live2D’s material separation guidance](https://docs.live2d.com/en/cubism-editor-manual/divide-the-material/) and [rotation deformer guidance](https://docs.live2d.com/en/cubism-editor-manual/making-and-rotation-of-rotationdeformer/). Independent expression controls follow its [standard parameter conventions](https://docs.live2d.com/en/cubism-editor-manual/standard-parameter-list/); native scene transforms use [Three.js Object3D](https://threejs.org/docs/#api/en/core/Object3D). These are design references; the implementation uses the engine’s own rigid paper geometry and facial canvas.
