# §C broad conversational evaluation — research, songwriting and general chat

**Date:** 2026-11-15/16 (UTC). **Mode:** anonymous, isolated guest sessions on the existing live Hugging Face Space `kamiloki/Swyrlz` (`modelId=700m`; explicit public-source lookup requested via `profileId=LALM+ONLINE`). **Deployment changes:** none. This is an evaluation, not a new release.

## Baseline run

[GitHub Actions run 43794957113](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43794957113), with individual machine-readable transcripts uploaded as three artifacts:

- `swrlz-broad-guest-qa-research-43794957113`
- `swrlz-broad-guest-qa-songwriting-43794957113`
- `swrlz-broad-guest-qa-conversation-43794957113`

**9 two-turn scenarios / 18 committed replies.** The diagnostic outcome is **4 PASS_EVIDENCE, 5 REVIEW, 0 BLOCKED** at the scenario level. A committed reply can still consist entirely of a failure message, so these are not 18 successful generations. Research: **0/3 full scenarios passed**. Songwriting: **0/2 full scenarios passed**. Ordinary chat: **4/4 passed mechanical gates**, with editorial caveats.

All test prompts and original generated text are in `scripts/eval_chat_research_lyrics_conversations.py` and the GitHub artifacts. Each scenario runs alone in its own guest browser session; no login, user archive, source deployment, existing copyrighted lyric text, or account file is used.

## Research findings

**Diablo II: Lord of Destruction**: first answer passed **11/11 checks** in **1.6s**, naming seven classes exactly once and correctly identifying the two expansion additions. Its two Blizzard source URLs are real and support these facts:

- https://classic.battle.net/diablo2exp/faq/general.shtml (base-game five)
- https://news.blizzard.com/en-us/article/23460551/diablo-ii-continues-to-inspire-blizzard-20-years-later (Assassin and Druid in LoD)

The subsequent follow-up (again **1.6s**) refused to name those two classes, stating it could not verify the roster from primary sources. The first response's research context was not reliably reused across turns (`RESEARCH_UNAVAILABLE` phase).

**Blues versus pop music form**: the prompt requested research into twelve-bar **AAB** verses versus verse/pre-chorus/chorus architecture and explicitly forbade copying published lyrics. The research router returned `LYRICS_VERIFICATION_BLOCKED` in **1.6s**, incorrectly treating music-form research as a request to recover existing song lyrics. All 5 factual/form checks failed. The following original two-stanza AAB generation reached the creative path, then committed `Generation failed: HTTP Error 500: Internal Server Error` after **186.2s**. The generation error is not a legitimate song.

**Boom-bap versus trap rhythmic flow**: the request compared beats, subdivisions, hi-hats and hook placement with public citations, and did not request existing lyrics. Research again returned `LYRICS_VERIFICATION_BLOCKED` in **1.6s**. The subsequent original eight-bar rap/short-hook request failed with HTTP 500 after **60.1s**. Structure, internal rhyme and cadence were therefore not actually tested for the rap case.

External form references used as the evaluation oracle (not supplied as a private answer to the model): Smithsonian Folkways https://folkways.si.edu/poetry-ballad-blues-stanzas/music/article/smithsonian and https://folkways-media.si.edu/docs/folkways/artwork/BRI00003.pdf ; Berklee College of Music https://online.berklee.edu/courses/songwriting-writing-hit-songs?pid=4727 and https://college.berklee.edu/bt/news/essential-features-of-hip-hop-production-tempo-instrumentation-rhythmic-feel-and-sonic-density.

## Original-song findings

**Synth pop:** a fully original song titled *Signal in the Rain* with prescribed sections was misrouted to a weather task. In **0.3s**, §C asked for a city or location instead of writing lyrics (`WEATHER_RETRIEVAL_BLOCKED`). The revision then triggered `LYRICS_VERIFICATION_BLOCKED` in **1.9s**. This is an intent-routing error, not evidence of poor rhyming or weak melodies.

