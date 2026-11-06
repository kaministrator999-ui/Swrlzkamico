# Accepted Station generation after stream EOF

Lifecycle: IMPLEMENTATION_VERIFIED / DOCUMENTATION_SYNCED candidate. Publication,
real inference and native editor/device acceptance remain pending their separate
coordinated retry; local browser fixtures are not live-editor acceptance.

## Baseline and scope

Canonical Chat base: `6a561f95296930449d2cc43648d12d24347c8966`, including the
latest CPU vision, accepted-image conversation, resync, watcher and cancellation
changes. Character tools were replayed onto that base as `6b22c0fb`; the original
`b07f219720503d112388e61a6216b9a51adec17e` receipt remains historical. This followup
retains acknowledged Station work when its event transport closes early.

The final candidate is replayed onto current accepted source
`9487a4f0d587da07aed77ecfe5474f7dd8aeeb61`; the vision v9–14 changes are retained.
The original commits mentioned above remain historical receipts. This entry's
older verification counts describe those earlier bounded checks; the final
handoff records the new source and the additional inspection/CAS regressions.

While exercising the embedded native workflow, the response stream ended after
an initial NDJSON record before the server generation was terminal. Browser send
cleanup hid Stop and released its local send guard. A failed snapshot request
could also end periodic reconciliation while the server continued waiting for
native receipts.

## Implementation

Stream EOF is a transport event. Chat retains the acknowledged request/thread,
continues reading authenticated snapshots, forwards only their existing scoped
native batch events and keeps Stop available until matching server terminal
evidence arrives. Recoverable snapshot failures schedule another bounded poll.
An exact persisted terminal assistant message reconciles a generation when the
active-generation projection is absent. Settled requests cannot be resurrected
by delayed nonterminal snapshots or late stream batches; unrelated history does
not displace current terminal evidence.

Account epochs and per-operation owner tokens guard send, sync and cancellation
cleanup. A previous account's response cannot block a new account's hydration,
open an old stream, release its composer or enable its pending Stop. Conversation
mutation retries also stop at an account change. The latest accepted-image
thread flow, image draft restoration and watcher/cancel behavior are retained.

Stop revokes the editor lease synchronously and requests server cancellation.
The client waits for actual terminal confirmation. A pre-admission Stop latches
across a pending lease acquisition; a late send acknowledgement receives a real
cancellation request. EOF, network errors and successful cancel requests never
manufacture completion, native receipts or success messages. The embedded send
button now honors its hidden state instead of remaining visible beneath Stop.

## Verification

- `node tests/test_forge_live_progress_browser.cjs`: actual controlled Chromium
  desktop 1440x900 and mobile 390x844, with a real NDJSON response ending before
  `FORGE_BATCH_READY`, two HTTP 503 snapshots, continued poll/batch forwarding,
  blocked competing submission, scoped native progress, immediate Stop revocation,
  held cancellation, unrelated-terminal rejection and terminal-only cleanup.
  Desktop also covers persisted terminal with no active projection, delayed
  nonterminal/ready events, stale account sync/cancel/ack ownership, pre-admission Stop and restoration
  of an unaccepted first-turn draft.
- `node tests/test_forge_chat_browser.cjs`: desktop, mobile and Android desktop
  site controlled browser scenarios pass.
- `node tests/test_chat_media_v1.mjs`, `node tests/test_forge_embed_frontend.mjs`,
  `node tests/test_forge_popup_mobile_recovery.mjs` (9 checks) and
  `node tests/test_chat_keyboard_ime_v292.mjs`: pass.
- `python tests/test_chat_vision_v1.py`: latest local vision/auth/queue/cancel,
  returning watcher and JSON image handoff checks pass with mocked inference.
- Mesh/planner/embed/studio backend suites: 19 + 32 + 25 + 7 = 83 cases pass.
  The first three use isolated `/tmp/swrlz-eof-review-deps` for the environment's
  missing `requests` dependency; no runtime dependency or model weight changed.

Documentation impact: Chat/Forge contract and this checkpoint receipt. No
protocol, paid service, model-weight, backend security or deployment change is
claimed by this recovery checkpoint. Documentation gate: PASS. Canonical source
staging and immutable Git source/tree receipts are recorded in the handoff after
commit. Promotion, the actual native model retry and device acceptance are the
next gates; no additional user permission is needed for this local verification.
