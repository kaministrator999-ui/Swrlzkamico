# Saved project revision downloads

A successful project edit can be stored as a short assistant message with its
artifact ID and committed revision, while the project files remain in the
artifact's revision snapshots. Chat now renders a compact saved-project card
for such a message, showing the revision and saved file count with an actual
ZIP download action. This includes projects containing only one source file.
Large project revisions do not reprint unchanged source files to expose the
download.

The action uses the existing session-owned archive endpoint and captures the
thread, artifact and displayed revision when rendered. A later revision or
navigation cannot retarget it. The original source message keeps its historical
revision download; the new edit message downloads the complete new revision,
including preserved files. Missing historical snapshots or inconsistent
artifact metadata do not create a download link. Server ownership and revision
validation remain authoritative, using the existing same-origin session cookie.

A failed or non-ZIP response does not create a download and leaves the action
available for retry. Source archives do not establish that a project builds or
runs correctly; the manifest and separate execution evidence retain that
distinction.

The real Chromium download regression renders the production message renderer
and checks changed-source revision2 bytes, unchanged revision1 bytes, captured
identity after navigation, denied response/retry, a one-file ZIP and a compact
2000-file revision card. This is UI/archive transport evidence with synthetic
saved-project fixtures, not model competence or deployed acceptance.
