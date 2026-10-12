# v213 — §wyrlz GitHub Project Engineering Workbench

Date: 2026-10-11 (America/Chicago). Release: existing Hugging Face Space with guarded snapshot and rollback. No real owner GitHub write was performed during release.

## Request, scope and continuity

User asked for extensive GitHub project-work capabilities like the existing ChatGPT/GitHub engineering workflow. This tier expands beyond v210 permission checks, v211 selected-local-model read planning and live statuses, v212 Actions inventory/manual workflow authoring/dispatch/PR controls. v213 adds repository engineering and source change governance. It begins **exactly** from published v212/v211.3 source `ccf4ee25cd206e10505cb432ea60b3af960c8ace`, preserving §wyrlz identity routing, first-message native Chat save acknowledgement, Google owner scoped encrypted history and authenticated GitHub OAuth, existing original Test Bench and accepted weights. No hidden paid inference service, separate AI persona, self-approved privilege expansion or automatic production merge.

Source: [draft PR #112](https://github.com/kaministrator999-ui/Swrlzkamico/pull/112), immutable `feature/github-project-workbench-v213@002f4bde2b2d142647019b22da21382c7047b2d6`. New module `hf_space/github_project_v213.py`, tests `hf_space/test_github_project_v213.py`, user guide `hf_space/GITHUB_PROJECT_WORKBENCH_V213.md`; integrated `hf_space/github_connection.py`, Chat UI and CI. Clean-room Chat source `1.1.10`.

## Actual capabilities

**Project understanding and evidence:** `@GitHub overview`, `@GitHub project guide`, `@GitHub project brief` (bounded README/Start/CONTRIBUTING/AGENTS excerpts), `@GitHub dependencies` (bounded build manifests), `@GitHub triage` (issues/PRs/Actions), `@GitHub tree [path]`, `@GitHub code search TERM`, `@GitHub file history PATH`, `@GitHub compare BASE...HEAD`, `@GitHub pr review ID` with changed files and head-SHA check runs, `@GitHub issue inspect ID` with bounded comments, `@GitHub checks SHA`, `@GitHub project readiness` (partial head-CI snapshot, **not deployment approval**), `@GitHub branch policy` (403 means unknown, not unprotected) and `@GitHub releases`. All source files, issue/PR text, code search results and comments are untrusted evidence. No invented CI passing claims or full inventory where GitHub results are paginated/truncated. OAuth/repository and REST authority checked per requested read; model planner restricted to up to three read tools with user-mentioned IDs/paths/refs only.

**Human-controlled source development:** `@GitHub edit file src/path.py on feature/name replace OLD :: NEW` proposes one bounded literal replacement in an existing <=90KiB UTF-8 source file on an existing feature/fix/chore branch. Denies protected, auth-secret, `.env`, `.github`, `.deploy`, versions, unknown/binary/config paths and default/runtime branches; verifies exactly one match, branch head SHA and Git blob SHA before proposal. Separate 10-minute one-use Google-owner/repository-bound `@GitHub confirm CODE` rechecks OAuth/repository write scope, branch SHA, file blob and exact old text before one GitHub Contents SHA-CAS PUT. Confirmation result must contain expected path and GitHub commit SHA. No generic model-created patch, arbitrary shell, auto merge/PR/deploy or invisible write. User can independently propose `@GitHub pr draft feature/name into main` with a bounded verified compare, protected changed paths rejected, head SHA and diff rechecked on confirmation; creates a DRAFT PR only, never merges.

**Guarded operations remain separate:** v212 static-template workflow creation, draft review, manual dispatch and retry (user-approved) are preserved, not bypassed. GitHub OAuth scope may only be expanded through explicit GitHub consent. Workflow text cannot authorize tool calls; protected release scripts cannot be manually triggered by model inference. No autonomous multi-step external write chain or self-granted permissions.

## Exact source validations

- [GitHub/Google account + v213 Python checks #38198415169](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38198415169): **SUCCESS** at exact published candidate source.
- [HF offline validation #38198418685](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38198418685): **SUCCESS** at same source.
- [Mobile integrity #38198418688](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38198418688): **SUCCESS** at same source.

Regression checks encompass prior v210–v212/v211.3 account/identity/native-save behavior, user-named model plan read gating, GitHub REST compare URL guard without traversal regression, code search/provider evidence, PR/check provenance, branch policy unknown reporting, source bounds and nested `.env` denial, one-time owner confirmation, CAS, stale branch and protected PR-diff rejection, live events and UI JS parsing. All are CI/synthetic checks; none used the real connected user's OAuth token or wrote to their selected repo.

## Governed existing-Space publication

Canonical `main:.deploy/HF_SPACE_REQUEST.txt` approved nonce `2026-10-11-v213-github-project-engineering-evidence-scoped-edit-001`, request commit `8fd4ed35a2381f0c71f9bf3200ccf7a4e9c2021f`, immutable source `002f4bde2b2d142647019b22da21382c7047b2d6`. [HF release run #38198521823](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38198521823) **COMPLETED/SUCCESS** (request and deploy jobs), including guarded R39 model reconstruction, 700M budget smoke, predeploy Space reference snapshot and upload.

- Existing Space `kamiloki/Swyrlz`: newly published revision `c88edf6c652d27831b43120ee80648cfd54bf8e4`.
- Predeploy rollback revision: `d54369376b3a73b9fb78049d1f766e095d031db9`.
- `hf-release-checkpoint` ID `11724343056`, `hf-rollback-checkpoint` ID `11724567405`, `hf-predeploy-reference` ID `11724826563`.
- Receipt explicitly states `verificationState=DEPLOYED_UNVERIFIED` and `knownGood=false`. No invented real-user acceptance.

## Registered runtime versions

Atomic guarded `runtime@e28d5945b71d9fb59446155af18beb537052afc5` was re-read successfully:

| Registered owner | Before | After |
| --- | --- | --- |
| Repository Work | 1.0.155 | **1.0.156** |
| Server Runtime | 2.3.367 | **2.3.368** |
| Web Chat | 1.5.105 | **1.5.106** |
| LALM Engine / Station | 2.1.191 | **2.1.192** |
| Google Account Architecture | 1.0.15 | **1.0.15 unchanged** |

`runtime:VERSION.txt` unchanged. Other modules unchanged because no respective runtime ownership changes.

## Owner acceptance / safe demo

Open `https://kamiloki-swyrlz.hf.space/` on the same verified Google account connected to the desired GitHub repository:

1. `@GitHub project guide`, `@GitHub overview`, `@GitHub project brief`, `@GitHub dependencies`, `@GitHub triage`, `@GitHub project readiness`. Verify actual evidence/repository references and correct missing-information statements.
2. `@GitHub tree`, `@GitHub code search SOME_IDENTIFIER`, `@GitHub compare main...feature/work`, `@GitHub pr review N` or `@GitHub checks SHA` against known real refs. Verify progress and Chat save/reload.
3. On a disposable feature branch **only if desired**, propose one exact literal source edit, inspect preview, and explicitly confirm. Validate new GitHub commit and isolated tests. A draft PR is another independently confirmed action; no merges/deploys automatically.
4. Keep production/release workflows under the existing governed snapshot/release controls and independently verify live OAuth scope/permissions. No real private owner mutation or live success was established during this deployment.

**Engineering status:** SOURCE / ACCOUNT + OFFLINE + MOBILE CI / GUARDED HUGGING FACE PUBLICATION / MODULE VERSION READBACK **FINISHED**. **SIGNED-IN ACCOUNT/OAUTH/TOOL BEHAVIOR AND REAL EDIT/PR ACCEPTANCE PENDING.**

## Future backlog — not present-tense capabilities

Safe multiline diff application with lint/patch static checks; trusted isolated source sandbox/test results; edit replay/durable checkpoints and reversible patch journals; code reference cross-index and symbol graph; check-run annotations/artifacts with redaction; issue/PR review comments with consent; ruleset/required-check/signed-commit visibility; granular GraphQL/code search capability feedback; Dependabot/advisory/dependency updates with owner approval; multi-repository bounded portfolio queries; provider webhook signature verification and event subscriptions; repository security scopes/installation permissions; reusable PR-to-test-to-reviewed-deploy guided missions with robust stop/approval gates; and live account acceptance instrumentation. Each must be explicitly implemented and tested, not silently added as a model's purported capability.
