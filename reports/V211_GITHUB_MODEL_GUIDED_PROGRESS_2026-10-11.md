# v211 — §wyrlz model-guided GitHub actions and live progress

Date: 2026-10-11. Governed integrated HF Chat/LALM release; runtime acceptance requires a real signed-in owner test.

## Purpose

User requested genuine model participation when §wyrlz uses its connected GitHub tools: choose relevant operations, reason at a high level about the next checks, and display progress as actual inference and tool events occur. This is **not** a request to display private raw chain-of-thought. The implementation shows inspectable planning/tool stages and verified evidence; generated planner text remains a private untrusted tool-selection suggestion, never a grant or executable GitHub instruction.

## Architecture

Canonical owner reused: `hf_space/github_connection.py` for encrypted Google-account-bound OAuth and live repository-role checks; `hf_space/station.py` for selected local inference and NDJSON lifecycle; `chat/§wyrlz/index.html` for the existing live progress/activity surface.

- Natural GitHub inspection requests or explicit `@GitHub ask`/`explore`/`analyze` use a bounded selected-local-model tool plan where a compatible inference backend is available. Exact `@GitHub permissions`/files/etc remain faster deterministic routing, with real status events rather than unnecessary inference. No new paid API service or agent daemon.
- Model is asked for strictly structured JSON containing at most three allowlisted READ checks. Permitted: permissions, files, branches, issues, pulls, commits; specific file or directory paths only when the user spelled out the path. No freeform external URLs, read of model-selected arbitrary sensitive paths, writes, merges, workflow dispatch, deletion or OAuth escalation.
- The planner receives no GitHub access token, stored Google subject, user profile, private chat history or credentials. Invalid/rejected/overlong/unavailable model output triggers safe labeled read-only heuristic fallback. Planner output is never treated as authorization.
- Before **every** requested read, existing GitHub repository identity and authenticated effective-access check runs. An unknown result is `ACCESS_UNVERIFIED`, not an invented "permission missing"; a known blocked write is explained by the existing v210 consent flow. Existing `@GitHub create issue`, `create branch`, and one-time confirmation continue under their v210 independent owner.
- Station now streams real `GITHUB_MODEL_PLAN_STARTED`, `GITHUB_MODEL_LOADING`, `GITHUB_MODEL_GENERATING`, `GITHUB_MODEL_PROGRESS`, `GITHUB_PLAN_READY`, `GITHUB_PERMISSION_CHECK`, `GITHUB_PERMISSION_VERIFIED`, `GITHUB_TOOL_STARTED`, `GITHUB_TOOL_COMPLETE`, `GITHUB_ACCESS_UNVERIFIED`, and `GITHUB_EVIDENCE_COMPLETE` events. Model-progress events are tied to observed model STATUS/delta output, no fake completion percentages.
- Existing Dragon Chat progress trail and action/work surface render observable phases and server-authored status summaries; the actual tool response is included as independently retrieved evidence. Native Chat Google-owner persistence and old records remain unchanged. Local Chat source VERSION `1.1.05→1.1.06`.

## Exact source and predeploy tests

[draft PR #104](https://github.com/kaministrator999-ui/Swrlzkamico/pull/104), branch `feature/github-model-guided-progress-v211`, immutable source commit `4da362e9f89339b37017c0a8aeba65948008f7d2` built on the published v209.1+v210 candidate `4db31fb5a8470e3784ee04c97dcaf871728af1b4`. CI at exact source:
- GitHub/account + new model progress regressions [#38172413647](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38172413647): **SUCCESS**
- Standard HF offline [#38172418055](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38172418055): **SUCCESS**
- Mobile UI [#38172418079](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38172418079): **SUCCESS**

One early account CI failure was due to an old test hardcoding v210 dispatcher; updated to assert new Station streaming ownership and preserved v210 write-confirmation owner, then rerun successfully. Regression tests cover natural routing, actual mock model JSON plan, observed model loading/generation/tool states, untrusted forbidden writes, no-token prompt, fallback, read denial and owner isolation assumptions. CI is synthetic, not account-authenticated acceptance.

## Guarded existing-Space publication

Canonical `main:.deploy/HF_SPACE_REQUEST.txt` nonce `2026-10-11-v211-model-guided-github-progress-001`, commit `f05f32f2aa8dd071c4cfe864e34a2a5e493e86d0`, pinned exact source `4da362e9f89339b37017c0a8aeba65948008f7d2`. [HF deployment workflow #38172514064](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38172514064) completed **SUCCESS** with request and deploy jobs passed. New `kamiloki/Swyrlz` revision `e5760d09a5e30a5ba1cfba3b52c28a4127248e49`; predeploy rollback revision `e77d03f2263bd3be1734fe32aeda16c3ce74c6a9`. GitHub artifact `hf-rollback-checkpoint` ID `11714731321`; release artifact `hf-release-checkpoint` ID `11714447048`. Workflow receipt says `DEPLOYED_UNVERIFIED`; no fake known-good promotion.

## Runtime versions

Atomic guarded `runtime` commit `2bda8d76f9b25ed9e2c5cda408dc1528bf4c32fa`, exact readback:
| Module | Before | After |
|---|---|---|
| Repository Work | 1.0.150 | 1.0.151 |
| Server Runtime | 2.3.362 | 2.3.363 |
| Web Chat | 1.5.101 | 1.5.102 |
| LALM Engine / Station | 2.1.187 | 2.1.188 |

Google Account Architecture stays at 1.0.14 (OAuth identity/grant contract unchanged); Runtime Manifest 152, Stream Contract V2, Online Research 1.0.30, and other modules unchanged. The `VERSION.txt` route index did not change.

## Live owner acceptance

Open `https://kamiloki-swyrlz.hf.space/` signed into the same Google account that owns the GitHub connection, then try:

1. `@GitHub ask show my repo permissions and recent pull requests`. Expect model planning phases when the selected local model is available, then explicit read verification and GitHub result stages, and grounded response. If model inference fails, expect a visible "safe deterministic fallback" plan rather than made-up reasoning.
2. `@GitHub permissions` and `@GitHub issues`: faster exact read commands should still report real GitHub tool progress, with no unnecessary scope escalation.
3. Check the existing activity/work surface during streaming. If GitHub is disconnected, user-facing explanation must require manual GitHub approval; if a private read is unverified, do not assert write permission is missing. No write test is required; only user-chosen exact writes and explicit confirmation can modify a repository.
4. Confirm new native Chat messages still survive reload and second browser; v209.1 saved-history owner acceptance remains a separate outstanding gate.

**Status:** SOURCE/CI/DEPLOYMENT/REGISTERED VERSION COMPLETE; SIGNED-IN REAL-ACCOUNT TOOL-PROGRESS AND CHAT SAVE ACCEPTANCE PENDING.
