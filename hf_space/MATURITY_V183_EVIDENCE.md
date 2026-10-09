# §wyrlz Model Maturity v183 — Verified Discovery and Paired Quality Receipts

**State:** isolated candidate, NOT deployed. Stacked on the still-draft v182 feature branch and must be reconciled/merged in order. Not model training.

## Source and architecture ownership

- Feature branch: feature/task-discovery-replan-v1. Base: feature/coder-adaptive-effort-v1 (draft PR #56). The first-hop estimator and its opt-in Qwen/700M model guidance are upstream in that branch.
- New pure code: hf_space/task_discovery.py and hf_space/maturity_pairing.py.
- New tests: hf_space/test_task_discovery_v183.py and hf_space/test_maturity_pairing_v183.py.
- CI: .github/workflows/verify-maturity-v183.yml, source tests only; no provider credentials, backend inference, secrets, HF deployment, dataset upload, model training or cost-incurring compute.

## Stage 2: after source discovery

The first-hop user-text task score can miss hidden source complexity. The new function reconcile_after_discovery(first_hop, evidence, trusted=False) **can only escalate** the tier when an authorized caller deliberately supplies trusted=True after verifying evidence. No HTTP endpoint or deployed caller currently supplies this privilege. Setting "trusted" or "sourceVerified" inside untrusted data is insufficient.

Evidence schema is purposely finite:
- affectedFiles, affectedOwners, dependencyEdges, failingTests: nonnegative integers capped at 1000; booleans, malformed strings and negatives ignored.
- riskTags: allowlisted tags only; values like authentication, persistence, production-release, destructive, active-credentials and data-loss are interpreted conservatively.
- No raw prompts, source blobs, user profiles, credentials or hidden reasoning are stored in the resulting summary.
- When evidence is missing or untrusted, retain original tier and mark UNVERIFIED_NOT_APPLIED.
- Multimodule verified evidence elevates to DEEP; confirmed destructive or data-loss risk elevates to CRITICAL.
- Never reduce previously known effort or grant tool permission. Authorization remains a separate user/Workstation/deployment mechanism.

**Important limitation:** The function is a pure policy component; a future safe integration needs a real authenticated Workstation tool/source receipt boundary and review. Do not wire model-provided JSON to trusted=True. A risk tier never proves a release is permitted.

## Paired baseline vs assisted-model quality measurement

The offline compare_pairs tool does **not** call GGUF models, assign semantic correctness, audit an external CI receipt or assert model advancement. It handles minimal metadata for baseline and candidate outputs:
- caseId, modelId, checkpointSha256, promptSha256, evaluatorId;
- outputSha256 for each run and a grader record with source=independent, receiptRef, technicalPass and intentPass;
- missing model output, grader, or either of two gates → UNSCORED rather than PASS or FAIL;
- reported pass/failed outcomes are compared only as **REPORTED_IMPROVED / REPORTED_REGRESSED / REPORTED_UNCHANGED**.
- Raw prompt, response, evaluator credential and arbitrary extra record fields are not copied into the returned summary.
- Public practice cases are never claimed to constitute a sealed unseen benchmark. An external reviewer must check actual source/model output and receipts before any performance gate or weight-training decision.

Local CLI after a genuine pair metadata document is assembled:

~~~bash
python hf_space/maturity_pairing.py --input /path/to/metadata.json
~~~

Output is a reported-only aggregate with canAuthorizeDeployment=false and provesWeightTraining=false. Without actual model output hashes and grader receipts, nothing is scored.

## Acceptance and next maturity step

1. Protected v183 branch CI must pass exact SHA, including existing 57 public v182 classification cases and new evidence/quality-contract tests.
2. Actual Qwen coder and LFM2-700M runs require a documented source revision, identical checkpoint and prompt hashes per A/B pair, disabled/enabled policy, stable environment and output receipts.
3. Separately grade both technical behavior (compiler/runtime/actual source evidence) and user-intent satisfaction, including negative constraints and no invented execution claims. One gate alone never passes.
4. Check cost, latency, context loss, extra tool attempts, regression incidence and full response shape across simple and complex prompts.
5. Validate unseen/hard paraphrase cases independently. Do not train on test cases then claim held-out generalization.
6. Merge source only after review and protected regressions. Flag activation and production deployment need their own approval, exact version controls and reversible release gate.
7. Add actual multi-worker/short-job-first scheduling with anti-starvation only in Station/Workstation owner, as a distinct proven feature; source complexity alone must not reorder user tasks without that owner.

**Model growth must be demonstrated by independent work product**. Current code adds a safer mechanism for discovery and the ability to compare reported evidence, not improved weights or successful hosted model competence.
