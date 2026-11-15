# §C: Stop, Continue code, and useful single-page HTML — November 14, 2026

## Diagnosis from authoritative Hugging Face Space
Target: `kamiloki/Swyrlz` (Hugging Face, not Vercel). Production source was inspected read-only before changes.

- **False "Continue code" prompting:** the Station automatically resumes saved incomplete code checkpoints in the same active task, yet its per-checkpoint status explicitly told the user to type Continue code. The coder also emits a manual Continue instruction when a bounded generation or validation attempt genuinely stops. These two states must not be conflated.
- **Stop not consistently actionable:** the Chat UI discarded any Stop click within 350 ms of the prior Send action. It also ignored Stop before a request ID was available despite showing the Stop button during admission.
- **Completed Continue code:** only a same-thread pending `pendingCodeGeneration` checkpoint triggered source continuation. Without one, the bare text was sent to the model with no grounded source-specific instruction. That can yield an irrelevant/no-op answer.
- **Generic webpage:** coding prompts demanded completeness, not an original interactive experience. The screenshot of "Digital Horizon" illustrated inert feature-card marketing rather than a working functional HTML demo.

## Targeted implementation
1. Replace the 350 ms time-based Stop suppression with a pointerdown-owned Stop gesture test, preventing synthetic Send-to-Stop clicks without rejecting a deliberate immediate Stop. During unacknowledged send admission, Stop sets `submission.cancelRequested` so the existing send routine refuses/withdraws the request. After admission, use the existing authenticated Station cancel route and server cancellation receipt. A failed cancel attempt shows a retryable error rather than claiming success. Native decoder cancellation remains in the existing token boundary path.
2. Only tell users to manually Continue when an incomplete draft actually paused; Station in-flight checkpoints correctly say automatic continuation is underway. A completed but unverified source says it needs repair, not another appended chunk. Paused draft bytes remain visible through the terminal snapshot.
3. For an explicit same-thread Continue command, always preserve verified checkpoint resumption. When no checkpoint exists and the thread contains prior code, instruct a meaningful one-feature revision with actual source and preserved functionality. With no grounded source, explain that nothing is queued instead of inventing project code. User-visible text remains exactly what was typed.
4. For unconstrained "make a cool webpage" coding prompts, choose one original responsive single-file concept with working interactivity, accessible controls and no fake feature cards/studio navigation. Explicit themes override the default.

## Deployment invariants
Three production files only: `qwen_coder_engine.py`, `station.py`, `chat/§wyrlz/index.html`. No changes to Qwen3.5-9B model/weights, CPU, decode/batch threads, context, account storage, live `§E`, third-party deployment, or project file permissions.

The patch script performs exact source-drift checks, Python AST parsing, full inline browser JS parsing, deterministic Stop gesture and same-thread code intent tests, and a model response-mode test. It retains original source bytes and hashes and publishes only if the live HF Space parent revision is unchanged. The release workflow verifies served Chat HTML and rolls back to the precise previous three-file revision on post-deploy verification failure.

No automatic claim of real phone button performance or generated webpage creativity is made from source-only tests; those require live post-deploy testing.
