# v218 — Grounded §E coding missions, focused source retrieval and GitHub CI truth

**Status:** candidate source. This is project-aware tool orchestration over the selected existing local coding model, **not** model-weight retraining or a claim of production gameplay correctness.

## Why this change matters

The v217 coding agent can use GitHub on the selected engine repository to inspect project architecture, choose existing files and propose exact, owner-reviewed code edits. However, large files often exceeded its original first-5,400-character context excerpt, meaning the intended function could be thousands of characters farther into a runtime script. v218 makes code excerpts goal-relevant across a verified full file rather than blindly copying its beginning. It adds actual GitHub check evidence after an approved feature-branch commit, without pretending that GitHub checks substitute for a rebuild or browser game testing.

The engine source of truth is `kaministrator999-ui/Swrlzkamico:main/projects/swrlz-forge-moba/`. It is not the separately published Chat/LALM source branch. The hosted game engine is a distinct Space with its own build/manifest/deployment controls.

## Conversational engine work

Requests such as "Can you build a starter pack for our game engine?", "Please improve our editor timeline" and "@GitHub ask add timeline Undo/Redo to our editor" now route to project-grounded planning rather than generic Chat discussion, provided an authenticated Google owner has selected the exact engine repository in GitHub settings. The assistant reads the current source manifest, default `main` commit and real code tree and displays relevant candidate files. It does **not** infer a repository write from ordinary language.

An explicit request to start editing continues through the existing bounded workflow:

1. `@GitHub create branch feature/engine-review from main` — propose the branch, then approve it through `@GitHub confirm CODE`. The suggested branch name is an example; pick an unused name.
2. `@GitHub engine code task Improve editor timeline scrubbing on feature/engine-review` — model selects from verified existing paths, sees relevant code and returns exact source-matching edits. Alternatively `@GitHub engine code propose projects/swrlz-forge-moba/runtime/anime_timeline.js on feature/engine-review :: Fix scrubbing when paused` targets a named file.
3. Inspect the complete shown source diff before sending a separate `@GitHub confirm CODE`. The server rechecks account, role, main SHA, branch SHA, manifest SHA and source blob hashes. No direct main or protected file changes are permitted.
4. `@GitHub engine code verify feature/engine-review` — read-only view of actual current diff paths and GitHub `check-runs` at the exact branch commit. An empty, pending or failed set **never** reports passing. A completed successful set is labeled "CI only", **not** working gameplay or released engine.
5. `@GitHub engine review feature/engine-review` — separately confirm a draft PR, run engine rebuild/sealed manifest validation, relevant desktop/phone Play and editor tests, and the dedicated engine publication process.

## Better source context

Use `@GitHub engine code context projects/swrlz-forge-moba/runtime/anime_timeline.js :: Fix seek/scrub playback` to retrieve goal-relevant exact portions from the selected engine source at a verified `main` Git blob. A large source is sampled as contiguous, original substrings, each with explicit character offsets **outside** the source fence. The local coding model gets the source header and up to four strongly relevant windows. The old code snippet returned in the model proposal must still occur exactly once in the independently retrieved full original blob.

The model receives no OAuth token or private user profile, and its output is an untrusted suggestion. It may return no patch if the requested code cannot be located safely. The source-context reader rejects empty/malformed data. Diff previews remain complete and bounded, with one-use explicit confirmation. Source text is never obeyed as instructions, and arbitrary GitHub mutations, paid tool calls, CI bypass and engine deployment are not inferred from the model.

## Real project-work limitations

This tier improves the ability to understand and edit the **existing** engine code. It does not yet:
- synthesize arbitrary new modules, game mechanics or complete starter packs end-to-end;
- automatically register runtime scripts in `build_space.py` or reseal `source-manifest.json`;
- execute the user's generated JavaScript or verify native Save/Load, Play/Stop, pathing or mobile behavior in the live editor;
- bypass scope consent, create branches/writes without approval, merge PRs or publish to the separate engine Space.

The v215 atomic engine pack tool separately provides a source-grounded **scene+descriptor draft derived from existing starter scenes**, not original gameplay programming. New fully independent game modes need project-specific code changes plus manifest, runtime registration and validation. Explain this distinction clearly rather than treating a cloned map as an implemented new engine feature.

## Evidence

`hf_space/test_engine_context_verification_v218.py` covers source terms beyond character 5,400, exact unmodified source substrings in a bounded prompt, simulated coding model proposals, real-checks/false-green CI logic, protective source paths, and natural request routing. The existing v217 source edits, v215 packs, v213 project understanding, v212 GitHub permission tools and native Chat save regressions must continue passing.

Only the Chat/LALM guarded Hugging Face release may publish this feature after exact CI verification and reconciliation with any newer production changes. Release CI is not signed-in Google/GitHub user acceptance, and cannot establish playable engine behavior by itself.
