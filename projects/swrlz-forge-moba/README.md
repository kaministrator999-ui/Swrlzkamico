# §wyrl§ Engine · Maker v8.0

Embervault Atelier is the canonical Dragon Den: a three-tier spatial workspace with a lower workshop, upper study gallery, and raised dragon council. The engine is developed through three perspectives: source capabilities, native editor authoring, and first-person Play verification.

## Use the den

- Lower floor: World Forge, Prototype Court, quiet arrival nook, and shared AI hearth.
- Upper study at 3.4m: Code Studio and Archive Garden, connected by two walkable ramps and a cross-room gallery.
- Dragon council at 4.6m: a quieter conversation station reached by a short ramp.
- Approach a station and press **E**, or click **Open**. Create, rename, edit, and download text/code files; keep station notes; import/export workspace JSON.
- **Save Project** stores the scene and every station's work in `.swyrl.json`. Device drafts also persist locally. Imported project files remain authoritative.
- Chat stations open the existing §wyrlz LALM chat in a new tab. Code files are editable source text. Headset rendering, controller input, executable coding sessions, and in-room inference are future integrations.

See [DEN_DESIGN.md](DEN_DESIGN.md) for the complete den plan, asset inventory, editor requirements, and author → Play → fix loop.

## Engine capabilities

Native reusable vault, oculus, end wall, support column, ramp, gallery deck, guardrail, and sign assets are in the Content Browser. Static groups preserve world placement, children, and station IDs. Three project-owned editor layers organize architecture/wayfinding, atmosphere/guardians, and project spaces.

Walking uses approved mesh support tops plus terrain, with height-aware rail/prop collision and passages under raised floors. Wisp flight remains available. The editor preserves manual visibility, layer visibility, undo/redo, and runtime roof behavior independently. Desktop docks collapse their actual grid columns, and Play fills the viewport.

Preferred APIs: `window.SWYRL_ENGINE_AGENT` and `window.SWYRL_ENGINE_BUILD`. Legacy `SWRLZ_FORGE_*` aliases remain active. New operations include `createLayer`, `listLayers`, `setLayerVisibility`, `assignActorsToLayer`, `configureWorkspace`, `openWorkspace`, `createSign`, and `updateSign`.

The scene belongs to `scenes/embervault-atelier.swyrl.json`; geometry and interaction tools remain engine-owned patch modules. Blank Starter and MOBA templates retain separate routes. The main Chat/LALM application is deployment-isolated.

## Source integrity and deployment

- Source manifest: `source-manifest.json`.
- Base: 99,591 bytes, SHA-256 `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`.
- Generated artifact: `swyrl_engine_v8_1.html`.
- Final size/hash: recorded in the manifest and generated `SOURCE.json`.
- Marker: `SWYRL_ENGINE_DEPLOY_MARKER: V8_1_PERFORMANCE_GRAPHICS`.
- Rebuild: `python projects/swrlz-forge-moba/build_space.py --output dist/swrlz-forge-moba`.
- Dedicated Space: `kamiloki/swrlz-forge-moba`.
- Live page: https://kamiloki-swrlz-forge-moba.static.hf.space/ .
- Production workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`.

The exact governed patch chain is in the manifest. Historical releases and receipts remain in [ROADMAP.md](ROADMAP.md). Every §E update synchronizes version surfaces, updates the roadmap, reconstructs and syntax-checks the artifact, then changes `DEPLOY_REQUEST.json` as the final repository mutation. Deployment completion requires the exact Actions run to succeed and the live host to serve the current marker; root `§tart_§E.md` defines that contract.
\n## v8.1 performance controls\n\nGraphics & Performance provides Auto/Low/Medium/High/Custom scalability, render scale, shadow quality, frame cap, and independent FPS/frame-time displays for Editor and Play/Simulate. Preferences persist locally. Auto adjusts render resolution from sustained frame time without changing gameplay simulation timing.\n