# Chat/AI v293 — GitHub Read-Tool Planning and Model Reasoning

**Date:** 2026-10-21
**Owner request:** Analyze GitHub tooling, model reasoning, their uses, and implement improvements under the `§§§§` Chat/AI scope.
**GitHub source authority:** `integration/chat-github-read-reasoning-v293` at `e90b2f395589da8cbfb0315a5c1db9f70e2afcb4`.
**Source review:** [PR #286](https://github.com/kaministrator999-ui/Swrlzkamico/pull/286), merged after offline tests.
**Release request:** `main:.deploy/HF_SPACE_REQUEST.txt`, request commit `b17c5322fca16dca502d85687250d38cbc911261`; target existing Space `kamiloki/Swyrlz`. The request is **not** proof of completed deployment or live behavior.

## Architecture and findings

- `hf_space/github_connection.py` is the canonical Station owner for OAuth-gated GitHub tools and read execution. `github_read_inference_v235.py` owns deterministic path/context reads; `github_workflows_v212.py` owns workflow read mechanisms; `brain_programming.py` continues to own programming intent. No second GitHub agent was created.
- Stage-1 routing prevented a natural-language request for existing safe issue/PR reads from reaching the already-implemented bounded model planner. The request was incorrectly called locked, even though checked read handlers existed.
- Some model-planned numeric target validation used substring checks, potentially confusing PR/issue 7 with 17. Model output was never a valid permission grant.

## Implemented and tested

1. Stage 1 now permits authenticated, **read-only** issue, pull request, commit and workflow/run checks, besides existing file/source reads.
2. Natural-language inspection can use the existing bounded model planner when multiple checks are useful; single clear checks prefer deterministic routing to avoid needless inference.
3. Candidate tools are mapped through a strict Stage-1 category/command allowlist, then independently checked by the existing Station GitHub access gate. Unsupported model output fails closed to bounded deterministic read selection. No prompt, secrets or hidden reasoning are used as permission.
4. Model-selected issue/PR identifiers must match complete user-named numbers; partial-number matches are rejected.
5. Multi-check Chat responses finish with a **single terminal event** rather than terminating after the first check.
6. Extended `hf_space/test_github_model_progress_v211.py` with Stage-1 read, fallback, malformed-plan, target-precision, non-mutation and completion regressions; `.github/workflows/hf-candidate-validation.yml` now executes them.

**Validation receipts:** [HF Candidate Offline Validation #39629222988](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39629222988) SUCCESS; [Chat v289 Repository Readiness #39629222608](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39629222608) SUCCESS on tested head `e88b0f96126f8181ea229e883436c00a79009edd`. The merged candidate has the identical Git tree `c05d4e420602ba95b06ec18617030c97700573c2`.

## Deliberate unchanged boundaries

- Model weights/Qwen/R39 weights unchanged; this is **tool-routing reasoning**, not training or a measured general IQ gain.
- GitHub write permission, branch/issue/PR mutations, workflow dispatch, confirmation authority, OAuth scopes, secrets, account identity and source provenance stay with existing server-owned gates.
- Chat UI/frontend, Forge Engine/§e, engine Space and engine versions unchanged.
- Concurrent source/feature branches are not merged by name and cannot silently override an immutable validated source SHA.

## Verified release, version lineage and remaining acceptance

The guarded Chat Space request **completed successfully**: [GitHub Actions run #39629570218](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39629570218) on trigger commit `b17c5322fca16dca502d85687250d38cbc911261`, with exact selected source `e90b2f395589da8cbfb0315a5c1db9f70e2afcb4`. The published existing `kamiloki/Swyrlz` Space revision is `2b9475e46675932d2651d2c899ea6efdee629779`; rollback snapshot preserves `215b0bb8234eb9234ffe9687cedf3a5e5934df22`. Publication and source provenance were observed in successful deployment-job logs and release artifacts; direct served-page functionality and owner handset behavior remain **not independently verified**.

The canonical [Server Roadmap](../../../SWRLZ_SERVER_ROADMAP.md) now records the full v293 governance and deployment event. `runtime` Repository Work was advanced `1.0.231 → 1.0.232` (`9a8c2fbbcf2c0a592b6723a1c546b59d2845379c`), and deployed Server Runtime `2.3.438 → 2.3.439` (`4a0b2d7daf5c5b5634949dc92d921b15174f869d`). Web Chat remains `1.5.156`, LALM Engine remains `2.1.201`, and model weights were not changed.

The first candidate's syntax failure and then deterministic-read routing failure remain documented in the roadmap as genuine implementation/validation failures repaired before the successful source release. No new permissions, alternate host, or engine deployment were authorized or used.


## Independent hosted acceptance — continuation 2026-10-21

[PR #287](https://github.com/kaministrator999-ui/Swrlzkamico/pull/287) adds a reusable read-only public live probe at `scripts/verify_chat_github_v293_live.py` and `.github/workflows/chat-github-v293-live.yml`. [Actions run #39657026690](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39657026690) COMPLETED/SUCCESS on exact tested head `48a2b343ef1b5d19203efe0b6d1ee0601e927d4b`. The script uses Python stdlib to make unauthenticated GET requests; no user cookies, GitHub token, inference-generation call, write call, or secret material is used.

**Actual hosted HTTP checks:** Hugging Face public Space metadata revision exactly `2b9475e46675932d2651d2c899ea6efdee629779` (matching the v293 release checkpoint); hosted Chat HTML HTTP 200 with canonical Chat `1.1.18`; `/api/hf/models` HTTP 200 with five model entries. Anonymous `/api/account/me`, `/api/github/status`, and `/api/github/start?access=public-write` each returned HTTP 401. No anonymous GitHub account access was observed. These are external runtime observations, not merely source-level or mocked checks.

**Integration and governed version:** [PR #287](https://github.com/kaministrator999-ui/Swrlzkamico/pull/287) merged by squash into `main` at `18d5f7db45d0f57cef1e69cccb9c24b966a7340f` after successful live CI. This is reusable testing/instrumentation only; it does not modify the deployed Chat application or authorize another HF publication. Canonical `runtime:versions/repository-work.txt` advances `1.0.232 → 1.0.233` at `a2debcd1d0a74e3d34a7e4d986e47f3f8b285727`. Deployed Server Runtime stays `2.3.439`; Web Chat stays `1.5.156`; LALM Engine stays `2.1.201`; §E unchanged.

**Still unverified:** an actual **authenticated** Google → GitHub signed-in live read/tool-selection session, any mobile/physical-device UX, and semantic quality of model-selected investigations under live connected user context. Anonymous 401 enforcement is not proof of full OAuth behavior. Do not claim that user acceptance or authenticated GitHub tool calls passed on the basis of this public probe.
