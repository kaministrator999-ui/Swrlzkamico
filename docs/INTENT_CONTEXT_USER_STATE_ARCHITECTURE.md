# §wyrlz Intent, Context, User State, and Durable Generation Architecture

Status: design + implementation contract
Branch baseline: dev @ de5893c791bec594bef1475e3af290edbf1d45cb (R39 hot v34)

## 1. Architectural finding

Intent-preserving contextual repair is a semantic reasoning capability. It does **not** belong in the tokenizer.

Current R39 flow is:

`chat request -> normalize payload -> render_chat_prompt(payload) -> BPE tokenize -> prefill -> decode -> stream events`

The tokenizer only converts the rendered text into model tokens. It has no reliable access to conversational intent, STT provenance, candidate alternatives, or repair confidence. Therefore corrections such as `death -> depth` must be decided before or during semantic reasoning, while preserving the original received text as evidence.

The correct boundary is:

`received message + recent context + provenance -> interpretation envelope -> prompt rendering / reasoning controller -> tokenizer`

The original user text remains immutable in the message record.

## 2. Contextual repair contract

Every received user message may carry an interpretation envelope:

```json
{
  "receivedText": "Must mean I have lots of death to be able to do that.",
  "provenance": {
    "modality": "speech",
    "provider": null,
    "overallConfidence": null,
    "uncertainSpans": [],
    "candidateAlternatives": []
  },
  "interpretation": {
    "repair": {
      "status": "PROBABLE",
      "originalSpan": "death",
      "candidate": "depth",
      "confidence": 0.94,
      "basis": ["recent-semantic-trajectory", "minimal-edit", "higher-context-fit"]
    },
    "interpretedMeaning": "The ability to name many animals implies broad/deep knowledge.",
    "ambiguity": []
  }
}
```

Rules:

- `receivedText` is the receipt and is never overwritten.
- Literal grammatical validity does not prove semantic fit.
- Prefer the smallest plausible repair that materially increases coherence.
- High confidence permits reasoning with the repaired interpretation while making the repair visible when useful.
- Medium confidence preserves both readings and avoids silently changing meaning.
- Low confidence asks or leaves the ambiguity unresolved.
- Provenance is evidence, not authority. A low-confidence STT span raises repair probability; context determines the repair.
- Typed input uses the same semantic-repair machinery.

## 3. Why this fits the current R39 architecture

### Tokenizer
No tokenizer mutation is required. Changing BPE behavior would destroy the distinction between `what was received` and `what was inferred` and would contaminate all downstream receipts.

### Prompt renderer
`render_chat_prompt()` is the correct serialization boundary. Future prompt rendering may include a compact, non-user-visible interpretation block before the user turn, for example:

```text
<|im_start|>system
INPUT_EVIDENCE modality=speech repair=PROBABLE original="death" candidate="depth" confidence=0.94
Use the probable interpretation while preserving the user's received text. Mention the correction only if useful.
<|im_end|>
```

The literal user turn must still contain the exact received text.

### v34 reasoning controller
v34 already profiles response scale, creative/technical intent, freshness sensitivity, complexity, and adaptive sampling. Contextual repair should compose with this controller as a separate interpretation phase rather than being folded into response-length heuristics.

Recommended order:

`message normalization -> provenance normalization -> contextual repair evidence -> intent profile -> reasoning contract -> adaptive generation -> prompt render -> tokenize`

## 4. General repair policy to teach now

The model should learn these distinctions:

- `death -> depth` after a conversation about knowledge/ability: probable repair.
- `I saw a dear in the woods -> deer`: probable repair.
- `I need a brake from work`: likely `break`, but make repair visible if consequential.
- `I want to break the car`: do not rewrite to `brake`; literal meaning is plausible.
- `that shit was sick`: slang; do not “correct” it.
- missing words where one insertion uniquely restores the sentence: infer cautiously.
- ambiguous pronouns with two live referents: do not silently resolve.
- coined terms whose meaning is established by the conversation: preserve them.

Training targets should reward **intent recovery + receipt preservation**, not normalized spelling.

## 5. Training data representation

Training/evaluation records should contain:

- `history`
- `received_text`
- optional `provenance`
- `literal_validity`
- `repair_candidates`
- `gold_interpretation`
- `repair_status`: `NONE | PROBABLE | AMBIGUOUS | CLARIFY`
- `confidence_band`: `HIGH | MEDIUM | LOW`
- `expected_user_visible_behavior`
- `anti_target` describing the failure mode to avoid

Do not train only positive repair examples. Include strong negatives where the unusual word is intentional.

## 6. Presentation intent / copyable blocks

Presentation is separate from semantic intent. The reasoning controller should emit or infer a presentation contract:

- `PROSE`: ordinary answer.
- `COPYABLE_BLOCK`: lyrics, prompts, scripts, commands, templates, configuration, structured snippets, or any artifact the user is likely to paste elsewhere.
- `CODE`: source code with language tag.
- `MIXED`: explanation plus one or more copyable blocks.

