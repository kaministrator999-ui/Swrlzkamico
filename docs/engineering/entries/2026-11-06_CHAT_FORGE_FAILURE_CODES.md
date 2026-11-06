# Bounded Forge failure diagnostics

Status: local implementation candidate on canonical Chat source
`6a561f95296930449d2cc43648d12d24347c8966` plus the character tools and stream
recovery followups. Live publication and inference/editor acceptance are pending.

A live native project request reached Forge planning and failed before batch
registration. The producer supplied a specific constant failure code, but Station
removed it while projecting the failure into saved statuses and stream events.
The user saw the generic failure sentence, preventing a focused repair.

Station now preserves codes only at its trusted Forge failure boundary. A code
must match `^FORGE_[A-Z0-9_]+$` and fit 96 characters. Invalid values and codes on
unrelated events are omitted. The same bounded field survives authenticated
snapshots, streamed failure status/terminal evidence and saved activity traces.
Chat shows that code in the inspectable activity log using literal text. This
does not expose arbitrary exceptions or alter operation authority, cancellation,
native receipts or model weights.

The regression suite checks a real authenticated Station request through stream,
snapshot and persisted trace, a known constant retained, and invalid/unrelated
values omitted. Controlled desktop/mobile Chromium checks the actual activity
renderer preserves the safe code and excludes invalid/unrelated values. Existing
vision/media and native tool checks remain passing. Verification: `PYTHONPATH=/tmp/swrlz-eof-review-deps python
hf_space/test_forge_chat_actions.py` (32 cases), the same environment with
`python hf_space/test_forge_station.py` (19 HTTP cases), and
`python hf_space/test_progress_timeline_v238.py` pass.
`node tests/test_forge_live_progress_browser.cjs` passes in actual controlled
Chromium desktop/mobile. The backend tests also raise a real HTTPException from
the trusted registration boundary: `FORGE_CONTEXT_CHANGED` survives, no batch
readiness/execution is claimed, and invalid/credential-like HTTP details remain
generic. Fixtures do not establish live inference success.

Documentation impact: Chat/Forge contract and this receipt. The next gate is the
coordinated live retry to identify and repair its actual failure using the
preserved code. No deployment was performed from this worktree.
