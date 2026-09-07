# §wyrlz Server 2.1.18

## Purpose
Move R39's dominant per-token matrix-vector workload out of Python/Numpy dequantize-then-matmul loops and into a compiled direct-quantized backend, while retaining the Python reference engine as the correctness/fallback oracle.

## Native backend
- New extension: `swyrlz._r39_native` built from `native/r39_native.c`.
- Direct quantized matvec kernels support `f32`, `f16`, `bf16`, `q4_0`, `q8_0`, `q4_k`, and `q6_k`.
- Kernels read SWRLZX quantized rows directly and accumulate dot products without materializing whole float32 matrices.
- Python bridge: `swyrlz/r39_native.py`.
- Build wiring: `setup.py`, `pyproject.toml`, and local editable install from `requirements.txt`.

## Hot runtime v8
`runtime_hot/r39_engine.py` now dispatches every heavy R39 matvec to the native extension when it is available. If the extension is absent or a native call rejects a tensor, the bounded Python/Numpy path remains available.

The hot engine keeps:
- warm per-worker R39 model reuse,
- intermediate-prefill vocabulary projection skipping,
- connection diagnostics,
- detached generation/replay,
- per-token prefill timing,
- decode-step timing.

The rejected v7 recurrent FP16 cache experiment is removed from the active path because measured prefill latency regressed.

## Validation
Run:

```bash
python scripts/verify_r39_native.py
```

The verifier compares every supported native quantizer against the Python reference dequantize-plus-matvec result on deterministic synthetic blocks.

## Version accounting
- Server source: `2.1.18`
- Hot runtime: `hot-boundary-v8-native-dispatch`
- Chat remains `1.3.18`; no Chat UI behavior changed in this server/backend revision.

## Deployment boundary
The compiled extension is a deployment artifact. Manual hot sync can install the v8 Python dispatcher immediately, but it cannot create the native `.so` on an already-running Server 2.1.16 worker. Native acceleration becomes active only after a Server 2.1.18 deployment/build installs the extension. Until then v8 reports and uses the Python fallback.
