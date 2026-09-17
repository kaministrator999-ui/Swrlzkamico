# R39 Conversation Acceptance Suite v1

## Purpose

This suite turns recurring conversational behavior into deterministic acceptance classes for the §wyrlz LALM runtime. It is intentionally not a transcript memorizer and does not encode user-specific facts. The target is general conversational competence: continuity, correction, reference resolution, task boundaries, requested depth, and truthful completion.

## Corpus evidence

The behavioral review used the supplied ChatGPT conversation export as aggregate evidence. The archive contained 27 JSON shards and approximately 2,608 conversations. A linearized pass produced about 36,595 user→assistant response pairs for heuristic analysis.

Aggregate cue samples from that pass included approximately:

- 14,691 short user turns (12 words or fewer)
- 637 exact short continuation turns such as generic continue/next/go-on forms
- 1,969 turns beginning with correction-like language
- 2,102 turns carrying deep/extended-style wording under the analysis heuristic

These counts are diagnostics, not training labels. The runtime must never infer that a phrase has one fixed meaning merely because it appears in a corpus category.

## Acceptance contract

Contract ID: `swrlz_conversation_acceptance_v1`

The runtime self-test currently covers these classes:

1. A deep/massive work request followed by a compact continuation preserves the active scope and continuation stance.
2. An explicit brief/short instruction overrides previously inherited deep scope.
3. Temporal phrases beginning with `next` do not become false continuation commands.
4. Referential micro-turns such as `do that too` can remain attached to the active trajectory and inherit its scope.
5. Corrections default to local repair rather than erasing unrelated accepted structure.
6. Explicit reset/from-scratch language creates a new-task/reset stance without treating `from scratch` alone as a demand for maximal verbosity.
7. Question + action turns preserve both acts and plan an answer-and-fulfill response.
8. Pure acceptance/humor turns remain socially compact instead of expanding into unnecessary mini-essays.
9. A generic acknowledgement cannot satisfy a deep work-bearing continuation when required content is still absent.

## Semantic completion rules

R39 v59 adds bounded completion floors only where conversational evidence justifies them:

- `massive` scope: minimum 120 substantive words before EOS may satisfy the response contract.
- `detailed` scope: minimum 64 substantive words.
- normal continuation: a 48-word floor is used only when the inherited response plan is itself substantial (planned output at least 320 tokens).

These floors are not quality scores and do not force every answer to be long. Explicit brief scope bypasses them. Simple direct answers remain allowed. The additional generic-ack guard fires only when a work-bearing stance would otherwise terminate as a short acknowledgement such as `Got it.` without performing the task.

## Trajectory boundary rules

Continuity must not tunnel indefinitely backward through conversation history. A substantive newer task is a boundary. Short acknowledgement, correction, humor, or deictic bridge turns may preserve the active trajectory when they do not establish a new task.

R39 v59 additionally treats temporal `next week/month/year/day/...` wording as content rather than a continuation operator.

## Response-quality telemetry

Completed responses expose bounded diagnostics:

- substantive word count
- repeated 3-gram ratio
- repeated 4-gram ratio
- prompt-token echo ratio
- whether the output opened as a generic acknowledgement
- remaining response-contract gaps

These are diagnostic signals, not hidden reasoning and not automatic factual-quality judgments. Prompt echo can be legitimate for technical names and terminology, so it must not be treated as a standalone failure.

## Pass policy

`inspect_engine()` publishes the deterministic acceptance result with pass count, total count, failures, and contract ID. Any future R39 revision that changes conversation routing should preserve or intentionally revise this suite. A regression must be visible rather than silently accepted.

## Privacy / generalization rule

No raw private transcript text is embedded into the runtime acceptance suite. Cases are generalized behavioral fixtures. Corpus-derived aggregate counts may guide test coverage, but runtime behavior must remain general-user capable.
