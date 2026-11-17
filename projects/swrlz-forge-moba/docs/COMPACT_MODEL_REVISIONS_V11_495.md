# §E v11.495 — smaller cloud transfers while preserving complete revisions

The Android screenshot showed **Save to account** taking about 128 seconds after the native model, selected project and validation stages had finished. This is the full account write/confirmation stage, not just local model loading.

A plausible major contributor is the old v11.486 archive format: each historic full scene contains *two identical base64 copies* of the Sorting Hat's UV PNG (active model and active level). Each old revision compresses to roughly 6.9 MB, then is base64 encoded again for storage in the account record. Seven revisions may inflate a native project to tens of megabytes.

This additive codec puts identical historic UV PNG strings into a shared pool stored in the **same account document**. Every historical snapshot retains its complete scene, rigs, mesh, UVs, animation and image references. The existing revision UI resolves those references transparently when rolling back. Existing legacy gzip+base64 revisions are migrated on the first next save; future saves retain the compacted records and append only the changed snapshot. New image variants receive separate pool entries.

Do not remove old revisions or assume all uploads take a fixed duration. The **first** save will spend extra time converting older snapshots; subsequent saves avoid repeatedly sending identical historical artwork. The progress panel will show the actual encoded MiB being sent, while the six real stages and immediate verified reopening from v11.494 remain intact. Storage on §C and network throughput remain possible independent bottlenecks.

Safety: Save to account still uses the original project and expected revision, rejects stale or unauthorized writes, does not retry ambiguous cloud saves, and never auto-overwrites or uploads the user's Sorting Hat. A separate v5 ZIP makes the physical mouth surface smoother/more texture-led, leaving the UV, skinning and clips unchanged.

Verification: `tests/model_revision_shared_texture_v11_495.cjs` checks historical round-trip, duplicate texture deduplication, multiple revisions, a changed texture, and a missing pool. Build all 472 source patches, validate SHA, package below the hosted static size limit and check public HTML/JS headers. Device transfer timing requires an Android retest after deployment.
