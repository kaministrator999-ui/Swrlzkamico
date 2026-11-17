# §E v11.492 — ZIP model update support

Owner request: the My Projects **Update Model** action must accept a ZIP directly.

This is an additive importer for v11.491, **not** a project import/recreation operation. A selected saved project is still identified by its immutable project ID, validated model part ID, current account revision and compare-and-swap save. The existing rolling project history remains in place.

The browser reads a single native .swyrl.json member from the archive (or one .json if no .swyrl.json exists). ZIP is decompressed locally using the platform's deflate-raw stream; it is not uploaded to §C or GitHub. The resulting parsed native model is passed to the existing rigorous sourceModel and supported checks. Archive files containing multiple candidate model JSONs are rejected rather than guessing.

Limits: 32 MiB archive / extracted JSON, at most 256 entries, CRC32 and exact decompressed-length checks; reject encrypted, ZIP64, multi-disk, unsafe paths, unsupported compression, missing/corrupt metadata and ambiguous model files.

Relevant regressions: tests/zip_model_update_v11_492.cjs (raw deflate, stored ZIP, single model amid other files, CRC failure, size claims, path traversal, multiple models and malformed archive); tests/cloud_model_update_recovery_v11_491.cjs (safe account read retry without replaying ambiguous writes).

Release process: full 469-patch source build, exact SHA seal and browser artifact MIME/size checks, then Hugging Face deploy to kamiloki/swrlz-forge-moba. Mobile device acceptance remains the user's test.
