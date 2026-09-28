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
