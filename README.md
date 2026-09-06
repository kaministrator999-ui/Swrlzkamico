# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.0.2**

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
- Forge ZIP-wrapper support for a `.zip` containing the verified R39 `.gz`

## Preferred Forge deployment path

Forge may upload either the exact R39 gzip directly or a ZIP wrapper such as `lalm§wyrlz.zip` containing the gzip. AUTO/CHUNKED transport stores immutable chunk blobs under `.transport/...` plus a `*.transport.json` manifest instead of attempting one oversized Git blob.

At runtime `/api/lalm` searches the deployed repository for Forge transport manifests, verifies the manifest and every chunk, reconstructs the transported payload, and then:

- if the payload is the exact R39 gzip, it uses it directly;
- if the payload is a ZIP wrapper, it opens the ZIP and locates the nested gzip that matches the exact R39 gzip size/SHA contract.

The server then decompresses that verified gzip and verifies the raw R39 size/SHA before reporting the model ready.

Current Forge upload in this repository:
- manifest: `lalm§wyrlz.transport.json`
- wrapper: `lalm§wyrlz.zip`
- transport: `chunked-git-blobs-v1`
- chunks: `.transport/lalm§wyrlz/...`

Optional overrides:
- `SWRLZ_R39_TRANSPORT_MANIFEST` — explicit repository-relative or absolute manifest path.
- `SWRLZ_REPO_ROOT` — explicit deployed repository root if the runtime working directory differs.
- `SWRLZ_R39_URL` — direct HTTPS cold-start fallback for the exact gzip.

Deployment:
1. Confirm the generated `*.transport.json` and `.transport/...` chunk files are committed.
2. Import this repository into a new Vercel project.
3. Set `SWRLZ_ADMIN_TOKEN` to a long random secret.
4. Deploy.
5. Open `/api/health`.
6. Open `/api/lalm`; it should reconstruct the Forge chunks, unwrap the ZIP when present, verify R39, and decompress it automatically.
7. `/api/admin` remains available as a manual fallback upload workbench.

Important: Vercel `/tmp` is ephemeral and instance-local. The committed Forge chunks are the durable source; `/tmp` is only reconstructed runtime state. External object storage via `SWRLZ_R39_URL` remains supported as an alternative.

`PACKAGE_VALIDATION.json` records the original clean-transplant archive validation. Revision 2.0.1 added direct Forge chunk transport reconstruction. Revision 2.0.2 adds ZIP-wrapped Forge transport support and synchronizes the server route version metadata.
