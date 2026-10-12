# v212 — GitHub Actions workflow workbench and manual trigger architecture

Date: 2026-10-11 (America/Chicago). Private owner engineering release notes. This reports one governed existing-Space publication, **not** real authenticated owner acceptance of any workflow mutation.

## Requested intent

Expand §wyrlz's connected GitHub account assistant into a practical Actions engineering tool: teach the model workflow anatomy/triggers/permissions, discover and inspect Actions files and run evidence, plan safe workflow creation, trigger approved manual checks, inspect outcomes, and show meaningful reasoning/tool progress. No silence around permissions, no self-granted OAuth scopes, no arbitrary release actions.

## Source and preservation

- Published prior source: `fix/assistant-brand-identity-clarity-v2113@6c928770b16ae16fe4694f93d45d6af9a07f3fa5`, includes v211.3 assistant-identity model-router guard and all earlier first-message native Chat durability fixes.
- Initial independently developed source v212 [draft PR #110](https://github.com/kaministrator999-ui/Swrlzkamico/pull/110) was based on v211.2. It was **not** published over the newer v211.3.
- Reconciled published source [draft PR #111](https://github.com/kaministrator999-ui/Swrlzkamico/pull/111), `feature/github-workflow-studio-v212-v2113-integrated@ccf4ee25cd206e10505cb432ea60b3af960c8ace`. This begins exactly at v211.3; preserves its `hf_space/model_router.py`, new identity tests, Station, Chat state and account store; carries v212 changes only in canonical GitHub tools and Chat settings. GitHub account CI workflow merges all v211.3 and v212 regressions. Clean-room Chat source version 1.1.09.

## Workflow engineering capabilities and truth contract

The existing Google-account-owned encrypted GitHub OAuth token and selected repository remain authoritative; model text and repository YAML are *data*, not authorization. §wyrlz can:
1. `@GitHub workflow guide` — teach workflow syntax, manual triggers, token permissions, branch/PR review and run outcomes.
2. `@GitHub workflows`, `@GitHub workflow inspect name.yml` — inspect real registered workflow names, active states, default-branch source and SHA.
3. `@GitHub workflow runs`, `@GitHub run status ID` — report observed queued/in-progress/completed, real conclusion, jobs and failed steps. Never fabricate a run success from a dispatch response.
4. `@GitHub ask show my repo workflows and Actions runs` — existing selected local model chooses bounded read-only workflow tools; actual Station inference, permission and execution phases appear live, no raw private chain-of-thought.
5. `@GitHub workflow create python-check as syntax.yml on feature/ci` (templates `python-check`, `node-check`, `repo-audit` only) — prepare a **new**, no-overwrite, immutable reviewed YAML template on an existing nonprotected feature/fix/chore branch, then require separate `@GitHub confirm CODE`. It does not automatically merge or enable dispatch.
6. `@GitHub workflow pr feature/ci into main` — a verified owner-bound **draft PR** proposal against the real default branch; requires separate confirmation; never merges.
7. `@GitHub workflow dispatch syntax.yml on main` with optional bounded nonsecret `with key=value` inputs — confirms workflow ID, active registration, `workflow_dispatch` default and target ref YAML, and both specific Git blob identities, then queues a one-use owner-bound proposal. On confirmation, refetches all current authorities before a fixed GitHub Actions dispatch. Protected/privileged/release/secret-bearing workflows are excluded and remain under GitHub UI or the independent production gate.
8. `@GitHub run retry ID` — a verified completed failure can queue a retry of its failed jobs only after the actual run-head workflow YAML source SHA, nonprotected content and owner consent are verified again. A retry acceptance isn't a successful run.

GitHub OAuth classic flow adds *optional* user-approved public-workflow/private-workflow grant modes requiring `workflow` plus repository write scope for authoring. `workflow-dispatch` verifies selected repository, role and write-capable scope. The provider remains the final source of truth; denied/unknown operations are not reported as successes. Chat Settings offers operation-specific permission checks, targeted user-driven upgrade, and Actions guide button. No secrets in browser/model/logs; no arbitrary workflow YAML, arbitrary shell commands, forced merges, secret editing, workflow enable/disable, unrestricted reruns or default-branch direct writes.

## Testing and CI evidence

- Account/GitHub Actions and legacy permissions + v211.3 assistant-identity tests [#38191831345](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38191831345): **SUCCESS** at exact integrated source SHA.
- HF offline validation [#38191833999](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38191833999): **SUCCESS**.
- Mobile integrity [#38191834065](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38191834065): **SUCCESS**.
- The synthetic GitHub tests verify OAuth operation selection, no silent writes, proposed authoring with replay rejection, PR/retry, protected name/content blocks, stale branches, same-owner confirmation, URL-encoded refs, manual trigger vs completion, safe real-run source ref YAML and source commit preservation. Early isolated CI failures were repaired; none tried real production GitHub writes. Exact integrated source subsequently passes.

## Canonical guarded publication

`main:.deploy/HF_SPACE_REQUEST.txt` new nonce `2026-10-11-v212-github-actions-workflow-workbench-integrated-v2113-001`, request commit `656ef84d19811ae4faac4f136fc6ab670a5ce1d8`, immutable source `ccf4ee25cd206e10505cb432ea60b3af960c8ace`. [GitHub Actions run #38191943975](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38191943975): **COMPLETED/SUCCESS** (request and deploy jobs). Before publication R39 reconstruction, 700M smoke, and existing Space snapshot succeeded. Exact `kamiloki/Swyrlz` new revision `d54369376b3a73b9fb78049d1f766e095d031db9`, rollback revision `64818d054d9b27e592bbcd963a8d9fbd4b602d0d`. GitHub release checkpoint artifact `hf-release-checkpoint` ID 11721871631; rollback checkpoint `hf-rollback-checkpoint` ID 11722110789. The release checkpoint explicitly states `verificationState=DEPLOYED_UNVERIFIED` and does not mark known-good.

## Atomic independent versions

Registered authority `runtime@4a82b204675870b664351a1ba59a085247e8a5c9`, read back after guarded version commit:

| Module | From | To |
|---|---|---|
| Repository Work | 1.0.154 | 1.0.155 |
| Server Runtime | 2.3.366 | 2.3.367 |
| Web Chat | 1.5.104 | 1.5.105 |
| LALM Engine / Agent tool route | 2.1.190 | 2.1.191 |
| Google Account/GitHub OAuth | 1.0.14 | 1.0.15 |

`runtime:VERSION.txt` index and all unrelated modules remain unchanged. Account profile/ChatGPT import, accepted model weights, original Test Bench and broader product projects untouched.

## Required owner live acceptance

From the existing Space https://kamiloki-swyrlz.hf.space/ with the same verified Google account that owns the GitHub connection:
1. Open GitHub Settings, select the repository, click Actions guide, and send the prepared command. Use the operation selector to check workflow-dispatch or workflow-create; verify that additional OAuth scope is offered only when the current request requires it.
2. Try `@GitHub workflows`, `@GitHub workflow runs`, `@GitHub workflow inspect <name.yml>`, and `@GitHub ask show my repo workflows and recent runs` to verify live model/tool progress and real retrieved results.
3. For authoring, select a disposable review branch and a safe template; inspect the proposal before optional explicit confirmation, then review the resulting draft PR manually. A workflow on a feature branch cannot be assumed manually runnable before GitHub registers it on the default branch.
4. Any `workflow dispatch` or `run retry` must be specifically owner chosen and confirmed. Check run ID and conclusion afterward; no real workflow was triggered on owner's behalf as part of this release.
5. Confirm native Chat new-thread save/reload and cross-browser retention independently; do not delete/reimport existing history as an attempted fix.

**Status: GOVERNED SOURCE/CI/DEPLOYMENT AND VERSION REGISTRY FINISHED; LIVE SIGNED-IN GITHUB OAUTH / USER CHOSEN WORKFLOW WRITE AND CHAT PERSISTENCE ACCEPTANCE PENDING.**
