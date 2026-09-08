# Server 2.2.4

Performance-focused R39 base release.

- Parallelizes Forge transport chunk acquisition during cold model hydration instead of downloading repository chunks serially.
- Reuses transport SHA verification instead of hashing the reconstructed packed model a second time.
- Computes the raw R39 SHA while decompressing, removing a second full 233 MB read.
- Changes native quantized matvec accumulators from double to float under the existing `-O3 -ffast-math` build so x86 SIMD can process wider lanes; runtime native/reference probes remain the coherence oracle.
- Adds `-funroll-loops` to the native extension build.
- Keeps the 2.1.21 hot runtime independent and does not change the Vercel deployment trigger.

Goal: reduce cold model-open latency and per-token forward latency while preserving reference-level logits. If native/reference drift rises beyond floating-point noise after deployment, revert the float accumulator change before further optimization.
