# SWRLZ Forge · Editor v4.1

## Project entry command

Use `§tart §E` or `@GitHub §tart §E` to enter the Forge engine workflow. The canonical router is [`/§tart_§E.md`](../../§tart_§E.md). Forge remains separate from the main §wyrlz AI Chat/LALM deployment lane.

## v4.1 source authority

v4.1 introduces a deterministic patch layer so bugfix passes no longer require rewriting the entire compressed HTML payload for every small change.

`build_space.py` now:

```text
reconstruct base v4 payload
→ verify base bytes + SHA-256
→ apply patches/v4_1.py
→ verify final v4.1 bytes + SHA-256
→ stage exact index.html
```

Base:
- artifact: `swrlz_forge_v4.html`
- bytes: `99591`
- SHA-256: `a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856`

Final:
- artifact: `swrlz_forge_v4_1.html`
- bytes: `100610`
- SHA-256: `647a80a6a1062e8e4068c63593cca3c5566fe8ee9da5dcdcbc1810d42673132f`
- deploy marker: `V4_1_GROUND_ADHESION_RUNTIME_CLEANUP`

## v4.1 fixes from mobile playtest

- hero group origin now sits at the terrain surface instead of being offset roughly one unit above it
- grounded movement uses step-down adhesion so descending slopes/river depressions does not temporarily turn the hero airborne
- jumping still breaks ground adhesion normally
- PIE hides the purple editor selection BoxHelper and restores it on Stop
- mobile PIE hides editor-only World/Inspector/help/tool controls and moves the play hint to a compact lower overlay
- the two default jungle walls are moved outward and reduced so they no longer sit awkwardly across the main combat area
- physics/Blueprint showcase props are removed from the default gameplay map but remain available from the Content Drawer
- exported playable HTML receives the same hero-grounding logic
- agent protocol version advances to `forge-agent-v2.1`

## Deployment

Target Space: `kamiloki/swrlz-forge-moba`

Live static host: `https://kamiloki-swrlz-forge-moba.static.hf.space/`

Workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

The workflow requires the actual Hugging Face-reported static host to serve the current build marker before the deployment is considered successful.

## Rebuild locally

```bash
python projects/swrlz-forge-moba/build_space.py --output /tmp/swrlz-forge-space
```
