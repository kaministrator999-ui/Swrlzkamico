# §tart §E — §wyrl§ Engine Build & Deploy Router

**Role:** canonical entrypoint for §wyrl§ Engine / browser world-engine work.

**Invocation:** `§tart §E` or `@GitHub §tart §E` means enter the dedicated §wyrl§ Engine lane, reconstruct current GitHub/Hugging Face truth, and continue independently from the §wyrlz AI Chat/LALM application.

## Canonical lane

```text
§wyrl§ Engine
GitHub: kaministrator999-ui/Swrlzkamico
  -> projects/swrlz-forge-moba/    (legacy path retained for lineage)
  -> .github/workflows/deploy-swrlz-forge-moba.yml
  -> HF Space: kamiloki/swrlz-forge-moba
  -> https://kamiloki-swrlz-forge-moba.static.hf.space/
```

## Startup contract

On `§tart §E`:

1. Read this router and the engine README.
2. Read `source-manifest.json`, `build_space.py`, every listed patch module, and `SPACE_README.md`.
3. Inspect current GitHub main, the latest §wyrl§ Engine deployment workflow, and current Hugging Face Space state.
4. Preserve the hard deployment boundary from the main §wyrlz AI Chat/LALM Space.
5. Preserve project separation: §wyrl§ Engine core ≠ MOBA example ≠ Dragon's Den project data.
6. Preserve source integrity and compatibility aliases.
7. For runtime changes, validate the final generated HTML and JavaScript before merge.
8. Merge validated changes to `main`.
9. Follow the dedicated engine deployment to terminal state.
10. Require the actual served static host to contain the current deploy marker before calling the release live.

## Current v5.1 source authority

```text
base:
  swrlz_forge_v4.html
  bytes 99591
  sha256 a8299fe89fbb98d15c6091751b7a66931a66efec8eec5cb464e1286f21895856

patches:
  patches/v4_1.py
  patches/v5_projects.py
  patches/v5_1_swyl_engine_seed_den.py

final:
  swyl_engine_v5_1.html
  bytes 129398
  sha256 a653064ce2be625d67d561a1db249a1bb4fa0637dc69377480cf6311e43fdf51

marker:
  SWYRL_ENGINE_DEPLOY_MARKER: V5_1_SEED_DEN
```

## Current project model

Default boot project:

**Dragon's Den — Seed Chamber**

Other built-ins:

- Blank Starter World
- MOBA Arena example

The Dragon's Den starter must remain an **immersive enclosed environment**, not a MOBA/open-world field. Its current architectural zones are:

```text
Wake Nook
    ↓
Main Council Chamber
├── Creator Alcove
├── Throne Side
├── Dragon Perch Side
├── Portal Hall Exit
├── Memory Vault Exit
└── Inference Core Exit
```

The Den currently includes dormant expansion exits and semantic hooks. Do not add launch pads or arbitrary game mechanics to the default starter unless explicitly requested.

## Engine naming and compatibility

User-facing name: **§wyrl§ Engine**.

Preferred new APIs:

- `window.SWYRL_ENGINE_BUILD`
- `window.SWYRL_ENGINE_AGENT`

Legacy `SWRLZ_FORGE_*` aliases remain armed so existing integrations do not break.

## Deployment truth contract

```text
reconstruct base
→ apply governed patch chain
→ verify final bytes/SHA
→ syntax-check generated module
→ upload dedicated static Space
→ obtain actual HF host/subdomain
→ fetch served page
→ require SWYRL_ENGINE_DEPLOY_MARKER: V5_1_SEED_DEN
→ SUCCESS
```

Never equate upload success with live serving success.

## Historical lineage

v5:
- GitHub engine release: `e3dcc4b24aa3737ef1fdfe1690421e8bf384b58b`
- HF revision: `16d49cbe240800baf138a33f23e86c21015ace57`

v4.1:
- GitHub: `5d22b9411597a872900a3e9efe457f04c7b74120`
- HF: `5c4bae00017273ab8d8de5aa512b329394a90de9`

These are checkpoints, not assumed current truth after later releases.


## Verified v5.1 deployment checkpoint

```text
Engine:
§wyrl§ Engine v5.1

GitHub source/deploy commit:
214b60c4225642db13e7e0601f45410d6aa0d408

Final source:
129398 bytes

SHA-256:
a653064ce2be625d67d561a1db249a1bb4fa0637dc69377480cf6311e43fdf51

Hugging Face revision:
e741f6541893c218cac9f662976a58ca0645460c

Static host:
https://kamiloki-swrlz-forge-moba.static.hf.space/

Stage:
RUNNING

Live marker:
SWYRL_ENGINE_DEPLOY_MARKER: V5_1_SEED_DEN

Live verification:
PASS on attempt 1
```

The current observed default project is **Dragon's Den — Seed Chamber**.

### v5.1 deployment debugging lineage

Preserve these failure receipts rather than rewriting them away:

1. The first v5.1 deployment rebuild passed, but the inline deployment receipt Python contained a literal `\n` sequence inside source and failed before upload.
2. The workflow was repaired, and generated §wyrl§ Engine JavaScript was explicitly syntax-checked with Node.
3. The next upload was correctly rejected by Hugging Face because `short_description` exceeded the 60-character metadata limit.
4. Space metadata was shortened without changing engine source.
5. The final deployment passed reconstruction, SHA/byte integrity, JavaScript syntax, Hugging Face upload, Space runtime status, and live marker verification on attempt 1.
