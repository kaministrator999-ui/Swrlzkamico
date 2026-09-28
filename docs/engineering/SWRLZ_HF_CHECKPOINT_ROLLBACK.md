# §wyrlz Hugging Face Checkpoints and Rollback

## Purpose

Every approved Hugging Face deployment must preserve an exact return path before the existing `kamiloki/Swyrlz` Space is mutated. A Git commit is engineering history; a checkpoint is a reproducible deployment state; a known-good release is a checkpoint that has subsequently passed runtime/user-visible verification.

## Checkpoint classes

1. **Pre-deploy rollback checkpoint** — created before upload. It records the current Space revision, the Git source commit preparing the candidate, the snapshot-manifest digest, and the workflow artifact that contains the prior Space text/configuration snapshot.
2. **Deployed candidate checkpoint** — created immediately after upload. It records the exact new Space revision, exact Git source commit, and the prior Space revision to which rollback points. It starts as `DEPLOYED_UNVERIFIED`.
3. **Known-good checkpoint** — a deployed candidate may be promoted only after the required runtime and user-visible acceptance checks pass. Deployment success alone never means known-good.

## Restore law

Rollback is a deployment-producing action and requires explicit user approval. Never silently roll back merely because verification failed.

For a rollback:
- select an immutable checkpoint;
- verify its source commit / Space revision and snapshot artifact identity;
- restore only the existing `kamiloki/Swyrlz` Space;
- do not create a replacement Space;
- rebuild/restart as required by Hugging Face;
- verify the resulting Space revision and the expected `/legacy`, `/probe`, Dragon Chat/Station and model routes;
- record the rollback and resulting truth state in `SWRLZ_SERVER_ROADMAP.md`.

A pre-deploy snapshot artifact is retained for 30 days and its compact rollback checkpoint manifest for 90 days by the current workflow. Artifact retention is therefore not permanent archival. The immutable Space revision and Git source commit are the long-lived identities; if long-term offline reconstruction becomes required, add a separate archival owner rather than assuming Actions artifacts live forever.

## Capability knowledge

The model-facing capability map should describe what the **current verified checkpoint can do**, not replay historical update notes. Historical progression stays in the Roadmap. When runtime project/capability retrieval is implemented, it must select capability records associated with the active verified checkpoint and keep them separate from user profile, user memory and thread history.

## Current automation

`.github/workflows/manual-hf-space.yml` now:
- snapshots the existing Space before approved deploy;
- emits `hf-rollback-checkpoint.json` and uploads it as the `hf-rollback-checkpoint` artifact;
- uploads the approved candidate;
- reads the resulting exact Space revision;
- emits `hf-release-checkpoint.json` as `DEPLOYED_UNVERIFIED` and uploads it as the `hf-release-checkpoint` artifact.

No automatic rollback or known-good promotion is performed. Those remain governed, evidence-based actions.
