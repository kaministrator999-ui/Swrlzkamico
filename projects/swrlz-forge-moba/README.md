# §wyrl§ Engine · Maker v8.8

Build and visit three independent starter workspaces: **Embervault Atelier**, the three-tier Dragon Den, and **Starforge Observatory**, a campus of floating islands beneath a quiet constellation sky. All three are native editor projects with their own layers, destinations, files, and notes. Development moves between engine source, native editor authoring, and first-person Play.

## Visit a workspace

The default Dragon Den has a lower workshop, a study gallery at 3.4m, and a dragon council at 4.6m. World Forge, Prototype Court, Code Studio, Archive Garden, AI Hearth, and Dragon Council provide six persistent stations. Walk between floors using the twin ramps and council connector, or press **T** / **Zones** in Play to choose one of eight destinations. The arrival directory sits beside the approach where visitors can read it; route signs distinguish upper study rooms from lower project courts.

Choose **Starforge Observatory** in Projects, or open [Starforge directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=starforge-observatory). Its seven destinations are Arrival, Constellation Garden, Code Island, Prototype Island, Archive Garden, Companion Chamber, and Observatory. Physical bridges and ramps connect the islands at 2.4m, 5.8m, and 7m. The Garden route guide sits at the edge of the path so the central route and project pads stay open. Six stations keep project work separate; the navy, brass, and jade environment travels with the project. Falling below its configured recovery height returns the visitor to Arrival through the same validated travel system.

Use WASD/arrows and mouse look in Play. Approach a station and press **E**, or click **Open**. Create, rename, edit, and download text/code files; keep station notes; import/export workspace JSON. **Save Project** stores the scene, destinations, environment settings, and every station's work in `.swyrl.json`. Device drafts also persist locally; explicit imported project files remain authoritative.

Chat stations open the existing §wyrlz LALM chat in a new tab. Project code is editable and downloadable source text. Headset rendering, VR controller input, executable coding sessions, and in-room inference are future integrations.

See [DEN_DESIGN.md](DEN_DESIGN.md), [STARFORGE_DESIGN.md](STARFORGE_DESIGN.md), and [VERIFICATION.md](VERIFICATION.md) for the plans, editor requirements, and evidence.

## Anime Studio starter · Episode 01

**v8.8 Pop-Up Book Video Creator:** Anime Play now unfolds a native Three.js book, independent gothic background/cathedral/workshop/desk scenery hinges, and distinctly separate illustrated Kami and §wyrlz wizard cels. **✦ Pop-Up Director** sets each layer's depth, side offset, parallax and unfold animation timings, stored in Save Project. The storybook style follows the earlier dark-fantasy wizard concept art without requiring a new generated image or external runtime. [Pop-Up Video Creator details](POPUP_VIDEO_CREATOR.md).

Choose **Ghosts in Different Forms** from **Projects** or [open the anime starter directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=anime-ghosts-ep01) **after v8.5 deployment**. This third project is independent of Embervault and Starforge: 62 editable actors, three scene-authoring layers, eight floating episode stages with T-menu destinations, eight workstations with editable script and direction files, and a guardian dragon. Press **Play** to run the native in-engine layered 2.5D cinematic: moving camera, animated procedural characters, dragon motion, editable-script subtitles, a timeline slider, previous/next scene, Pause, and **Explore Set** to resume the ordinary first-person Play mode. **Watch Episode 01** separately screens the original procedural 2m14s 2D animation in a modal.

The **Play** cinematic uses native Three.js camera parallax across six illustrated cel layers (background, atmosphere, midground, characters, effects, foreground), with scripted scene-specific transforms. The Layers button toggles these layers; during Play, scene signs and prop actors are temporarily hidden to avoid clipping and restored upon Stop/Explore Set. HUD captions wrap within mobile viewports.  the separate **Watch Episode 01** remains a canvas player. §E does not yet provide general drag-and-drop native keyframe editing, audio-track editing, or MP4 rendering. The episode is a focused engine-capability prototype, not a completed television animation pipeline.

