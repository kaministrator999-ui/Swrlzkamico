# §wyrlz Coder Project School — Stack + Architecture (v1)

**State:** SOURCE CURRICULUM ONLY / NOT WEIGHT-TRAINED / NOT LIVE-PREFILL ACTIVATED.  
**Audience:** the deployed Qwen2.5-Coder-1.5B-Instruct GGUF programming route, a repository-enabled coding assistant, and future independently evaluated student models.  
**Canonical owners:** [Project Start](../../§wyrlz_§tart.md), [Programming LALM Runtime Architecture](../../docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md), [Architecture Reconciliation Protocol](../../docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md), [Version Evolution](../../SWRLZ_VERSION_MODULE_EVOLUTION.md). This is **teaching material**, not a second policy/architecture authority.

**Cross-language continuation:** [Coder Academy v2 — Kotlin, Java, TypeScript and Rust](CROSS_LANGUAGE_CURRICULUM_V2.md) extends this source-backed course to technologies that are not yet current repository implementation dependencies. It includes four stand-alone teacher examples and [12 ungraded cross-language exercises](cross_language_practice_v2.json). Learn relationships before proposing an actual migration. A course file is not a trained model or activated prefill.

## 0 — Read current source, not the age of a document

A correct student answers **what is implemented and on which branch**, not merely what a contract proposes. Refresh actual files, manifests, SHAs, module authorities, runtime evidence and deployment status before a project patch.

- `main`: project contracts, Forge native engine source and its **separate** release workflow, stable application infrastructure and historical artifacts.
- `runtime`: `VERSION.txt`, `versions/*.txt`, runtime-hot pages/assets and manifest; do **not** infer missing runtime content from a `main` 404.
- **Observed route mismatch at inventory:** `runtime:runtime_pages/manifest.json` maps `/chat/§wyrlz` to `chat/§wyrlz/index.html`, but that file was **not present in the inspected `runtime` tree**; `feature/hf-space-manual-deploy:chat/§wyrlz/index.html` is present and the HF Station separately serves that route. This is an authority/activation reconciliation case: inspect current hosting source and live route before declaring either route healthy or deleted.
- `feature/hf-space-manual-deploy`: current selected Hugging Face Chat/Station/model-route application package. Pin the selected source SHA before engineering its runtime.
- **Two different Spaces:** Chat/LALM `kamiloki/Swyrlz`; §wyrl§ Engine `kamiloki/swrlz-forge-moba`. They must never share a deployment trigger accidentally.
- **Historical caution:** the root packaging metadata and old Vercel entrypoints exist for lineage. Current Chat publication is through the guarded Hugging Face request on `main`.

At first inventory (2026-10-09), the inspected `main`, `runtime`, and HF candidate trees contained Python, JavaScript, HTML, CSS, C, JSON/JSONL, YAML and TOML; no `.kt`, `.java`, `.ts`, `.tsx`, or `.rs` implementation files were found in those three trees. This does **not** mean the languages are unsupported as user-requested coding targets; it means they are not verified current repository implementation languages.

## 1 — Project languages and boundaries

| Actual source | Learn | Source examples | Correct owner |
|---|---|---|---|
| Python 3 | type/contracts, async, HTTP, routing, tests, builds | `hf_space/station.py`, `hf_space/model_router.py`, `api/index.py`, `projects/swrlz-forge-moba/build_space.py` | Server/Brain/build by explicit component |
| JavaScript (browser) | DOM, state ownership, events, streams, browser rendering | `chat/§wyrlz/index.html`, `projects/swrlz-forge-moba/runtime/anime_timeline.js` | Mask/Chat or Forge engine; do not copy across products |
| HTML5 and CSS | accessibility, responsive composition, style/state geometry | clean-room Chat, `projects/swrlz-forge-moba/runtime/*.css` | owning browser surface |
| C native | CPython/NumPy extension, memory/dtype, OpenMP flags, Python fallback | `native/r39_native.c`, `native/r39_batch.c`, `setup.py` | R39 native extension |
| Three.js/WebGL (JS library) | scene graph, camera, `Group`, `Box3`, textured planes, transforms | `projects/swrlz-forge-moba/runtime/anime_stage.js`, `anime_emergence.js` | §wyrl§ Engine renderers |
| JSON / JSONL | canonical schemas, source proofs, saved project transforms, eval records | `runtime_pages/manifest.json`, `projects/swrlz-forge-moba/source-manifest.json`, `training/` | owning manifest/project/training ledger |
| YAML / TOML / shell | CI, exact dependencies/build contracts and guarded release | `.github/workflows/*.yml`, `pyproject.toml` | CI and package ownership |

