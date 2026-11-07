# §C Vision v2 — Single-image deep analysis and evidence fusion

Status: **design proposal, not implemented or deployed**. This document does not change production model configuration. Scope: local Hugging Face Space image analysis; no third-party inference API or unapproved hardware upgrade.

## Goal

Treat a complex single image (turnaround, blueprint, UI, diagram, comic, screenshot, reference sheet) as a *related collection of spatial views*, analogous to integrating consecutive screenshots of one long answer. Reconstruct subject identity and cross-panel relationships **before** generating a user-facing answer. Preserve observations and provenance without fabricating details or forcing a short reply.

## Verified baseline (source audit, 2026-11-06)

- `hf_space/chat_vision.py`: `ggml-org/SmolVLM-500M-Instruct-GGUF`, pinned Q8_0 weights and mmproj.
- Overview: longest side 384px, up to 88 generated tokens; detail retry 640px / 144 tokens; manual L3 768px / 192 tokens. Crops already derive from original image rather than a downscaled intermediary.
- Existing paths: `_prepare_image`, `_detail_regions`, `_reference_figure_columns`, `_cross_view_evidence_index`, `_ask_vision_local`.
- `hf_space/model_router.py`: `_vision_evidence_digest`, `_ground_vision_handoff`, `_guard_vision_answer`; a fallback can replace hallucinated stories with observed facts. The recent 2–4-sentence preference is too restrictive for complex reference sheets.
- `hf_space/requirements.txt` currently pins `llama-cpp-python==0.3.35` (CPU wheels). Compatibility with Qwen3/3.5 multimodal variants must be tested; official GGUF existence alone is NOT runtime verification.
- `hf_space/runtime_capacity.py` already provides read-only cgroup CPU/RAM limits and observed consumption. Inspect live measurements before committing to parallel models or upgrades.
- The original uploaded pixels stay in request memory; retain that privacy and auth contract.

## Planned stages and acceptance criteria

| ID | Stage | Input -> output | Failure / validation |
|---|---|---|---|
| 0 | Source fidelity | Uploaded source bytes -> oriented dimensions, hash per request, original-resolution working image | Reject oversized/invalid data; never silently upscale or claim original pixels were retained when unavailable |
| 1 | Global survey | Source -> image category, subject count hypothesis, page layout, headings, overall composition | Distinguish page sections from story frames; record uncertainty. Do not classify every whitespace gap as a panel |
| 2 | Region discovery | Overview + original pixels -> semantic ROIs with normalized bounding boxes and region labels | Validate box boundaries, overlap and coverage; detect columns, panels, insets, close-ups and diagram labels instead of fixed equal slices |
| 3 | High-detail inspection | Each ROI sourced from original pixels -> observable traits, objects, shape, material/color clues, symbols, visible text | Use adaptive crop size and output budget, not a blanket 88-token ceiling; never claim unseen detail |
| 4 | Entity linking | ROI observations -> stable subject and object IDs, candidate cross-region links, spatial relationships | Recognize one character shown five ways; keep independent characters separate; mark ambiguous associations |
| 5 | Evidence reconciliation | Linked observations -> merged facts, conflicts, alternatives, provenance | “stick/wand/purple object” may describe one accessory; do not assert three objects; do not arbitrarily discard contradictions |
| 6 | Selective re-inspection | Uncertain material claims -> bounded targeted second looks and updated evidence | Spend extra inference only on unresolved, relevant claims; stop at a configurable budget and report remaining uncertainty |
| 7 | Grounded synthesis | Evidence graph + user query -> natural, appropriately detailed response | A character sheet merits detail; no hard 2–4-sentence cap. Distinguish observed traits from inferences, no invented powers |
| 8 | Task-specific reasoning | Grounded description + established project context -> relevant modeling/UV/material/animation guidance when requested | Geometry-vs-texture advice must cite observed shape/surface clues; no unasked-for fictional lore |
| 9 | Provenance and telemetry | Actual stage events and source records -> UI status and exportable records | Events represent real work, not decorative “thinking”; separate pending, success, failure, cancellation, model inferences and user-visible answer |

## Proposed internal record (not a required public API)