See [ANIME_STARTER.md](ANIME_STARTER.md) for the project contract, validation steps, and next feature probes.

## Author in the editor

Reusable vault, oculus, end wall, support column, ramp, gallery deck, guardrail, sign, floating island, constellation sky, astrolabe, visitor, and companion assets are in the Content Browser. Static groups preserve world placement, children, and station IDs. Each starter has three project-owned editor layers; these visibility groups are independent of physical floor height.

The Details dock's **Teleport Zones** panel creates or edits a destination's name, description, world X/Z, feet Y, heading in degrees, and accent. Enable **Show destination markers** to display landing rings and heading arrows; markers start off by default and the preference persists on this device. Use **Frame Destination** to inspect a selected landing without losing the current orthographic viewing axis. Previews are optional editor helpers, independent of actors, collision, and project saves, and disappear in Play/Simulate. **Use Selected** and **Use Visitor** copy a world position; keep the landing pad supported and clear of edges, rails, and props, then test it in Play. Travel validates floor support, the visitor footprint, and body/head clearance, clears movement, releases pointer lock, and restores the prior pause state. Unsafe or hidden landings produce feedback and leave the visitor in place.

Walking uses visible approved mesh support tops plus terrain, with height-aware rail/prop collision and passages below raised floors. Wisp flight remains available. The editor preserves manual visibility, layer visibility, undo/redo, and runtime roof behavior independently. Desktop docks collapse their actual grid columns, and Play fills the viewport. Unknown prefab requests return `null` without modifying the selected actor; new blank projects start with their own empty layer list. Replacing a project during Play/Simulate first stops the session and clears its runtime state.

Preferred APIs are `window.SWYRL_ENGINE_AGENT` and `window.SWYRL_ENGINE_BUILD`; legacy `SWRLZ_FORGE_*` aliases remain active. Zone operations are `listTeleportZones`, `upsertTeleportZone`, `removeTeleportZone`, `openTeleportMenu`, `closeTeleportMenu`, and `teleportToZone`. `configureProject` edits project metadata, including environment settings. Preview APIs are `configureZonePreview`, `inspectZonePreview`, and `frameTeleportZone`. Existing layer, sign, and workstation APIs remain available.

Scene data belongs to `scenes/embervault-atelier.swyrl.json` and `scenes/starforge-observatory.swyrl.json`; reusable tools remain engine-owned patch modules. Blank Starter and MOBA retain separate routes. The main Chat/LALM application is deployment-isolated.

## Graphics and performance

**Graphics & Performance** provides Auto/Low/Medium/High/Custom presets, render scale, shadow quality, frame cap, and independent FPS/frame-time displays for Editor and Play/Simulate. Preferences persist locally. Auto adjusts render resolution from sustained frame time without changing simulation timing. The v8.2 bootstrap-order repair remains in the governed patch chain.

## Source integrity and deployment

- Source manifest: `source-manifest.json`.
- Base: 99,591 bytes, SHA-256 `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`.
- Generated artifact: `swyrl_engine_v8_8.html`.
- Final artifact: 644,951 bytes, SHA-256 `06c55a0d090bd6ffa9383ff44f914b922a841de7dc03284a50955cb4036478cd`. `SOURCE.json` also records hashes for the episode player and editable stage file.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_8_POPUP_STORYBOOK_DIRECTOR`.
- Rebuild: `python projects/swrlz-forge-moba/build_space.py --output dist/swrlz-forge-moba`.
- Dedicated Space: `kamiloki/swrlz-forge-moba`.
- Live page: https://kamiloki-swrlz-forge-moba.static.hf.space/ .
- Production workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`.

The manifest defines the governed 47-patch chain for the v8.7 anime cel layering. [ROADMAP.md](ROADMAP.md) preserves historical releases and receipts. Every §E update synchronizes version surfaces, updates the roadmap, reconstructs and syntax-checks the artifact, then changes `DEPLOY_REQUEST.json` as the final repository mutation. Completion requires the exact Actions run to succeed and the served host to verify the current marker and artifact integrity; root `§tart_§E.md` defines that contract.
