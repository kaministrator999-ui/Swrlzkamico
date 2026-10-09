# §wyrlz Lyric Ocean v4 — Formal Diversity + Source-Anchored Editing

**Project workstream:** `§wyrlz_§tart.md` → Chat/LFM2-700M creative lyric path.
**Candidate only:** `feature/archive-grounded-lyric-craft-v1`, draft [PR #54](https://github.com/kaministrator999-ui/Swrlzkamico/pull/54).
**Not production. No GGUF weights changed. No independent live-model creativity benchmark or LoRA training.**

## Ocean-first progress as inspectable, distinct source material

| Material | Count | Provenance and validity |
| --- | ---: | --- |
| Private creative archival candidates | 261 across 172 conversations | Private user export, all source lyrics kept off GitHub; mixed/uncertain signals |
| Original prompt combinations | 768 | Public synthetic scenarios (48) × craft lenses (16), NOT_RUN |
| Metadata-only repair drills | 64 | Synthetic bad-pattern/repair goals, NOT_RUN |
| v2 short lyric demonstrations | 24 / 192 lines | Public source-independent instructor drafts |
| v2 longer full-arc studies | 6 / 196 lines | Public source-independent instructor drafts |
| v3 longer full-arc studies | 8 / 252 lines | Public source-independent instructor drafts |
| v4 contrasting formal studies | 8 / 249 lines | Public source-independent instructor drafts, ungraded |
| **Total complete song studies** | **22 / 697 lines** | Pending independent editorial, rights and vocal-performance review |
| **Total complete + short illustrative lines** | **889 lines** | Teaching exposure, not gold SFT targets |
| v3 explicit before/after repair cases | 24 | Public synthetic, ungraded |
| v4 line-anchored proposed source revisions | 14 | Concrete public song passages; revisions unapproved |
| General 700M craft cues | 48 | Bounded selector chooses two |
| Form-specific cues | 8 | At most one per explicit form request |
| Provisional editorial reviews | 14 | Same-author assistant scores, NOT blind or independent |
| Editorial rubric dimensions | 12 | Anchored 0–4 descriptions, no self-certified gold |

The v4 form-gap studies deliberately go beyond repetitive 32-line narrative rap. `CROSS_FORM_COMPLETE_SONGS_V4.json` includes **intimate R&B (30 lines), ensemble percussion cypher (28), gentle lullaby (28), uneven-count art rock (32), unrhymed spoken word (27), clipped funk (32), chopper freestyle (40), and acoustic folk story (32)**. These are **intended rhythmic shapes**; no audio or live musician alignment has been verified. A 5/4 label alone cannot establish actual five-beat musical accuracy.

### What is better about the editorial discipline

`PROVISIONAL_EDITORIAL_PASS_V4.json` reviews all 14 preceding longer synthetic songs (v2 + v3) along five applicable rubric dimensions and includes exact cited **line numbers** for strengths and defects. These scores are explicitly *assistant provisional* and may be biased because the author is reviewing its own work. Do not promote them to independent evaluator scores.

`EVIDENCE_LINKED_REVISIONS_V4.json` extends that feedback into 14 specific proposed before/after repairs, each referring to the **exact original public song line**. A check verifies matching source text. Two edits explicitly warn that surrounding lines must also be changed to avoid creating a new context/rhyme defect. **These are unapproved candidate edits, not silent amendments to the evidence songs.**

Source ownership and traceability matter: old versions remain untouched, critical observations point to exact lines, and editorial edits don't overwrite a previous example simply to improve a score.

### 700M direct conditioning, kept affordable

- The original `hf_space/music_structure.py` ontology and structure-only reference isolation remain authoritative.
- `hf_space/lyric_craft_school.py` still gates original writing, not lyric lookup, coding or critique. It combines compact general guidance, **two relevant general cue cards**, and at most **one additional form-specific card** when the user explicitly specifies its form.
- `hf_space/lyric_form_cues_v4.json` carries eight abstract hints. It contains no lyric lines or personal archive text.
- The entire public ocean **does not get inserted into each inference**: no expensive growing per-request prefill, no verbatim reference memorization, and no user-private archive exposure.
- Source updates to this branch are not yet a deployed model improvement. The 700M may only actually use these cues after accepted guarded integration to the Hugging Face Chat candidate.

### Verification and separation

The dedicated `.github/workflows/lyric-ocean-integrity.yml` validates corpus counts, exact evidence anchors, creativity-only prompts, bounded form-selection cues and Python syntax on relevant PR changes. The older HF candidate offline suite may still fail its three pre-existing unrelated assertions about `coder` route enumeration, an old code-artifact expectation, and obsolete `kind=="DELTA"` source spelling. Treat those as separate project work, never mask them through unrelated lyric revisions.

### Further breadth before artistic benchmark

Extend long-form examples in genuinely missing cells (non-English prosody with qualified speakers, true instrument-grounded timing, diverse performer roles, gospel/choir alternatives, acoustic harmony, rap without scenery-driven narrative, and song styles that call for far less text). Keep the content fresh instead of permuting the same hook or rhyme words.

After enough clean, independent editorial coverage, freeze a corpus version, reserve **new unseen** prompts, and score baseline/current candidate under identical inference conditions. Do not test model quality on training/exposure items; the user explicitly prioritized depth before the main creative evaluation.

**Weights boundary:** GGUF files cannot be considered newly trained from prompt policy or a stored dataset. Only an actual supported fine-tune/adapter, rights/consent review and independent acceptance process could justify that claim. No such work has run.