**Not verified as production dependencies:** React, Vue, Angular, TypeScript, Java/Kotlin/Gradle, Rust/Cargo, an npm-managed Forge app. Do not add one just because a generic programming model prefers it.

### Architecture lesson: language choice is not component ownership

A prompt that says “fix the Chat header” does not mean Python; first trace the runtime route and owner. “Make the Forge character grip follow its wrist” belongs to the engine's socket/rig data and shared renderer, not the Chat UI. “Fix model selection” belongs to the explicit inference routing boundary, not Forge or Chat CSS.

## 2 — Dependency school: NEVER mix install environments

| Environment | Manifest/owner | Verified declarations at inventory |
|---|---|---|
| Current HF Chat runtime | `feature/hf-space-manual-deploy:hf_space/requirements.txt` | `gradio>=5,<7`; `spaces>=0.30,<1`; `numpy==2.2.6`; `requests>=2.32,<3`; `google-auth>=2.35,<3`; `fastapi>=0.115,<1`; `uvicorn>=0.30,<1`; `huggingface_hub>=1.16,<2`; `llama-cpp-python==0.3.35` plus CPU wheel index |
| Separate HF 700M test bench | `hf_700m_test/requirements.txt` | `gradio>=5,<7`; `huggingface_hub>=0.34,<2`; `llama-cpp-python==0.3.35` (CPU wheels) |
| Legacy/stable root Python package | `main:requirements.txt`, `pyproject.toml` | `fastapi==0.116.1`; `numpy==2.3.2`; `pydantic==2.11.7`; `google-auth>=2.35,<3`; `requests>=2.32,<3`; `vercel-queue` in root package; `urllib3>=2.2,<3` in root requirements |
| C extension build | `setup.py` | Python setuptools/wheel, NumPy C headers; optional OpenMP compiler flags (do not assume compiler/OpenMP always available) |
| Forge static package | `projects/swrlz-forge-moba/build_space.py` | Python standard library reconstruction and JS runtime using Three.js; CI uses Python 3.11 and Node 22 for validation |
| Governed 700M LoRA experiment (not active coder training) | `training/700m/train_lora.py` | imports `datasets`, `transformers`, `peft`, `trl` only when training runs; not a production HF runtime requirement |

**Exercise A:** A future engineer wants to “fix NumPy version mismatch” by setting the root and HF manifests to one number. Reject the change pending environment-specific runtime evidence. Explain why build/ABI compatibility, candidate source ref, and independent testing matter.

## 3 — Chat product: Mask → Station → Brain/model → Station → Mask

```text
Audience
  ↓ user interacts with HTML/CSS/JS Chat Mask
/chat/§wyrlz (chat/§wyrlz/index.html)
  ↓ Chat state request / generation stream endpoints
HF FastAPI Station (hf_space/station.py)
  ↓ operational admission, request/thread/artifact lifecycle, stream events
Brain/model router (hf_space/model_router.py + brain_programming.py)
  ↓ semantic coding intent? route to Qwen coder; otherwise selected supported model
  ├─ Qwen2.5-Coder-1.5B Instruct GGUF → hf_space/qwen_coder_engine.py
  ├─ LFM2-700M GGUF → hf_space/lfm2_700m_engine.py
  ├─ stock LFM2-350M GGUF → hf_space/original_engine.py
  └─ R39 native-owned route (not interchangeable with Qwen)
  ↓ generated events / validation / persistence/projection
Station stream → Chat Mask renders response
```

