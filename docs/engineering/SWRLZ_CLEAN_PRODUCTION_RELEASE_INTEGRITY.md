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
→ TRIGGER / VERIFY STALE-DEPLOYMENT CLEANUP
→ TRIGGER ONE PRODUCTION REQUEST
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

## 3. Cleanup gate

Only after candidate integrity passes:

- confirm the canonical Vercel project is `swrlzkamico-o3nu` / `prj_dGgleDMgkOQ57wULKlDH5fcYj9Yp`;
- trigger the repository-owned stale-deployment cleanup mechanism;
- observe the GitHub Actions result rather than inferring success from the trigger commit;
- require cleanup success before the production request.

Never create or substitute another Vercel project.

## 4. Production trigger gate

The canonical production trigger is the governed `.deploy/REQUEST.txt` mutation consumed by `.github/workflows/manual-vercel-production.yml`, unless a later canonical contract explicitly replaces it.

Before writing the request, verify:

- candidate integrity preflight passed;
- cleanup completed successfully;
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
cleanup PASS
production workflow PASS
canonical Vercel deployment observed
expected source/revision observed
runtime/health verification PASS
roadmap closure recorded
```

Never report `deployed` from a commit alone.
