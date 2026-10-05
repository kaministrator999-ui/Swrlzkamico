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
3. Read `source-manifest.json`, `build_space.py`, current patch modules, and `SPACE_README.md`.
4. Read `.github/workflows/deploy-swrlz-forge-moba.yml`.
5. Inspect current GitHub main, last Forge workflow result, and current Hugging Face Space state before editing.
6. Keep edits scoped to Forge unless an explicit integration requires another subsystem.
7. Preserve base and final integrity contracts whenever source patches change.
8. Merge the validated candidate to `main`.
9. Observe the dedicated Forge workflow through terminal status.
10. Require publication success **and live-page marker verification** before calling the release live.
11. Report the exact GitHub source commit, HF Space revision, build version/marker, and failure path if any.

## Current v4.1 source authority

```text
base artifact: swrlz_forge_v4.html
base bytes: 99591
base sha256: a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856

patch: patches/v4_1.py

final artifact: swrlz_forge_v4_1.html
final bytes: 100610
final sha256: 647a80a6a1062e8e4068c63593cca3c5566fe8ee9da5dcdcbc1810d42673132f
deploy marker: V4_1_GROUND_ADHESION_RUNTIME_CLEANUP
```

## v4.1 state

The current bugfix pass addresses real mobile playtest evidence:

- hero feet align to the terrain surface instead of carrying the old +1.05 group offset
- grounded step-down adhesion follows slopes and river dips without hovering
- PIE hides editor BoxHelper selection chrome and restores it on Stop
- mobile PIE suppresses editor-only World/Inspector/help/tool clutter
- the default jungle walls are relocated away from awkward combat positions
- example-only physics/Blueprint actors no longer clutter the default MOBA map
- exported runtime uses the same grounded movement model
- agent API: `forge-agent-v2.1`

## Deployment truth contract

```text
rebuild base
→ verify base integrity
→ apply governed patches
→ verify final integrity
→ upload dedicated static Space
→ obtain actual Space host from Hugging Face
→ fetch live page
→ require current build marker
→ SUCCESS
```

Do not regress to a guessed Space hostname or treat upload alone as proof of live state.

## Verified v4 deployment lineage

The previous v4 checkpoint remains:

- engine commit: `948489ba3c255c69e78ccb321f9239fba566c437`
- final verified workflow commit: `b6190a91c27a9f451335d12ea251a9c50ddaf11d`
- HF revision: `0945cd9417bdcb4331f2d86a2297b67b1895d6b0`
- actual host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`

This is historical lineage after v4.1 becomes current.

## Bottom line

**`§tart §E` = load Forge from GitHub, preserve its separate deployment lane, reconstruct/patch/verify the exact engine source, deploy only to `kamiloki/swrlz-forge-moba`, verify the actual static host serves the current marker, then continue from observed truth.**
