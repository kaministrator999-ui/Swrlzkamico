# §E v11.493 — Sorting Hat ZIP detection and saved-project load diagnosis

User acceptance evidence:
- On Android, Update Model displayed `Unexpected token 'P', "PK"... is not valid JSON` after a ZIP file selection. This is a ZIP member being passed to a JSON parser on an older code path or without a proper archive discriminator.
- My Projects showed **The Sorting Hat · Revision 6** but clicking Open project returned `Could not open project. Your active scene was preserved.` The account record's existence establishes a new revision; this generic error does not identify whether download, decode, validation, scene load, or a cancelled dirty-state prompt caused the failure.

v11.493 retains v11.492's bounded archive decompressor and treats the ZIP binary signature as authoritative even if Android renames the file or hides its extension. A malformed file with .zip extension is reported explicitly. It does not accept multiple model members.

Cloud project opening retries **only read-only** `cloud.load` transport failures (at most three). It checks the returned project ID and leaves the existing native scene recovery path intact. A rejected import or account request records the exact error and displays it on the selected My Projects card, rather than a misleading generic failure. A cancelled unsaved-changes prompt is reported as a cancellation.

This release deliberately does **not** overwrite, delete, repair, roll back, or attempt to access the user's actual authenticated Sorting Hat revision 6. Physical-device acceptance requires reproducing Open and reporting the new specific error. Do not label the saved account bytes as corrupt without validation.

Tests: `tests/project_load_diagnostics_v11_493.cjs` (ZIP magic, ordinary JSON, malformed ZIP, transient cloud load, wrong ID, error reset); preserve regressions v11.491 and v11.492, full build source SHA, current-version static asset receipts and HF public responses.
