# §wyrlz Lyric Ocean — Evidence and Quality Protocol v3

**Scope:** bounded source-independent songwriting curriculum; still in the isolated draft PR, **not released to Hugging Face Chat and not model-weight trained**.

## Principle: abundance before benchmarks, evidence before promotion

The user asked to build an ocean of lyrics, genres, correction examples and relationships before judging the model's performance. This means broad and deliberately *non-repetitive* teaching material, not prematurely assigning gold labels or running a narrow creativity test after a handful of prompts.

Core seed assets already present before v3: 768 original prompts across 48 scenarios and 16 mechanisms, 64 metadata-only failure/repair drills, 48 bounded runtime craft cards, 24 eight-line synthetic demonstrations (192 lines), and 6 longer synthetic compositions (196 lines).

Added in v3:
- **8** additional newly authored, longer complete songs (**252 lines**) in `original_complete_songs_v3.json`: narrative freestyle, absurdist comedy, melodic ballad, alternating two-voice dialogue, fast technical rap, noir storytelling, poetic argument/cypher, and theatrical comic storytelling;
- **24** actual before/after synthetic lyric examples in `original_revision_pairs_v3.json`; each supplies two weak lines, two revised lines and a specific defect explanation;
- **12** editorial dimensions with anchored 0–4 scores in `editorial_rubric_v3.json`.

**Composite teaching material:** 14 longer songs / **448** longer-song lines; 24 short demonstrations / 192 additional example lines; total **640 longer/shorter example lines**; plus the 768 prompts, 64 metadata drills, 48 targeted cards and 24 rewritten pairs. All counts reflect *documents and instructor drafts*, not successful evaluation or training.

## Archive evidence repair — private sources remain private

The user-supplied archive ending August 30, 2026 was examined locally; the existing v2 casebook has **261** selected creative responses across **172** conversations. The prior heuristic reported **136 positive signals**, **90 exploratory**, **35 corrections/negative**. Those categories were provisional and must not be interpreted as 136 confirmed favorites.

The stricter **v3 provenance audit** searched the original archive for all 261 response hashes and matched all of them. **248** feedback snippets were confirmed as direct message-parent replies; **2** were immediate chronological user messages; **2** occurred after intervening assistant messages; **9** could not be matched to the expected immediate next user feedback. A conservative lexical analysis yielded **29 possible explicit endorsements**, **9 possible explicit corrections**, and **223 other/uncertain** cases. Positive-sounding language, even in a direct reply, is not an objective rating of the song.

**Privacy firewall:** Only aggregate counts, review methodology and abstract craft relations are in this public repo. No raw song, archive prompt, user quote, message/thread identifier, user biography, or favorite selection is embedded here. The exhaustive case-level v3 audit, editor queue and source comments are delivered as a private downloadable artifact held outside GitHub.

## Review lifecycle and evidence states

1. **FOUND_IN_ARCHIVE:** assistant output hash located in original archive. This supports provenance only.
2. **FEEDBACK_LINKED:** source reply is a direct parent or immediate chronological user turn. This supports relationship only, not approval.
3. **ENDORSEMENT_POSSIBLE / CORRECTION_POSSIBLE / UNCLEAR:** conservative natural-language screening; still uncertain.
4. **EDITOR_REVIEWED:** an independent reader judges the full work in context; documents the specific evidence and constraints.
5. **RIGHTS_CLEARED:** source/reference and privacy checks completed; no borrowed lines, hooks, recognizable imitation or private material in public/training data.
6. **TRAINING_ACCEPTED:** complete, well-edited, rated target with explicit approval for training use and separated evaluation holdout. **No material is at this stage.**

Avoid circular evidence: a model that generated an example cannot independently certify its own quality. Do not call synthetic examples high-quality gold merely because an automated script counted rhyme tokens or the model praised itself.

## Quality school — anchored scoring

Use `editorial_rubric_v3.json` for **12 independent dimensions**. Rate each on 0–4 *only after* reading exact lyrics and prompt:
source alignment, meaning/coherence, rhyme architecture, cadence/performability, full-form completion, hook/refrain design, scene/imagery, narrative development, emotional truth, comic/battle logic, voice/originality, and revision quality.

Nonapplicable dimensions should be **N/A**, not 0 (e.g. a pure freestyle is not defective for having no chorus). Keep independent ratings separate from preference signals. Each score needs one cited line/turn in the private file or a source-independent observation. A song may be subjectively beloved but formally imperfect; do not erase either fact.

## Repair-pair acceptance

Each before/after pair must: (1) name a fault observed in *the before*, (2) change the actual words of the offending lines, (3) preserve subject and the user's hard constraints, (4) remain performable, (5) avoid introducing a new issue, and (6) give a specific technical explanation. Compare with untouched passing requirements before promotion. The 24 synthetic pairs satisfy a structural data shape but are **not independently artistically scored**.

## Exposure and inference boundaries

Public original drafts and explanations can serve as optional writing-guide/curriculum resources; they are **not fed verbatim into every 700M inference**. The deployed-size path must still select only a couple of relevant source-independent craft hints from the compact 48-card catalog, so the user's mobile chat stays responsive. LFM2-700M model weights are unchanged; Qwen coding model and §wyrl§ Engine are untouched.

When actual parameter updates become appropriate, use a rights-cleared trainable base checkpoint with license-compatible adapters, a separate holdout, cross-form creative evaluation, anti-copy tests, and an explicit promotion gate. A GGUF prompt patch is instruction conditioning, *not learned weights*.

## Breadth gaps for subsequent composition work

The existing ocean includes more raps than deeply reviewed folk, R&B, acoustic, instrumental-meter alignment, true multi-performer cyphers, multilingual stress systems, non-Western time signatures and first-person character studies. Expand **complete** examples in missing genre/tempo/form cells, not just duplicated technical 4-line snippets. More is useful only when meaning, musicality and variety also rise.

## Engineering ownership and checks

- Work only on `feature/archive-grounded-lyric-craft-v1` / draft PR #54, rechecking remote SHA to avoid interference.
- Current source base owner: `feature/hf-space-manual-deploy`. Do not publish or trigger another HF deployment from this curriculum pass.
- Version/roadmap authority reconciliation belongs at verified integration, with one deploy owner across chats.
- Basic static/syntactic and integrity checks may run during corpus expansion. The independent creative A/B benchmark is intentionally deferred, respecting the user's ocean-first request.
- Historical CI failures elsewhere in the HF validation lane must be tracked honestly; they are not proof of either success or failure of new song quality.