Verified entrypoints: `hf_space/app.py` mounts the Station and Gradio probes, `station.py` exposes `/chat/§wyrlz`, `/api/chat_state`, `/api/lalm_station/stream`, `/api/lalm_station/sync`; `model_router.py::dispatch` routes detected coding tasks to `coder`. The Qwen engine loads `Qwen/Qwen2.5-Coder-1.5B-Instruct-GGUF` using `hf_hub_download` and `llama_cpp.Llama` (CPU GGUF path). The code provides a **runtime policy/context**, not a claim that this curriculum is already loaded into Qwen weights.

**Owner separation:** Brain owns intent/semantic classification and candidate contract checks; Station owns operational lifecycle and delivery, **not semantic grading**; Mask owns display; evaluator/test evidence owns acceptance. Keep canonical stored history distinct from a transient inference-facing context projection.

**Product caveat:** `hf_space/station.py` calls itself an HF in-process candidate and warns against claiming full durable account/queue parity from its process-local code. Verify actual activated runtime rather than extrapolating from unused legacy API modules.

**Exercise B:** A coder request accidentally launches web research instead of generating code. Trace `brain_programming.programming_intent` → `model_router.dispatch` → coder generation; do not “fix” this by duplicating intent classification in the Chat DOM.

## 4 — Native R39: Python ↔ C is an ABI boundary

`main:setup.py` builds `swyrlz._r39_native` and `swyrlz._r39_batch` from C sources under `native/`, with NumPy include directories, optimized compiler flags, optional `-fopenmp`, and a Python fallback path in the engine. A C-level shape/dtype/ABI bug is not corrected by changing text in the frontend. Check native compile provenance, import boundaries, expected data shape/dtype, and whether a fallback was legitimately selected.

**Exercise C:** A Python/R39 request raises `ModuleNotFoundError` for an extension. Determine whether the exact wheel/extension was built against the running Python/NumPy ABI; do not invent a pip package with a similar name.

## 5 — §wyrl§ Engine: deterministic build and owned scene systems

```text
main:projects/swrlz-forge-moba/source-manifest.json
   ↓ ordered gzip+base64 payload chunks and verified base SHA/bytes
build_space.py
   ↓ call apply(html) for each listed Python patch IN MANIFEST ORDER
   ↓ verify final HTML SHA/byte count
   ↓ package media and SOURCE.json receipts
static HF Space: kamiloki/swrlz-forge-moba
   ↓ browser Three.js world / editor / Play / Watch
project-owned scene JSON + workspaces + timed animation
```

Current `source-manifest.json` names **§wyrl§ Engine v9.4 source candidate**, 53 ordered patches, expected final **1,044,257 bytes** and SHA-256 `cd761d29218dc36d0f0626968bfa9882584388c55f84411ce37caac16f4c1f01`. These values are **build expectations**, not evidence v9.4 is currently live. `§tart_§E.md` owns the dedicated engine readiness and deployment process; no Chat/LALM release trigger can substitute for `projects/swrlz-forge-moba/DEPLOY_REQUEST.json`.

### Engine object responsibilities

- `runtime/anime_timeline.js`: saved `anime-timeline-v1`, 9 tracks, interpolation, undo/redo transaction hooks, keyframe editing, time/track bounds; one shared owner for Preview/Play/Watch.
- `runtime/anime_stage.js`: paper character/scenery groups, textures, scene camera, rendered actors and authored transforms. Uses `THREE.Group`, `THREE.TextureLoader`, `THREE.Box3` and related native Three.js constructs.
- `runtime/anime_editor.js`: UI controls for the *same* timeline. Never create a separate shadow timeline.
- `runtime/anime_socket_model.js`: persistent `anime-rig-sockets-v1` character socket/connection tree; `runtime/anime_rig_model.js` owns rig key data and the renderer applies it.
- `runtime/anime_scenery_model.js`, `runtime/anime_scenery_renderer.js`: individual scenery cutout transforms and depth.
- `runtime/anime_emergence.js`: `anime-book-emergence-v1` book-opening logic anchored to the **physical page hinge**, not a camera-relative screen offset.
- `runtime/*.css` and editor JS: UI presentation of these same native state owners.

Editor responsibilities must not override renderer truth, and rendering must not silently mutate project save-state. Native Save/Load, undo/redo, Play/Watch parity, route/workspace separation, actor-camera bounds, and expected source hashes are protected invariants.

