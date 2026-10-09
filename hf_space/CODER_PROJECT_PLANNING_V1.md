# §wyrlz Coder Project Planning — Model Proposal and Controlled Build

**State:** Isolated GitHub source candidate; NOT deployed; no changed Qwen or 700M model weights. Stacked on draft code-delivery and staged-workspace PRs. Live lyric-model releases are independent.

## From requirements to code ZIP

A user describes a software project and presses **Plan**. Chat prepares a reviewable planning request but does NOT send it automatically. When the user sends it, the existing coder route is instructed to return ONE fenced swrlz-project-manifest JSON object with these fields:

- schema = "swrlz-project-manifest-v1"
- title and optional bounded goal
- files: 1 to 32 entries with path, language, purpose and dependsOn (paths of prerequisite files).

Example JSON body:

{
  "schema": "swrlz-project-manifest-v1",
  "title": "CLI Demo",
  "goal": "Build a small CLI and tests",
  "files": [
    {"path":"tests/test_app.py","language":"python","purpose":"Tests","dependsOn":["src/app.py"]},
    {"path":"src/app.py","language":"python","purpose":"Implementation","dependsOn":[]}
  ]
}

The backend parses ONLY an actual completed assistant message from the same cookie-owned thread. It rejects malformed, oversized, duplicate, unsafe, self-referential, unresolved or cyclic file plans. File generation order is computed via a deterministic dependency walk.

**Review project plan** displays filenames and dependencies. The user explicitly confirms; the Station re-reads the same source and requires matching SHA-256 of the complete message and the canonical plan before creating a workspace. Approving the same unchanged plan again reuses its existing workspace, rather than creating a duplicate. A model-proposed plan is not permission to install dependencies, run tools, deploy, or spend inference credits without further consent.

The approved workspace continues to use the canonical Station codeArtifacts and immutable source artifact revisions. Its progress includes nextReadyPaths, chosen from actual completed dependency files. **Generate next planned file · 1 request** prepares exactly one code-generation prompt, then separately confirms before using the existing model send path ONE time. No unattended multi-call loop, hidden fees or model-created tool authorization.

Generated source must be a completed response and pass the existing file path/source hash/revision checks before the user attaches it. A ZIP unlocks only after every required manifest file is attached and the workspace is finalized.

**Structural completeness IS NOT code validity:** validationState remains NOT_RUN, meaning code is not automatically compiled, independently tested or checked for complete satisfaction of user intent.

## Ownership

- hf_space/qwen_coder_engine.py — explicit planning response-mode guidance, NOT model weights.
- hf_space/project_manifest.py — strict pure schema validator, source digest, dependency DAG.
- hf_space/station.py — same-cookie/thread committed-message preview and approval, source SHA comparison, idempotent resume.
- hf_space/staged_workspaces.py — approved plan stored in the existing Station owner; next-ready dependencies.
- chat/§wyrlz/index.html — Plan button, model response review/approval, same-session resume and bounded one-request generation.
- Python builtins and existing dependencies only. No separate storage/database authority.

## Limits and future work

- This is a **user-governed assistant-led planner**, not fully autonomous end-to-end project generation.
- The manifest is model-authored and approved by the user; it may omit real requirements. An independent requirements checker is still needed to prevent a structurally READY but semantically incomplete project from being called finished.
- Session state remains process-local. Resume is valid within that session only; a restart or cookie loss still discards the workspace. Durable account-backed workspace storage, protected export/import, retention, encryption and recovery require a separate approved implementation.
- At most 32 UTF-8 files, 1 MiB each, 8 MiB total; no binary packages or unbounded inference costs.
- No real hosted Qwen plan or generated multi-file project was graded in this isolated CI. Synthetic fixture/source checks do not prove model competence, actual UI acceptance or production correctness.
- Later bounded orchestrators may add explicit step and resource budgets, real compiler/test execution, pause/cancel and resumability. No feature here silently performs those actions.

## Release boundary and evidence

Branch feature/coder-manifest-planner-v1 is stacked above draft PR #59 (staged source workspaces), which is stacked above draft PR #58 (single-file/ZIP download). CI workflow verify-project-manifest-v189.yml verifies parser/schema, dependency graph, SHA and cookie-scoped approval, idempotent resume, previous ZIP/workspace regressions and JavaScript syntax. This test workflow name does not imply a production version and must not be confused with independently deployed lyric releases.

Only merge after parent PRs are integrated, current HF source is reconciled and all protected model/Chat/lyric/online/repair gates and actual browser/mobile usage are verified. No guarded HF or separate Forge production deployment request is changed here.
