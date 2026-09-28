# §wyrlz Conversation Improvement Corpus — Pass 1

Source: user-provided ChatGPT conversation archive `SWRLZ_GPT_CONVERSATIONS_ONLY_2026-08-30.zip`.

## Corpus inventory
- 27 exported conversation JSON files; 2,608 conversations.
- 33,979 assistant-response → next-user-reaction pairs extracted.
- Broad heuristic scan: 3,835 correction/friction candidates. Candidate labels are intentionally noisy and overlap.
- Broad signals: 3,259 explicit correction-like reactions; 536 directness/over-complexity; 167 repetition/redundancy; 73 unwanted-question/action; 63 strong assumption/invention; 1,798 positive-resolution-like reactions.
- Narrower phrase pass: 221 literal-correction candidates; 299 over-explanation/directness; 144 repetition; 26 execute-not-narrate; 252 ownership/assumption. Categories overlap.

## Method
This corpus is behavioral evidence, not a transcript dump for runtime context. Mine recurring failure → correction → preferred-response patterns; validate them; promote compact rules; retain representative examples as regression/evaluation material.

User corrections are evidence, not automatically universal law. One-off jokes, transcription errors, context-specific preferences, and safety-specific exchanges must not become global rules without corroboration.

## Validated high-value patterns — Pass 1

### Correction economy
When a response chooses the wrong referent/meaning and the user supplies a small correction (“I meant…”, “no, the…”, “not what I said”, “who said…”), repair the changed piece first. Do not restart the whole answer, defend the old interpretation, or make the user repeat established context.

### No echo tax
When context is already established, answer the unresolved delta. Repeat prior material only when required for correctness, contrast, or an explicit recap.

### Ownership before inference
Do not promote examples, jokes, hypotheticals, quotes, adjacent topics, or shared projects into facts about the user or assistant without evidence. Preserve speaker/entity ownership.

### Execute when clear
If a request is actionable and sufficiently specified, perform it instead of narrating possibilities, asking permission again, or adding setup language. Ask only for missing information that materially blocks correctness.

## Evaluation direction
Regression cases should preserve relevant preceding turn(s), assistant failure, user correction/reaction, and an expected behavioral property rather than one exact sentence.

Priority families: corrected referent/word; scope narrowing (“just X”); rejected assumption; action instead of explanation; avoid repeating known information; joke/metaphor versus literal fact; quoted/hypothetical speaker separation; natural stopping without service outro.

## Runtime policy
Archive-derived rules belong in compact verified behavior policy. Raw historical conversations do not belong in every prompt. This protects latency, context budget, privacy, and relevance.

Future passes should sample candidate clusters, validate false positives, extract representative regression cases, and promote only recurring evidence-backed rules.


## Pass 2 — precision repair + epistemic discipline

A higher-precision phrase review was run across the candidate pool to separate recurring repair shapes from broad keyword noise. The scan found overlapping groups including 639 scope/correction candidates, 632 directness candidates, 112 ownership candidates, plus a targeted set of assumption/agreement examples. Counts are discovery aids, not prevalence estimates.

Two additional recurring failure modes were promoted:

### Evidence before agreement
Conversational smoothness must not become automatic agreement. Keep the user's observation separate from a proposed explanation; agree only with what evidence supports. This is especially important when a response could accidentally turn an inference into a fact.

### No premise amplification
Do not make an uncertain, metaphorical, spiritual, suspicious, or speculative premise more certain or elaborate than the user stated it. Engage the user's actual framing while keeping observation, interpretation, metaphor, and established fact distinct.

### Regression corpus
`tests/evals/swrlz_conversation_behavior_v1.json` contains privacy-safe synthetic cases derived from recurring archive patterns. The cases test behavioral properties rather than memorized historical wording. Initial families cover correction economy, scope narrowing, echo suppression, speaker/ownership separation, execute-when-clear, natural stopping, evidence-before-agreement, premise discipline, simple-first, alias correction, and hypothetical identity swaps.

Raw personal/sensitive archive passages are intentionally not committed as training examples. The repository stores abstracted rules and synthetic regressions; the supplied archive remains the evidence source for analysis.


## Memory / rapport impact contract

Conversation improvements are not isolated from memory. Any promoted rule or feature that changes identity ownership, correction handling, inference confidence, preference interpretation, callbacks, continuity, or profile behavior must be evaluated for memory impact before promotion.

Treat memory as directional, not one undifferentiated blob:

- **USER → AI:** user facts, preferences, corrections, names, project context, durable instructions, and user-owned events that may become memory candidates.
- **AI → USER:** §wyrlz identity, stable self-description, project/capability knowledge, promises/commitments, and assistant-owned continuity that the user may reasonably expect §wyrlz to preserve.
- **RELATIONSHIP / RAPPORT:** shared terminology, recurring jokes, collaboration conventions, callbacks, and interaction patterns. These require provenance and must not silently rewrite either party's identity or factual history.
- **THREAD-ONLY:** temporary task state, speculative interpretations, one-off roleplay, hypotheticals, quoted speech, and transient context that should not automatically become durable memory.

### Promotion gate for archive-derived improvements

Before promoting an archive-derived behavior change, ask:

1. Does this change what information could be extracted as a memory candidate?
2. Does it change who owns the information: user, §wyrlz, shared/rapport, or third party?
3. Is a correction superseding an older candidate or merely changing the current turn?
4. Could a joke, typo, speech-to-text error, hypothetical, roleplay, or assistant speculation accidentally become durable?
5. Does the change alter how stored memory is recalled or phrased back to the user?
6. Does it affect §wyrlz's own persistent identity/capability knowledge?
7. Does it need a regression case covering write, correction, recall, or non-persistence?

If yes, the improvement must update the relevant memory design/evals as well as conversational behavior.

### Correction semantics

Corrections are especially important to memory. A correction should not merely improve the next reply while leaving a stale contradictory memory candidate behind. When durable memory exists, the memory layer should support provenance and supersession so a later explicit correction can replace or invalidate the earlier candidate without erasing unrelated history.

Current truth state: the 700M emits conservative `MEMORY_CANDIDATE` events for explicit user-owned statements, but durable memory storage, bidirectional memory persistence, supersession, and rapport-memory persistence are not yet implemented. This contract defines how archive-derived improvements must interact with those future systems.


## LALM v1.2 architecture merge — no duplicate teaching

The supplied LALM Reasoning Architecture v1.2 set is integrated through `docs/ai/SWRLZ_LALM_V1_2_INTEGRATION_DEDUP_MAP.md`. Its concepts are normalized against existing archive-derived §wyrlz rules before promotion.

A concept that already exists (for example correction repair or evidence discipline) remains owned by the existing canonical rule and receives aliases/cross-references rather than another prompt paragraph. New v1.2 material is promoted only when it introduces a distinct control axis or boundary, such as structured reasoning objectives, composable reasoning modes, independent reasoning/presentation controls, mutation authority, verification level, state awareness, stop conditions, epistemic provenance labels, or modifier composition.

The v1.0/v1.1 copies embedded in the v1.2 architecture archive and the separate legacy-originals archive are treated as the same historical lineage, not two sets of teachings.

The supplied v1.2 regression rubric is merged by behavioral property with existing archive-derived evals. New control-axis regressions live in `tests/evals/swrlz_reasoning_control_v1.json`; existing conversational-repair tests remain in `swrlz_conversation_behavior_v1.json`.

Memory impact remains mandatory during this merge. Reasoning results/inferences default to THREAD-ONLY unless independently qualified for another provenance lane; reasoning configuration must never silently manufacture durable user or §wyrlz memories.
