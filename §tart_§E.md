# §tart §E — SWRLZ Forge Engine Build & Deploy Router

**Role:** canonical entrypoint for SWRLZ Forge / browser-engine work.

**Invocation:** `§tart §E` or `@GitHub §tart §E` means enter the dedicated Forge engine lane, reconstruct current source/deployment truth, and continue independently from the §wyrlz AI Chat/LALM application.

## Canonical lane

```text
GitHub: kaministrator999-ui/Swrlzkamico
  -> projects/swrlz-forge-moba/   (legacy folder name; engine is generic in v5)
  -> .github/workflows/deploy-swrlz-forge-moba.yml
  -> Hugging Face: kamiloki/swrlz-forge-moba
  -> https://kamiloki-swrlz-forge-moba.static.hf.space/
```

## Startup contract

On `§tart §E`:

1. Read this router and the Forge README.
2. Read `source-manifest.json`, `build_space.py`, all listed patch modules, and `SPACE_README.md`.
3. Inspect current GitHub main, last Forge workflow, and Hugging Face Space state.
4. Preserve the hard boundary from `kamiloki/Swyrlz`.
5. Preserve project/template separation: engine core ≠ MOBA example.
6. Preserve base and final source integrity.
7. Merge validated runtime changes to `main`.
8. Follow the dedicated Forge deploy workflow to terminal state.
9. Require the live static host to serve the current build marker before calling the release live.

## Current v5 source authority

```text
base:
  swrlz_forge_v4.html
  bytes 99591
  sha256 a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856

patch chain:
  patches/v4_1.py
  patches/v5_projects.py

final:
  swrlz_forge_v5.html
  bytes 120501
  sha256 c5b44363460fc29ec3a119967c082c1fd95b035d781c50a4affa9d8ecd686593

marker:
  V5_PROJECT_TEMPLATES_DRAGONS_DEN
```

## v5 project model

Forge starts in **Starter World**, not the MOBA.

Built-in templates:

- `default` / `sandbox` → Starter World
- `moba` → MOBA Arena Example
- `dragons-den` → Dragon's Den

Project state is serialized into normal `.forge.json` saves and can be loaded later. The project record owns `name`, `template`, `kind`, and `environment`.

MOBA runtime systems are explicitly gated by `currentProject.kind === 'moba'`.

Dragon's Den provides embodied-agent anchors and decorative actors but does **not** claim that spatial voice transport is implemented. Roles/tags exist so the later LALM/voice bridge has explicit semantic locations.

## Dragon's Den canonical v5 content

```text
Council Rune Dais
├── Memory Crystal
├── §wyrlz Dragon
├── Forge Dragon
├── Coder Dragon
├── Kamilion Throne
├── Code Portal
├── World Portal
├── Spatial Voice Anchor
├── Inference Core
├── Arcane rune crystals
├── cavern perimeter
├── Visitor Pawn
└── Ascension Pad
```

The Den is an example project: users can edit it, save variants, reload them, export them, or delete/rebuild actors without mutating Forge's default template.

## Deployment truth contract

```text
reconstruct base
→ verify base
→ apply governed patches
→ verify final v5 bytes/SHA
→ upload dedicated static Space
→ obtain actual host from Hugging Face
→ fetch served page
→ require V5_PROJECT_TEMPLATES_DRAGONS_DEN
→ SUCCESS
```

Never infer that upload success means the browser is serving the new engine.

## Historical checkpoints

v4.1:
- GitHub: `5d22b9411597a872900a3e9efe457f04c7b74120`
- HF: `5c4bae00017273ab8d8de5aa512b329394a90de9`

Future `§tart §E` runs must replace history with observed current truth rather than assuming this or any v5 revision remains latest.