**Country storytelling:** first generated a substantial, original lyric in **97.7s** with Verse 1, Chorus, Verse 2, Chorus, Bridge and Final Chorus; repeated chorus text was preserved on the **69.1s** revision. It omitted the requested standalone title. The revision retained the porch-light scene and transformed “son” to “sis”, but did not unambiguously establish the requested **sister as the sender**. Its story's causal details and bridge are also editorially weaker than mere section-label checks suggest. **6/7** and **2/3** checks, respectively. No audio or beat-alignment was tested; textual form is not proof of musical flow.

## Ordinary-chat findings

All four two-turn scenarios passed their programmed checks (8/8 replies), with a median committed-response latency of **40.8s**:

- **Corrections and retained constraints:** mascot silver owl preserved, banner teal correctly changed to amber (**7.8s / 43.1s**).
- **Kitchen planning:** correctly reprioritized preheat, vegetable prep and chilled-container labels when 30 minutes became 18 minutes (**26.2s / 52.4s**). Editorial problem: invented a “relief cook who just arrived” without any basis in the user's scenario, while the coworker had actually called out.
- **Overtime math:** computed $475 and then $570 correctly, with regular/overtime components, using the requested 45h and 40h threshold (**67.7s / 35.4s**). Editorial problem: intermediate notation included `$40 - 40 = 0 hours?` and `$40 × 12`, confusing dollars with hours, despite correct final numbers.
- **Humor to debugging:** understood “gremlin in the app” metaphor, then gave plausible debugging categories (**38.6s / 64.7s**). Technical problem: the suggested `buttonElement.getEventListeners()` is **not** a standard DOM method; Chrome DevTools exposes `getEventListeners(element)` as a console helper, not an element method. `buttonElement.addEventListener.toString()` also does **not** show registered listeners. Keyword grading missed this failure.

## Diagnostic interpretation

The **primary current failure is intent dispatch**, not lack of general conversational ability. Music theory research and original song creation are being incorrectly caught by protected lyrics retrieval and weather heuristics. These guards should remain for genuine current weather and requests to retrieve copyrighted lyrics, but not trigger on ordinary discussion of blues/pop form or on original-song titles containing “rain”.

The research evidence should be tagged and preserved across turns with explicit provenance so a correctly sourced fact does not become “unverified” in the immediate next response. The HTTP 500 creative-generation failures need separate server-side investigation; do not treat an error string as a successful song or assume prompt text was the cause without runtime logs.

For songwriting, add evaluation that inspects: repeated chorus/hook preservation across revisions; genre-appropriate *but flexible* arrangement; AAB lyric line repetition in blues; numbered bar count and internal rhyme in rap; narrative movement across verses; bridge contrast/turn; and preservation of named people/story facts. Musical performance, actual stressed syllables and timing against a beat need audio/beat or human-performance evidence—**not** claims based on line labels alone.

## Highest-priority corrective investigation (not deployed in this test)

1. Unit-test intent routing with contrastive requests: “research AAB blues form” vs “retrieve the lyrics to an existing song”; “write a synth-pop song titled Signal in the Rain” vs “show rain forecast for Chicago”.
2. Inspect research provenance handling and immediate follow-up context; prevent repeating an unsupported lookup when the same conversation already contains adequate verified sources.
3. Inspect genuine creative-music HTTP 500s, with the exact generation phases and server error class, then verify resource handling, bounded retry/fallback and truthful failure reporting.
4. Add genre- and story-aware lyric QA alongside existing generic response checks; do not overfit to one canned verse template.
5. Strengthen conversational factual QA for invented entities, dimensional math, and browser API correctness rather than relying solely on keyword presence.

**Run semantics:** `PASS_EVIDENCE` means the chosen mechanical checks passed. `REVIEW` means at least one check failed; these are not all independent model or infrastructure defects. The original response and a concise failure list are retained for human review.
