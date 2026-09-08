# Server 2.2.2 production deployment trigger

This commit intentionally changes the production branch to force the Vercel Git integration to enqueue a fresh production deployment from the current `main` state.

Expected server version after deployment: `2.2.2`
Expected entrypoint commit lineage includes: `fb548a4eae5fd3023761294360fd3404606f78f3`

Retry trigger: 2026-09-07 21:28 America/Chicago after the previous deployment was manually redeployed from the stale 21a5efa snapshot. This commit exists only to make Vercel build the current `main` tree rather than redeploying that old snapshot.
