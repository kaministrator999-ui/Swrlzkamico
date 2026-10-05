# §tart §E — SWRLZ Forge Engine Build & Deploy Router

**Role:** canonical entrypoint for SWRLZ Forge / browser-engine work.

**Invocation:** when the user says `§tart §E` or `@GitHub §tart §E`, treat it as an execution command to enter the engine project, reconstruct its current source/deployment state, and continue engine work from GitHub through its dedicated Hugging Face deployment path.

This router exists specifically so Forge can be engineered and deployed **separately from the §wyrlz AI Chat / LALM application**.

---

## 1. Engine identity and boundaries

### GitHub source repository

```text
kaministrator999-ui/Swrlzkamico
```

### Engine project root

```text
projects/swrlz-forge-moba/
```

### Dedicated deployment workflow

```text
.github/workflows/deploy-swrlz-forge-moba.yml
```

### Dedicated Hugging Face Space

```text
kamiloki/swrlz-forge-moba
```

### Standalone live page

```text
https://kamiloki-swrlz-forge-moba.hf.space/
```

### Hugging Face project page

```text
https://huggingface.co/spaces/kamiloki/swrlz-forge-moba
```

The Forge Space is a **static Space** and is independent from the main AI Chat/LALM Space `kamiloki/Swyrlz`.

**Hard boundary:** Forge work must not deploy through, overwrite, or repurpose the main Chat/LALM Hugging Face workflow or Space unless the user explicitly asks to integrate the two systems.

---

## 2. §tart §E execution contract

When `§tart §E` is received:

1. Use the GitHub connector.
2. Open `kaministrator999-ui/Swrlzkamico`.
3. Read this document first.
4. Inspect `projects/swrlz-forge-moba/README.md`.
5. Inspect the current engine source manifest and builder:
   - `projects/swrlz-forge-moba/source-manifest.json`
   - `projects/swrlz-forge-moba/build_space.py`
   - `projects/swrlz-forge-moba/SPACE_README.md`
6. Inspect `.github/workflows/deploy-swrlz-forge-moba.yml`.
7. Reconstruct the current engine source/deployment state before editing.
8. Keep engine work scoped to the Forge project and its dedicated deployment workflow unless another subsystem is explicitly required.
9. After runtime-affecting engine updates, commit the finished candidate and let the dedicated Forge workflow deploy it to `kamiloki/swrlz-forge-moba`.
10. Observe the terminal GitHub Actions result and report the exact GitHub source commit plus Hugging Face Space revision when available.

Do not stop at “file found” or “ready.” The startup result should tell the user the current Forge source state, deployment state, live target, and any unresolved engine work discovered.

---

## 3. Current source-of-truth layout

The current Forge v2 editor originated as one HTML project. The exact source bytes are preserved losslessly in the repository as gzip + base64 chunks:

```text
projects/swrlz-forge-moba/
├── README.md
├── §tart linkage via this root router
├── SPACE_README.md
├── source-manifest.json
├── build_space.py
├── DEPLOY_REQUEST.json
└── payload/
    ├── part-01.txt
    ├── part-02.txt
    ├── part-03.txt
    ├── part-04.txt
    ├── part-05.txt
    └── part-06.txt
```

`source-manifest.json` owns the integrity contract for the current serialized HTML source:

- original byte length;
- SHA-256;
- payload encoding;
- ordered payload chunk list.

`build_space.py` reconstructs the original `index.html` byte-for-byte, verifies its hash and byte count, and stages the deployable Space package.

Current accepted source integrity after the Unreal-inspired v3 pass:

```text
artifact: swrlz_forge_unreal_pass_v3.html
bytes: 89746
sha256: 5459e050394a7cbab9bcf0cde16598975611dd0896273f9c04a21e45c309a2a9
```

The design study that informed this pass is recorded in `projects/swrlz-forge-moba/UNREAL_STUDY.md`.

If the engine source changes, update the payload and `source-manifest.json` together so the builder continues to prove the deployed HTML came from the intended GitHub source.

If the project is later refactored into normal editable source files/modules, update this router and `build_space.py` in the same governed change so the source authority never becomes ambiguous.

---

## 4. Canonical engine build flow

```text
user asks for Forge change
        ↓
§tart §E
        ↓
GitHub: kaministrator999-ui/Swrlzkamico
        ↓
projects/swrlz-forge-moba/
        ↓
inspect current source + manifest + deployment workflow
        ↓
implement engine/editor/game changes
        ↓
update source integrity manifest
        ↓
commit to main
        ↓
path-filtered GitHub Action
.deploy? NO
main Chat/LALM deployment? NO
        ↓
.github/workflows/deploy-swrlz-forge-moba.yml
        ↓
rebuild exact index.html
        ↓
verify byte count + SHA-256 + Space metadata
        ↓
create/update dedicated static Space
        ↓
kamiloki/swrlz-forge-moba
        ↓
https://kamiloki-swrlz-forge-moba.hf.space/
        ↓
capture deploy receipt + HF revision
```

This is the canonical Forge deployment lane.

---

## 5. Separation from AI Chat / LALM

Forge and the AI Chat share a GitHub repository today, but they have different runtime/deployment owners.

### Forge

```text
projects/swrlz-forge-moba/**
    -> deploy-swrlz-forge-moba.yml
    -> kamiloki/swrlz-forge-moba
```

### AI Chat / LALM

```text
main §wyrlz application source
    -> its guarded HF application deployment chain
    -> kamiloki/Swyrlz
```

Engine work must not casually modify:

