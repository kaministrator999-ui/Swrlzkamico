# Server 2.3.175 — R39 v47 conversation trajectory repair

**Server Runtime:** 2.3.175  
**LALM Engine:** 2.1.58 / `2.1.58-hot-conversation-trajectory-repair-v47`  
**Deployment:** NONE  
**Restart:** NONE

## Purpose

Improve Chat's LALM from longitudinal conversation-export findings without moving cognition into the Chat mask. The Brain now receives a compact trajectory policy that treats dialogue as evolving state rather than isolated prompts and adds bounded correction/convergence handling for normal inference.

## Behavior

- Resolve pronouns, compressed wording, callbacks, slang, coined forms, deliberate punctuation, and Unicode from recent context before asking the user to restate them.
- Preserve meaningful raw surface notation such as `§` rather than silently normalizing it away.
- Distinguish the active conversational thread from superficial keyword/topic similarity.
- Use callbacks only when they help the current turn.
- Calibrate confidence to available evidence: commit when context supports an inference, but do not invent missing facts.
- Calibrate response shape and length to the turn instead of forcing one verbosity template.
- When the current turn looks like a correction, re-read the relevant trajectory, identify the smallest invalidated assumption/referent/scope/relation/tone/abstraction level, preserve unaffected state, and repair the substance first.
- Do not claim a corrected interpretation was intended all along; avoid apology spam and whole-task rewrites when a local repair is sufficient.
- Treat acceptance-like wording as contextual convergence evidence only, not a permanent preference or factual truth.
- Preserve v46 language-preference handling and greeting/check-in repetition behavior.

## Corpus findings represented

This event operationalizes the highest-confidence behavioral lessons from the user's ChatGPT conversation export: correction chains are trajectories rather than binary labels; reactions require context; sparse corrections can be directional; repair should be local; thread continuity differs from topic similarity; confidence should be evidence-calibrated; raw user notation can carry semantics; and response quality depends on response shape as well as content.

The raw export itself is not committed into the runtime model and no personal-fact corpus is hardcoded into the Brain. Behavior, personal memory, and general knowledge remain separate concerns.

## Architecture

- Mask: unchanged; factual transport only.
- Brain/LALM: owns trajectory interpretation, repair policy, confidence calibration, raw-surface semantic preservation, and response-shape guidance.
- Server/body: unchanged except chronological Server event authority.
- Existing zero-prefill social fast paths remain intact.

## Lineage

Baseline authorities at event entry and version-assignment boundary remained:
- Server Runtime 2.3.174
- LALM Engine 2.1.57 / v46

Staged implementation lineage:
- R39 v47 source commit: `137fc1761b5284e7d4e03bf68073ac316734858d`
- v47 hot loader update: `510512e9e24b4bdc7748519574b966e7c844bd89`
- hot inference manifest update: `df16820a94291509f0ea49e94a6e2ed42b50eb43`
- LALM authority update: `5587b513e693193dff56ac8c1e44452a03077d66`
- Server authority update: `76ad37b038fc7d40a3e6f99bda17e287510b3cdc`

## Verification

Before promotion, re-read runtime authorities to detect concurrent advancement. After promotion, verify `runtime_hot/r39_engine.py`, hot manifest revision, LALM authority, Server authority, and engine inspection fields. No Vercel deployment or restart is required for this runtime-hot event.
