# Server Runtime 2.3.131 / LALM Engine 2.1.42 — Social Semantic Acceptance

## Problem
A live acceptance test on LALM Engine 2.1.41 showed a simple `Hey 👋` turn producing `Good morning!` while the same visible answer leaked `(Context: 6:16 PM, evening)`. This proved that the correct approved temporal anchor reached the model, but prompt constraints alone were insufficient: decoding could contradict the supplied daypart and relay internal temporal scaffolding.

The same turn also demonstrated why short social responses should satisfy final-copy semantics before visible commit rather than stream an invalid prefix and attempt repair afterward.

## Change
`runtime_hot/r39_engine_v32.py` adds a LALM-side semantic acceptance gate for exact social greetings.

- Exact greeting candidates are buffered privately before any assistant DELTA is committed.
- Candidate text is rejected if it contradicts the approved request-time daypart.
- Internal temporal/controller scaffolding such as `(Context: ...)`, `localTime=`, `daypart=`, or policy labels is rejected before commit.
- Service-desk closers such as `anything else I can help with`, `let me know if`, `here whenever you need`, and `helping hand` are rejected for simple greeting turns.
- A valid model candidate is committed unchanged.
- An invalid candidate is never shown; the controller emits a deterministic short response derived only from the approved daypart, or a neutral `Hey 👋` when no approved daypart exists.
- STATUS telemetry records when the semantic guard rejected a private candidate so the correction is observable rather than silently masquerading as raw model success.

Non-social generation is unchanged and continues through the v31/v30 lineage.

## Invariant
For a simple social greeting, visible assistant text must never contradict approved request-time temporal facts or expose internal temporal/context scaffolding. Short social output is accepted before visible commit.

## Versions
- Server Runtime: 2.3.131
- LALM Engine: 2.1.42
- LALM Revision: `2.1.42-hot-social-semantic-acceptance-v32`
