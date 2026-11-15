# §C guest-only conversational evaluation

## Scope

This test-only harness exercises the existing Hugging Face Space \`kamiloki/Swyrlz\` without a Google account, session cookie secrets, or a second Space. No changes to production Chat, its authentication policy, inference model, personal account data, or §E are made. Each case uses a fresh Playwright browser context. The evaluator refuses to use any context that reports a signed-in user. Tests send synthetic messages only.

## Two complementary lanes

- **Chromium UI:** opens the real chat page, types into the composer, clicks Send, observes the committed model response, verifies the answer appears on the screen and sometimes reloads the browser mid-conversation.
- **Anonymous API:** uses guest \`/api/lalm_station/send\` and \`/api/lalm_station/sync\` with unique thread/request IDs to test multi-turn continuity and response quality independent of the UI.

Each batch runs **four scenarios of two turns** (eight possible model responses) **sequentially** to protect the existing shared free Hugging Face capacity. There are three batches, 12 scenarios total. Individual turns time out after 130 seconds; there are no unbounded retries and no background schedule.

| Batch | Focus |
|---|---|
| 1 | Guest UI reload and context recall, surgical Python repair, corrections, intent before code |
| 2 | Real HTML button UI, counter changes, responsive layout, one cohesive color picker |
| 3 | Guest UI reload and phrase recovery, whole-document code output, minimal repairs, quoted-data boundaries |

## Results and integrity

The workflow writes \`reports/chat-guest-eval/summary.md\` and \`report.json\`, plus a screenshot of the guest UI on failure when available. Synthetic prompts/responses are redacted and truncated to 8,000 characters per answer; account data and cookies are never recorded. Reports are stored as GitHub Actions artifacts for 14 days. These test inputs contain no real user messages.

\`PASS_EVIDENCE\` means a limited regex, static HTML, or Python AST assertion passed. It does **not** imply deep comprehension or guarantee generated code executes correctly. \`REVIEW\` means evidence was missing and requires manual assessment; it is not necessarily a model failure. \`BLOCKED\` means a browser/transport/session problem prevented completion. Generated code is **never executed** by this workflow.

UI checks and API checks can differ because UI model routing is taken from the deployed interface, while the API lane explicitly requests model \`700m\`. Do not claim cross-model speed comparisons without checking the deployed route.

## Running

Workflow: \`.github/workflows/chat-guest-eval.yml\`.

- Pull requests and ordinary changes to this harness default to **smoke**, which tests the evaluator fixtures and Chromium context isolation but makes **no** §C model calls.
- In GitHub Actions choose **§C guest-only conversation evaluation (Chromium + API)** → Run workflow → \`live\` and batch \`1\`, \`2\`, or \`3\`.
- A deliberate change commit containing \`[chat-guest-live]\` can request one live batch 1 on push. It is intentionally not scheduled.
- GitHub Actions permissions are read-only. Nothing is deployed or automatically patched based on results.

For local fixture verification with Playwright installed:
\`python -m py_compile scripts/eval_chat_guest_suite.py\`
\`python scripts/eval_chat_guest_suite.py --mode smoke --batch 1\`
Set \`SWRLZ_EVAL_CHROMIUM_PATH\` if using system Chromium rather than a Playwright-installed browser.

Compare matching scenario transcripts and verified deployed revisions before attributing changes to improvements. Existing authenticated two-user pilot remains preserved for provenance; this is the account-free evaluation path.
