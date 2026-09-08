from __future__ import annotations

import numpy as np

from swyrlz import r39_inference as ref
from swyrlz import r39_native


def row_bytes(kind: str, cols: int) -> int:
    if kind == "f32": return cols * 4
    if kind in {"f16", "bf16"}: return cols * 2
    if kind == "q4_0": return (cols // 32) * 18
    if kind == "q8_0": return (cols // 32) * 34
    if kind == "q4_k": return (cols // 256) * 144
    if kind == "q6_k": return (cols // 256) * 210
    raise ValueError(kind)


class FakeModel:
    def __init__(self, kind: str, cols: int, rows: int, raw: np.ndarray):
        self.desc = {"w": {"kind": kind, "shape": (cols, rows)}}
        self.raw = raw
    def _raw(self, name: str):
        return self.raw


def _set_half(raw: np.ndarray, offset: int, value: float) -> None:
    raw[offset:offset + 2] = np.frombuffer(np.float16(value).tobytes(), dtype=np.uint8)


def _run_case(rng: np.random.Generator, kind: str, cols: int, rows: int, *, scale: float | None = None) -> float:
    rb = row_bytes(kind, cols)
    raw = rng.integers(0, 256, size=rb * rows, dtype=np.uint8)
    chosen = 0.03125 if scale is None else scale
    if kind in {"q4_0", "q8_0"}:
        stride = 18 if kind == "q4_0" else 34
        for off in range(0, raw.size, stride):
            _set_half(raw, off, chosen)
    elif kind == "q4_k":
        for off in range(0, raw.size, 144):
            _set_half(raw, off, chosen)
            _set_half(raw, off + 2, chosen / 2)
    elif kind == "q6_k":
        for off in range(0, raw.size, 210):
            _set_half(raw, off + 208, chosen)
    x = rng.standard_normal(cols).astype(np.float32)
    expected = ref._deq(kind, raw, (cols, rows)) @ x
    actual = r39_native.matvec(FakeModel(kind, cols, rows, raw), "w", x)
    if actual is None:
        raise AssertionError(f"native dispatch returned None for {kind}")
    err = float(np.max(np.abs(expected - actual)))
    if not np.allclose(expected, actual, rtol=2e-4, atol=2e-3):
        raise AssertionError(f"{kind} mismatch: max_abs_error={err}")
    return err


def main() -> None:
    if not r39_native.available():
        raise SystemExit("native R39 extension is not available")
    rng = np.random.default_rng(39)
    cases = [
        ("f32", 96, 7),
        ("f16", 96, 7),
        ("bf16", 96, 7),
        ("q4_0", 256, 7),
        ("q8_0", 256, 7),
        ("q4_k", 512, 7),
        ("q6_k", 512, 7),
    ]
    for kind, cols, rows in cases:
        err = _run_case(rng, kind, cols, rows)
        print(f"{kind}: ok max_abs_error={err:.6g}")

    # Production R39 quant scales can be fp16 subnormals. This explicitly guards
    # the conversion bug that made native quantized matvec outputs exactly 1/2
    # of the reference values when the scale exponent field was zero.
    subnormal = float(np.float16(2.0 ** -20))
    for kind, cols, rows in [("q4_0", 256, 7), ("q8_0", 256, 7), ("q4_k", 512, 7), ("q6_k", 512, 7)]:
        err = _run_case(rng, kind, cols, rows, scale=subnormal)
        print(f"{kind} subnormal-scale: ok max_abs_error={err:.6g}")

    print("native R39 quantized matvec equivalence: PASS")


if __name__ == "__main__":
    main()
