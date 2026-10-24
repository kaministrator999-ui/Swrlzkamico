# §wyrlz Code Deliverables v184 — single files and structured ZIP archives

**Status: ISOLATED SOURCE CANDIDATE. NOT LIVE OR WEIGHT-TRAINED.**

## Delivery contract

- A committed, completed code artifact with exactly **one text file** offers a direct **Download file** link. Filename comes from its safe relative artifact path.
- Two or more saved files offer a single **Download ZIP** link, preserving relative project directories. The previous grouped "Download all" behavior (several separate browser downloads) is replaced.
- If the user specifically requests a ZIP/archive on the generation turn, even a single file is downloaded as a ZIP.
- Normal explanations, incomplete streaming responses, rejected candidate code, or lyrics should not yield fabricated download links. A normal code-fenced file becomes an artifact when the completed response is committed.

## Existing architecture reused

Qwen emits full source blocks with language and file metadata (example header: python file=src/main.py). Brain retains canonical intent and acceptance constraints; Qwen is not trusted to create URLs. Station already owns per-thread codeArtifacts, historical revisions, source hashes, and caller-cookie session state. New GET /api/lalm_station/artifacts/download derives file bytes ONLY from the selected committed artifact revision. The Chat Mask renders a same-origin link once the completed artifact is available. Existing user-visible code syntax and per-file code block copy/download remain intact.

### Example ZIP layout

- project-files.zip
  - README.md
  - src/app.py
  - tests/test_app.py

When all files share a root directory, use that folder as the archive basename. An explicitly archived single README.md can download as README.zip. Archive creation is pure stdlib Python ZIP_DEFLATED, no new runtime dependencies.

## Trust and safety

- No arbitrary disk path is accepted as download input. Reject zip-slip/path traversal, absolute/drive paths, reserved Windows names, ambiguous duplicates, control characters, overlong names, excessive nesting, more than 32 files, any file over 1MiB and aggregate text over 8MiB.
- No archive data is uploaded to GitHub, no generated program is executed. Delivery uses in-memory bytes, Content-Disposition: attachment, private no-store, nosniff and same-origin response headers.
- A download needs valid same-session cookie, thread ID, artifact ID, numeric revision and exact revision SHA. Cross-session, stale revision/hash and corrupt source content are denied; historical immutable revisions can still be fetched when the in-memory session persists.
- HF Station state is process-local, NOT durable storage. A server restart/session expiration may invalidate a previously rendered link; long-term accessible downloads require later authenticated durable artifact storage.
- Archive content is complete relative to **the artifact files actually produced**; it does NOT prove the code compiles or all requested multi-file requirements are satisfied. Preserve both technical-validity and user-intent evaluation gates.
- Explicit filename/ZIP request is not an authorization to modify the user's GitHub repo or deploy code.

## Not yet implemented

Larger projects that exceed the current Qwen output cap need a **staged multi-turn workspace builder**, rather than printing fake/truncated code: a file manifest with required paths, source hashes, per-file completion, resumable/cancellable generation, file-by-file verification, and a download ZIP only after the artifact passes completeness checks. Also not included: compiled binaries, images, non-UTF8 files, or automatically resolving a natural-language cross-turn request to "ZIP my old code" into a specific saved artifact. Users can download a saved artifact via its completed-message link.

## Verification and promotion

Development branch: feature/coder-download-packages-v184 (based on existing HF candidate source). CI workflow: .github/workflows/verify-code-packages-v184.yml. It verifies exact downloadable bytes, ZIP directory structure, path/size limits, explicit archive intent, cookie/session isolation, revision hashes, tiny code, lyric exclusion, and frontend inline JavaScript syntax.

Branch CI is not hosted Chat acceptance. Before merge and guarded production deployment, run existing streaming/Chat/repair/lyric regressions and a real browser check on mobile/desktop; retain a rollback reference. No change to current production Space, model weights, server versions or request nonce is implied by this isolated candidate.