For songs/lyrics specifically, default to a fenced block when the request is to *produce the song itself*. Commentary can remain outside the block.

The UI already renders fenced blocks. The UI enhancement required next is a per-`pre` copy affordance that copies only the block contents, in addition to the existing whole-message copy action.

## 7. User identity and account model

Google identity is an authentication provider, not the storage key itself.

Canonical server identity:

```text
user_id = stable server-generated UUID
identity_provider = google
provider_subject = verified Google `sub`
```

Never key durable records by display name or mutable email. Email is profile metadata. The verified Google `sub` is an external identity mapping to the internal `user_id`.

Required tables/collections conceptually:

- `users(user_id, created_at, updated_at)`
- `user_identities(user_id, provider, provider_subject, email, email_verified, claims_updated_at)`
- `user_profiles(user_id, display_name, preferences_json, model_preferences_json, ui_preferences_json, version)`
- `threads(thread_id, user_id, title, created_at, updated_at, archived_at)`
- `messages(message_id, thread_id, user_id, role, received_text, provenance_json, interpretation_json, committed_text, state, created_at, updated_at)`
- `generation_jobs(request_id, user_id, thread_id, assistant_message_id, state, last_seq, created_at, updated_at, completed_at)`
- `generation_events(request_id, seq, event_type, payload_json, created_at)`

Strong uniqueness constraints:

- `(provider, provider_subject)` unique
- `(thread_id, user_id)` ownership enforced
- `(request_id, seq)` unique
- request IDs idempotent per user

## 8. Login flow

The existing GIS test proves browser credential receipt only. Production flow must be:

`GIS credential -> POST /api/auth/google -> server verifies signature + issuer + audience + exp -> map Google sub to internal user_id -> issue HttpOnly Secure SameSite session -> GET /api/me -> load user state`

Do not trust browser-decoded JWT claims for authorization.

The Google Web Client ID should be deployment configuration, not a user-entered production setting.

## 9. Durable server-owned generation

Current detached R39 jobs are useful acceleration but instance-local. The browser must become a subscriber, not the owner.

Target contract:

1. `POST /api/chat/jobs` creates/idempotently returns a generation job.
2. Server commits user message and empty assistant message before inference.
3. Durable execution owns generation until terminal state or explicit cancellation.
4. Every committed stream event is journaled with monotonically increasing `seq`.
5. `GET /api/chat/jobs/{request_id}/events?after=<seq>` replays missed events and tails new events.
6. Browser navigation, logout, refresh, visibility changes, or transport loss **do not cancel generation**.
7. Explicit Stop sends cancellation for that request.
8. Re-login restores threads, finds nonterminal jobs, replays from each message's stored `last_seq`, and continues live.

A local in-memory `_JOBS` cache may remain as a hot-worker optimization. It must never be the durable authority.

## 10. Vercel constraint

The current `/tmp` state is ephemeral and instance-local, so it cannot be the authoritative user/chat/job store. Durable generation should use Vercel Workflow (or an equivalent durable executor) and a durable data store. The storage adapter must remain abstract until the project's actual connected durable store is confirmed. Private Vercel Blob is viable for append/checkpoint documents but is not automatically a relational database; a transactional database/Redis-compatible store may be preferable for concurrent message/event indexing.

Do not implement production persistence by silently writing user state to `/tmp`.

## 11. Minimal implementation ladder

### M1 — safe now
- add interpretation/provenance schema
- add contextual-repair policy to next R39 hot controller
- add training/evaluation corpus
- add presentation intent policy
- add per-code-block copy UI
- preserve exact received text

### M2 — authentication boundary
- server-verify GIS ID token
- map provider subject -> internal user
- issue secure server session
- expose `/api/me`

### M3 — durable account/chat state
- choose/confirm durable storage provider
- implement user/thread/message repositories
- migrate browser-local thread state after explicit user opt-in/sign-in
- browser becomes a cache, not authority

### M4 — durable generation
- create durable workflow/job owner
- journal events
- reconnect/replay endpoint
- restore active jobs across login/navigation/runtime restarts

## 12. Evaluation gates

Contextual repair:
- high-confidence semantic anomaly repaired correctly >= target threshold
- intentional unusual/slang tokens preserved
- exact received text unchanged in persisted message record
- no silent repair when two candidates remain plausible

Presentation:
- song/lyrics/template/code requests produce copyable blocks
- ordinary conversation does not get wrapped gratuitously

Account isolation:
- user A cannot enumerate/read/update user B's threads or jobs
- logout removes session access but does not cancel owned active jobs
- relogin restores owned threads and in-progress job replay

Durability:
- disconnect stream mid-generation -> generation reaches terminal state
- reconnect with `afterSeq=N` receives exactly N+1 onward, no duplicate committed text
- process/instance replacement does not lose committed user message, assistant deltas, or terminal state

## 13. Non-goals

- tokenizer autocorrection
- rewriting stored user text
- treating STT as inherently less trustworthy than typed input
- browser-local JWT decoding as authorization
- `/tmp` as durable account storage
- navigation/visibility loss as cancellation
