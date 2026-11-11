# §wyrlz hosting retirement gate — 2026-11-11

**Current hosting authority:** GitHub source and guarded releases → existing
Hugging Face Space `kamiloki/Swyrlz`. Vercel is retired as a deployment
target and must not be reintroduced.

## Confirmed source cleanup

- Vercel-only source files, old hosting Queue subscriber and deployment
  probes have been removed from active `main`.
- Vercel project `swrlzkamico-o3nu` has no active production deployment or
  returned deployment history as of this audit. Preview deployments were
  disabled and its build step was configured to be skipped.
- No Vercel-named paths remain in the current `main` tree.
- The Chat account-state Redis migration now fails closed on Redis or legacy
  read errors, migrates with `SET ... NX`, verifies the stored record, and
  no longer contains a Vercel Blob writer. First authenticated read still
  supports a **read-only** legacy Blob fallback if credentials are present.
- The active runtime collector on the `runtime` branch still expects private
  Vercel Blob for state and immutable archived snapshots. It is NOT safe to
  remove that dependency or delete the Blob store without a verified export.

## Required evidence before irreversible retirement

1. Confirm all historical account-state objects were migrated into canonical
   Redis, not merely the most recent logged-in account. Export an inventory
   and count/verify records and revisions; do not expose user data in CI.
2. Export the collector's private state, snapshots and document objects, with
   checksums, and verify that a new durable backend restores the same data.
   Never substitute ephemeral Hugging Face Space disk for durable storage.
3. For large collector snapshots, the recommended Hugging Face-native
   replacement is an **attached private Storage Bucket volume**. Account
   setup or new paid storage requires the owner's approval. Confirm an
   attached, writable bucket and test persisted content after a Space restart.
   Redis remains the authority for account records and may coordinate
   mutations; do not put large snapshot objects into a small Redis tier
   without inspecting size and cost.
4. Deploy changes through the **existing guarded Hugging Face Space workflow**
   only after source/package compatibility, snapshot, rollback and live
   authentication/streaming/collector acceptance pass. Do not assume a
   successful source-level workflow means the Space is updated.
5. Disconnect the old Vercel project's GitHub link and verify that the
   provider no longer posts deployment status checks; then delete the
   historical Vercel project through the owner's confirmation in Vercel.
   Verify independent Redis and Blob resource retention/backup before
   deleting their credentials or provider accounts.

**Never infer successful data migration from the old project's zero active
deployments, zero project connector connections, or inactive hosting state.**

## Read-only validation

The `read-only-hf-storage-inventory.yml` GitHub workflow reports only the
number of Hugging Face volume attachments and attached Bucket volumes;
it never creates resources, writes files, prints tokens or modifies the Space.
The static `verify-hf-hosting-authority.yml` workflow prevents reintroduction
of retired Queue and deployment configuration. Older protocol IDs and
browser cache keys remain until a compatible client data migration is proven.
