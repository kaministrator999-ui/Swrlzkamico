# 700M harvested verified successes

Canonical pipeline: [§wyrlz 700M Weight-Learning Pipeline](../../docs/engineering/SWRLZ_700M_WEIGHT_LEARNING_PIPELINE.md)  
Project entry: [§wyrlz §tart](../../§wyrlz_§tart.md)

This ledger records successful cases already demonstrated in historical test evidence. It intentionally separates **verified behavior** from **trainable exact-source records**. A case is not moved into JSONL until its exact original prompt, exact candidate bytes, and evaluator receipt are all recoverable.

## Status legend

- **PROMOTABLE** — exact prompt/source/evaluator receipt are all present.
- **EVIDENCE READY / SOURCE RECOVERY NEEDED** — independent pass is documented, but exact candidate bytes or exact prompt still need recovery from retained run artifacts.
- **HELD-OUT CANDIDATE** — preserve for regression rather than training.
- **DO NOT TRAIN** — failure/ambiguous result; useful only as negative/repair evidence.

## Harvested successes

| ID | Capability | Verified result | Training status | Evidence note |
| --- | --- | --- | --- | --- |
| H700-001 | JavaScript sorting repair | Explicit-guidance repair passed named API, frozen input, stable equal timestamps, unchanged input/object references, empty arrays, and singletons; all 4 behavioral groups passed. | EVIDENCE READY / SOURCE RECOVERY NEEDED | Latest repeat documents a real shallow copy and numeric ascending comparator, but the review summary does not contain the full exact candidate bytes. Recover from saved run-results/source before normalization. |
| H700-002 | JavaScript add function | Initial plain-script function passed all 5 arithmetic cases. | EVIDENCE READY / SOURCE RECOVERY NEEDED | Preserve as a compatibility exemplar. Exact saved source and original prompt should be recovered rather than reconstructed from summary prose. |
| H700-003 | JavaScript add ES-module variant | Guided `export function add(a,b){return a+b}` passed all five sums when evaluated as an ES module. | HELD-OUT CANDIDATE | Useful for teaching that arithmetic correctness and loading-format compatibility are distinct. Do not use as a positive target for a plain-script contract. |
| H700-004 | JavaScript chat rendering repair | Earlier correction passed isolated browser checks for literal text, replacement, empty input, unchanged input array, and direct list-item structure. | EVIDENCE READY / SOURCE RECOVERY NEEDED | Recover exact corrected source and unchanged browser fixture from retained round-1 artifacts. |
| H700-005 | Python conversation-history function | Earlier first answer passed all 7 checks, preserving supplied-list identity and independent omitted/None histories. | EVIDENCE READY / SOURCE RECOVERY NEEDED | Strong independent-success example; exact source/prompt need recovery from retained round-1 artifacts. |
| H700-006 | Python API token validation partial | Corrected result passed 17/18 but still accepted `True`. | DO NOT TRAIN | Keep as a negative/repair example only; no independent full pass. |
| H700-007 | Python parse_max_tokens latest repair | Directed repair passed only 1/20. | DO NOT TRAIN | Strong negative example for exact-type/None/range semantics and regression after guidance. |
| H700-008 | JavaScript sorting receipt-only fragments | Wrapper lost/truncated; API could not load. | DO NOT TRAIN | Negative example for complete-source/API preservation. |
| H700-009 | JavaScript add receipt repetition | Forty repeated error headings and no code. | DO NOT TRAIN | Negative example for repetition/no-code rejection. |

## Corpus construction rule

The next normalization pass should recover exact artifacts for H700-001, H700-002, H700-004, and H700-005 from retained test outputs. At least one independently passing case from each capability family should be reserved as held-out rather than trained on.

Do **not** fabricate missing code from these summaries. The historical reviews prove pass/fail behavior, but training requires byte-exact targets and provenance.
