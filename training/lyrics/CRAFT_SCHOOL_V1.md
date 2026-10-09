# §wyrlz Original-Lyric Craft School v1 — archival technique synthesis

**Status:** STAGED SOURCE / NOT MODEL-WEIGHT TRAINING / NOT PRODUCTION-ACTIVATED.
**Owner:** \`hf_space/lyric_craft_school.py\` supplies bounded original-song technique to the existing 700M engine. It is not a second music ontology, a retrieval handler, a chat frontend rule, or an independent trainer.

## Source and privacy

An owner-provided conversation archive was reviewed privately for assistant-created song candidates and later user reactions. **No conversation transcripts, private creative lines, private feedback, personal facts, song title rankings or uploaded archive bytes are in this public repository.** The private review corpus remains a user-held artifact. The lessons below describe only abstract craft skills.

## Practices to teach by form, not by wording

- **Full performable verses:** develop a topic for multiple coherent passages, honoring requested length. Movement every few lines is more valuable than a stack of four-line fragments.
- **Rhyme architecture:** internal multi-syllable rhyme pockets, distinct end-rhyme families, natural grammar, meaningful words, controlled transitions between rhyme sounds.
- **Breath/cadence:** alternate quick syllabic runs with intelligible accent lines; leave performance room; do not mistake maximum density for maximum musicality.
- **Story and stakes:** begin with a tangible setting or decision, change the situation, then earn an emotional or narrative turn.
- **Comic mechanics:** establish an understandable scene, misdirect, turn a literal meaning, deliver the punchline, and allow the listener to catch it.
- **Hooks/refrains:** recurrence and altered callbacks can anchor a full song, but a freestyle normally stays continuous. Repetition without meaning is padding.
- **Linguistic freshness:** use the specific subject's vocabulary; avoid defaulting to the same glitch/crown/fire/street/status palette regardless of topic.
- **Output discipline:** song first, actual line breaks, no lengthy preamble or explanation. Preserve explicit user choices on profanity, length, tempo, genre, labels and concept.

## Current integration

- The existing \`music_structure.py\` remains responsible for song/freestyle ontology, structure-only reference separation and verified-source presentation.
- \`lyric_craft_policy\` gates the complementary compact craft prefill to *generation requests only* in \`lfm2_700m_engine.generate_events\`; a projected structure-only follow-up also receives it.
- Song search, lyric retrieval, criticism, analysis and programming turns do not activate the craft prefill.
- Prompt-only changes **do not** change the GGUF model weights or provide independent proof of improved rhyme quality.

## Verification and next gates

1. Run \`python tests/test_archive_grounded_lyric_craft_v182.py\`, plus broader music regression tests against the exact branch head; check that lyrics lookup still retrieves rather than generating.
2. Benchmark at least 12 unseen creative prompts: fast chopper, strong storytelling, absurd humor, long introspective verse, catchy hook, one uninterrupted freestyle, non-rap songwriting, continuity and source-reference isolation.
3. Score syllable performability, end/internal rhyme, section shape, premise originality, explicit constraint adherence, nonborrowed text, repetition/word filler, and generation latency against the untouched current production model route.
4. Only after branch integration, version/roadmap reconciliation and a passing guarded HF release is a **deployed** claim justified. Independently test the hosted model's songs after deployment.
5. Actual weight learning is a distinct project: user-authorized clean samples, rights/privacy review, independent evaluator/holdout, compatible 700M fine-tune/adapter, baseline comparison and explicit checkpoint promotion.

**Safety and concurrency:** The source branch targets the existing HF Chat candidate; do not touch the independently deployed §wyrl§ Engine. The new policy intentionally contains no sampled lyrics and does not override either Project Start or Programming/Model architecture.


## v2 Ocean expansion — parallel archive breadth before quality benchmarking

The continuation is owned by [`LYRIC_OCEAN_CURRICULUM_V2.md`](./LYRIC_OCEAN_CURRICULUM_V2.md) and its indexed exercises/demonstrations:
- [`lyric_ocean_practice_v2.json`](./lyric_ocean_practice_v2.json) — 768 original scenarios, 64 contrastive repair drills;
- [`original_demonstrations_v2.json`](./original_demonstrations_v2.json) — 24 different eight-line treatments;
- [`original_full_compositions_v2.json`](./original_full_compositions_v2.json) — six longer complete-arc drafts;
- [`../../hf_space/lyric_craft_catalog_v2.json`](../../hf_space/lyric_craft_catalog_v2.json) — 48 reusable runtime-specific teaching cards, selectively retrieved by the same 700M craft policy.

The 261-case user-private archive review is deliberately **not** copied into this repository. **No actual model fine-tuning, held-out success labeling, new adapter, or production activation is established.** Existing lyric structure/reference isolation remains in `hf_space/music_structure.py`. The next implementation owner should not silently replace the 700M creative hook with a separate music-policy writer.
