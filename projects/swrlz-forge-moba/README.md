# SWRLZ Forge · Editor v4

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the Forge engine workflow. The canonical router is [`/§tart_§E.md`](../../§tart_§E.md). Forge remains separate from the main §wyrlz AI Chat/LALM deployment lane.

## v4 source of truth

The editor still deploys as one browser-native HTML project. Its exact bytes are stored losslessly as gzip+base64 chunks under `payload/`; `build_space.py` reconstructs `index.html` and rejects a mismatched byte count or SHA-256.

- artifact: `swrlz_forge_v4.html`
- bytes: `99591`
- SHA-256: `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`
- deploy marker: `V4_SOLID_TERRAIN_LOCKED_VIEWS`

## v4 changes

### Camera/view correctness

- separate Perspective and Orthographic editor cameras
- Top / Front / Right are truly locked orthographic authoring views
- Perspective/Free camera can intentionally inspect underneath the world
- switching views resets the camera cleanly instead of inheriting a stale orbit state
- Play mode always uses the perspective gameplay camera and restores the prior editor view afterward
- transform gizmo scales down on phone-sized displays

### Solid world presentation

- terrain now has a dark underside plus vertical edge skirts instead of behaving like a transparent sheet
- underside inspection no longer makes trees and towers look as if they float through an invisible floor
- river/terrain scenery receives a brighter lighting and fog pass
- extra cliff rocks, bridges, trees, emissive cores and aura details improve the example map

### Editing

- Terrain Snap toggle
- Snap Selected to Ground
- actor-aware terrain offsets for walls, rocks, heroes and props
- stronger mobile Tools drawer so the primary viewport is not buried under the desktop toolbar

### Physics

- PhysicsBody props now resolve simple XZ blocker collisions
- gravity, bounce, ground drag and terrain following remain active in simulation/play

### Collaboration/agent

- ghost → Bake remains the authoritative authoring boundary
- bounded browser agent surface remains available as `window.SWRLZ_FORGE_AGENT`
- API schema advances to `forge-agent-v2`

## Deployment

Target Space: `kamiloki/swrlz-forge-moba`

Live static host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`

Workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

v4 adds a live acceptance gate after upload: GitHub Actions requests the actual `hf.space` page with a cache-busting build query and requires the v4 deploy marker before declaring the deployment successful. Upload success alone is no longer treated as proof that users are receiving the new build.

## Unreal study

The v3 Unreal-derived architectural study remains in [`UNREAL_STUDY.md`](./UNREAL_STUDY.md). v4 primarily hardens the editor behavior exposed by real mobile testing.

## Rebuild locally

```bash
python projects/swrlz-forge-moba/build_space.py --output /tmp/swrlz-forge-space
```
