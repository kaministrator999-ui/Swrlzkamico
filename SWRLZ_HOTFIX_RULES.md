# §wyrlz Hotfix + Deployment Rules — READ THIS SECOND

**Role:** canonical owner of repository mutation mechanics, runtime/main boundaries, deployment approval, and hotfix verification.

**Startup order is owned by `§wyrlz_§tart.md`.** This document is second in that sequence.

---

## 1. Core boundary

```text
runtime = durable live application / runtime-hot source
main    = stable loader, infrastructure, deployment/config, engineering-contract boundary
```

Use the architecture reconciliation protocol to decide **where the behavior belongs first**. Then apply this document to decide how that owner may be changed and verified.

Do not move behavior to the wrong plane merely to avoid deployment.

---

## 2. Deployment authorization + corrective-retry boundary

Deployment remains a privileged action, but this repository carries a bounded project standing authorization defined by Project Start.

Before any deployment-producing action, establish from current source/evidence:

1. the exact canonical trigger/action;
2. which production surface it affects;
3. the exact source ref/candidate being published;
4. whether the change actually requires stable publication or is deployment-inert/runtime-hot;
5. whether the action is the terminal deployment for the governed update or a corrective retry of a §wyrlz-caused implementation/packaging failure.

Authorization rules:

- The user's repository standing approval covers the **terminal canonical Hugging Face deployment required to complete a governed runtime-affecting update**.
- It also covers **corrective re-deployments within the same governed scope when an earlier attempt failed because of §wyrlz-owned syntax, validation, packaging, wiring, or deployment-handoff defects**, provided the failure was inspected and the candidate was materially repaired before retry.
- It does **not** authorize a different product decision, a new Space, unrelated feature work, paid infrastructure, destructive rollback to a materially different state, or any action outside the original governed scope.
- If the user's current message explicitly narrows or revokes deployment authority, honor that narrower instruction.
- Documentation-only/source-governance commits remain deployment-inert.

Do not ask the user to re-authorize a retry whose sole purpose is to repair a defect §wyrlz just introduced inside the already-authorized deployment path. Do ask when the underlying idea/behavior must be remade, authorization/credentials are missing, a provider blocks progress, or safe repair is no longer clear.

A branch name alone does not prove deployment capability. A `main` commit is not automatically a deployment. The canonical request/workflow boundary below determines deployment truth.


---

## 3. Current production deployment-control contract — Hugging Face

The current application hosting/deployment authority is the existing Hugging Face Space `kamiloki/Swyrlz`.

**Vercel is deprecated for current §wyrlz application deployment.** Vercel-era workflows/configuration may remain in the repository as historical provenance, rollback/reference material, or migration evidence, but they are not a current production deployment path and must not be selected for new application releases.

### Canonical HF deployment branch + workflow

For the current HF candidate/release path, the deployment source branch is:

```text
feature/hf-space-manual-deploy
```

The canonical publish workflow on that branch is:

```text
.github/workflows/manual-hf-space.yml
```

It supports inspect/benchmark/validate/deploy modes and publishes only to the existing `kamiloki/Swyrlz` Space. Deploy mode requires explicit approval, snapshots the current Space before upload, records rollback/release checkpoints, validates the isolated package, and verifies required model/Chat integration before publication.

Current HF package/runtime-owned files on that branch include `hf_space/*`, the staged `accepted_runtime/lalm/r39_engine.py`, canonical Chat source staged by `scripts/prepare_hf_space.py`, and related HF validation/build scripts.

### Deployment gate

Ordinary source commits to `feature/hf-space-manual-deploy`, `runtime`, or `main` do not themselves publish the Space.

The canonical source-controlled production trigger is:

```text
main:.deploy/HF_SPACE_REQUEST.txt
  -> main:.github/workflows/hf-space-request.yml
  -> main:.github/workflows/manual-hf-space.yml
  -> SOURCE_REF=feature/hf-space-manual-deploy
  -> existing Space kamiloki/Swyrlz
```

