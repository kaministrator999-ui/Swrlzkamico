from __future__ import annotations

import argparse
import time

import numpy as np

from swyrlz import _r39_batch, _r39_native


def row_bytes(kind: str, cols: int) -> int:
    if kind == "f32": return cols * 4
    if kind in {"f16", "bf16"}: return cols * 2
    if kind == "q4_0": return (cols // 32) * 18
    if kind == "q8_0": return (cols // 32) * 34
    if kind == "q4_k": return (cols // 256) * 144
    if kind == "q6_k": return (cols // 256) * 210
    raise ValueError(kind)


def valid_raw(kind: str, cols: int, rows: int, rng: np.random.Generator) -> bytearray:
    if kind == "f32":
        return bytearray(rng.normal(0, 0.08, size=(rows, cols)).astype("<f4").tobytes())
    if kind == "f16":
        return bytearray(rng.normal(0, 0.08, size=(rows, cols)).astype("<f2").tobytes())
    if kind == "bf16":
        f = rng.normal(0, 0.08, size=(rows, cols)).astype("<f4").view("<u4")
        return bytearray((f >> 16).astype("<u2").tobytes())
    rb = row_bytes(kind, cols)
    raw = bytearray(rng.integers(0, 256, size=rows * rb, dtype=np.uint8).tobytes())
    scale = np.float16(0.02).tobytes()
    minimum = np.float16(0.01).tobytes()
    for r in range(rows):
        base = r * rb
        if kind in {"q4_0", "q8_0"}:
            block = 18 if kind == "q4_0" else 34
            for b in range(cols // 32): raw[base + b * block:base + b * block + 2] = scale
        elif kind == "q4_k":
            for b in range(cols // 256):
                off = base + b * 144
                raw[off:off + 2] = scale
                raw[off + 2:off + 4] = minimum
        elif kind == "q6_k":
            for b in range(cols // 256):
                off = base + b * 210 + 208
                raw[off:off + 2] = scale
    return raw


def run(kind: str, cols: int, rows: int, batch: int, repeats: int) -> None:
    rng = np.random.default_rng(39)
    raw = valid_raw(kind, cols, rows, rng)
    x = np.ascontiguousarray(rng.normal(0, 1, size=(cols, batch)).astype(np.float32))

    expected = np.stack([
        np.asarray(_r39_native.matvec(kind, raw, cols, rows, x[:, t]), dtype=np.float32)
        for t in range(batch)
    ], axis=1)
    actual = np.asarray(_r39_batch.matmat(kind, raw, cols, rows, x), dtype=np.float32)
    diff = np.abs(expected - actual)
    denom = np.maximum(np.abs(expected), np.float32(1e-6))
    print(f"{kind}: shape={rows}x{cols} batch={batch} maxAbs={float(diff.max()):.6g} maxRel={float((diff/denom).max()):.6g}")

    t0 = time.perf_counter()
    for _ in range(repeats):
        for t in range(batch): _r39_native.matvec(kind, raw, cols, rows, x[:, t])
    serial_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    for _ in range(repeats): _r39_batch.matmat(kind, raw, cols, rows, x)
    batch_s = time.perf_counter() - t0
    print(f"  repeated-matvec={serial_s:.4f}s batch-matmat={batch_s:.4f}s speedup={serial_s/max(batch_s,1e-9):.2f}x effective={batch*repeats/max(batch_s,1e-9):.1f} vectors/s")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cols", type=int, default=1024)
    p.add_argument("--rows", type=int, default=1024)
    p.add_argument("--batch", type=int, default=64)
    p.add_argument("--repeats", type=int, default=2)
    p.add_argument("--kind", action="append", choices=["f32","f16","bf16","q4_0","q8_0","q4_k","q6_k"])
    args = p.parse_args()
    kinds = args.kind or ["q4_k", "q6_k", "q4_0", "q8_0"]
    for kind in kinds:
        if kind in {"q4_k", "q6_k"} and args.cols % 256: raise SystemExit("q4_k/q6_k require cols divisible by 256")
        if kind in {"q4_0", "q8_0"} and args.cols % 32: raise SystemExit("q4_0/q8_0 require cols divisible by 32")
        run(kind, args.cols, args.rows, args.batch, args.repeats)


if __name__ == "__main__": main()
