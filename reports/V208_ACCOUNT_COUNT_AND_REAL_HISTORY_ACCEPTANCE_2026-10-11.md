# v208 — Live account history/count acceptance repair

Date: 2026-10-11 (America/Chicago)

## Acceptance input and observed failure

The owner uploaded a **local native §wyrlz session export** and a screenshot of Settings/Chat drawer stating that **2,556 imported ChatGPT conversation threads** are stored in the encrypted read-only archive. The export timestamp was 2026-10-11 09:56 local. A native conversation between 09:53–09:56 recorded five failed/incorrect 700M responses to live account questions:

- current imported exported-conversation thread count (instead of reading the archive's count, public online-research `freshness-intent` was triggered; model guessed a much smaller number);
- current native/account chat thread count (model said it lacked documents);
- cumulative number of imported messages (model said it lacked documents);
- which conversations were present five months earlier (treated as an import-process count question or ignored actual dates);
- which conversations were discussed yesterday (model lacked private retrieved evidence and requested file attachment).

These are **user acceptance failures** even though v203 import, v204 browsing, v205 opt-in recall, v206 private history search and v207 facets were previously source/CI/deployment successful. The private export was used as *local diagnostic evidence only*, not added to repository files.

## Root cause

1. Account statistics had no deterministic Station lookup. `_run` allowed freeform model inference and public online search to answer a question about the signed-in account's own Redis index.
2. Stored imported threads and the **addedMessages** count from one ZIP reimport were incorrectly conflatable. The importer did not expose an authoritative cumulative total of currently stored original text messages.
3. History lookup was gated behind the existing user-enabled memory preference, but disabled/error/no-match status was not surfaced to the user; Station caught private-retrieval exceptions and proceeded as though it had no evidence.
4. Explicit history questions about a month N months ago were not reliably classified or date-window normalized. Generic token `chat` was inadvertently used as a topic keyword even for date-only requests, filtering away relevant threads.

## Implementation

Source `feature/private-account-facts-v208`, pinned commit `e85859fc558646e10d3f2e94212d147817974b5b`.

- `hf_space/private_account_facts_v208.py` recognizes strict, current account count requests, uses the server-verified Google owner and encrypted Redis archive `ZCARD` to answer the **exact current imported thread count**. Native snapshot thread/message counts are kept separate. No third-party lookup, no model-generated number, no untrusted user-provided ownership.
- For cumulative imported text messages, checks the existing ready v205 memory index with a newly added integer `messageCount` per archived thread. If unavailable, starts a bounded read-only per-account background worker that reads original encrypted archived records and accumulates the counts **without storing any plaintext transcript copy**. While counting, answers transparently with a verified thread count and counting progress, rather than confusing incremental messages added in the last import with total stored messages or inventing a total.
- The tally cache is process-local, owner-keyed and invalidated by archive delete/all-delete and the archive import start/end. The original encrypted ZIP import, archive, native threads and account identity remain unchanged.
- `hf_space/station.py` routes deterministic account figures (and explicit memory-disabled/error/not-ready responses) through the existing assistant DELTA/COMPLETE event transport; this prevents a public online lookup or unreliable 700M inference path from answering these facts. Relevant retrieval excerpts still go through the established bounded historical evidence path when available.
- `hf_space/personal_history_lookup.py` recognizes requests for past chat catalogs N calendar months ago, normalizes their local time range (e.g., October 11 → May 1–June 1 for five months ago), and strips generic `chat` tokens for date-only archive searches.
- Feature is behind existing Google authentication and historical recall opt-in. Disabling memory prevents personal content recall but not access to the account's own numeric catalog statistics. No change to universal §wyrlz persona, inference weights, user profile or public search provider.
- Limitations: existing v207 private history lookup remains bounded and lexical, so it cannot guarantee exhaustive recall; on first count request with a cold server, computing total imported **messages** may require waiting for the background count worker. A server restart can require re-counting but never re-uploading.

## Tests and release

- `hf_space/test_private_account_facts_v208.py`: five live-question formulations with synthetic placeholders, exact imported-owner ZCARD 2,556, distinct native counts, non-invention of cumulative message count, background count progress and ready count, indexed count reuse, epoch invalidation, 5-calendar-month time window, and presence of server-owned deterministic dispatch.
- Initial CI failures exposed two issues and were corrected before final release: lexical word `chat` included in date-only search keywords, and a test expectation differing from the formatted phrase `stored visible text messages`.
- [GitHub account CI #38150707591](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150707591): **SUCCESS**.
- [HF candidate CI #38150707582](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150707582): **SUCCESS**.
- [Draft PR #99](https://github.com/kaministrator999-ui/Swrlzkamico/pull/99), base v207.
- [Guarded HF deployment #38150791117](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38150791117): **SUCCESS**, published to existing `kamiloki/Swyrlz` at Space revision `75adf3fc54a6da99b729fe532308c190f64919ce`.
- Rollback Space revision `94274f10d6f2ff41ce651928c720897a7a3b0246`.
- Deployment receipt `DEPLOYED_UNVERIFIED` — **publication verified, signed-in Android acceptance pending**.

## Version authorities (only modules touched)
- Repository Work **1.0.146 → 1.0.147**.
- Server Runtime **2.3.358 → 2.3.359**.
- LALM Engine **2.1.183 → 2.1.184**.
- Google Account **1.0.12** unchanged; Web Chat **1.5.99** unchanged; Online Research module unchanged.

## Next owner acceptance

In the signed-in §wyrlz Chat, reload after deployed revision is live, then ask the same five questions in a native thread. The current imported count should be read directly and accurately from encrypted storage, not inferred. The cumulative message count may initially show progress and be available on a later request. For historical conversation searches, confirm Settings → ChatGPT imports → enable private recall and wait for **Ready**. If disabled or unavailable, the model should give the exact reason rather than pretend no source conversations exist. Confirm no public search card appears for private count requests. Real mobile acceptance and actual messages returned for October 10 or five months earlier remain *unverified* until the owner retests.
