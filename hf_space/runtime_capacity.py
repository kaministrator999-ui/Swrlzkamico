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

# Per-response observations use only the cgroup controller already visible to
# this process. They are NOT model-exclusive allocations: concurrent chat,
# vision and system work share the same counters.
import threading
import time

RESOURCE_USAGE_SCHEMA = "swrlz-response-resource-usage-v1"


def _read_cgroup_cpu_usage_usec(root: Path) -> int | None:
    """One bounded cgroup-v2 cpu.stat counter; never read process tables."""
    try:
        with (root / "cpu.stat").open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES + 1)
        if len(raw) > MAX_FILE_BYTES:
            return None
        text = raw.decode("ascii")
    except (OSError, UnicodeDecodeError):
        return None
    for line in text.splitlines():
        key, sep, value = line.partition(" ")
        if key == "usage_usec" and sep:
            return _counter(value.strip())
    return None


class ResponseResourceMeter:
    """Best-effort shared-container CPU/memory window for one inference request.

    Sampled peak is the highest sampled cgroup usage, not model RAM, and not
    the historical cgroup memory.peak high-water mark. CPU usage is also
    shared with concurrent workloads. Missing controllers stay explicit null.
    """

    def __init__(self, cgroup_root: Path = Path("/sys/fs/cgroup"),
                 sample_interval_seconds: float | None = 1.0):
        self._root = cgroup_root
        self._interval = sample_interval_seconds
        self._started = time.monotonic()
        self._capacity = runtime_capacity_snapshot(cgroup_root)
        self._cpu_start = _read_cgroup_cpu_usage_usec(cgroup_root)
        self._max_memory = self._capacity["memory"]["currentBytes"]
        self._samples = 1 if self._max_memory is not None else 0
        self._lock = threading.Lock()
        self._closed = threading.Event()
        self._result = None
        self._worker = None
        if sample_interval_seconds is not None and sample_interval_seconds > 0:
            self._worker = threading.Thread(target=self._sample_loop, daemon=True,
                                            name="response-resource-sampler")
            self._worker.start()

    def _sample_loop(self) -> None:
        while not self._closed.wait(self._interval):
            self.sample()

    def sample(self) -> None:
        observed = runtime_capacity_snapshot(self._root)["memory"]["currentBytes"]
        if observed is None:
            return
        with self._lock:
            if self._result is not None:
                return
            self._samples += 1
            self._max_memory = (observed if self._max_memory is None
                                else max(self._max_memory, observed))

    def finish(self) -> dict:
        """Idempotent; does not block inference on the sampler's next tick."""
        with self._lock:
            if self._result is not None:
                return dict(self._result)
            self._closed.set()
        ended = time.monotonic()
        cpu_end = _read_cgroup_cpu_usage_usec(self._root)
        ending = runtime_capacity_snapshot(self._root)
        end_memory = ending["memory"]["currentBytes"]
        with self._lock:
            if self._result is not None:
                return dict(self._result)
            if end_memory is not None:
                self._samples += 1
                self._max_memory = (end_memory if self._max_memory is None
                                    else max(self._max_memory, end_memory))
            wall_ms = max(0, round((ended - self._started) * 1000))
            cpu_delta = (max(0, cpu_end - self._cpu_start)
                         if cpu_end is not None and self._cpu_start is not None
                         and cpu_end >= self._cpu_start else None)
            cpu_cores = (round(cpu_delta / (wall_ms * 1000), 3)
                         if cpu_delta is not None and wall_ms > 0 else None)
            memory = self._capacity["memory"]
            cpu = self._capacity["cpu"]
            self._result = {
                "schema": RESOURCE_USAGE_SCHEMA,
                "scope": "shared-cgroup-v2",
                "isolatedModelAttribution": False,
                "wallTimeMs": wall_ms,
                "capacity": {
                    "cpuLimitCores": cpu["limitCores"],
                    "cpuLimitState": cpu["state"],
                    "memoryLimitBytes": memory["limitBytes"],
                    "memoryLimitState": memory["limitState"],
                },
                "observed": {
                    "cgroupCpuUsageUsecDelta": cpu_delta,
                    "averageCgroupCpuCores": cpu_cores,
                    "memoryStartBytes": memory["currentBytes"],
                    "memoryEndBytes": end_memory,
                    "memoryPeakSampledBytes": self._max_memory,
                    "memorySampleCount": self._samples,
                },
                "attribution": ("Shared container readings include concurrent work; "
                                "they are not exclusive CPU/RAM use by this model."),
            }
            return dict(self._result)
