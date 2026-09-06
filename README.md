# §wyrlz Clean Vercel SERVER Transplant

Server revision: **2.0.6**

This package is for a **brand-new GitHub repository and brand-new Vercel project**.

It intentionally does **not** include the old `.git` history or a monolithic 226 MB R39 Git blob. That avoids dragging the multi-GB repository history into the new deployment and avoids GitHub's regular single-blob size limit.

Included:
- one FastAPI/Vercel entrypoint at `api/index.py`
- `/api/health`
- `/api/admin` unified phone/server workbench
- `/api/lalm`
- exact repaired R39 size/SHA contract
- gzip -> raw verification
- Forge chunked Git transport reconstruction (`chunked-git-blobs-v1` / `v2`)
- Forge ZIP-wrapper support for a `.zip` containing the verified R39 `.gz`
- Vercel bundle-size handling: `.transport/**` is excluded from deployment/function bundles and missing chunks are streamed from the deployment's exact GitHub commit at runtime
- hot Gate 5 execution with R39 load/verification performed inside the same function invocation
- arbitrary binary/text uploads, directory browsing, media/PDF/text/binary preview, text editing, SHA-256, rename, delete, folder creation, runtime logging, and response-safe chunked downloads

## Unified runtime boundary

Revision 2.0.5 consolidated the former `api/admin.py`, `api/lalm.py`, and `api/health.py` serverless entrypoints into the single `api/index.py` FastAPI application. Vercel routes `/api/*` through that entrypoint, so Admin, health, LALM loading, file operations, and Gate 5 use one function definition instead of three separately packaged functions.

Vercel `/tmp` is still ephemeral and instance-local and Vercel may scale a function to multiple instances. Therefore the hot Gate 5 action does **not** assume that a previous `/api/lalm` request populated the same instance. `RUN HOT GATE 5` calls `ensure_r39()` inside the same invocation immediately before executing `/tmp/swrlz-admin/live/gate5_live.py`. It exports these local paths to the script:

- `SWRLZ_R39_PATH=/tmp/swrlz-admin/live/SWYRLZ_LALM_R39_PHYSICAL_BASE_REPAIRED.§wyrlzx`
- `SWRLZ_LALM_PATH` — same verified raw R39 path
- `SWRLZ_R39_GZ_PATH` — verified packed gzip path
- `SWRLZ_LIVE_DIR=/tmp/swrlz-admin/live`

This gives Gate 5 a verified local model in the exact runtime invocation that launches it.

## Admin workbench

`/api/admin` accepts any file type through chunked binary-safe upload. The workbench can browse `/tmp/swrlz-admin`, create folders, preview/edit UTF-8 text/code files up to the editor limit, preview images/video/audio/PDF files, show a binary hex preview, calculate SHA-256, rename, and delete files. Admin actions require `SWRLZ_ADMIN_TOKEN` through the `x-swrlz-admin-token` request header.

Revision 2.0.6 adds large-file downloads without sending an oversized Vercel response. `download-info` returns the file size, MIME type, chunk size, and source runtime instance. `download-chunk` then serves at most 3 MiB per `206 Partial Content` response and rejects the transfer if Vercel moves it to a different runtime instance. The browser loops over those chunks with a visible progress bar. When the browser supports the File System Access API, chunks are written directly to the selected destination rather than accumulating a large R39-sized Blob in browser RAM; other browsers fall back to Blob assembly.

The workbench also exposes `LOAD / VERIFY LALM`, `RUN HOT GATE 5`, runtime state, and the full Gate 5 runtime log. Upload and download sessions retain the instance ID guard so a multi-chunk transfer fails explicitly and can be restarted if Vercel moves it to a different runtime instance.

## Preferred Forge deployment path

Forge may upload either the exact R39 gzip directly or a ZIP wrapper such as `lalm§wyrlz.zip` containing the gzip. AUTO/CHUNKED transport stores immutable chunk blobs under `.transport/...` plus a `*.transport.json` manifest instead of attempting one oversized Git blob.

The root transport manifest remains bundled with the server. The large `.transport/**` chunk directory and preserved `SWRLZ_NEW_SERVER_GITHUB_READY.zip` archive are excluded from the Vercel deployment input with `.vercelignore`, while the Python function configuration also excludes them with the documented `api/**/*.py` function glob. When a chunk is not present locally, the R39 loader streams it from `raw.githubusercontent.com` using Vercel's Git repository owner/slug and exact deployment commit SHA, then verifies the chunk SHA before accepting it.

At runtime the loader verifies the manifest and every chunk, reconstructs the transported payload, and then:

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
1. Confirm the generated `*.transport.json` and `.transport/...` chunk files are committed to GitHub.
2. Import this repository into Vercel.
3. Set `SWRLZ_ADMIN_TOKEN` to a long random secret.
4. Deploy. Vercel should exclude the large transport/archive payload from the deployment bundle.
5. Open `/api/health`.
6. Open `/api/lalm` to verify the public R39 reconstruction path.
7. Open `/api/admin`, set the admin token, and use `LOAD / VERIFY LALM` or `RUN HOT GATE 5`.

Important: the committed Forge chunks are the durable model source. `/tmp` is reconstructed runtime state, not persistent storage. External object storage via `SWRLZ_R39_URL` remains supported as an alternative.

`PACKAGE_VALIDATION.json` records the original clean-transplant archive validation. Revision 2.0.1 added direct Forge chunk transport reconstruction. Revision 2.0.2 added ZIP-wrapped Forge transport support. Revision 2.0.3 added runtime streaming of excluded Forge chunks from the exact GitHub deployment commit. Revision 2.0.4 fixed the Vercel Python function glob and added `.vercelignore`. Revision 2.0.5 consolidated all API behavior into one FastAPI function, made Gate 5 load R39 in the same invocation, and upgraded the Admin workbench into a binary-safe file manager/viewer/editor. Revision 2.0.6 adds response-safe chunked downloads for large files, including the full R39 artifacts.