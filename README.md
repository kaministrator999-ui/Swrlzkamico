# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.0.3**

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
- Vercel bundle-size handling: `.transport/**` is excluded from Python function bundles and missing chunks are streamed from the deployment's exact GitHub commit at runtime

## Preferred Forge deployment path

Forge may upload either the exact R39 gzip directly or a ZIP wrapper such as `lalm§wyrlz.zip` containing the gzip. AUTO/CHUNKED transport stores immutable chunk blobs under `.transport/...` plus a `*.transport.json` manifest instead of attempting one oversized Git blob.

The root transport manifest remains bundled with the server. The large `.transport/**` chunk directory is excluded from Vercel Python function bundles so the function stays below Vercel's 500 MB uncompressed Python bundle limit. When a chunk is not present locally, `/api/lalm` streams it from `raw.githubusercontent.com` using Vercel's Git repository owner/slug and exact deployment commit SHA, then verifies the chunk SHA before accepting it.

At runtime `/api/lalm` verifies the manifest and every chunk, reconstructs the transported payload, and then:

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
- `SWRLZ_GITHUB_OWNER`, `SWRLZ_GITHUB_REPO`, `SWRLZ_GITHUB_REF` — fallback GitHub source coordinates when Vercel Git system environment variables are unavailable.

Deployment:
1. Confirm the generated `*.transport.json` and `.transport/...` chunk files are committed.
2. Import this repository into a new Vercel project.
3. Set `SWRLZ_ADMIN_TOKEN` to a long random secret.
4. Deploy.
5. Open `/api/health`.
6. Open `/api/lalm`; it should stream the excluded Forge chunks from GitHub, reconstruct the ZIP, unwrap the nested gzip, verify R39, and decompress it automatically.
7. `/api/admin` remains available as a manual fallback upload workbench.

Important: Vercel `/tmp` is ephemeral and instance-local. The committed Forge chunks are the durable source; `/tmp` is only reconstructed runtime state. External object storage via `SWRLZ_R39_URL` remains supported as an alternative.

`PACKAGE_VALIDATION.json` records the original clean-transplant archive validation. Revision 2.0.1 added direct Forge chunk transport reconstruction. Revision 2.0.2 added ZIP-wrapped Forge transport support. Revision 2.0.3 excludes large Forge chunks from Vercel Python function bundles and streams them from the exact GitHub deployment commit at runtime.
