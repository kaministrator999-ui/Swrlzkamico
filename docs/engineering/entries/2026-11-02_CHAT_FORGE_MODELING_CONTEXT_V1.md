# §C Model Atelier contextual teaching v1 — candidate engineering receipt
**Date:** 2026-11-02
**Status:** SOURCE CANDIDATE; model inference evaluation and deployment NOT YET VERIFIED.

## Scope
User authorized connecting the Model Atelier Academy to the existing §C conversational 700M, Qwen coder, and Qwen native planner. This candidate belongs to the existing `hf_space` Chat code and does not modify the independent §E engine source, protected source manifest, native editor operation allowlist, Google/account stores, or the §E deployment request.

## Source owner and placement
Base branch: `feature/chat-forge-exact-design-approval-v2-20261031`.
New `hf_space/forge_modeling_lessons.py` is a pure, small, topic-gated reference selector. It chooses at most one relevant subject paragraph and emits at most 1,150 characters; unmatched ordinary tasks emit zero extra context. It requires a modeling term plus either explicit §E/Forge/Model Atelier reference or a trusted Model Atelier workspace summary from the original server source.

- `hf_space/lfm2_700m_engine.py`: optional bounded lesson next to existing read-only `nativeEditorEvidence` prompt policy.
- `hf_space/qwen_coder_engine.py`: same selector for coder/conversation answer route.
- `hf_space/brain_forge.py`: existing JSON-only native planner includes modeling context only when relevant.
- `hf_space/forge_chat_actions.py`: pass the current human request and server-revalidated native snapshot to the existing Brain-owned planner. No new permissions or operations.
- `hf_space/test_forge_modeling_lessons_v1.py`: local deterministic teacher-source checks (not a student-evaluation PASS).

## Truth and safety
The current native Chat Model Atelier operation allowlist remains mesh.add/set/select/duplicate/remove plus native editor.undo/redo in isolated batches. Existing `project.create` remains one operation in a fresh project-specific batch; grouping, component sculpting, UV/texture mapping, rigging, animation and Quest hand tracking are NOT newly exposed to the Chat tool. The active host lease, approval/preview, exact validated snapshot IDs, server and host receipts and failed/unknown mutation handling stay with their original owners. No training weights are changed by a prompt-context patch.

## Evidence and limitations
The related main-branch Academy has 36 public source-grounded practice cases (source/anchor checks previously 36/36). This branch adds a deterministic routing test file. The GitHub connector can read/write source but does not provide a model inference runner or an executable Python shell in the target repository; do not claim the new test file ran, that student answers passed, or that a Hugging Face revision contains these edits without a separate observed test/deploy receipt.

Before release, run `PYTHONPATH=hf_space python hf_space/test_forge_modeling_lessons_v1.py` and compile modified Python modules, verify exact target branch/revision and protected no-op behavior on unrelated requests. Then run separate instrumented student probes: at least one 700M read-only how-to, one Qwen edit planning case, one unsupported rigging case, one negated/destructive request and one stale/missing-host case. Keep true held-out cases distinct from the public Academy. No live editing without actual user approval and native receipts.

## Corrective source evidence
The original patch attempt briefly introduced one escaped newline in the Brain function signature and a duplicate Qwen injection while tool actions were overlapping. Both were explicitly removed/repaired on this feature branch before review. Historical failure is retained here; no test PASS is inferred from static source inspection.

## Delivery
**Current status:** PR-ready candidate. Do not rotate `.deploy/HF_SPACE_REQUEST.txt` or claim that either model's weights were trained. A later source-compatible, guarded Chat-only release and live behavioral acceptance is required to call this active.
