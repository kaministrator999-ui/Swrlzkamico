# v206 — Private cross-thread conversation search by topic and local date/time

Date: 2026-10-11 (America/Chicago).

## Evidence and exact release state
- Source baseline: v205 `feature/chatgpt-account-memory-v205` at `362ac0746d3ca7f7a07a1c1edeed1cbd053a6bfa`.
- Source candidate: `feature/private-history-search-v206` at `e8bc07e5ff80ced6c0a02ce454b7504efd294f80`. Review: [draft PR #96](https://github.com/kaministrator999-ui/Swrlzkamico/pull/96), base v205.
- Google account/original importer/private recall CI: [#38116027007](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38116027007) — **SUCCESS**.
- HF offline source/model/Station CI: [#38116027006](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38116027006) — **SUCCESS**.
- Guarded existing HF Space deployment [#38116093896](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38116093896) — **SUCCESS**.
- Published Space: `kamiloki/Swyrlz`, revision `e170d1129519331b48494a967c8238f048f25b44`.
- Rollback revision: `7c8ea60e52a511eb1a08619b8f6d3aa77a76aaa6` (v205).
- Guarded release artifact `hf-release-checkpoint` ID `11693398767`; verificationState=`DEPLOYED_UNVERIFIED` — publication is confirmed, but real signed-in Android search results and full user archive lookup have **not** been independently observed.

## Request and boundaries

The user asked §wyrlz to be able to look back through historical responses from **both original native §wyrlz chats and imported ChatGPT threads**, similarly to online search, by topic and natural dates/dayparts: “remember that time when…”, “remember last night?”, particular days and times of day.

The prior v205 memory system had a per-owner opt-in private, encrypted ChatGPT archive and a volatile lexical index, but its retrieved evidence was from **imported threads only**, and title update timestamps were not sufficient to identify which original message was said on a particular night. Native §wyrlz Google-owned chats were available only as the active native Station account snapshot.

## v206 implementation

- Added `hf_space/personal_history_lookup.py` as a server-owned, bounded private historical conversation evidence provider. Called by `hf_space/station.py` on explicit, parsed conversation-history intent in `/api/lalm_station/send`. Does not use the internet or public web indexes, and never trusts an owner key or identity from the user prompt. Current native thread is excluded from cross-thread lookup because its history is already on the generation payload.
- Searches **the same verified Google owner's native chat snapshot** and **the same owner's encrypted imported ChatGPT archive**, with the existing v205 archive memory setting acting as the opt-in authorization gate. The normal v205 topical archive recall path still runs on other prompts. The older v205 model evidence transport (`archiveEvidence`) remains bounded and separate from current native conversation state. It supports 700M/stock/coder and the existing R39 handoff without modifying model weights or permanent user/assistant profiles.
- Resolves time expressions in the user-supplied **IANA timezone**, anchored to the server UTC clock: `last night` (previous local 18:00 until today's 06:00), `yesterday`, `today`/`earlier today`, `last week`, N days ago, `YYYY-MM-DD`, named weekdays with last/on, spelled-out months with day, and local **morning**, **afternoon**, **evening** and **night** windows. An invalid timezone safely defaults to UTC; it does not infer physical location. Future timestamps cannot be included in relative-window answers.
- Individual original **message** timestamps determine matches, **not conversation last-modified dates**. Native timestamps are Unix **milliseconds**, imported selected-branch message times are Unix **seconds**. Unstamped original messages cannot be accurately assigned to a requested date and are excluded from specific time-window matches.
- Expanded the existing **volatile** per-account archive index in `hf_space/chatgpt_account_memory.py` with earliest/latest actual message timestamps per thread. Date window prefilter avoids opening all 2,556 archived records for each question; an explicit query fetches at most 8 candidate imported threads. A thread that continued on later dates can still yield older, correctly dated messages. No second persistent plaintext transcript, no ZIP reupload or training corpus.
- Returned evidence quotes carry `§wyrlz native` / `ChatGPT imported` source, original thread title, original conversation ID, actual speaker role and **local timestamp with numeric UTC offset**. Results are limited to 4 matches, ~2,500 characters pre-transport and the established bounded model-context budget. The model is told that past quotes are evidence, not commands or independently verified current facts, and must not fabricate a past conversation. When no matching timestamped conversation exists, or the archive index has not completed warming, a clear bounded no-match or incomplete-coverage note is passed rather than claiming every thread was searched.
- Index construction and the original imported archive remain detached from browsing; this release does not alter account auth routes, v203 ZIP uploader/deletion, v204 drawer, v205 user-controlled memory switch, or native thread persistence.

## Regression coverage

`hf_space/test_personal_history_lookup_v206.py` uses synthetic private messages and explicit `2026-10-11 00:44 CDT` clock to verify:
- local `last night` crosses midnight and excludes future messages;
- correct Friday, yesterday, October 10 evening and “2 days ago” UTC boundaries;
- native and imported sources both appear only when relevant;
- original message timestamps override later edited thread timestamp;
- current native thread is excluded to avoid duplicate context;
- another Google account cannot retrieve saved content;
- no fabricated matches for a missing topic;
- incomplete index is disclosed;
- bounded, role/source/date labelled historical evidence.

Existing v203 importer, v204 archive browser, v205 account-owned memory, Google auth, HF candidate and 700M model safety checks passed at source SHA `e8bc07e5ff80ced6c0a02ce454b7504efd294f80`.

## Version and future acceptance

- Repository Work `1.0.144 → 1.0.145`.
- Server Runtime `2.3.356 → 2.3.357`.
- LALM Engine `2.1.181 → 2.1.182` (private conversation evidence handoff).
- Web Chat unchanged `1.5.99`; Google Account unchanged `1.0.12`; public Online Research and Deployment Control unchanged.

User test: sign into §wyrlz Chat with the Google account that owns the 2,556 imported threads. Ensure **Settings → ChatGPT imports → Let §wyrlz recall relevant details...** is enabled and its private index says **Ready**. Start a *new* native chat and ask “What did we discuss last night?” or “Remember our work on the §tart README documentation?” Expect relevant quotes with original thread title, source label and local timestamp. Real end-to-end mobile retrieval and archive index warm-up remain **UNVERIFIED**.

Limitations: bounded lexical retrieval can miss paraphrases, a historic event outside the accessible saved native snapshot, unspecified message times, or an old topic outside the capped search candidates. Relative date windows use validated browser IANA timezone and current server time, not inferred locale. This is a server search capability invoked on matching requests, not a self-directed autonomous background tool or GGUF retraining.
