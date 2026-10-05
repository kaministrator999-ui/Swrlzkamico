# §tart §E — SWRLZ Forge Engine Build & Deploy Router

**Role:** canonical entrypoint for SWRLZ Forge / browser-engine work.

**Invocation:** `§tart §E` or `@GitHub §tart §E` means enter the dedicated Forge project lane, reconstruct current GitHub/Hugging Face state, and continue engine work independently from the §wyrlz AI Chat/LALM application.

## Canonical lane

```text
GitHub: kaministrator999-ui/Swrlzkamico
  -> projects/swrlz-forge-moba/
  -> .github/workflows/deploy-swrlz-forge-moba.yml
  -> Hugging Face: kamiloki/swrlz-forge-moba
  -> https://kamiloki-swrlz-forge-moba.static.hf.space/
```

**Hard boundary:** never route ordinary Forge releases through `kamiloki/Swyrlz` or the AI Chat/LALM deployment workflows.

## Startup contract

On `§tart §E`:

1. Read this router.
2. Read `projects/swrlz-forge-moba/README.md`.
3. Read `source-manifest.json`, `build_space.py`, and `SPACE_README.md`.
4. Read `.github/workflows/deploy-swrlz-forge-moba.yml`.
5. Inspect the current GitHub main revision, last Forge workflow result, and current Hugging Face Space state before editing.
6. Keep edits scoped to the Forge project unless an explicit integration requires another subsystem.
7. For runtime-affecting changes, update the exact source payload and manifest together.
8. Merge the validated candidate to `main`.
9. Observe the dedicated Forge workflow through terminal status.
10. Require both publication success **and live-page marker verification** before calling the release live.
11. Report the exact GitHub source commit, HF Space revision, build version/marker, and any failures encountered.

## Current v4 source authority

```text
artifact: swrlz_forge_v4.html
bytes: 99591
sha256: a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856
deploy marker: V4_SOLID_TERRAIN_LOCKED_VIEWS
```

The source is stored losslessly in six gzip+base64 payload chunks. `build_space.py` reconstructs the exact HTML and verifies its integrity before deployment.

## v4 editor state

Forge v4 includes:

- separate Perspective and Orthographic editor cameras
- locked Top / Front / Right authoring views
- unrestricted Perspective/Free camera including underside inspection
- solid terrain underside + edge skirts
- brighter lighting/fog and improved scenery
- smaller mobile gizmos
- mobile Tools drawer
- Terrain Snap and Snap Selected to Ground
- World/Local transform spaces and transform snapping
- Outliner, Details, Components, Content Drawer, Output Log
- Undo/Redo and Build Validation
- Play In Editor / Simulate In Editor / Pause / Play From Here / Keep Simulation Changes
- PhysicsBody gravity/bounce/drag plus simple blocker collision
- MOBA lane/minion/tower/runtime systems
- ghost → Bake authoring
- `window.SWRLZ_FORGE_AGENT` using `forge-agent-v2`
- standalone HTML runtime export

## Deployment truth contract

A GitHub/HF upload receipt is not sufficient by itself.

The v4 workflow must:

```text
rebuild exact source
  -> verify SHA/bytes
  -> upload dedicated static Space
  -> request the live hf.space page with cache-busting query
  -> find V4_SOLID_TERRAIN_LOCKED_VIEWS
  -> only then report deployment SUCCESS
```

If the live marker check fails, treat the release as not-live and debug the serving/cache/build state.

## Historical lineage

Initial dedicated Forge deployment:
- GitHub: `3024b4e8d81ec515ab8d08d6d7d2b81547e57f4b`
- HF: `a22686c4b1326c10fd8884965b18cdad8e50224e`

v3 deployment checkpoint:
- GitHub: `018b7351c5d473018ac5ca5a0ff4a0079c98fb8f`
- HF: `650c0defa60d0db3f68e9a93b3f39384a23c8da8`

These are historical checkpoints only. Never assume they remain current.

## Verified v4 deployment checkpoint

```text
Forge version:
v4

GitHub release/workflow commit:
b6190a91c27a9f451335d12ea251a9c50ddaf11d

v4 engine payload first published from:
948489ba3c255c69e78ccb321f9239fba566c437

Source SHA-256:
a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856

Hugging Face Space revision:
0945cd9417bdcb4331f2d86a2297b67b1895d6b0

Actual HF static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Space stage:
RUNNING

Live marker verification:
PASS on first attempt
```

Deployment debugging lineage is intentionally preserved:

1. v4 upload itself succeeded, but the first live gate used an assumed non-static `.hf.space` host and correctly received HTTP 404.
2. the next pass asked Hugging Face `SpaceInfo` for the actual host and discovered the required `.static.hf.space` hostname;
3. that verifier then exposed a shell `pipefail` false-negative: `grep -q` found the marker and closed the pipe, causing curl exit 23;
4. the verifier was repaired to download the page first and grep the file;
5. the final run fetched the Hugging Face-reported static host and found `V4_SOLID_TERRAIN_LOCKED_VIEWS` on attempt 1.

Do not regress to a guessed Space hostname. Always use Hugging Face's reported host/subdomain and live-marker validation.

## Bottom line

**`§tart §E` = load Forge from GitHub, preserve the separate engine lane, change the engine, validate exact source, deploy only to `kamiloki/swrlz-forge-moba`, verify the actual live page is serving the new marker, then continue from that observed truth.**
