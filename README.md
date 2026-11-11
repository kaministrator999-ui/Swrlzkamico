# §wyrlz — Hugging Face Hosted LALM Server

## Hosting authority

**Hugging Face is the active hosting and deployment authority for §wyrlz.**

- Canonical Space: `kamiloki/Swyrlz`
- Canonical Chat source: `chat/§wyrlz/index.html`
- Historical/default HF integration branch: `feature/hf-space-manual-deploy` (not assumed current; guarded deployments pin the exact validated source ref or commit SHA)
- Vercel: **DISCONTINUED / historical only**

Do not plan, trigger, repair, or require Vercel deployments for current §wyrlz work. Existing Vercel source, contracts, changelogs, and release receipts remain in repository history for provenance and migration reference only; they are not current deployment authority.

## Current operating rule

Current application work targets the existing Hugging Face Space. Preserve the established HF manual guarded deployment path, rollback lineage, model routes, Chat architecture, authentication boundaries, and validation gates.

For Chat changes, edit the canonical clean-room Chat first, synchronize the HF deployment branch/package as required, run source/static validation, then use the existing HF deployment/acceptance flow. Never create a replacement Space merely to recover from a failed deployment.

## Repository lineage

Obsolete Vercel-specific deployment guides and manifests have been removed from the active tree; their prior revisions remain accessible in Git history. The legacy Queue subscriber has been replaced with an HF process-owned dispatcher. Generations are still recorded in Redis, but an HF process restart can interrupt an in-flight task. Temporary generation transcript checkpoints now use Redis with a 30-minute TTL. Legacy Blob account-state migration and collector storage still require verification before removing credentials or deleting historical hosted resources. Where an older release record conflicts with this hosting policy, Hugging Face remains authoritative.

## Current migration state

The existing Space is `kamiloki/Swyrlz`. Recent HF work integrates the Glitch Dragon Chat, selectable LALM routes, 700M context/output-budget repairs, and HF-local Google identity support. Live acceptance remains evidence-driven: source completion is not equivalent to a deployed/live verification receipt.

## Governance

Project Start, Roadmap, version authorities, deployment documentation, and future follow-through must describe Hugging Face as the current hosting authority and Vercel as retired. Historical records should be preserved rather than rewritten or deleted.

## Hosting cleanup migration status (2026-11-11)

- The active deployment gate is `.github/workflows/manual-hf-space.yml`; its
  validation, pinned source, rollback snapshot, and exact-Space checks must remain.
- Vercel-only live collector verification workflow and probes were retired
  because they point to the obsolete Vercel host and require old credentials.
- Legacy Vercel Blob account-state read fallback (`api/chat_state.py`) remains
  temporarily to support migration of any historical account state to Redis.
  Verify state parity and data retention before removing that path or deleting
  the old project or Blob store.
- The frozen-web collector still has legacy Blob storage expectations on its
  runtime branch. Its persistence must be migrated before removing old storage.
- Browser localStorage compatibility keys and older stream contract identifiers
  are intentionally preserved to avoid discarding user cache/session data.
- These GitHub changes have not themselves deployed the new runtime to HF.
