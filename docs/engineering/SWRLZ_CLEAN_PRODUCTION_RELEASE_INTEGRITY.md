# §wyrlz Clean Production Release Integrity Guide

**Role:** canonical preflight and release-integrity procedure for governed stable Server deployments.

**Purpose:** make cleanup and deployment deterministic by proving the candidate is internally valid *before* destructive/remote release stages begin.

## 1. Mandatory order

For every stable production candidate:

```text
SOURCE / ACCEPTED-RUNTIME MUTATION
→ REGISTER EXACT ACCEPTED BLOBS + LINEAGE
→ RUN PREPARED-RUNTIME INTEGRITY PREFLIGHT
→ VERSION + ROADMAP RECONCILIATION
→ VERIFY CANONICAL VERCEL PROJECT LOCK
→ PROVE PRODUCTION WORKFLOW SUCCESS PATH FROM SOURCE + KNOWN-GOOD EVIDENCE
→ TRIGGER ONE PRODUCTION REQUEST
→ PRODUCTION WORKFLOW PREPARES REPLACEMENT ARTIFACT
→ PRODUCTION WORKFLOW CLEARS ALL PREVIOUS CANONICAL-PROJECT DEPLOYMENTS
→ VERIFY ZERO PREVIOUS DEPLOYMENTS REMAIN
→ DEPLOY THE ALREADY-PREPARED ARTIFACT
→ OBSERVE GITHUB ACTIONS
→ VERIFY VERCEL RECEIVED THE DEPLOYMENT
→ VERIFY RUNTIME / HEALTH / EXPECTED REVISION
→ CLOSE ROADMAP EVENT
```

Do not advance to cleanup or production request while an earlier gate is unverified.

## 2. Accepted-runtime integrity gate

Any mutation under `accepted_runtime/` must be reconciled against `accepted_runtime/accepted.json` in the **same governed candidate**.

For each changed accepted target:

1. fetch/read the final bytes that will exist in the candidate;
2. compute/use the exact GitHub blob SHA for those bytes;
3. update the matching `files[].sourceBlobSha` or `overlayChain[].sourceBlobSha`;
4. update `sourceCommit` when that field records the changed source lineage;
5. re-read the target and manifest after mutation; and
6. run the same integrity boundary used by production preparation: `python scripts/prepare_runtime_generation.py --accepted-root accepted_runtime --output-root <temporary-output>` or the repository's current canonical equivalent.

A commit SHA, source SHA from another path, earlier blob SHA, intended content, or successful source mutation is **not** a substitute for the final accepted target's Git blob identity.

If preparation reports `accepted source blob mismatch` or `accepted overlay blob mismatch`, STOP. Repair the registration and rerun preflight. Do not trigger cleanup or production deployment.

## 3. Cleanup semantics and pre-trigger proof

The standalone `Purge Stale Vercel Deployments` workflow is **maintenance-only**. It intentionally protects the deployment currently serving the production alias and deletes only other stale deployments. A green standalone purge therefore does **not** mean the current production server was cleared, and it is not the release gate.

The canonical production workflow owns destructive replacement cleanup. Before triggering it:

- confirm the canonical Vercel project is `swrlzkamico-o3nu` / `prj_dGgleDMgkOQ57wULKlDH5fcYj9Yp`;
- inspect the current production workflow source and a known-good historical run;
- prove the candidate satisfies every statically/repository-verifiable prerequisite through the last pre-deploy gate;
- verify that the workflow prepares the replacement artifact **before** destructive cleanup;
- verify that its destructive cleanup targets only the canonical project and has an explicit post-delete acceptance check requiring zero previous deployments before `vercel deploy`.

**The trigger itself is never the experiment.** Know why the invocation should succeed before invoking it. GitHub Actions executes the proven release path; it is not the first diagnostic probe.

Never create or substitute another Vercel project.

## 4. Production trigger gate

The canonical production trigger is the governed `.deploy/REQUEST.txt` mutation consumed by `.github/workflows/manual-vercel-production.yml`, unless a later canonical contract explicitly replaces it.

Before writing the request, verify:

- candidate integrity preflight passed;
- the production success path has been proved from current workflow source, current candidate state, and known-good evidence;
- the workflow's destructive cleanup includes a post-delete zero-remaining acceptance gate;
- `TARGET=production`, `APPROVED=1`, and the intended `SOURCE_REF` are correct;
- `SOURCE_COMMIT` identifies the final candidate intended for deployment;
- no later source mutation has made that candidate stale.

After the request, inspect the actual GitHub Actions run. A trigger commit is not proof of workflow success, and workflow success before the deploy step is not proof Vercel received a deployment.

## 5. Failure localization

Diagnose the earliest failed boundary.

- Cleanup workflow fails → repair cleanup; do not deploy.
- Prepared-runtime verification fails → repair accepted/source integrity; do not blame Vercel.
- Production workflow fails before `vercel deploy` → no new Vercel deployment exists.
- Vercel build/deploy fails → inspect that deployment's build evidence.
- Deployment succeeds but runtime verification fails → preserve deployment identity and diagnose runtime/activation.

Compare **known-good run → failed run → governing workflow/source contract** before changing trigger machinery. One successful trigger and one failed trigger with the same contract does not by itself prove the trigger is broken.

## 6. Definition of a clean release

A release is clean only when all are evidenced:

```text
accepted integrity PASS
pre-trigger success-path proof PASS
destructive cleanup inside production workflow PASS with zero previous deployments remaining
production workflow PASS
canonical Vercel deployment observed
expected source/revision observed
runtime/health verification PASS
roadmap closure recorded
```

Never report `deployed` from a commit alone.