- the main Chat/LALM Space target;
- `.deploy/HF_SPACE_REQUEST.txt`;
- `.github/workflows/hf-space-request.yml`;
- `.github/workflows/manual-hf-space.yml`;
- Chat/LALM runtime packaging;
- model/runtime deployment contracts.

Likewise, ordinary Chat/LALM changes must not be treated as Forge releases.

If a future agent tunnel intentionally connects the AI to Forge, preserve the boundary:

```text
AI / agent inference
        ↓
bounded Forge command/API tunnel
        ↓
ghost/proposal layer
        ↓
validation
        ↓
user/authorized bake
        ↓
authoritative scene
```

Integration does not mean deployment ownership is merged.

---

## 6. Deployment trigger behavior

The Forge workflow is path-filtered to **deployment-affecting Forge files only**:

```text
projects/swrlz-forge-moba/payload/**
projects/swrlz-forge-moba/source-manifest.json
projects/swrlz-forge-moba/build_space.py
projects/swrlz-forge-moba/SPACE_README.md
.github/workflows/deploy-swrlz-forge-moba.yml
```

It also supports manual workflow dispatch.

Documentation-only changes such as `§tart_§E.md` or `projects/swrlz-forge-moba/README.md` are deployment-inert and must not publish a new Space revision merely because documentation changed.

Therefore a completed **deployment-affecting Forge source change** on `main` automatically starts the dedicated Hugging Face deployment.

The deployment job must:

1. checkout the exact triggering GitHub commit;
2. run `build_space.py`;
3. validate reconstructed `index.html`;
4. validate Hugging Face static-Space metadata;
5. use the repository `HF_TOKEN` secret;
6. create/update only `kamiloki/swrlz-forge-moba`;
7. upload the staged Space folder;
8. capture a deployment receipt containing the source commit and resulting Space revision.

Do not use the main `kamiloki/Swyrlz` deployment chain as a shortcut for Forge.

---

## 7. Failure/debug loop

If the Forge GitHub Action fails:

```text
workflow failure
    ↓
read exact failed step + logs
    ↓
identify source/build/metadata/HF failure
    ↓
repair only the owning Forge source/workflow
    ↓
commit corrected candidate
    ↓
observe new Forge deployment run
    ↓
report source/static/deployed/live truth separately
```

Do not call a failed deployment successful merely because the commit exists.

Creation-history example: the first Forge deploy reached Hugging Face but failed metadata validation because `short_description` exceeded Hugging Face's 60-character limit. The metadata was corrected and the next dedicated Forge workflow completed successfully. Preserve failures like this as evidence instead of rewriting history.

---

## 8. Current initial successful deployment lineage

Initial dedicated deployment:

```text
GitHub source commit:
3024b4e8d81ec515ab8d08d6d7d2b81547e57f4b

Hugging Face Space:
kamiloki/swrlz-forge-moba

HF Space revision:
a22686c4b1326c10fd8884965b18cdad8e50224e
```

This is historical lineage, not a permanent claim that the same revision is current. On every `§tart §E` invocation, inspect the current GitHub and Hugging Face state rather than assuming this initial deployment is still latest.

---

## 9. Engine architecture direction

Current Forge capabilities include:

- browser-native Three.js editor;
- searchable hierarchical World Outliner with folders and visibility;
- Details-style Transform / Components / Gameplay / Physics inspector;
- transform gizmos with World / Local space;
- translation / rotation / scale snapping;
- Perspective + Top / Front / Right cameras;
- Lit / Unlit / Wireframe viewport modes;
- Undo / Redo transaction history;
- Content Drawer, asset search, Output Log, and Build Validation;
- reusable actor-component metadata and runtime execution;
- Play In Editor and Simulate In Editor;
- Pause / Resume, Play From Here, and Keep Simulation Changes;
- ghost placement → Bake;
- bounded `window.SWRLZ_FORGE_AGENT` editor command API;
- MOBA prefabs and prebuilt three-lane arena;
- terrain, river, foliage, rocks, walls, camps, towers, and cores;
- hero movement, gravity, jumping, terrain following, and blocker collision;
- minion waves and lane combat;
- tower combat and simple physics bodies;
- project JSON save/load;
- standalone playable HTML export with component behavior support;
- mobile editor controls.

Planned architecture may evolve toward:

```text
Forge Editor
├── Scene graph
├── Asset/prefab system
├── Physics/collision
├── Components/scripts
├── Materials/terrain
├── Project persistence
├── Multiplayer collaboration
│   ├── per-user presence orb
│   ├── ghost/proposal layers
│   └── Bake/commit revisions
├── Agent command tunnel
│   ├── read scene
│   ├── propose ghost edits
│   ├── validate/test
│   └── request/perform authorized bake
└── Exported runtime/game
```

Prefer editor-camera precision for creation. FPS/player-style control belongs to play/test mode, not as the default editing model.

---

## 10. Definition of done for Forge changes

A Forge update is complete when applicable:

- current engine source authority was read first;
- implementation is scoped to the Forge project;
- no accidental Chat/LALM deployment path was touched;
- source integrity data matches the new source;
- the dedicated Forge workflow rebuilt the project successfully;
- Hugging Face publication completed successfully;
- the resulting Space revision was observed;
- live-page behavior was verified when the change requires it;
- any failure/repair path is reported accurately.

---

## Bottom line

**`§tart §E` means: enter SWRLZ Forge as its own project lane, read this router, operate from `projects/swrlz-forge-moba/`, build from GitHub source, deploy only through `.github/workflows/deploy-swrlz-forge-moba.yml`, publish only to `kamiloki/swrlz-forge-moba`, and keep that entire engine lifecycle separate from the §wyrlz AI Chat/LALM deployment path.**
