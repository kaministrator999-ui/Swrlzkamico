# §E v11.533 account project opening

Status **source candidate**. The live baseline is v11.532. This checkpoint covers opening a full native project from the Google account library. The §C modeling session and project geometry are outside this release.

## Failure and repair

Kami saw the project and its revision in My Projects, then received “Could not open project: see § Chat account status. Your active scene was preserved.” The account download itself returned HTTP 200 for revision 5 and passed its SHA-256 check. The downloaded native project contained 13 editable parts. A separate browser can read the account project while another browser has it open. Account reads authorize the Google owner independently of the editor's §C action lease.

In the assembled v11.532 browser source, the outer v11.528 account-open wrapper changed a `cloud:<id>` picker value to a raw ID and called its captured loader without passing an argument. The original loader accepts a raw ID only as an explicit argument. It rejected that call before downloading the project or recording a diagnostic. The wrapper could also report success if a prior account link already matched the target, even when the latest attempt had failed.

The appended v11.533 patch passes the normalized ID explicitly through the existing checked account loader. The picker selection and default options remain intact. Success requires a confirmed native load and matching account revision. Downloaded data must carry the requested ID and a positive revision before the editor changes. The direct editor, §Chat picker, startup and immersive paths retain the same authenticated transport, version cache, recovery and native import. The card and §Chat surface available failure reasons. The separate model asset path and v11.532 save acknowledgement behavior are preserved.

## Verification and lineage

The v11.532 predecessor was rebuilt and verified at 10,996,103 bytes and SHA-256 `62ac2d3c524a6dd58d6ba4a826cadbb8455a0bd90d2fc2a03aa0c90643c6e382`. The independent `scripts/verify_v11_533_release.py` rebuild applied all 510 patches and checked 78 asset digests, JavaScript parsing, native history, the account-save chain, and the revision cache. The rebuilt index and Modeler pages are identical at 10,996,598 bytes and SHA-256 `f1073aab6e0f4619605e0fd3461ae0ba6b77631a04be4bc93b26400b842e50e6`.

`tests/project_account_open_v11_533.cjs` tests the composed source with a controlled account transport and native import boundary. It reproduces the predecessor rejecting the request without a download and misreporting success with a retained link. The corrected path passes across raw and prefixed IDs, a picker selection, failure diagnostics, declined confirmation, invalid ID and revision, concurrent workspace changes, native import rollback, and cache behavior for matching and mismatched revisions.

An isolated mobile Chromium run reproduced the exact My Projects error on the served v11.532 page and JavaScript. The Open action sent zero account download requests. The same controlled Chat transport with the sealed v11.533 candidate sent one request for the expected ID, imported the exact revision 5 document, populated all 13 editable mesh rows, and rendered the model in the native WebGL viewport. The card reported **Project opened.** Both runs captured zero browser page errors. This fixture did not access or mutate a live account.

Static packaging and JavaScript syntax checks passed. Each HTML entry is 682,469 bytes with SHA-256 `15bf0073fde5ce761dec89be2555a5be97d2913f25f163681667ed5de8c03e80`. The compact delivery module is 9,480,404 bytes with SHA-256 `be3e59d2fa32b4abb4c1f666690c9f3f8a530da5f5bee85397c6a72a2bcd35f6`. Compaction reported an existing duplicate object key in the world-build relay outside the account-open patch.

The private model fixture stays outside Git and the Hugging Face package. Publication follows the existing GitHub workflow with a separate `DEPLOY_REQUEST.json` commit after the source commit. Verify exact hosted files and a fresh signed-in account load before marking the owner-visible issue resolved. No account writes are required for that acceptance check.
