# §wyrlz Staged Project Workspaces v185

**Status: ISOLATED CANDIDATE. NOT DEPLOYED, NOT WEIGHT TRAINING.**

## User-visible assembly

The previous v184 feature packages one completed Chat response. The v185 project workspace joins source files from multiple *different completed responses* into a manifest-controlled project.

1. After a code response is complete, click **Project workspace**. Supply a project title and a list of ALL required relative source filenames, one per line.
2. The server creates a project in the same process-local caller session and thread; every source file added is from an already committed code-artifact revision and SHA. Browser input never supplies source bytes.
3. Subsequent completed code responses can be attached to the same project, preserving previous files. Each attachment advances an optimistic workspace revision; stale concurrent writes are rejected.
4. Incomplete work shows completed/required counts and names of remaining source files. A **Prepare next file** action writes a suggested next-file request into the composer; the user decides when to send it. No invisible model generation or credit-consuming background loop is started.
5. When every required path has source content, Station finalizes the workspace and enables **Download assembled ZIP**. The ZIP retains the safe relative paths and is assembled in memory on a session-scoped GET.
6. All structural file paths being present does **not** prove the generated code compiles, passes tests or meets the user's full original requirements; validationState remains NOT_RUN.

For example, a manifest naming src/app.py, tests/test_app.py and README.md stays at 1/3 after only the first response. Its final ZIP is locked until all three named files were attached.

## Canonical architecture

Station owns projectWorkspaces on the existing thread, alongside the existing codeArtifacts and immutable source revisions. The pure staged_workspaces.py helper does not call inference, touch a local filesystem, push to GitHub or grant tool permissions.

Endpoints (all bound to existing caller session and thread):
- POST /api/lalm_station/workspaces — creates required-file manifest;
- GET /api/lalm_station/workspaces?threadId=... — lists bounded progress metadata;
- POST /api/lalm_station/workspaces/attach — optimistic revision + exact committed artifact ID/revision/SHA;
- POST /api/lalm_station/workspaces/finalize — all required paths present before READY;
- POST /api/lalm_station/workspaces/cancel — cancels without releasing incomplete work;
- GET /api/lalm_station/workspaces/download — READY revision/source hash required; ZIP response no-store, nosniff and same-origin.

A download response includes X-Workspace-Validation: not-run to prevent accidental compiler/test success claims. There is no public raw filesystem path or unauthenticated ZIP endpoint.

## Safety and current limits

- At most 5 workspaces per thread, up to 32 UTF-8 files per workspace, 1MiB per file, 8MiB total; shared v184 path validation also rejects traversal, absolute paths, reserved Windows components and duplicate names. v185 additionally rejects file-vs-directory collisions.
- No user/editor input may overwrite source without matching optimistic revision; same-session/thread boundaries and source checks are mandatory.
- Workspaces are **process-local**. A server restart, session expiration or cookie loss prevents resume. Durable account-backed storage requires separate authority, retention/export policy and tests.
- The manifest currently comes from the user, not an independent semantic requirements planner. Project presence is a structural readiness gate, not proof it implements every requirement.
- No autonomous multi-turn file-generation loop, binary artifacts, compiler runs, mobile visual acceptance or trained GGUF weights are claimed. Later increments can add verified dependency-aware planning, on-device resume and independently tested final archives.

## Promotion

This candidate is stacked on v184 and must not merge or deploy ahead of its base. Source-only GitHub Action workflow verify-staged-workspaces-v185.yml tests manifest/version/zip and session isolation, the original v184 package tests, and JavaScript syntax. Whole-HF regression and live browser testing remain separate release gates. No Hugging Face or Forge deployment request is modified.