**Exercise D:** A mage's left-hand staff floats away after rotating the wrist. Trace wrist→hand→grip ownership in `anime_socket_model.js`, rig state/renderer, then inspect shared rendered output. Do not compensate with a hardcoded screen-space offset in editor CSS.

## 6 — Releases, version lineage and cross-chat collaboration

- For Chat/LALM, documentation/training-only work is deployment-inert. A validated production update targets **existing** `kamiloki/Swyrlz`, selecting the current candidate source through the guarded `main:.deploy/HF_SPACE_REQUEST.txt` → `.github/workflows/hf-space-request.yml` → `.github/workflows/manual-hf-space.yml`. No competing new Space.
- For §E/Forge, the dedicated `projects/swrlz-forge-moba/DEPLOY_REQUEST.json` and `.github/workflows/deploy-swrlz-forge-moba.yml` are separate. Engine v9.4 is not automatically live simply because `source-manifest.json` names it.
- `runtime:VERSION.txt` points to module-owned `versions/*.txt`; bump Repository Work for completed governed work, only the changed modules for component mutations, and Server Runtime only for an actual Server release.
- Separate AI chats may share one repo but **not** uncommitted private conversation state. Use task branches, SHA-protected updates, source receipts, a single integration owner, and independent regression/activation checks.
- Keep all diagnostic cameras privacy-bounded: no tokens, raw user profile, private conversation content or credentials in the training pack or a GitHub issue.

**Exercise E:** A second chat has already committed a newer Web Chat version and the first chat proposes a UI fix from an older blob. The only correct start is re-fetch and reconcile the current owner/version/branch HEAD. A code patch against stale bytes is not acceptable.

## 7 — How to use these lessons (not how to fake training)

**Study sequence:** (1) branch/source authority; (2) languages/dependencies; (3) Chat event path; (4) native C boundary; (5) Forge build and object ownership; (6) release gates and concurrency. For each module: retrieve cited source, explain it in your own words, locate one invariant and its owner, solve the exercise, then require independent test or source-based evaluator evidence.

**Practice/evaluation:** [project_stack_architecture_v1.json](project_stack_architecture_v1.json) contains 12 **ungraded** exercises with source anchors and acceptance/rejection criteria. They are *public practice tasks*, not leakage-safe held-out tests or independently verified positive training samples.

**Evidence ladder:**
```text
Documented lesson → model/session reads it → observed coding response
→ compiler/pytest/node/browser/real build evaluator PASS with receipts
→ exact corrected source+original request+provenance recovered
→ curated TRAIN / truly separate HELD-OUT sets
→ specialist-specific fine-tune + held-out comparison, if justified
→ guarded activation + live acceptance
```

The existing `training/700m/train_lora.py` is a governed **700M** student trainer. Do not silently run it against Qwen or assume it trained the coder. A Qwen-specific weight-training pipeline and dataset/provenance contract would need independent review, environment support, model-specific tests and promotion approval. This pack alone changes **zero model weights** and is not automatically injected into the production coder prompt.

## Source index (read exact branch and current commit before acting)

- `main:§wyrlz_§tart.md`; `main:§tart_§E.md`.
- `main:docs/engineering/SWRLZ_PROGRAMMING_LALM_RUNTIME_ARCHITECTURE.md`; `main:docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`; `main:docs/engineering/SWRLZ_700M_WEIGHT_LEARNING_PIPELINE.md`.
- `feature/hf-space-manual-deploy:hf_space/{app,station,model_router,brain_programming,qwen_coder_engine,lfm2_700m_engine}.py`; `hf_space/requirements.txt`.
- `main:requirements.txt`, `pyproject.toml`, `setup.py`, `native/r39_native.c`, `native/r39_batch.c`.
- `main:projects/swrlz-forge-moba/{source-manifest.json,build_space.py,ANIMATION_STUDIO.md,DEPLOY_REQUEST.json}`; `runtime/anime_*.js`; `main:.github/workflows/deploy-swrlz-forge-moba.yml`.
- `runtime:VERSION.txt`, `runtime:versions/*.txt`, `main:SWRLZ_SERVER_ROADMAP.md`.

**Teacher's rule:** Source truth first; explain the relationship, not a memorized file name; an answer is not a passing implementation until separately verified. 
