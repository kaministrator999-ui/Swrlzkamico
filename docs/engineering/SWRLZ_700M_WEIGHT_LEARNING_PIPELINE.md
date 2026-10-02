# §wyrlz 700M Weight-Learning Pipeline

**Start router:** [§wyrlz §tart](../../§wyrlz_§tart.md)

**Role:** canonical operating document for turning independently verified 700M coding successes and repair trajectories into training data, LoRA/checkpoint candidates, and eventually promoted production weights.

## 1. Why this exists

The live 700M currently receives substantial runtime policy/context to compensate for behavior that is not yet reliably internalized. Stable, reusable programming behavior should migrate into trained parameters where evidence supports it, while task-specific requirements remain runtime state.

```text
MODEL WEIGHTS
  learn reusable behavior:
  preserve APIs / repair from receipts / keep contracts / produce complete code / avoid regressions

RUNTIME CONTEXT
  carries this job:
  current request / exact requirements / current candidate / newest failure evidence
```

This pipeline exists to reduce repeated prefill without confusing runtime prompting with actual model learning.

## 2. Evidence boundary

A generation is **not** training truth because it completed, sounded confident, or was self-reviewed.

Promotion requires independent evidence such as compiler/runtime/test/browser checks. Failed candidates may be retained as repair/contrast examples only when paired with exact failure evidence and a separately validated corrected target.

## 3. Harvest path

```text
historical test/review evidence
→ identify independently verified successes
→ recover exact original prompt
→ recover exact candidate bytes
→ recover exact acceptance evidence
→ normalize swrlz-700m-training-example-v1
→ redact secrets/unrelated personal context
→ split TRAIN vs HELD-OUT
→ train LoRA candidate
→ run held-out + protected regression suite
→ compare against untouched base/current production student
→ promote only if acceptance improves without protected regressions
```

The harvest ledger lives at [training/700m/harvested_successes.md](../../training/700m/harvested_successes.md). The executable trainer lives at [training/700m/train_lora.py](../../training/700m/train_lora.py).

## 4. Training record

A promotable record must include:

- `schema=swrlz-700m-training-example-v1`
- stable contract/example ID
- exact original request
- compact requirements/invariants
- exact candidate/revision identity
- failure evidence when applicable
- exact independently validated corrected target
- evaluator type, runtime/command, observed result, and `PASS`
- language/runtime
- provenance
- redaction status

If exact candidate bytes are not available, the case remains **HARVESTED / NOT TRAINABLE** until recovered. Do not reconstruct source from prose summaries.

## 5. Weight-update policy

Default first-stage adaptation is LoRA/PEFT over the unquantized LFM2-700M checkpoint. Rank, alpha, learning rate, epochs, and target modules are training parameters, not immutable architecture. Adjust them from held-out evidence rather than intuition alone.

Start conservatively:
- rank 16
- alpha 32
- dropout 0.05
- 2 epochs
- learning rate 2e-4

If held-out behavior underfits, increase capacity/steps carefully. If general behavior regresses or examples are memorized, reduce rank/epochs/learning rate or broaden the validated corpus. Never promote merely because training loss decreased.

## 6. Promotion gate

A trained adapter/checkpoint must beat or materially improve the current student on the intended coding/repair suite without protected regressions. The independent evaluator owns the pass/fail result; the producer model does not grade itself.

Only after that gate may the adapter be merged or otherwise packaged, quantized for the runtime target, published with provenance, and selected by the live 700M route.

## 7. Runtime/deployment boundary

Creating or editing training data, trainer code, or this document does not change live weights and does not require a chat deployment by itself.

A new trained model becomes active only after:
1. training completes,
2. held-out evaluation passes,
3. the model artifact receives a durable revision/provenance identity,
4. the runtime model reference is updated to that artifact, and
5. the normal guarded deployment + live verification path succeeds.

## 8. Current state

- Training pipeline source exists.
- Historical successes are being harvested into the ledger below.
- Exact-source recovery is required before any harvested case becomes a trainable record.
- No LoRA/checkpoint has yet been promoted into the live 700M route.
