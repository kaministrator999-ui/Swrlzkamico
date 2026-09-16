# Server 2.3.185 / Web Chat 1.5.44

## Scope
Runtime-hot Chat continuity and Activity log interaction repair. No LALM, stream-contract, stable API, dependency, deployment, or restart change.

## Terminal recovery presentation
A locally observed empty stream failure is no longer immediately promoted to a user-visible error while canonical transcript recovery is still viable. The recovery layer first moves the assistant turn into a bounded `RECONNECTING` / `Checking canonical response…` state, suppresses the synthetic local error, and checks the exact request ID against `generation-transcript-v1`.

If the server reports terminal `COMPLETED` with non-empty assistant text, that exact text is restored and the turn becomes complete. If bounded recovery is exhausted, the original failure is restored and may then be shown to the user. Retrieval does not regenerate or alter LALM output.

## Activity log ownership
`chat_activity_expansion_state_v1.js` makes Activity log disclosure state user-owned. Opening or closing a message Activity log records `message.meta.activityExpanded`; subsequent message rerenders and stream updates restore that state rather than collapsing the disclosure. New streaming messages may still begin expanded until the user explicitly changes them.

## Runtime authorities
- Server Runtime: 2.3.185
- Web Chat: 1.5.44
- Runtime manifest: 109

## Verification target
1. Reproduce a local stream-close/canonical-complete race and confirm the transient red failure does not flash before canonical recovery.
2. Confirm the exact server response replaces the recovering state.
3. Open an Activity log while updates/renders continue and confirm it stays open until explicitly closed.
4. Confirm a genuinely unrecoverable request exposes its error only after bounded recovery is exhausted.
