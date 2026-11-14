# §C Aiven Valkey egress and code-finalization optimization

This patch targets the **actual Hugging Face Space** at `kamiloki/Swyrlz`,
not the alternate repository-side `api/durable_redis_store.py` code.

## Problem reproduced in live source

- The Chat browser polls `/api/lalm_station/sync` approximately every
  **2 seconds** when visible.
- Before this patch, `station._refresh_account_chat` decoded the entire
  account's encrypted chat history about every **10 seconds** while idle.
- `account_chat_store._decode_native_chat` fetches each encrypted chunk
  separately, up to 640 KB per chunk. This can multiply Redis traffic when
  generated code or imported history makes account snapshots large.
- The UI also received the entire conversation-thread projection on every
  poll, even with no state change.
- Saved code drafts exposed the `file=index.html project=...` fence
  metadata inside the source pane. The metadata is **deliberate and required**
  by the project-file protocol; it is not malformed HTML.
- An HTML document ending in `</html>` with a missing final Markdown
  code fence could trigger more generation/repair work even when its file
  body was finished. Output-length receipt must remain truthful.

## Exact changes

1. `account_chat_store.peek_chat_revision`: a bounded Redis EVAL reads
   the canonical CAS envelope **server-side** and returns only its integer
   revision over the TLS connection, instead of transferring and decrypting
   the entire account history on every idle check. It uses the original
   account key and has no extra mutable revision index.
2. `station._refresh_account_chat`: skip full history retrieval when the
   remote and local revisions match. Force refresh still loads complete
   history. Missing, corrupt or regressed revisions fail closed.
3. `station.sync` and the browser client: conditional `ifRevision`
   responses transmit only contract, revision and `unchanged:true`
   while the session has **no active generation**. Preserve full state on
   initial hydration, focus, account changes, writes and generation activity.
   The browser invalidates its hydration flag after account-epoch changes.
4. `qwen_coder_engine._swrlz_close_complete_html_fence`: only finish
   a single, structurally complete HTML document when the existing
   project-file parser accepts it. Preserve the opening fence's filename
   and project metadata exactly. Incomplete scripts, absent body closure,
   partial HTML and multi-file drafts remain incomplete.
5. `programming_telemetry.completion_validation`: retain the provider's
   actual `finishReason="length"` in the receipt. Permit
   source-contract acceptance only when a full parsed artifact exists **and**
   all deterministic source checks pass. This is not a claim that JavaScript
   executed successfully.
6. `chat/§wyrlz/index.html`: visually separate the file label from the
   provisional source pane while leaving the underlying draft unchanged,
   scroll-follow intact, and resume metadata preserved.

## Safety and tests

- The GitHub test workflow exercises finished/missing fences, malformed
  HTML, rejected source contracts, truthful output-length telemetry and
  fail-closed revision responses.
- A guarded live-source patcher compiles every Python file, checks the
  active browser script using `node --check`, simulates account Redis
  revision changes including forced refresh and rollback, and snapshots
  the exact original files before publishing.
- Hugging Face publication is source-SHA pinned to avoid overwriting
  concurrent updates, and has a production runtime probe with automatic
  rollback on acceptance failure.
- Only five Space source files change; no Redis namespace, encryption
  key, user records, accounts, or model weights are changed.
- Runtime smoke tests and actual user phone acceptance remain separate
  from deterministic code tests. A lower exact Upstash byte count cannot
  be proven without the old provider's usage metrics.

## Expected impact

For an unchanged chat projection, a periodic full encrypted snapshot
GET is replaced by one tiny integer response. For an unchanged idle
browser poll, a full JSON state response is replaced by a bounded
`unchanged:true` marker. Actual bandwidth savings depend on history
size, tab count, active-generation duration, forced refreshes and write
frequency.

The browser retains its responsiveness, and no optimization is allowed
to silently discard a valid generation or change an account's ownership.
