# SWRLZ Forge · MOBA Lab

Browser-native 3D MOBA editor/runtime prototype.

## Source of truth

The exact editor HTML is stored losslessly as gzip+base64 payload chunks under `payload/`.
`build_space.py` reconstructs the original `index.html` byte-for-byte for deployment.

## Hugging Face deployment

Target Space: `kamiloki/swrlz-forge-moba`

GitHub workflow: `.github/workflows/deploy-swrlz-forge-moba.yml`

Any push to `main` that changes this project folder automatically rebuilds the editor and deploys it to the dedicated static Hugging Face Space. The workflow also supports manual dispatch.

This Space is deliberately separate from the main §wyrlz chat/server deployment.

## Current feature set

- Three.js 3D editor viewport
- hierarchy/outliner and transform gizmos
- MOBA prefab placement
- ghost placement → Bake workflow
- prebuilt three-lane arena
- terrain height variation and depressed river
- trees, bushes, rocks, walls, camps, towers, cores
- hero movement, gravity, jumping, terrain following and blocker collisions
- minion lane movement/combat
- tower combat
- JSON save/load and playable HTML export
- mobile-focused editor controls

## Rebuild locally

```bash
python projects/swrlz-forge-moba/build_space.py --output /tmp/swrlz-forge-space
```

The output folder contains the exact deployable Hugging Face static Space package.