An approved request uses `TARGET=kamiloki/Swyrlz`, `APPROVED=1`, the exact `SOURCE_REF`, and a fresh `REQUEST_NONCE`. The guarded workflow validates the package, preserves the predeploy Space revision/rollback lineage, uploads only after the gates pass, and captures the deployed revision.

Validate/inspect/benchmark work does not publish the Space.

If a deployment attempt fails before upload because of §wyrlz-owned candidate defects, fix the candidate, rerun deployment-inert validation, then issue a fresh request nonce and retry the same canonical path under the bounded corrective-retry authorization. Never create a replacement Space to escape a failed run.

### Historical Vercel material

Do not use `.github/workflows/manual-vercel-production.yml`, old Vercel aliases, project IDs, deployment receipts, or Vercel-era guides as current deployment instructions. They are historical unless a later explicit governance change reactivates Vercel.

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

A `main` mutation and a production deployment are separate concepts. Under the current fail-closed Git contract, ordinary `main` commits are deployment-inert and should proceed without deployment approval. Verify again after deployment-control changes or contradictory platform evidence, not after every ordinary commit.

If applying a stable change to production requires the explicit manual deployment workflow or another deployment-producing action, pass the Deployment Approval Gate first.

Documentation-only commits are expected to remain deployment-inert. If one produces a deployment, treat that as a deployment-control defect and reconcile the platform integration before continuing ordinary `main` work.

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
- advance Repository Work for the completed governed repository tier;
- advance Server Runtime only when an actual Server release/deployment advances deployed Server lineage;
- bump only components/modules that actually changed;
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

- `versions/repository-work.txt`
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
- [ ] Repository Work / Server / affected-component authority baseline captured;
- [ ] issue work inspected existing logs/cameras automatically;
- [ ] observability gap instrumented only if needed;
- [ ] deployment capability checked from current configuration **and current platform evidence**;
- [ ] terminal deployment/corrective retry is covered by current explicit or standing authorization;
- [ ] ordinary Git commits remain deployment-inert and the HF request file is the intentional publish trigger;
- [ ] HF deployment verification is bound to the exact selected source SHA + captured Space revision/rollback lineage;
- [ ] only intended owners/files changed;
- [ ] version authorities re-read at commit boundary;
- [ ] concurrent advances reconciled;
- [ ] Repository Work, Server (only if released/deployed), and actually changed component versions assigned correctly;
- [ ] roadmap/release record updated;
- [ ] post-change authorities re-read;
- [ ] source/static/runtime/live verification classified honestly;
- [ ] no legacy injector/loader/fallback unexpectedly overrides the intended source;
- [ ] any corrective retry followed a concrete diagnosed §wyrlz-owned failure and a materially repaired candidate.

---

## 12. Failure handling

A failed governed attempt is not silently erased.

When validation or deployment fails:

1. inspect the exact failing boundary/log;
2. classify ownership of the failure;
3. if §wyrlz caused it and repair is safely inside the authorized scope, repair it immediately, revalidate, and continue the same work turn through the canonical path;
4. if the product idea itself must change, authorization/credentials are missing, the external provider is blocking progress, or safe repair is unclear, stop with that concrete blocker and return the decision to the user;
5. preserve failure/correction lineage according to the version/roadmap contract.

Do not rewrite history to make a failed attempt look like it never happened, and do not substitute a failure report for a repair that §wyrlz can safely complete herself.

---

## Bottom line

**Architecture tells you where the change belongs. This document tells you how to mutate that owner safely. Prefer runtime-hot changes for runtime-owned behavior, keep stable infrastructure on main, keep ordinary Git commits deployment-inert, use the guarded existing-Space Hugging Face request/workflow path for publication, repair and retry §wyrlz-owned failures inside the authorized scope, preserve durable/version authority, and verify actual platform behavior before declaring the deployment boundary complete.**