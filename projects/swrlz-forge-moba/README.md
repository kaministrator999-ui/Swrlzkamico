# §wyrl§ Engine · Maker v8.4

Build and visit two independent spatial workspaces: **Embervault Atelier**, the three-tier Dragon Den, and **Starforge Observatory**, a campus of floating islands beneath a quiet constellation sky. Both are native editor projects with their own layers, destinations, files, and notes. Development moves between engine source, native editor authoring, and first-person Play.

## Visit a workspace

The default Dragon Den has a lower workshop, a study gallery at 3.4m, and a dragon council at 4.6m. World Forge, Prototype Court, Code Studio, Archive Garden, AI Hearth, and Dragon Council provide six persistent stations. Walk between floors using the twin ramps and council connector, or press **T** / **Zones** in Play to choose one of eight destinations. The arrival directory sits beside the approach where visitors can read it; route signs distinguish upper study rooms from lower project courts.

Choose **Starforge Observatory** in Projects, or open [Starforge directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=starforge-observatory). Its seven destinations are Arrival, Constellation Garden, Code Island, Prototype Island, Archive Garden, Companion Chamber, and Observatory. Physical bridges and ramps connect the islands at 2.4m, 5.8m, and 7m. The Garden route guide sits at the edge of the path so the central route and project pads stay open. Six stations keep project work separate; the navy, brass, and jade environment travels with the project. Falling below its configured recovery height returns the visitor to Arrival through the same validated travel system.

Use WASD/arrows and mouse look in Play. Approach a station and press **E**, or click **Open**. Create, rename, edit, and download text/code files; keep station notes; import/export workspace JSON. **Save Project** stores the scene, destinations, environment settings, and every station's work in `.swyrl.json`. Device drafts also persist locally; explicit imported project files remain authoritative.

Chat stations open the existing §wyrlz LALM chat in a new tab. Project code is editable and downloadable source text. Headset rendering, VR controller input, executable coding sessions, and in-room inference are future integrations.

See [DEN_DESIGN.md](DEN_DESIGN.md), [STARFORGE_DESIGN.md](STARFORGE_DESIGN.md), and [VERIFICATION.md](VERIFICATION.md) for the plans, editor requirements, and evidence.

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
- Generated artifact: `swyrl_engine_v8_4.html`.
- Final artifact: 533,612 bytes, SHA-256 `58252d18ee4fedf3acb9b5ccbb8e19dbc10c421345deb507a016151ab1ceca62`; the manifest and generated `SOURCE.json` record the same authority.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_4_WAYFINDING_ZONE_PREVIEW`.
- Rebuild: `python projects/swrlz-forge-moba/build_space.py --output dist/swrlz-forge-moba`.
- Dedicated Space: `kamiloki/swrlz-forge-moba`.
- Live page: https://kamiloki-swrlz-forge-moba.static.hf.space/ .
- Production workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`.

The manifest defines the exact governed 43-patch chain. [ROADMAP.md](ROADMAP.md) preserves historical releases and receipts. Every §E update synchronizes version surfaces, updates the roadmap, reconstructs and syntax-checks the artifact, then changes `DEPLOY_REQUEST.json` as the final repository mutation. Completion requires the exact Actions run to succeed and the served host to verify the current marker and artifact integrity; root `§tart_§E.md` defines that contract.
