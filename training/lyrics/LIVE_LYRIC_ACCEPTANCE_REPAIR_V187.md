# Live Lyric Acceptance Repair v187 — Source-grounded handoff

**Private input:** The user provided an exported 700M Dragon Chat session for a creative 40-line continuous freestyle with no chorus. The private JSON and its assistant lyrics were analyzed locally; **neither the export nor any verbatim generated line is committed to the public repository**.

## Actual v186 failure (2026-10-09)

- User requested exactly **40** lyrical lines and a continuous, no-hook freestyle; actual response contained **36** lyrical lines in nine four-line stanzas.
- The response had an unnecessary refusal before the lyrics, a self-certifying note after, repeated generic words, and no observable finished mystery arc. Internal rhyme/cadence quality remained weak.
- On-device route selected the intended `700m`, `candidateValidation.status=NOT_APPLICABLE`, `candidateAttempts=1`, `maxResponseTokens=768`. No structured lyric acceptance guard was applied. The run took about **26.1 seconds**, with first visible delta around **13.4 seconds**; those are observational values for this one case, not a population benchmark.
- Source cause: direct-song turns fell through the generic streaming route; the existing buffered, source-isolating verifier only handled structure-only *reference transformations*. User request was ordinary original writing and bypassed that verifier.

## v187 source correction

- `hf_space/lyric_output_contract.py` extracts bounded explicit line count (4–120), continuous verse and no-chorus constraints **only after an original-writing intent gate**. It distinguishes actual lyric lines from refusals, metadata and section labels. It rejects incorrect counts, unrelated pre/post commentary, unrequested chorus labels and stanza gaps when continuous was requested.
- `hf_space/lfm2_700m_engine.py` keeps model choice, programmer/repair routing, imported reference-structure logic and normal conversational streaming intact. **Explicitly constrained direct creative lyrics** now get a bounded output budget (**1600 tokens for the observed 40-line case; up to 2048 for longer requested cases**), buffered draft validation **before display**, and at most **one** source-independent correction attempt if formal constraints fail. No fabrication/padding of missing lines. Presentation is one copyable lyric block only when the formal gate passes.
- When both drafts violate hard formal constraints, a bounded honest failure statement is returned and `CANDIDATE_VALIDATION` remains `REJECT`; do **not** pretend an incorrect count or refusal meets the contract. Workstation operational completion is distinct from artistic acceptance.
- `tests/test_lyric_output_contract_v187.py` reproduces the **36-of-40 / refusal / explanatory note / separate four-line stanza** failure using an invented synthetic fixture; tests the correct 40-line acceptance, explicit no-hook/continuous checks, no lyric invention, and non-creative request isolation.
- Existing Lyric Ocean integrity workflow includes this new regression and module compilation.

## Evidence and boundaries

- Latest exact candidate commit is discoverable at the head of `feature/lyric-output-acceptance-v187`; all changes reviewed as draft [PR #61](https://github.com/kaministrator999-ui/Swrlzkamico/pull/61), stacked on the **already deployed** v186 lyric source, not concurrently active coder branches.
- Static HF + lyric CI must be green on the candidate's exact SHA before any future guarded release.
- **Semantic truth limitation:** Deterministic PASS certifies observable line/form/metadata rules only. It cannot tell whether a phrase is a meaningful rhyme, whether the mystery was genuinely solved, or whether a performance fits a beat. The 700M has **not** been fine-tuned; the creative-craft curriculum is still abstract prompt conditioning.
- A real new hosted/user playback is required to establish meaningful artistic progress. With buffering and an optional retry, some requests may show longer time before text appears; avoid claiming latency improvements without actual evidence.

## Next owned acceptance

After guarded publication, compare the same user prompt under `700m`: requested line count, single uninterrupted verse, no pre/post, `candidateValidation` PASS/REJECT, attempt count/first-response latency, how clues accumulate and whether the mystery actually resolves. Keep a separate human editorial score for rhyme/multisyllabic pockets and deliverability; don't turn structural PASS into a high artistry grade.

**Confidentiality:** User-proprietary chat context and historical favorite lyrics remain off-GitHub and are never included in model inputs by this patch.
