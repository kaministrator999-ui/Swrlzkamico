# §C · 16K coding context and guarded live code preview — 2026-11-13

## User-reported failure
In a real HTML coding conversation, `Now improve it` failed with:
`Mandatory prompt/profile or current source uses 4944 tokens; only 3968 input tokens remain while reserving 4096 output tokens.`
The deployed inference context was 8192 tokens. The 4096 output reserve left 3968 input after the 128-token safety margin, which could not fit 4944 mandatory tokens. The existing guard correctly refused to truncate user source.

## Release
- Source-of-truth: exact current Hugging Face Space `kamiloki/Swyrlz`, not stale checked-out files.
- Guarded release workflow: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43527491335
- Preflight audit: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43527312499
- Accepted live Space commit: `15adc2c14b74bc95de7b48f075d387fe0e1fbac6`.
- Original source `bd5ea5c14fae1a1815385441018f4230affcc6de` backed up with file SHA-256 manifest before mutation and retained as a workflow artifact for rollback.

## Changes deployed
1. Shared Qwen3.5-9B Q4_K_M resident server, general engine and coding engine context: **8192 → 16384 tokens**.
2. Full HTML-page output reservation: **4096 → 8192 tokens**. Adaptive context fitting computes the minimum input needed by mandatory system + current request/source, reduces the output allowance when necessary, and never silently discards mandatory source.
3. Dedicated `CANDIDATE_PREVIEW_DELTA` and `CANDIDATE_PREVIEW_RESET` events for guarded coding generations. Inference now exposes generated code progressively while preserving the existing deterministic structural/contract validation and up to three candidate attempts.
4. Station stores preview bytes **ephemerally**, not as accepted chat text. The NDJSON stream sends preview deltas independently of final `DELTA`. Rejected attempts reset the visible preview before a retry.
5. Chat HTML renders an explicitly labeled draft in a responsive, text-only code panel (HTML escaped using `textContent`). It does not provide accepted-code Copy/Download actions, voice output or saved chat artifacts for unverified draft text. The ordinary validated code block appears only when the final `DELTA` passes the existing gate.
6. Unchanged: 16 effective CPU cores, 18 decoder and prefill threads, same model weights and revision, source auth and permissions, §E, stored chat threads, user profiles, voice, cache_prompt, one-request concurrency.

## Live acceptance
Tested anonymously through the actual `/api/lalm_station/send`, `/api/lalm_station/stream` and cookie-scoped `/api/lalm_station/sync` endpoints. The first synthetic attempt was invalidated by a session/request-ID mismatch during restart, and was not accepted. A subsequent matched request passed.

| Metric | Verified |
| --- | --- |
| Model | Qwen3.5-9B |
| Context window in live request | **16,384** |
| Reserved output tokens | **8,192** |
| Input tokens in synthetic HTML request | 2,789 |
| First provisional code | **40.75 seconds** |
| First accepted final code | **171.06 seconds** |
| Total time | 171.06 seconds |
| Final response size | 5,591 characters |
| Existing candidate validation status | **PASS** |
| Final HTML present | **Yes** |
| Live release workflow | **Success** |

The provisional code appeared **130.31 seconds before** the validated HTML. This is a user-visible latency improvement for guarded coding, **not a claim that native model generation became faster**. The output had to complete and pass validation before being saved as final.

At context 16,384, the original reported 4,944-token mandatory input plus 8,192 reserved output plus 128 safety tokens would occupy 13,264 tokens, leaving 3,120 spare tokens. This addresses that exact budget overflow in principle; the user's specific large HTML was not uploaded into a synthetic test or modified on their behalf.

## Boundaries and follow-up
- 16K is a measured 2× context increase, not a claim of arbitrary unlimited tokens. Going to 32K may increase KV-cache memory and CPU prefill cost; benchmark and protect the existing fast conversational route before any further increase.
- On a genuine source repair or longer complex coding task, the model may still need multiple candidate attempts; the provisional pane is expressly unverified and can be reset.
- Browser JS syntax and server code AST checks passed. Live stream and chat endpoint integration passed. Actual mobile browser visual placement has not been independently observed in a user-owned session.
- An additional read-only regression workflow checks short chat and small-code correctness after context expansion.
