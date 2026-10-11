# v208.1 — Private conversation counts and calendar-history retrieval follow-up

Date: 2026-10-11 · existing hosted application: `kamiloki/Swyrlz`.

## Source and release provenance

- Previous live v208 source: `e85859fc558646e10d3f2e94212d147817974b5b`, deployed Space revision `75adf3fc54a6da99b729fe532308c190f64919ce`.
- Updated source branch: `feature/private-account-facts-v208`, exact tested candidate commit **`6a1e55af26dcfe0dc03dafc8e8aa19d251741f36`**.
- Review: [draft PR #99](https://github.com/kaministrator999-ui/Swrlzkamico/pull/99) (same feature branch, updated tests and follow-up).
- Google account/source isolation [CI #38155344415](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38155344415): **SUCCESS**.
- HF offline candidate [CI #38155344246](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38155344246): **SUCCESS**.
- Repeated HF candidate validation [CI #38155347697](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38155347697): **SUCCESS**.
- Guarded HF deployment [run #38155453196](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38155453196): **SUCCESS**. R39 reconstruction, 700M profile budget, source staging and prior revision snapshot completed.
- New hosted Space revision: **`645229dfbc1c4d29329c682458a9e860910a2577`**.
- Previous live revision kept for rollback: **`75adf3fc54a6da99b729fe532308c190f64919ce`**.
- Guarded release checkpoint artifact **`hf-release-checkpoint` ID `11708562081`**, `verificationState=DEPLOYED_UNVERIFIED`. Publication is proven by the workflow; the signed-in Android retrieval and account-owned indexing remain **unverified**.

## What the user's acceptance tests revealed

The native §wyrlz conversation export recorded real user tests on 2026-10-11 at approximately 09:53–09:56 Central, and the user's mobile screenshot showed **2,556** saved imported ChatGPT conversations. Before v208, the hosted model guessed a handful of threads or invoked public internet search instead of reading its authenticated archive, did not distinguish cumulative message total from latest import delta and did not reliably locate historical conversations by date.

The v208 direct answer route already repairs the primary count question: it checks the authenticated Google user's encrypted archived conversation index (`ZCARD`), counts native account-owned threads and user/assistant messages separately and optionally derives total stored imported message count from the existing ephemeral archive index or an incremental read-only background count worker. Count queries return a deterministic signed-in-account result through DELTA/COMPLETE, bypassing public online search and free-form model guesses. The original ZIP, 2,556 encrypted records, native snapshot and general model weights remain unchanged.

## Final follow-up in v208.1

1. `hf_space/personal_history_lookup.py`: accepts literal **`5 months ago`** and natural-language **`five months ago`**, including “about five months ago”. Both resolve to the **local calendar month** of May 2026 when the server date is October 11, 2026 in `America/Chicago` (May 1 00:00 through June 1 00:00, end exclusive, transformed to UTC). Time marker words do not become topical search terms; date-constrained history lookup continues to use *original message timestamps*, not last-updated thread times.
2. `hf_space/station.py`: when a Google owner requests private-history lookup but the account's memory preference is disabled, return clear instructions to enable it under Settings → ChatGPT imports. If account history retrieval raises an error, send a truthful temporary-error response rather than silently falling through to unsupported model inference. No public internet search is used for authenticated account-count requests.
3. `hf_space/chatgpt_import_job.py`: completing a detached ZIP import invalidates the transient cumulative message count cache as well as the existing per-owner memory index. The archive records are unaffected.
4. `hf_space/chatgpt_account_memory.py`: extends the temporary per-document index with the number of visible saved messages, allowing cumulative message counts without re-reading all encrypted transcripts when the complete index is already warm.
5. `hf_space/test_private_account_facts_v208.py`: synthetic tests include observed acceptance question forms, direct account count and no-web handoff, owner totals versus import-progress deltas, native versus imported text message counts, indexed count reuse, invalidation, yesterday / numeric-month and written-out-month historical queries, non-guessing private-memory status. No customer ChatGPT conversation text is in the repository tests.

## Release versions

- Repository Work: `1.0.147 → 1.0.148`.
- Server Runtime: `2.3.359 → 2.3.360`.
- LALM Engine: `2.1.184 → 2.1.185`.
- Web Chat unchanged `1.5.99`, Google Account Architecture unchanged `1.0.12`. Online Research and Deployment Control not changed.

## Signed-in acceptance still required

Sign into the original §wyrlz Chat account, refresh, and ask a new native thread the exact private count: “How many ChatGPT conversations did I import?” The correct result is whatever the authenticated account's archive `ZCARD` shows; the user screenshot previously showed **2,556**, and this number must not be hardcoded. Ask “How many imported messages are stored?”—the first attempt may say counting and give progress, with a later attempt yielding the cumulative count. For historical retrieval (“What conversations did we have five months ago?” and “What did we discuss yesterday?”), enable the **private memory opt-in** in Settings → ChatGPT imports and wait for the index to say **Ready**. Answers should cite actual bounded conversation evidence or report incomplete matches; synthetic tests do not establish that the live archive search is accurate.

**Release state:** TESTED / GUARDED-PUBLISHED / OWNER MOBILE ACCEPTANCE PENDING.
