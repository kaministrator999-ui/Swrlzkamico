# §wyrlz Hotfix + Deployment Rules — READ THIS SECOND

**Role:** canonical owner of repository mutation mechanics, runtime/main boundaries, deployment approval, and hotfix verification.

**Startup order is owned by `SWRLZ_PROJECT_START.md`.** This document is second in that sequence.

---

## 1. Core boundary

```text
runtime = durable live application / runtime-hot source
main    = stable loader, infrastructure, deployment/config, engineering-contract boundary
```

Use the architecture reconciliation protocol to decide **where the behavior belongs first**. Then apply this document to decide how that owner may be changed and verified.

Do not move behavior to the wrong plane merely to avoid deployment.

---

## 2. Deployment Approval Gate — hard stop

No repository action that can actually cause deployment/redeployment is implicitly authorized by a request to fix, implement, test, document, commit, merge, refactor, or architect.

Before a deployment-producing action, establish from **current configuration/workflows**:

1. the exact trigger/action;
2. why it causes deployment;
3. which production surface it affects;
4. whether a non-deploying runtime path is architecturally correct instead;
5. the exact action awaiting approval.

Then **STOP and obtain explicit user approval before performing that deployment-producing action**.

A branch name alone does not prove deployment capability. A `main` commit is not automatically a deployment. A documentation file is not automatically deployment-capable. An explicit deploy action remains deployment-producing even when ordinary Git commits are inert.

If deployment capability is genuinely uncertain, treat the proposed action as deployment-capable until current configuration is inspected.

---

## 3. Current deployment-control principle

The current production workflow must be re-checked each event; never permanently assume yesterday's configuration.

When Git-based deployment is disabled and only an explicit workflow/request path deploys, ordinary documentation or source commits that do not hit that trigger are non-deploying.

If configuration changes later, re-evaluate immediately.

---

## 4. Runtime-hot work

Ordinary runtime-owned work normally belongs on `runtime`, including supported:

- Chat/page HTML, JS, and CSS;
- runtime page assets/manifests;
- stream UI/behavior;
- runtime-loadable LALM/R39 code;
- runtime-owned module version authorities;
- runtime behavior already supported by the stable loader.

Typical flow:

```text
fetch current runtime source
→ capture version/SHA baseline
→ reconcile architecture
→ inspect diagnostic evidence when fixing an issue
→ make smallest coherent change
→ re-read version authorities
→ reconcile concurrency
→ assign Server + changed-module versions
→ update roadmap/release record
→ commit runtime
→ re-read authorities
→ request/reload
→ verify behavior + ownership + activation as applicable
```

Ordinary runtime-hot changes do **not** require a deployment or restart unless current architecture/configuration proves otherwise.

---

## 5. Stable/main work

`main` owns stable boundaries such as:

- API routes/middleware not provided by runtime-hot architecture;
- authentication/security/session infrastructure;
- runtime loader/source-resolution infrastructure;
- hydration/sync infrastructure;
- build/deployment configuration;
- stable server capabilities the current runtime loader cannot supply;
- engineering-contract documentation.

A `main` mutation and a production deployment are separate concepts. If the mutation itself is inert, it may be committed without pretending it deployed. If applying it to production requires an actual deployment-producing action, pass the Deployment Approval Gate first.

---

## 6. Smallest coherent change

Make the smallest change that fits the reconciled architecture.

Do not:

- replace a complete page for a one-line behavior fix;
- add another late injector because the canonical owner is inconvenient;
- create another state store to avoid understanding the current one;
- revive `dev` or `/tmp` as durable authority;
- add another loader/fallback without reconciling current activation precedence;
- duplicate another module's version literal;
- treat a compatibility adapter as the canonical owner unless architecture explicitly changed.

“Smallest” means smallest **coherent** change, not smallest diff regardless of architecture.

---

## 7. Versioning relationship

`SWRLZ_VERSION_MODULE_EVOLUTION.md` owns version semantics.

For a governed event:

- capture current authorities and SHAs at entry;
- re-read them immediately before version assignment/commit;
- reconcile concurrent advances;
- advance the overall Server lineage as required by the evolution contract;
- bump only modules that actually changed;
- update module-owned `versions/<module-id>.txt` authorities;
- update `VERSION.txt` only for module routing/registration changes;
- record the event in the roadmap/release record.

Do not carry stale planned version numbers through a concurrent project advance.

---

## 8. Automatic diagnostics relationship

For issue/fix/debug work, `SWRLZ_CHAT_CAMERA_LOGS.md` applies automatically.

Before guessing at a fix:

- inspect existing repository-side evidence;
- inspect accessible live/runtime/workflow logs;
- correlate versions/request IDs/operation IDs where possible;
- add bounded instrumentation only when an actual observability gap remains;
- fix the canonical owner;
- re-check the same evidence after the change.

Instrumentation is part of the affected component when it changes runtime behavior and follows that component's version/deployment rules.

---

## 9. Cold-start / durability rule

Durable authority lives in repository/runtime state and approved persistent stores, not disposable process state.

A cold start/restart must be able to reconstruct active runtime behavior from durable authority.

Do not use `/tmp`, in-memory module objects, browser cache, or one worker's process state as the only source of truth.

---

## 10. Version authority router

`VERSION.txt` maps stable module IDs to the authoritative module-owned version files.

Examples include:

- `versions/server-runtime.txt`
- `versions/server-ui.txt`
- `versions/web-frontend.txt`
- `versions/web-chat.txt`
- `versions/stream-contract.txt`
- `versions/lalm-ui.txt`
- `versions/lalm-engine.txt`
- `versions/online-research.txt`
- `versions/admin-web.txt`
- `versions/google-account.txt`
- `versions/client-apk.txt`
- `versions/server-apk.txt`
- `versions/frozen-web-collector.txt`
- `versions/deployment-control.txt`

Always read the current registry rather than treating this list as permanent.

Cross-module consumers query the owner; they do not maintain duplicate numeric copies.

---

## 11. Verification checklist

Before closing a governed update, verify as applicable:

- [ ] current target source fetched;
- [ ] architecture owner reconciled;
- [ ] Server/module authority baseline captured;
- [ ] issue work inspected existing logs/cameras automatically;
- [ ] observability gap instrumented only if needed;
- [ ] deployment capability checked from current configuration;
- [ ] explicit approval obtained before any deployment-producing action;
- [ ] only intended owners/files changed;
- [ ] version authorities re-read at commit boundary;
- [ ] concurrent advances reconciled;
- [ ] Server and actually changed module versions assigned correctly;
- [ ] roadmap/release record updated;
- [ ] post-change authorities re-read;
- [ ] source/static/runtime/live verification classified honestly;
- [ ] no legacy injector/loader/fallback unexpectedly overrides the intended source;
- [ ] no unapproved deployment/restart occurred.

---

## 12. Failure handling

A failed governed attempt is not silently erased.

Record the failure according to the version-evolution contract. A corrective attempt is a new governed event when the contract requires it.

Do not rewrite history to make a failed attempt look like it never happened.

---

## Bottom line

**Architecture tells you where the change belongs. This document tells you how to mutate that owner safely. Prefer runtime-hot changes for runtime-owned behavior, keep stable infrastructure on main, prove deployment capability from current configuration, never trigger deployment without explicit approval, preserve durable authority, version from current state, and verify the actual owner/activation path before declaring the work done.**