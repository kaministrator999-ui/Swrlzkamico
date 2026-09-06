# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.0.1**

This package is for a **brand-new GitHub repository and brand-new Vercel project**.

It intentionally does **not** include the old `.git` history or a monolithic 226 MB R39 Git blob. That avoids dragging the multi-GB repository history into the new deployment and avoids GitHub's regular single-blob size limit.

Included:
- FastAPI/Vercel routes
- `/api/health`
- `/api/admin` phone upload workbench
- `/api/lalm`
- exact repaired R39 size/SHA contract
- gzip -> raw verification
- Forge chunked Git transport reconstruction (`chunked-git-blobs-v1` / `v2`)

## Preferred Forge deployment path

Forge may upload `SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx.gz` with CHUNKED/AUTO transport. Forge stores immutable chunk blobs plus `SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx.gz.transport.json` in the repository instead of attempting one oversized Git blob.

At runtime `/api/lalm` searches the deployed repository for that transport manifest, verifies the manifest's exact R39 size/SHA contract, verifies each chunk's size/SHA, reconstructs the gzip into `/tmp/swrlz-admin/live`, verifies the whole gzip again, decompresses it, and verifies the raw R39 size/SHA.

Optional overrides:
- `SWRLZ_R39_TRANSPORT_MANIFEST` — explicit repository-relative or absolute manifest path.
- `SWRLZ_REPO_ROOT` — explicit deployed repository root if the runtime working directory differs.
- `SWRLZ_R39_URL` — direct HTTPS cold-start fallback for the exact gzip.

Deployment:
1. Upload the R39 gzip to this repository through §wyrlz Forge using AUTO or CHUNKED transport.
2. Confirm the generated `*.transport.json` and `.transport/...` chunk files are committed.
3. Import this repository into a new Vercel project.
4. Set `SWRLZ_ADMIN_TOKEN` to a long random secret.
5. Deploy.
6. Open `/api/health`.
7. Open `/api/lalm`; it should reconstruct and verify the repository chunks automatically.
8. `/api/admin` remains available as a manual fallback upload workbench.

Important: Vercel `/tmp` is ephemeral and instance-local. The committed Forge chunks are the durable source; `/tmp` is only reconstructed runtime state. External object storage via `SWRLZ_R39_URL` remains supported as an alternative.

`PACKAGE_VALIDATION.json` records the original clean-transplant archive validation. Revision 2.0.1 adds the post-extraction Forge chunk transport compatibility described above.
