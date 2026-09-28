# §wyrlz LALM v1.2 Integration & Deduplication Map

## Purpose
Integrate the supplied LALM Reasoning Architecture v1.2 document set without teaching the same behavior twice. Existing implemented §wyrlz behavior remains canonical where it already satisfies a v1.2 concept. The v1.2 material contributes only missing control semantics, stronger formal structure, or new regression coverage.

## Source lineage
Authoritative supplied v1.2 sources:
- `LALM_Reasoning_Ontology_Programmable_Control_Architecture_v1.2.docx`
- `LALM_Unified_Intent_Reasoning_Execution_Presentation_Lexicon_v1.2.docx`
- `LALM_Reasoning_Control_Protocol_Mode_Matrix_v1.2.docx`
- `LALM_Intent_Reasoning_Control_Test_Suite_Rubric_v1.2.docx`

The architecture archive also contains v1.0/v1.1 lineage. The separate legacy-originals archive duplicates those historical v1.0/v1.1 documents. Legacy files are provenance/reference, not an additional runtime teaching layer.

## Canonical deduplication rule
Before adding any concept:
1. normalize its semantic meaning;
2. locate an existing §wyrlz rule/control/eval with the same behavioral effect;
3. classify it as **EXISTING**, **EXTEND**, **NEW**, or **LEGACY-ONLY**;
4. keep exactly one canonical runtime owner;
5. add aliases/cross-references to that owner instead of duplicating prose;
6. add a regression only when it tests a genuinely new axis, boundary, or composition behavior.

Do not count synonymous wording as additional intelligence. Inheritance and aliases should compress repeated semantics.

## Crosswalk: v1.2 → current §wyrlz

| v1.2 concept | Existing §wyrlz owner | Classification | Integration |
| --- | --- | --- | --- |
| Intent before reasoning | SIMPLE-FIRST / DYNAMIC MIRROR | EXTEND | Formalize as control pipeline; do not duplicate prompt prose |
| Reasoning depth independent of presentation length | ADAPTIVE EXPRESSION + response modes | EXTEND | Add explicit independent fields in control contract |
| Evidence / epistemic calibration | EVIDENCE & CORRECTION, EVIDENCE BEFORE AGREEMENT, NO PREMISE AMPLIFICATION | EXISTING | Reuse; map v1.2 epistemic labels onto same owner |
| Current state outranks assumptions | Project Mode source-of-truth-first | EXTEND | Add state-awareness field and tests |
| Tool/mutation authority boundary | Existing explicit-approval/deployment governance | EXTEND | Formal mutation-authority ladder; no new permission implied |
| Corrected referent / intent repair | CORRECTION ECONOMY | EXISTING | Alias v1.2 repair semantics to existing rule |
| Stop when complete | CONVERSATIONAL response mode / NO ECHO TAX | EXTEND | Add explicit stop-condition field |
| Concise ≠ shallow | SIMPLE-FIRST + ADAPTIVE EXPRESSION | EXTEND | Regression for brief + deep composition |
| Compound modifier preservation | none as formal resolver | NEW | Add composition/conflict resolver |
| Reasoning objective | none as structured field | NEW | Add objective vocabulary/schema |
| Reasoning modes/pipelines | Project Mode is coarse only | NEW | Add composable mode configuration; no persona replacement |
| Verification ladder | validation exists operationally but not normalized | NEW | Add explicit verification level |
| Presentation contract | response modes/formatter exist | EXTEND | Normalize length/order/include fields |
| Epistemic provenance labels | evidence rules exist but labels not normalized | NEW | Add observed/retrieved/derived/inferred/assumed/unknown representation |
| Memory provenance | corpus memory contract | EXISTING/EXTEND | Bind control decisions to USER→AI / AI→USER / RAPPORT / THREAD-ONLY |
| Ontology inheritance | no serialized concept registry yet | NEW | Future registry should use inheritance to prevent duplicated rules |

