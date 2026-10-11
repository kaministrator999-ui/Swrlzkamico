# v207 — Advanced private history search

Date: 2026-10-11.

## Release receipt
- Source branch: `feature/private-history-toolkit-v207`.
- Pinned source commit: `2147f8e9a363e6d01e646f86fa31e41cb6865cc7`.
- [Draft PR #97](https://github.com/kaministrator999-ui/Swrlzkamico/pull/97), based on v206.
- [Account and import CI #38117141954](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38117141954): SUCCESS.
- [HF candidate CI #38117141969](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38117141969): SUCCESS.
- [Guarded HF deployment #38117199469](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38117199469): SUCCESS.
- Published Space `kamiloki/Swyrlz`: revision `94274f10d6f2ff41ce651928c720897a7a3b0246`.
- Rollback checkpoint: `e170d1129519331b48494a967c8238f048f25b44`.
- Deployment receipt `DEPLOYED_UNVERIFIED`: production publication is confirmed, actual authenticated Android acceptance remains pending.

## New capabilities
1. **Source-scoped search.** Opt-in account history lookup can be restricted to original native §wyrlz threads or the separate imported ChatGPT archive.
2. **Speaker-specific search.** User may ask for only their own earlier words or only old assistant responses. The result retains the correct historical speaker label.
3. **Exact quotations.** Searches for text in explicit quotation marks verify that it actually appears in the selected message, not merely the thread title. The ephemeral archive index now also tracks a compact vocabulary from older assistant turns so their distinctive wording can be located. Old assistant statements remain untrusted evidence, not identity/profile instructions.
4. **Decisions, unfinished tasks and corrections.** A category match requires actual text suggesting a decision, next step or correction; the system does not silently invent an action item from an unrelated title.
5. **Expanded temporal windows.** Local time search accepts date intervals, the previous or current weekend, last/this week or month, explicit named month/year, rolling periods such as the past seven days and local clock expressions on a dated day. Existing yesterday/last night/weekday/daypart parsing remains.
6. **Safe follow-up refinement.** If the immediately preceding topic was an explicit private-history search, a short message such as “only the imported ones” reuses its topic and substitutes the latest requested source or speaker filter. An intervening unrelated user prompt blocks stale topic inheritance.

## Security, provenance and scope
- Pure query parser: `hf_space/personal_history_query_v207.py`.
- Query engine: `hf_space/personal_history_lookup.py`; source, role, content and time constraints are verified against real text and original message timestamps.
- Existing ephemeral owner-specific archive index: `hf_space/chatgpt_account_memory.py`; bounded assistant term vocabulary added for retrieval only.
- Existing Station inference bridge receives the recent active-thread history as contextual query-planning input, never another account's identifier.
- No new user data uploaded to GitHub, no new plaintext permanent corpus, no duplicate chat contents, no change to Google authentication, ZIP import, native saved conversation snapshots or model weights. Search remains behind the user-controlled memory opt-in.
- Evidence remains bounded to a small number of quoted, attributed historical messages; the imported search preselects a maximum of eight candidate threads and is not an exhaustive every-message scan on every request.
- A quote absent from the searched candidate set may be missed; do not overclaim a complete archive-wide negative result.

## Tests and versions
The new synthetic `hf_space/test_personal_history_toolkit_v207.py` covers source/speaker filters, distinctive literal quoted messages, tagged replies, decisions/pending/corrections, dated clock and calendar ranges, stale follow-up exclusion, no-match behavior and owner isolation. All existing v203–v206 tests pass. CI was rerun after correcting an intent-trigger case for plural “chats” and a date-range test expectation.

- Repository Work: `1.0.145 → 1.0.146`.
- Server Runtime: `2.3.357 → 2.3.358`.
- LALM Engine: `2.1.182 → 2.1.183`.
- Web Chat `1.5.99`, Google Account `1.0.12`, Online Research and Deployment Control unchanged.

## Remaining live acceptance
The owner should sign into §wyrlz Chat, ensure Settings → ChatGPT imports → private-memory opt-in shows READY, and test distinctive older topics with source and speaker filters. The supported upgrade is to the existing server-side search; there is no new sidebar button and no ZIP re-upload. Production release and offline test success do not prove that any individual personal memory has been retrieved correctly from the signed-in user's full archive.