```json
{
  "schema": "swrlz-vision-evidence-v2",
  "model": {"repo": "pinned-model-id", "revision": "immutable-revision", "backend": "tested-runtime"},
  "layout": {"kind": "turnaround-sheet", "confidence": "tentative"},
  "regions": [{"id": "view-1", "bbox_xywh_norm": [0.0, 0.0, 0.2, 0.7], "label": "front?", "status": "model-suggested"}],
  "entities": [{"id": "subject-1", "kind": "character", "region_ids": ["view-1", "view-2"], "link_status": "tentative"}],
  "observations": [{"subject_id": "subject-1", "region_id": "view-2", "attribute": "hair", "value": "white", "source": "vision-model-output", "verified": false}],
  "unresolved": [{"question": "Is handheld object a wand or staff?", "region_ids": ["view-1", "view-3"]}],
  "events": [{"stage": "high-detail-inspection", "state": "completed", "elapsed_ms": 0}]
}
```

Coordinates are illustrative schema examples, NOT model-derived boxes. “verified” means verified against source pixels by a separate check/human; model agreement alone is not proof. Prefer confidence categories over invented numerical scores.

## Model candidate bake-off (no production swap without tests)

1. **Qwen3.5-2B**: strongest first *evaluation* candidate from Qwen's reported vision metrics; official multimodal weights, community GGUF conversions. Validate encoder/projector, quant, llama.cpp integration and runtime.
2. **Qwen3-VL-2B-Instruct-GGUF**: official Qwen GGUF plus matching projector, documented current llama.cpp support.
3. **SmolVLM2-2.2B-Instruct-GGUF**: useful within-family comparison against 500M.
4. **Qwen3-VL-4B-Instruct-GGUF**: higher-cost challenger if measured latency/capacity permits.

Sources: https://huggingface.co/Qwen/Qwen3.5-2B ; https://huggingface.co/Qwen/Qwen3-VL-2B-Instruct-GGUF ; https://huggingface.co/ggml-org/SmolVLM2-2.2B-Instruct-GGUF ; https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct-GGUF .

### Runtime compatibility gate

Current `llama-cpp-python==0.3.35` is **not automatically validated** against newer GGUF vision architectures. Reproduce a one-image load + projector inference in an isolated candidate environment; if unsupported, benchmark a newer pinned llama.cpp/libmtmd or an isolated `llama-server` backend behind a small adapter. Preserve the existing production baseline until real loading and contract tests pass. Do not assume the server's physical hardware; check existing cgroup observations.

## Benchmark harness

Use the same **original** images and prompts for each model and pipeline configuration:

- 5-view character turnaround + accessory/inset/palette details (user-owned reference only with explicit consent to add permanent fixtures; synthetic fixture otherwise).
- UI screenshots with overlapping panels; blueprint with labels, inset closeups and dimensions; ordinary single-object photo; multi-entity scene; ambiguous/cropped/blank input.
- One-image-with-many-panels test and multiple-separate-images-of-the-same-source test must converge on the same relationships, not necessarily identical phrasing.
- Ground-truth checklist per sample: regions and directions, subject identity links, supported attributes, shared accessories, readable symbols/text, contradictions, unsupported additions.
- Record precision and recall of supported details, entity-link correctness, region coverage, unsupported-claim rate, OCR/diagram accuracy, end-to-end latency, peak/steady memory, CPU utilization, and cancellation/queue behavior.
- Include negative tests for “multiple powers/identities” invented from different views and for overly short answers that omit visible details.
- Qualitative human verification: no acceptance based only on keyword counts or the model scoring its own output.

## Implementation order (small, reversible increments)

A. Snapshot current baseline and exact user-visible output; label any observations unverified. Check live cgroup measurements.

B. Add a model-independent structured evidence graph and ROI provenance without changing current inference; preserve legacy plain-text handoff and chat export.

C. Improve semantic ROI discovery; keep current column detector as fallback. Source crops from original pixels with coordinates.

D. Add adaptive per-region prompts, targeted re-inspection and cross-region entity linking. Do not replace observations with a deterministic short summary.

E. Run side-by-side isolated candidate models; choose *measured* improvement against actual reference-sheet accuracy and latency; pin model, projector, backend, revision.

F. Route verified evidence into §C's existing conversational model and project context. Expand output based on user question and image complexity; stay grounded.

G. Ship behind a selectable/rollbackable experimental flag, preserve legacy model, then compare user phone/Quest results before default promotion.

Never infer that a successful deployment proves visual understanding; require observed runtime execution and human-reviewed test images.
