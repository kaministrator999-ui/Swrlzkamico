# 700M validated learning corpus

This directory is the governed handoff from runtime evaluation to actual model training.

Only independently accepted examples may be promoted. Generation completion or self-review is not a training label.

Required record fields: schema `swrlz-700m-training-example-v1`, contractId, originalRequest, requirements, candidateId/revision, optional failureEvidence, correctedTarget, evaluator evidence with PASS, language/runtime, provenance, and redaction status.

Promotion: candidate → independent evaluator PASS → normalized example → held-out regression → LoRA/fine-tune candidate → independent regression → checkpoint promotion.

Never include credentials, secrets, unrelated personal profile data, or unverified self-graded outputs.


## §E Model Atelier source-learning track (teacher material only)

The first Forge modeling course is at [../forge-modeling/README.md](../forge-modeling/README.md), with [36 public practice/rubric scenarios](../forge-modeling/academy_v1.json), an optional [bounded context reference](../forge-modeling/model_context_v1.txt), and an [offline source-fixture verifier](../forge-modeling/verify_academy.py). This helps teach the 700M conversation student the difference between interpreting a modeling request, describing editor UI, proposing a currently permitted native edit, and claiming a completed host-side operation.

**No record in the public practice set is a training PASS.** Before a LoRA sample can be harvested, capture the actual model candidate, independent validator/behavioral evidence, exact corrected target and redaction/provenance. Maintain a separate held-out evaluation set. This directory alone does not install a prompt, change inference routes, update weights or deploy Chat.
