# Project filename metadata and bounded browser downloads

**Deployment status (2026-10-27):** the implementation described here is in deployed source `f925e2012ed7ece820e3272700bc6619846c2085`. Runtime/model acceptance remains scoped by [the current checkpoint](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md); dated preparation claims below are historical.

This repair belongs to the editor/project completion checkpoint. It changes file
identity extraction and download capacity, not generated code or execution truth.

Explicit `file=`, `path=` or `filename=` fence attributes remain authoritative.
When none is present, the source parser can read an unambiguous filename from
the first nonempty line of a source fence: an HTML filename comment, a compatible
language's `//`, `/* */` or `#` filename comment, or a Markdown filename heading.
Examples are `<!-- index.html -->`, `/* styles.css */`, `// editor.js` and
`# README.md`. Names containing spaces need one pair of quotes or backticks.
Ordinary prose, URLs, interpreter shebangs, later comments and arbitrary quoted phrases are ignored. Metadata trimming uses the same explicit whitespace set in Python and JavaScript, including a leading UTF-8 BOM; source bytes are never trimmed.
A whole filename with an extension, or a recognized extensionless source name,
is required; this is not a heuristic that searches an entire response for paths.

The comment/heading and every source byte stay intact, including blank lines and
CRLF. The metadata does not grant filesystem or GitHub permission. Existing
portable path, traversal, reserved-name, Unicode/case collision, file/directory
collision, file-count and byte limits apply to every inferred name before an
artifact can be persisted or downloaded. Intended unsafe names reject rather
than being normalized into a different source identity. Conflicting explicit
header attributes do not fall back to a comment. The browser follows the same
metadata rule and rejects unsafe display names; the server remains authoritative
for whole-project collisions and owned revision downloads.

The shared `leading_file_metadata_matches_path` helper validates the leading
label and the authoritative stored path, then accepts only an exact full-path
match or a safe single basename matching that path. Completeness and GitHub
proposal checks use it to avoid mistaking a legitimate first filename label such
as `// todo.js` for a TODO implementation placeholder. Only that first matching
metadata comment is exempt; later TODO comments, differently named labels and
unsafe paths retain the ordinary rejection behavior. No source bytes are removed.

The browser archive limit is now40MiB, covering the backend's32MiB source bound
plus ZIP/manifest overhead for up to2048 files. It still checks the response type,
HTTP result, declared byte count, actual Blob size and a safe download name.
Only a saved session-owned artifact/revision supplies a ZIP URL. The change does
not fabricate a download for streamed or rejected source.

Verification:24 archive/Station unit tests pass, including filename comments,
quoted paths, explicit-header authority, byte-preserving ZIPs, unsafe metadata,
collisions and a2000-file metadata-to-ZIP round trip. The real Chromium download
suite passes for the same metadata, existing ownership/revision/error behavior,
a backend-built text-source ZIP above the former8MiB limit, and a40MiB+1 declared
size rejected without allocating that body. The large browser fixture uses
bounded code-viewer overflow so its intentionally large text does not expand the
test page to millions of pixels.

The observed Qwen7B editor drafts remain failed model evidence. Recognizing their
filename comments does not repair their script loading, nonexistent APIs,
selection or transformation behavior, and does not make their README claims true.

The download browser suite also runs the actual production message-rendering
closure on complete HTML/CSS/JavaScript/Markdown fences and an unfinished HTML
stream. This catches failures between source parsing and code-block creation,
including the reviewed initialization-order regression that helper-only tests
missed. Code remains inert text; the original full response remains available
separately from the renderer's existing terminal-newline display convention.
