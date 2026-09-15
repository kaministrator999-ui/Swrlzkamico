# Server Runtime 2.3.170 / LALM 2.1.53 / R39 v42

## Scope
Runtime-hot LALM optimization and bounded diagnostics. No deployment or restart.

## Changes
- Exact simple social openers are resolved inside the LALM boundary by the existing social classifier and safe finalizer without model prefill/decode.
- Added bounded `SWRLZ_R39_CAMERA` diagnostics for payload shape, rendered-prompt size/token count, render failures, and social fast-path timing.
- Diagnostics never log prompt/history/response text or credentials.
- Non-social requests continue through v41 inference unchanged after observation.

## Baseline
Production v41 `Hey 👋` request `web:mu30rtur:32860854021466003796`: 315 uncached prefill tokens, 29.908 s prefill, 10.53 tok/s, 13 decode tokens, 5.974 s decode compute, 35.974 s total, COMPLETED.

## Acceptance
1. Exact `Hey 👋` emits `social-fastpath-enter` and `social-fastpath-complete`, no model prefill metrics, and canonical assistant terminal COMPLETED.
2. A non-social request emits payload and rendered-prompt diagnostics plus normal v41 deep telemetry.
3. Compare prompt token count and prefill/decode timing before further optimization.

## Authority
- Server Runtime: 2.3.170
- LALM Engine: 2.1.53
- R39 revision: `2.1.53-hot-social-fastpath-prefill-cameras-v42`
