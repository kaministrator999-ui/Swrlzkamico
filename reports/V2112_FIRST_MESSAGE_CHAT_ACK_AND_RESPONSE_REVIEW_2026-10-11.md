# v211.2 — First user message immediately creates visible native Chat thread

Date: 2026-10-11. Existing Hugging Face Space: `kamiloki/Swyrlz`.

## Owner-identified behavior

With v211.1, newest-first Chats sorting, Versions footer and scrollable mobile sidebar began working. However, the owner observed that a new native thread did not become visible in the sidebar until the model completed inference. Desired behavior is **CLIENT → SERVER durable first-message commit → HTTP 202 accepted → visible selectable thread → independent AI inference**.

The owner also uploaded a private account Chat export and requested review of recent human/AI exchanges. That export was analyzed in a private working environment and was **not** committed or attached to this report. Do not log user transcripts, private profile contents, names of third parties or OAuth tokens.

## Verified cause and change

`hf_space/station.py:/api/lalm_station/send` already appends the first user message, commits the Google-owner encrypted Redis CAS snapshot, and only then returns HTTP 202. The inference work is separate. The clean-room Chat client displayed the submitted user bubble optimistically in the active view but held its thread in `pendingDraftThread`, which `renderThreads` did not include until a later reconciliation.

- Source based on published v211.1 `fix/native-chat-mobile-sidebar-access-v2111@2284fccb589625449fc83405e170fcd428864834`, preserving full mobile sidebar/Versions, newest-first native Chats/export, v211 GitHub model-guided progress and prior durable encrypted native storage.
- Isolated released [draft PR #108](https://github.com/kaministrator999-ui/Swrlzkamico/pull/108), `fix/native-chat-first-send-ack-v2112@f81ffd43647a8796feb47ebd6c3c0ad80f5df545`.
- After receiving *matching successful* server 202 ACK, promote the already-persisted pending thread into the browser's visible chat list, render immediately, and initiate nonblocking authoritative sync. Do not wait for model streaming or inference completion. A missing/rejected ACK does not create a phantom confirmed saved thread, and repeated promotion cannot duplicate the list entry.
- Existing retry/draft restoration, CAS, Redis snapshots, Google owner authentication and model behavior remain unchanged. Chat local source/camera/meta version **1.1.07→1.1.08**.
- A queued/slow/failed model response must not remove a successfully saved first user message from the accessible thread list.

## Validation on exact published source

- [Google/account CI #38174752781](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174752781): **SUCCESS**, including Node ACK-gated promotion before stream test and Station endpoint synthetic `/send` 202 → durable first user message → immediate `/sync` during *nonterminal* generation.
- [HF offline #38174756719](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174756719): **SUCCESS**.
- [Mobile integrity #38174756722](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174756722): **SUCCESS**.
- One guarded canonical [HF production workflow #38174894177](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174894177): terminal **SUCCESS**. Source pin, isolated package, R39 compatibility, 700M inference smoke, previous Space snapshot and publish checks passed.
- New Space revision `a583a03912723c9f24200a14de0fcbd491b409f2`, rollback previous revision `6c06b10f6328da082ead77a77c1d1b690495bb17`.
- Immutable release checkpoint artifact `hf-release-checkpoint` ID `11715526895`: `knownGood=false`, `verificationState=DEPLOYED_UNVERIFIED`. Publication is real; signed-in Android owner first-message visibility remains behavioral acceptance pending.

## Runtime module authority

Atomic `runtime@4266cd0d9054efa555bcd4c252db765422616ff3`, reread matching:
| Registered module | Before | After |
|---|---|---|
| Repository Work | 1.0.152 | **1.0.153** |
| Server Runtime | 2.3.364 | **2.3.365** |
| Web Chat | 1.5.103 | **1.5.104** |

LALM Engine 2.1.189 and Google Account 1.0.14 unchanged, since their runtime source/identity contracts were not modified. Other registered modules including §E, Stream Contract, Runtime Manifest and Online Research unchanged.

## Separate private export response-quality findings (no raw user data included)

A limited examination of a user-owned session export found **15 native threads**, with recent turns showing inconsistent 700M responses to simple social openings: one direct friendly conversational reply, other replies changing into identity documentation, fictional example dialogue or analysis of an invented third-party response. A greeting containing a temporal word triggered public search even without a public-facts request; the source `hf_space/online_tools.py:classify_online_request` uses `_FRESHNESS` matching `today` in general text. Earlier historical/account-count questions sometimes produced unsupported guesses or asked for an uploaded document despite existing account data, while more recent verified private-count paths responded with known 2,556 imported-thread counts.

**Scope and epistemics:** These are export-derived response defects and source-trigger evidence, **not** proof of a training failure or a complete explanation for all model generations. Source `hf_space/lfm2_700m_engine.py` already contains assistant/user identity provenance instructions, so persona-role failures require response-grounding and generation tests, not simply restating persona text. A future independent LALM-engine tier should: (a) distinguish social exchange from factual freshness/search, (b) anchor output to actual user role/turn rather than invented third parties, (c) avoid fabricated dialogue unless explicitly requested, (d) prefer authenticated private account/history tools over public results or guesses, and (e) test these on non-private synthetic samples across model routes. No automatic model inference, routing or research configuration changes were made in v211.2.

## Actual owner acceptance still required

Open the existing Space under signed-in Google account. Tap **+ New chat**, enter a small non-sensitive first message, send, and **open the drawer while the model still shows queued/generating**. The new chat should already appear (and be selectable) immediately after the verified server acceptance. Reload once inference finishes and confirm it persists. Repeat in a second browser with the same account. On an actual rejected send or disconnected network, draft recovery should not falsely claim a saved chat. If failure persists, provide safe status only—never secret account cookies or full private transcripts.

**Tier result:** SOURCE / CI VERIFIED; GUARDED PUBLICATION SUCCESS; REGISTRY READBACK VERIFIED; LIVE ANDROID NEW-THREAD TIMING ACCEPTANCE PENDING. Separate response-quality work identified but not modified.
