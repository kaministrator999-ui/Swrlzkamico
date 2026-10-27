"""Bounded, read-only observations of the visible cgroup v2 resource controls.

The parser is pure. The reader consults only four fixed controller files; it
never inspects environment variables, process tables, account data or models.
Observed controller values do not establish that any model can run safely.
"""
from __future__ import annotations

from pathlib import Path
import re
from typing import Mapping

SCHEMA = "swrlz-runtime-capacity-v1"
MAX_FILE_BYTES = 512
MAX_COUNTER = (1 << 63) - 1
_FILES = ("memory.max", "memory.current", "memory.peak", "cpu.max")


def _counter(text: str) -> int | None:
    if not re.fullmatch(r"[0-9]{1,19}", text):
        return None
    value = int(text)
    return value if value <= MAX_COUNTER else None


def _bounded_text(value: str | None) -> str | None:
    return value.strip() if isinstance(value, str) and len(value) <= MAX_FILE_BYTES else None


def _memory(value: str | None, *, limit: bool = False) -> tuple[int | None, str]:
    text = _bounded_text(value)
    if limit and text == "max":
        return None, "unlimited"
    number = _counter(text) if text is not None else None
    return (number, "measured") if number is not None else (None, "unavailable")


def _cpu(value: str | None) -> dict:
    missing = {"quotaMicros": None, "periodMicros": None, "limitCores": None,
               "state": "unavailable"}
    text = _bounded_text(value)
    if text is None or "\n" in text or "\r" in text:
        return missing
    fields = text.split()
    if len(fields) != 2:
        return missing
    period = _counter(fields[1])
    if not period:
        return missing
    if fields[0] == "max":
        return {"quotaMicros": None, "periodMicros": period, "limitCores": None,
                "state": "unlimited"}
    quota = _counter(fields[0])
    if not quota:
        return missing
    return {"quotaMicros": quota, "periodMicros": period,
            "limitCores": quota / period, "state": "measured"}


def parse_runtime_capacity(files: Mapping[str, str | None]) -> dict:
    """Parse only approved controller values, retaining unknown versus unlimited."""
    limit, limit_state = _memory(files.get("memory.max"), limit=True)
    current, current_state = _memory(files.get("memory.current"))
    peak, peak_state = _memory(files.get("memory.peak"))
    cpu = _cpu(files.get("cpu.max"))
    known = any(state != "unavailable" for state in
                (limit_state, current_state, peak_state, cpu["state"]))
    return {"schema": SCHEMA, "source": "cgroup-v2" if known else "unavailable",
            "scope": "visible-cgroup",
            "memory": {"limitBytes": limit, "limitState": limit_state,
                       "currentBytes": current, "currentState": current_state,
                       "peakBytes": peak, "peakState": peak_state},
            "cpu": cpu}


def runtime_capacity_snapshot(cgroup_root: Path = Path("/sys/fs/cgroup")) -> dict:
    """Read a bounded snapshot; unavailable files never expose paths or errors."""
    values = {}
    for name in _FILES:
        try:
            with (cgroup_root / name).open("rb") as stream:
                raw = stream.read(MAX_FILE_BYTES + 1)
            values[name] = raw.decode("ascii") if len(raw) <= MAX_FILE_BYTES else None
        except (OSError, UnicodeDecodeError):
            values[name] = None
    return parse_runtime_capacity(values)
