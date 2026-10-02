# 700M validated learning corpus

This directory is the governed handoff from runtime evaluation to actual model training.

Only independently accepted examples may be promoted. Generation completion or self-review is not a training label.

Required record fields: schema `swrlz-700m-training-example-v1`, contractId, originalRequest, requirements, candidateId/revision, optional failureEvidence, correctedTarget, evaluator evidence with PASS, language/runtime, provenance, and redaction status.

Promotion: candidate → independent evaluator PASS → normalized example → held-out regression → LoRA/fine-tune candidate → independent regression → checkpoint promotion.

Never include credentials, secrets, unrelated personal profile data, or unverified self-graded outputs.
