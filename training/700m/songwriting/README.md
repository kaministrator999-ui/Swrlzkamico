# §wyrlz 700M — First-Pass Songwriting Weight Adaptation

**Owner:** 700M model-training research (offline; separate from active Chat/LALM runtime).
**Goal:** Make the original 700M more likely to produce an original, complete, coherent
rap on its FIRST generation, without runtime craft-prefill, retry, or continuation.

This workstream DOES NOT change the production GGUF, Station, §tart, model router,
module versions, deploy request, or published model. It must not merge into the
active chat-import feature branch without integration review.

## 1. Untouched baseline and exact first-pass receipts

Use the original full-precision model, not a pre-guided §wyrlz generation path.
The model already has general conversational training; the experiment adds no
§wyrlz lyric policy, story outline, original song snippets, or extra teacher text.

Dependencies for benchmark: Python, PyTorch, transformers >=4.55, accelerate.
Optional candidate evaluation: peft. LFM2 must be supported by the installed
transformers version.

Command:

    python training/700m/songwriting/benchmark_first_pass.py \
      --output /private/700m-bare-first-pass.jsonl

The 16 held-out prompt *tasks* in prompts.jsonl are ORIGINAL evaluation
requests with no target lyrics. Benchmark result files include raw model output
and should be stored privately, not committed by default. Each task gets
exactly one generation. A completed token budget is not an excuse to retry.

For a future trained adapter, run the SAME script, checkpoint, seed, prompts,
decoding settings and max token cap, adding:

    --adapter /private/adapters/songwriting-v1 \
    --output /private/700m-songwriting-candidate.jsonl

The training environment uses full-precision 700M weights; this matches the
LoRA target. A separate quantized GGUF test is mandatory before any live
adoption; 4-bit GGUF may behave differently.

Each receipt logs actual generated token count, EOS, whether the cap was
reached, elapsed inference time, RAW text, and necessary form-only checks.
It never claims that simple line counting proves real bars, flow, rhyme quality,
independent creativity, or story coherence.

## 2. Separating model failure from runtime truncation

A candidate that ends via EOS well before the token cap may have learned to
stop early; a candidate that reaches the configured cap may be constrained by
the decoder, not its own decision to finish. Test this at 2048 output tokens
before attributing missing endings to weight quality. Control prompt-length,
seed and sampling settings across base and adapter.

## 3. Governed corpus: NO auto-labeling

No historical user chat exports, artist lyrics, copyright references, private
conversation payloads, unverified model generations, or favorite-song words may
be silently treated as training examples. Do not commit private reviewed
corpora. The user owns project material and rights/consent must be checked.

Each line of a PRIVATE JSONL dataset must have:
- schema=swrlz-700m-songwriting-sft-v1
- unique id, split=train or holdout, status=APPROVED
- exact prompt and independently approved, original completed response
- origin=commissioned-original, author-original or reviewed-model-original
- rightsCleared=true, privacyReviewed=true
- at least two DISTINCT named reviewer attestations with originalityChecked
  and approved=true, and 4/5 or better in rhyme, flow, coherence, completion
  and originality

Reviewers must actually review the text; filling out the JSON fields without
evaluation is NOT verification. The schema catches missing receipts, not fraud
or hidden plagiarism. The held-out split must remain hidden from training.
For pilot weight training: at least 32 reviewed train records + 8 holdouts;
a larger diverse corpus is preferable and these minima are NOT an assurance
of musical improvement.

Validate without downloading weights:

    python training/700m/songwriting/train_songwriting_lora.py \
      --dataset /private/songwriting-reviewed.jsonl \
      --output-dir /private/adapters/songwriting-v1 --dry-run

## 4. LoRA model learning (never the quantized GGUF)

After corpus review and compute approval, on a compatible CUDA machine:

    python training/700m/songwriting/train_songwriting_lora.py \
      --dataset /private/songwriting-reviewed.jsonl \
      --output-dir /private/adapters/songwriting-v1

Dependencies: torch, transformers >=4.55, accelerate, peft.
Trainer uses the LFM2 tokenizer's original chat template, masks prompt
tokens so the loss trains assistant completion, and refuses oversized
examples instead of silently truncating. LoRA default: rank 16, alpha 32,
2 epochs, learning rate 2e-4. A successful adapter export is an EXPERIMENT,
not evidence that weights improved or a production permission.

## 5. Independent comparison and promotion boundaries

For every benchmark prompt, blind reviewers should score BOTH outputs (base
and candidate, shuffled) from 1–5 on rhyme, performable flow, coherence,
originality, and full-song completion. Log independent reviewers, source
fingerprints and actual scores. Report FIRST-PASS metrics only; no candidate
selection after multiple generations and no retry filters.

Check held-out average quality and per-domain outcomes, exact-form
compliance, EOS-vs-cap terminations, response length, and latency. Run
protected general-chat, code, identity/privacy and longer-conversation
regressions. The adapter must meaningfully improve held-out first-pass
quality without protected regressions. Only THEN consider merging weights,
quantizing, replacing the live GGUF MODEL_REPO/MODEL_FILE reference and
following normal guarded deployment and observed behavior verification.

**Current status:** first-pass benchmark, corpus governance, and LoRA
candidate software are source-ready. No reviewed private dataset, actual
model benchmark result, GPU training execution, adapter, quantization,
production promotion or live behavior improvement is claimed here.

## 6. Verification

Stdlib-only tests (do not download/load model):

    cd training/700m/songwriting
    python -m unittest -v test_songwriting.py

Canonical parent policy: docs/engineering/SWRLZ_700M_WEIGHT_LEARNING_PIPELINE.md.
