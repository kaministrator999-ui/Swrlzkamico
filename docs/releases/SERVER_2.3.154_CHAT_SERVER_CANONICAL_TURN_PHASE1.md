# Server 2.3.154 — Server-canonical Chat turn phase 1

**Overall Server authority:** runtime `2.3.154`  
**Web Chat:** runtime `1.5.27`  
**Web Frontend:** runtime `1.0.4`  
**Stream Contract:** `V2` unchanged  
**Google Account:** unchanged  
**LALM:** unchanged

## Purpose

Align Web Chat with the SERVER APK ownership model and the Mask / Human / Brain contract. The browser presents and relays factual turn data; authenticated durable user/assistant messages and the prior conversation history sent toward the LALM are owned by the server.

## Stable server implementation

- `api/chat_turn_state.py` owns account-scoped canonical Chat turn commits in the existing private Chat-state Blob store.
- Authenticated user messages are committed before generation begins.
- The server reconstructs prior LALM history from the authenticated canonical thread and excludes the just-committed current request because the prompt travels separately.
- Browser-supplied history remains only a signed-out compatibility input. For an authenticated canonical turn it is replaced before the existing Chat route normalizes/forwards the request.
- Assistant DELTA/RESET output is observed without changing the V2 stream and committed at COMPLETED/CANCELLED/FAILED terminal state.
- Durable user/history failures fail closed before generation.
- Structured private events correlate the same account scope, thread ID, message IDs, and request ID across:
  - `CHAT_MESSAGE_ACCEPTED`
  - `CHAT_MESSAGE_COMMITTED`
  - `CHAT_HISTORY_CANONICALIZED`
  - `CHAT_GENERATION_STARTED`
  - `CHAT_GENERATION_TERMINAL`

## Main lineage

- initial canonical turn store: `b9856ae567ad8ecbbb434767548f95c750fe7af9`
- initial Chat transaction/lifecycle integration: `3bb8b9e54a7166e513f20c1083a26da6a5934758`
- canonical server-history reader: `73c20055d9de35bd9d61c6add06ff367eb1e4c4f`
- signed-in request history replacement + lifecycle receipt: `4c40e6338bbbe36bb7a9d139597f41c174851cd7`

## Runtime companion work

Runtime manifest `95` is already live from the `runtime` branch:

- outgoing stream requests receive the exact browser-created USER/ASSISTANT message IDs and timestamps so server and visible UI refer to the same turn records;
- `chat_runtime_loader_v3.js` derives child asset revision from its manifest-versioned loader URL instead of hardcoding `93`;
- `chat_stream_incremental.js` fixes the waiting-state temporal-dead-zone crash;
- whole-state browser synchronization remains temporarily enabled as compatibility transport until this stable server transaction is deployed and verified.

Runtime lineage:

- turn-ID transport: `ddc5a5272860b4939ed8ad8b4e8dd1ac06e31b47`
- manifest-derived asset revision: `b88ddf6b81ae75d361222cad4d236392e4ab91b3`
- incremental renderer repair: `16891c6f138cc68ac2737720fcc6c972e92d86bb`
- manifest 95: `00667fe2899b1b938a0eb0d0566a2b9776ec2e3e`
- runtime release record update: `c856e05446c4dad017f569e8da7ff4dfcbc23f81`

## Camera/context audit

`runtime/web/chat_context_camera.js` remains a client transport/display diagnostic observer. It captures the winning generation branch and raw-vs-display information in browser message metadata.

`runtime/web/chat_context_canonical.js` currently constructs a browser-side history relay. Once this stable phase is deployed, that relay is no longer authoritative for authenticated turns because the stable server replaces it with history rebuilt from private account state. A later runtime phase can therefore simplify/retire browser history ownership without risking conversation loss.

## Deployment state

- Runtime Web Chat/frontend companion changes: LIVE; no Vercel deployment required.
- Stable Python transaction/history changes: staged on `main`; NOT live until a production deployment of a main commit containing the lineage above.
- Git deployment is disabled in `vercel.json`; no deployment was triggered by these source commits.

## Verification state

Verified now:

- runtime manifest 95 is live on the canonical production origin;
- the live loader derives revision 95 instead of pinning 93;
- the live incremental renderer contains the TDZ repair;
- the live account-state companion attaches canonical turn IDs;
- runtime authorities read Server 2.3.154 / Web Chat 1.5.27 / Web Frontend 1.0.4.

Pending production stable deployment and signed-in test:

- USER commit occurs before generation;
- server-canonical history replaces browser history;
- assistant terminal commit is durable;
- lifecycle logs correlate one request from accepted through terminal state;
- cross-browser state reflects the canonical server records.

## Next phase after production acceptance

Retire remaining whole-state browser message authority. Browser localStorage becomes disposable cache/presentation only; server APIs own authenticated message mutations, deletion/tombstones, and canonical hydration.

```text
MASK / browser
    -> relay text + factual IDs
HUMAN / server
    -> authenticate
    -> commit USER
    -> build canonical prior history
    -> invoke/transport generation
    -> commit ASSISTANT terminal
BRAIN / LALM
    -> interpret/reason/generate
MASK
    -> render server truth
```
