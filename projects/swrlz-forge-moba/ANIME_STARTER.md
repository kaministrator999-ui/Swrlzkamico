# Anime Studio starter · Ghosts in Different Forms · Episode 01 · v8.7

## Starter contract

The §wyrl§ Engine Projects hub offers **Ghosts in Different Forms**, an original anime-inspired mini-episode starter. This is a **real, selectable native editor project**, not a manual file import or a replacement for either existing world.

Canonical project ID: `ghosts-different-forms-ep01`
Project selector key and direct URL: `anime-ghosts-ep01`; `?project=anime-ghosts-ep01`.

- 62 actors; uniquely named and identified
- Three authoring layers: sets, lighting/effects, and cast/narrative
- Eight separate floating stages; eight saved travel zones; eight editable workspace stations
- One guardian dragon; player wisp/visitor
- Dialogue, stage directions, and per-scene production notes in station files
- Native `Save Project` / `Load Project` preserves the set, notes, and world metadata
- Native **Play** begins a real-time camera/dialogue 3D cinematic and playback HUD. Use **Explore Set** to enter the ordinary walking Play/T-zone mode and visit the eight sets
- **Watch Episode 01** in the editor opens the original animated HTML screening; Exit returns to editor
- The deployed screening file is bundled locally with the app, not fetched from a paid runtime

## Honest animation boundary

The **Play** mode runs a project-scoped **native Three.js cinematic**: 134 seconds of camera interpolations, in-scene temporary procedural performers, dragon bob/rotation, light/particle effects, editable-script subtitle cues, scrub/pause/next/previous scene, and Explore Set. Script lines come from the eight stage workstation `script.md` files. The **Watch Episode** player remains a separate procedural HTML canvas animation. Camera/cast motion in native Play is currently scripted by the prototype, not editable through a general-purpose UI keyframe editor; this is the next engineering limitation. Do not label the screening as native timeline animation or claim exports to MP4 from §E. This distinction is intentional: the starter pack exposes exactly which native editing capabilities work and which cinematic features still need implementation.

## Source files

- Native scene: `scenes/ghosts-in-different-forms-ep01.swyrl.json`
- Screened episode: `episodes/ghosts-in-different-forms-ep01.html`
- Runtime editor integration: `patches/v8_5_anime_starter.py`
- Governed build packaging: `build_space.py`

## Acceptance tests

1. Projects hub shows Anime Studio alongside Embervault and Starforge; pressing Play starts native cinematic, not an unexplained first-person aerial view.
2. Opening Anime Studio loads its 62 actors, three layers, eight stations, eight travel zones.
3. Editing a dialogue station and saving/reloading preserves the changed file.
4. Native Play cinematic advances seconds, performs camera/actor motion, reads dialogue cues, accepts Pause/scrub/next, and Explore Set returns to first-person Play > T with eight supported destinations.
5. The separate Watch button opens the original 2D Episode 01 in a modal without navigating away or overwriting editor data.
6. Close screening disposes the iframe source and returns focus.
7. Direct `?project=anime-ghosts-ep01` boots the same starter.
8. Starting a different project hides the screening control. Returning to Anime Studio restores it.
9. Existing Embervault and Starforge remain unchanged.
10. Engine reconstruction, native module syntax, bundled-screening integrity, and served-host hashes must pass before claiming production success.

## Future capability probes

- Native per-actor animation clips and interpolation
- Cinematic camera paths and a shot/timeline editor
- Dialogue track and audio recording/import
- Asset binding between in-world scene actors and screenplay
- Exportable video capture and reproducible render settings

Do not silently build features beyond these requirements or confuse an editor-integrated screening iframe with an executable engine animation timeline.

## v8.7 · 2D anime cels with 3D parallax (candidate)

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
