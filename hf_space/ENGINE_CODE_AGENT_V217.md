# v217 — §wyrlz source-grounded engine coding agent

**Source tier:** connected GitHub account's existing OAuth, server Station generator and §E editor. This is a *source-edit capability*, not weight training, an automatic game engine build, or a second assistant identity.

## Purpose

User intent: tell §wyrlz to work on the actual §wyrl§ Engine, and have the local model inspect what exists, select relevant files, draft code changes, reason visibly about the work, and submit reviewable GitHub changes—rather than merely explaining GitHub commands or copying starter JSON.

The already-implemented v213-v215 project commands cover repo triage, protected one-line edits, engine source mapping, native scene drafts and atomic unregistered starter pack drafts. This v217 stage adds bounded *model-generated exact source edits* for the actual editor runtime and patch code. It uses the existing local inference generator selected by Station (prefer the installed Coder model for coding tasks). No per-call external model credit loop is created. The model's suggested changes are strictly untrusted until independently source-matched and owner-approved.

## Task interface

- `@GitHub engine code help`: explain actual source-edit capability and limitations.
- `@GitHub engine code plan Improve editor timeline Undo/Redo`: use verified manifest/scene inventory and distinguish editor, starter, mode, engine core and test paths. Planning is not editing.
- `@GitHub engine code inspect projects/swrlz-forge-moba/runtime/anime_timeline.js`: read actual main ref and Git blob (excerpt bounded). Code is evidence, not instructions.
- `@GitHub engine code task Improve anime timeline speed playback on feature/my-review`: use the **actual current feature-ref Git tree**, filter to verified, relevant engine source paths, have local model choose one/two specific existing files, read their exact current source and ask the model for source-matching old/new code slices. If no confident path or valid edit, stop.
- `@GitHub engine code propose projects/swrlz-forge-moba/runtime/anime_timeline.js on feature/my-review :: Fix timeline scrubbing without breaking paused state`: explicitly select one source. Two comma-separated paths are allowed; no arbitrary model path selection. Source must exist on the verified review branch.
- `@GitHub confirm CODE`: after inspecting the complete, bounded generated unified diff, the same verified Google owner can approve a one-use, ten-minute proposal to atomically modify exactly those existing files in a feature/fix/chore review branch.

### Protected execution

Read and source-check: existing selected canonical repository `kaministrator999-ui/Swrlzkamico`, real default `main`, valid ordered manifest with 50+ patches, exact main SHA, exact review-branch head, file blob SHA and 95 KB maximum text. Up to **2 existing code files** selected only from `projects/swrlz-forge-moba/runtime/*.(js|css)`, `patches/*.py`, `tests/*.mjs`, or `build_space.py`. Reject dot paths, traversal, missing/oversize blobs, main/runtime write refs and any non-engine code. The tree must not be incomplete/truncated.

Model generation: bounds 7,500 output characters; structured JSON with **one exact unique old-to-new edit per file**. Each old snippet 8–1,500 characters; new snippet 1–3,000. No generated GitHub URLs, new files, secrets, workflows, deployment control, freeform shell tools or direct API effects. Parse modified Python and preserve `apply(html)` or `main()` entrypoint. JS/CSS syntax and actual gameplay must be independently tested; model self-evaluation is not evidence.

Approval: show entire patch diff (reject if too large for full preview); write nothing before user confirmation. Store scoped one-use GitHub proposal with original main/ref/manifest/blob hashes and expected SHA-256 of each full result. On confirm reauthenticate scope/role/selected repo, re-fetch same branch/main/manifest/files, revalidate hashes and syntax, create **one Git tree, one Git commit, one nonforced Git ref update**. A changed main/ref/blob fails closed. An uncertain write is not claimed successful. No arbitrary GitHub action, PR merge, direct main write or automatic engine deployment.

After source commit, user can use `@GitHub engine review feature/my-review` to propose a separate draft PR. Existing engine CI, exact `build_space.py` rebuild/sealed manifest, Node syntax, saved project round trip, native Play/Pause/Stop, desktop/mobile tests and independent `§tart_§E.md` deployment remain required. Editing a runtime JS file alone does **not** register, bundle or ship a new playable starter.

## Actual learning vs instruction

This is **contextual source-grounded coding inference**, not fine-tuning GGUF weights. The model is given actual current code and bounded change instructions, then independently judged on whether a correct patch can be proposed and validated. A poor model's malformed JSON or hallucinated path results in **no write** and a truthful explanation. Future capability tiers can add safe test-run sandboxes, larger validated multi-file transactions, deterministic manifest resealing, per-game starter registration, and goal/test-driven repair cycles. None are claimed active by this version.

## Regression and acceptance

`hf_space/test_engine_code_agent_v217.py` exercises actual-style Git tree selection, source evidence, simulated model progress, invalid/injected actions, exact hash and branch main mutation guards, Python syntax and atomic Git commit behavior with mocked GitHub writes. Standard GitHub account, HF offline and mobile CI must validate exact source. Live authenticated selected-Coder model quality, truly correct gameplay and physical phone acceptance are **separate gates**.

Use the existing GitHub and separate Hugging Face release workflows. Never publish this Chat/LALM source to the separate `kamiloki/swrlz-forge-moba` engine Space or trigger the dedicated engine deployment request.