## Compact control contract
The v1.2 documents define a richer internal grammar. For the current small-model path, the target is a compact resolved contract, not the full documents in every prompt:

```text
intent.operation
intent.target
intent.scope
reasoning.objective
reasoning.modes[]
reasoning.depth
reasoning.breadth
reasoning.technicality
reasoning.evidence_threshold
reasoning.state_awareness
execution.mutation_authority
execution.allowed[]
execution.forbidden[]
verification.level
presentation.length
presentation.density
presentation.order
presentation.include[]
memory.provenance_lane
stop_condition
```

Only activated/non-default controls should eventually be serialized into the 700M context.

## Memory coupling
Control resolution and memory must not evolve independently:
- intent/reasoning results are normally THREAD-ONLY;
- explicit durable user facts may create USER→AI candidates;
- stable §wyrlz identity/capability facts belong AI→USER;
- shared callbacks/conventions may belong RAPPORT only with provenance;
- inferred reasoning conclusions must not silently become durable memory;
- corrections must be able to supersede stale durable candidates when persistence is implemented.

## Test-suite merge policy
The supplied v1.2 rubric extends—not replaces—the existing archive-derived behavior evals. Deduplicate tests by behavioral property. Keep archive-derived tests for conversational repair/rapport failures; add v1.2 tests for independent control dimensions, authority, state, epistemics, composition, and reasoning/presentation separation.

## Truth state
This document is an integration map. It does not claim that a structured reasoning controller, ontology registry, durable memory, or mutation-authority engine is live. Current 700M behavior remains prompt/rule driven plus deterministic response-mode selection and conservative MEMORY_CANDIDATE extraction.


## Convergence learning architecture

The 700M path now has a lightweight **Convergence Candidate** concept to connect collaborative discovery with later intelligence improvement without turning every conversation into permanent memory.

### Purpose
When a thread contains a real repair/discovery trajectory and the user explicitly confirms the resulting answer, §wyrlz may emit a compact review candidate. The candidate preserves enough of the local trajectory to support later analysis while remaining **THREAD-ONLY** and **review-only**.

### Runtime event
`CONVERGENCE_CANDIDATE` / schema `swrlz-convergence-candidate-v1`

Current detector is intentionally conservative and deterministic:
- requires prior correction/scope-repair language in supplied history;
- requires an explicit user confirmation marker in the current turn;
- emits no extra model inference pass;
- never writes durable memory;
- never self-promotes a rule or fact;
- carries a bounded recent trajectory window for later review.

### Review/promotion pipeline
```text
thread trajectory
→ convergence candidate
→ human/system review
→ extract validated conclusion + pattern + failed approach + decisive cue/evidence
→ classify epistemic status and provenance
→ deduplicate against existing knowledge/rules/evals
→ route to one or more destinations:
   knowledge
   pattern-recognition library
   behavior/intelligence rule
   USER→AI memory
   AI→USER self/project knowledge
   RAPPORT memory
   regression/eval
→ future retrieval/recognition
```

The trajectory is evidence; it is not the final teaching itself. The goal is to let later §wyrlz builds compress previously expensive discovery into faster recognition when conditions match, while retaining the original path as fallback evidence.

### Compression gain
Reviewed convergence records should eventually track whether the same class of problem requires fewer turns after promotion. A useful future metric is:
- original turns-to-convergence;
- later analogous turns-to-convergence;
- whether a validated one-turn answer became possible without loss of correctness.

### Latent-answer recognition
A separate target behavior is **latent-answer recognition**: if §wyrlz's own generated reasoning/context already contains a sufficient answer, foreground it instead of continuing to search, elaborate, or contradict it. This is distinct from missing knowledge and should receive dedicated regression coverage.

### Deduplication requirement
Convergence review uses the same EXISTING / EXTEND / NEW / LEGACY-ONLY gate as the v1.2 architecture merge. Rediscovering an existing concept should strengthen evidence, add conditions/exceptions, or add a distinct regression—not create a duplicate teaching.
