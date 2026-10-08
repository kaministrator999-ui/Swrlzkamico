# Anime Studio starter · Ghosts in Different Forms · Episode 01

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
- Native Play + `T` to navigate between the eight sets and walk around them
- **Watch Episode 01** in the editor opens the original animated HTML screening; Exit returns to editor
- The deployed screening file is bundled locally with the app, not fetched from a paid runtime

## Honest animation boundary

The *screening* is a procedural HTML canvas animation with authored timed scenes, subtitle/caption controls, and playback, distinct from the 3D engine. The **3D stages** are editable and can be explored in Play; they do not currently animate actors along the screening's camera/dialogue keyframes. Do not label the screening as native timeline animation or claim exports to MP4 from §E. This distinction is intentional: the starter pack exposes exactly which native editing capabilities work and which cinematic features still need implementation.

## Source files

- Native scene: `scenes/ghosts-in-different-forms-ep01.swyrl.json`
- Screened episode: `episodes/ghosts-in-different-forms-ep01.html`
- Runtime editor integration: `patches/v8_5_anime_starter.py`
- Governed build packaging: `build_space.py`

## Acceptance tests

1. Projects hub shows Anime Studio alongside Embervault and Starforge.
2. Opening Anime Studio loads its 62 actors, three layers, eight stations, eight travel zones.
3. Editing a dialogue station and saving/reloading preserves the changed file.
4. Play > T offers eight destinations. Teleport must reject unsupported or blocked coordinates.
5. Watch opens Episode 01 in a modal/iframe without navigating away or overwriting editor data.
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
