# v198 — Rap skill ladder and A/B benchmark

**Product decision:** Teach the local 700M performable rap in small, manageable steps instead of adding more simultaneous requirements. Keep user-requested exact lines, tone, no chorus, and narrative constraints as real acceptance checks. This is bounded inference-time guidance, not GGUF model training or a promise of musical quality.

**Research-derived abstractions** (not lyrics, reproductions or artist imitation):
- Beat pocket before wording; fit spoken stresses against a simple rhythmic loop — informed by rap writing/scatting tutorials, including Cole Mize.
- Phonetic rhyme families rather than matching spelling endings — demonstrated in Eminem's pronunciation-based rhyme explanation.
- Contrast dense fast bars with short accented endings and rests — noted in analyses of Tech N9ne's fast rhythmic delivery.
- One understandable punchline setup, then a changed-meaning turn — freestyle practice technique discussed in Harry Mack instructional material.

**Integration:** Original-writing gate in `lyric_craft_school.py` → ONE short cue from `rap_micro_curriculum.py` → existing online-research technique cards → model writes its own lyrics → existing strict shape and completion validator. Five possible focuses: `pocket`, `flow`, `rhyme`, `punch`, `story`. The user gets the full requested output; the lesson isn't an output-length limit. An explicit `without rap coaching` bypasses the cue. Operator disable `SWRLZ_RAP_MICROLESSON_ENABLED=0` is also supported. Only focus identifier, never a private user scenario, enters count-specific validation receipts.

## Live controlled prompts

Run in §wyrlz Chat, then rerun *the same* request with `without rap coaching`. Add `without online research` to BOTH to isolate the local coaching. Later repeat with online research on. Keep any existing 40-bar stress test as a separate challenge; don't silently make it easier.

1. **Pocket (4 bars):** “Write 4 rap bars about losing a bus pass; make the rhythm bouncy; no chorus.”
2. **Rhyme (8 bars):** “Write 8 rap bars about a vending machine eating a dollar, using meaningful multisyllabic internal rhymes; no chorus.”
3. **Flow (16 bars):** “Write 16 chopper rap bars about missing a train, switch between rapid phrases and short hard hits; no chorus.”
4. **Combined stress (40 bars):** “Write a 40-line original chopper freestyle about a clockmaker solving a mystery. Keep it continuous, use meaningful internal rhymes, alternating rapid-fire and short punchlines. No chorus.”

## How to score honestly

- **Mechanical gate:** exact lyric line count, requested no-chorus/continuous form, no refusal/prelude; incomplete output is a failure.
- **Human performance gate:** can a rapper actually land the stresses and breathe? Are phonetic rhymes natural, setups/punchlines intelligible, meaning advancing, and repeated/filler lines limited?
- **Runtime evidence:** `candidateValidation.rapMicroFocus`, `candidateValidation.lyricResearch`, attempt count, generation time, and whether cache was used. Do not infer quality solely from those fields.
- **Limitations:** Source CI validates contracts and short cues, not sung or spoken flow. Actual A/B quality requires a real live model output and comparison; no quality improvement is claimed before that evidence.
