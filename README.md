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

Obsolete Vercel-specific deployment guides and manifests have been removed from the active tree; their prior revisions remain accessible in Git history. Legacy Queue and Blob integrations discovered during the audit must be migrated and verified before removing their credentials or deleting historical hosted resources. Where an older release record conflicts with this hosting policy, Hugging Face remains authoritative.

## Current migration state

The existing Space is `kamiloki/Swyrlz`. Recent HF work integrates the Glitch Dragon Chat, selectable LALM routes, 700M context/output-budget repairs, and HF-local Google identity support. Live acceptance remains evidence-driven: source completion is not equivalent to a deployed/live verification receipt.

## Governance

Project Start, Roadmap, version authorities, deployment documentation, and future follow-through must describe Hugging Face as the current hosting authority and Vercel as retired. Historical records should be preserved rather than rewritten or deleted.
