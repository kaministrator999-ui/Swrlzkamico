# §wyrlz Clean Production Release Integrity Guide

**Role:** canonical preflight and release-integrity procedure for governed stable §wyrlz AI Chat/LALM deployments.

**Current production authority:** existing Hugging Face Space `kamiloki/Swyrlz`.

**Historical note:** Vercel-era cleanup/deployment procedures are retained elsewhere as lineage only. They are not current release instructions unless a later governed migration explicitly reactivates Vercel.

## 1. Mandatory current order

For every stable Hugging Face production candidate:

```text
SOURCE / ACCEPTED-RUNTIME MUTATION
→ REGISTER EXACT ACCEPTED BLOBS + LINEAGE WHEN ACCEPTED_RUNTIME CHANGED
→ PREPARE / VALIDATE THE EXACT HF CANDIDATE
→ VERSION + ROADMAP RECONCILIATION
→ VERIFY CANONICAL HF TARGET + SOURCE_REF + REQUEST GATE
→ SNAPSHOT EXISTING SPACE / ROLLBACK REVISION
→ GUARDED HF DEPLOY REQUEST
→ WATCH GITHUB WORKFLOW TO TERMINAL
→ CAPTURE DEPLOYED SPACE REVISION
→ VERIFY RUNTIME / HEALTH / EXPECTED REVISION
→ LIVE USER-VISIBLE ACCEPTANCE WHEN APPLICABLE
→ CLOSE ROADMAP EVENT
```

Do not use production as the first syntax/test probe. Do not create a replacement Space to recover from a failed candidate.

## 2. Accepted-runtime integrity gate

Any mutation under `accepted_runtime/` must be reconciled against `accepted_runtime/accepted.json` in the **same governed candidate**.

For each changed accepted target:

1. fetch/read the final candidate bytes;
2. compute/use the exact GitHub blob SHA for those bytes;
3. update the matching `files[].sourceBlobSha` or `overlayChain[].sourceBlobSha`;
4. update `sourceCommit` when that field records changed source lineage;
5. re-read the target and manifest after mutation; and
6. run the repository's current accepted/prepared-runtime integrity boundary before publication.

A commit SHA from another path, earlier blob SHA, intended content, or successful source mutation is **not** a substitute for the final accepted target's Git blob identity.

If integrity reports a source/overlay mismatch, STOP publication, repair registration, and rerun preflight.

## 3. Hugging Face candidate-preparation gate

The active source package is built from the explicitly selected deployment source (normally `feature/hf-space-manual-deploy`) through the existing preparation/deployment scripts and workflows.

Before publishing:

- verify `hf_space/README.md`, `hf_space/app.py`, `hf_space/requirements.txt`, and required staged runtime/model/Chat files exist;
- parse/compile the Python owners included by the workflow;
- preserve the pinned original Test Bench contract;
- verify required native/R39/model provenance gates;
- run deterministic regressions relevant to the changed behavior;
- preserve existing Chat/inference integration;
- ensure the exact source SHA selected for deployment is the one just validated.

A failed validation is **not** a deployment failure and must not upload a new Space revision.

## 4. Canonical Hugging Face request gate

Current deployment is source-controlled through:

```text
main:.deploy/HF_SPACE_REQUEST.txt
  → main:.github/workflows/hf-space-request.yml
  → main:.github/workflows/manual-hf-space.yml
  → SOURCE_REF=feature/hf-space-manual-deploy
  → kamiloki/Swyrlz
```

An approved production request must name:

```text
TARGET=kamiloki/Swyrlz
APPROVED=1
SOURCE_REF=<exact intended source ref>
REQUEST_NONCE=<fresh unique nonce>
```

The request file is the intentional publish trigger. Ordinary Git/documentation commits remain deployment-inert.

## 5. Snapshot and rollback integrity

Before upload, the guarded workflow must snapshot/record the existing Space revision and rollback checkpoint.

The workflow must preserve enough evidence to answer:

- what Space revision was serving before this deployment;
- what exact Git source SHA/ref produced the candidate;
- whether candidate validation passed;
- whether upload was attempted;
- what Space revision resulted;
- which prior revision is the rollback target if a later explicit rollback is needed.

Do not call an upload “known good” merely because the upload step succeeded.

## 6. §wyrlz-owned failure recovery

Failure recovery follows the ownership rule in Project Start and Hotfix Rules.

When a validation/deployment failure is caused by §wyrlz's own syntax, malformed wiring, packaging, missing staged file, regression, or deployment handoff:

1. inspect the exact failing step/log;
2. repair the actual cause;
3. re-run all deployment-inert validation required for the corrected candidate;
4. issue a fresh guarded request nonce when a new deployment attempt is needed;
5. rerun the same existing-Space HF path;
6. preserve the failed attempt and corrective attempt in roadmap/release lineage.

Do not return a safely repairable §wyrlz-caused failure to the user as unfinished implementation work.

Corrective retries are bounded: each retry requires a concrete diagnosed cause and materially repaired candidate. Stop for a genuine user-owned product decision, missing authorization/credentials, unsafe action, external provider blocker, or when further retries are no longer evidence-driven.

## 7. Failure localization

Diagnose the earliest failed boundary.

- Source/static regression fails → repair source; no publication occurred.
- HF package validation fails → repair packaging/staging; no publication occurred.
- Snapshot/authorization gate fails → repair that gate before upload.
- Workflow fails before upload → no new Space revision was published.
- Upload fails → preserve predeploy revision and inspect provider/workflow evidence.
- Upload succeeds but revision/runtime verification fails → preserve deployment identity and diagnose activation/runtime.
- Runtime works but user-visible behavior fails → treat it as behavioral acceptance failure, not deployment failure.

## 8. Definition of a clean release

A stable HF release is clean only when the applicable gates are evidenced:

```text
candidate source/integrity PASS
deployment-inert validation PASS
exact SOURCE_REF/SHA identified
predeploy Space snapshot/rollback checkpoint PASS
guarded HF workflow terminal PASS
deployed Space revision captured
runtime/health/revision verification PASS
user-visible acceptance PASS when required
roadmap closure recorded
```

Never report `deployed` from a commit or trigger alone. Never report `live fixed` from source/static validation alone.

## Bottom line

**Prepare the exact candidate, prove it before upload, preserve the current Space, deploy only through the guarded existing-Space Hugging Face path, repair §wyrlz-owned failures inside the authorized scope, capture the resulting revision, and distinguish deployment success from live behavioral acceptance.**
