# Saved project files and revision archives

**Deployment status (2026-10-27):** the implementation described here is in deployed source `f925e2012ed7ece820e3272700bc6619846c2085`. Runtime/model acceptance remains scoped by [the current checkpoint](entries/2026-10-25_EDITOR_PROJECT_COMPLETION.md); dated preparation claims below are historical.

A generated source project is one session/account-owned artifact with a stored
file tree. Its ZIP is built from that saved revision, including every file's
exact content, relative path and checksum. Historical revision URLs keep their
original snapshots when the current project changes.

Continuing a selected project now treats returned, explicitly named complete
files as updates or additions to its existing tree. An exact matching path is
replaced in its original position; a new safe path is appended. Every omitted
file remains unchanged. Omission never authorizes deletion, a rename, a new
project or a provider operation. Removal needs a separately supported explicit
operation. The complete merged tree is checked for portable paths, Unicode/case
and file/directory collisions, file count and source-byte limits before commit.

Multi-file edits require actual filename metadata in a fence header or the
existing safe leading filename-comment protocol. Parser-generated `code.html`
or `file-2.txt` fallback names cannot silently select a multi-file destination.
For compatibility, a project containing exactly one source file can receive one
unlabelled file of the same language; its unique authoritative path is retained.

Station verifies the owner/thread, target artifact, positive current base
revision and source hash. It also hashes the actual current stored files before
merging, so stale metadata cannot bless tampered source. A stale/ambiguous/unsafe
candidate creates no revision. A successful merge creates the same artifact's
next immutable snapshot, parent revision/hash and updated downloadable ZIP.

Ordinary edits of that verified local artifact take precedence over broad
GitHub coding-intent inference. Explicit GitHub/repository requests keep their
provider owner and existing permissions. No local revision grants repository
write access or changes account identity.

The shared pure merge helper is also usable by the source-validation owner:
language, dependency and application checks must inspect the composed project,
while checks for new placeholders inspect the returned changes. Storage merging
alone would not fix a one-JavaScript-file edit incorrectly rejected for omitting
unchanged HTML. The model policy therefore requests complete changed/new files
at their original paths and explains that omissions are preserved.

Verification uses the real Station HTTP admission/worker/sync/download path and
the real coding engine with controlled model drafts: four files at revision1,
one changed named JavaScript file, the same four files at revision2, unchanged
revision1 ZIP bytes, per-file/ZIP hashes and a foreign-session404. This proves
project continuity and the inference protocol, not actual learned model quality,
compiler execution, browser behavior or signed-in provider acceptance.

For an ordinary edit naming exact stored paths (or an unambiguous basename),
both models receive the complete selected files and a truthful path index
bounded to4KiB. The full canonical artifact remains unchanged in server state
for merge and project validation. Only an exact matching canonical assistant
history snapshot is projected; unrelated/raw/stale source is not rewritten.
Ambiguous names, repairs, imported raw code and explicit whole-project/all-files
requests keep full-source handling and its finite context/output limits. The
output floor therefore reserves the selected complete file set instead of
requiring every unrelated project file to be emitted again. An unselected
file's contents are not claimed as inspected by the model.

Eight selected-context regressions include both real engine message builders
with a controlled model and2000 stored files, while validating the resulting
full2000-file canonical tree. This is bounded context/storage evidence, not a
model-generated Android app or proof of autonomous large-project competence.
