"""Isolated, CPU-only Qwen3-VL GGUF runtime for the existing image analysis route.

Does not replace the production llama-cpp-python wheel. A pinned official
llama.cpp llama-server runs on loopback only, with the model and projector
selected by chat_vision.py. Uploaded images stay on the same HF Space machine.
The local server's stream is adapted to create_chat_completion's event shape.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request

LLAMA_CPP_COMMIT = "fd27b2034905f8dadd8bd6d2cc44595f4929d391"
UPSTREAM_URL = "https://github.com/ggml-org/llama.cpp.git"
SERVER_PORT = 16943
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
START_TIMEOUT = 240
# Aggressive CPU trial: 8/14 -> up to 12 decode / 16 image-prefill.
# Use cgroup quota as the ceiling; affinity alone can expose host CPUs.
# Model weights/context/batches, cancellation and serialized vision are unchanged.
def _bounded_thread_plan(decode_target: int = 12, batch_target: int = 16) -> tuple[int, int]:
    from runtime_capacity import runtime_capacity_snapshot
    try:
        available = len(os.sched_getaffinity(0))
    except (AttributeError, OSError):
        available = os.cpu_count() or 1
    cap = max(1, min(16, int(available)))
    cpu = runtime_capacity_snapshot().get("cpu") or {}
    quota = cpu.get("limitCores")
    if isinstance(quota, (int, float)) and not isinstance(quota, bool) and 0 < quota < 1e6:
        cap = min(cap, max(1, int(quota)))
    return min(decode_target, cap), min(batch_target, cap)

DECODE_THREADS, BATCH_THREADS = _bounded_thread_plan()
PARALLEL_REQUESTS = 1

_build_lock = threading.Lock()
_server_lock = threading.Lock()
_server_proc = None


def _exe_path() -> Path:
    configured = os.environ.get("SWRLZ_QWEN_LLAMA_SERVER", "").strip()
    if configured:
        path = Path(configured)
        if not path.is_file() or not os.access(path, os.X_OK):
            raise RuntimeError("QWEN3_VL_SERVER_BINARY_INVALID")
        return path
    root = Path(tempfile.gettempdir()) / ("swrlz-llamacpp-" + LLAMA_CPP_COMMIT[:12])
    exe = root / "build" / "bin" / "llama-server"
    if exe.is_file() and os.access(exe, os.X_OK):
        return exe
    with _build_lock:
        if exe.is_file() and os.access(exe, os.X_OK):
            return exe
        for command in ("git", "cmake", "c++"):
            if shutil.which(command) is None:
                raise RuntimeError("QWEN3_VL_BUILD_TOOL_MISSING: " + command)
        root.mkdir(parents=True, exist_ok=True)
        if not (root / ".git").is_dir():
            subprocess.run(["git", "init", str(root)], check=True, timeout=45,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "-C", str(root), "remote", "add", "origin", UPSTREAM_URL],
                           check=True, timeout=45, stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        # The exact immutable upstream commit is fetched; no mutable master build.
        subprocess.run(["git", "-C", str(root), "fetch", "--depth=1", "origin", LLAMA_CPP_COMMIT],
                       check=True, timeout=180, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(root), "checkout", "--detach", LLAMA_CPP_COMMIT],
                       check=True, timeout=45, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        revision = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                           text=True, timeout=10).strip()
        if revision != LLAMA_CPP_COMMIT:
            raise RuntimeError("QWEN3_VL_SOURCE_REVISION_MISMATCH")
        subprocess.run(["cmake", "-S", str(root), "-B", str(root / "build"),
                        "-DCMAKE_BUILD_TYPE=Release", "-DLLAMA_BUILD_TESTS=OFF",
                        "-DLLAMA_BUILD_EXAMPLES=OFF", "-DLLAMA_CURL=OFF",
                        "-DGGML_NATIVE=OFF", "-DLLAMA_BUILD_SERVER=ON"],
                       check=True, timeout=180, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
        subprocess.run(["cmake", "--build", str(root / "build"), "--target", "llama-server",
                        "--parallel", "2"], check=True, timeout=900,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not exe.is_file():
            raise RuntimeError("QWEN3_VL_SERVER_BINARY_MISSING")
    return exe


def _healthy() -> bool:
    try:
        with urllib.request.urlopen(SERVER_URL + "/health", timeout=2) as response:
            body = json.load(response)
        return isinstance(body, dict) and (body.get("status") == "ok" or
                                            body.get("status") == "ready")
    except (OSError, ValueError, urllib.error.HTTPError):
        return False


def _ensure_running(model_path: str, projector_path: str) -> None:
    global _server_proc
    if _server_proc is not None and _server_proc.poll() is None and _healthy():
        return
    with _server_lock:
        if _server_proc is not None and _server_proc.poll() is None and _healthy():
            return
        if _server_proc is not None and _server_proc.poll() is None:
            _server_proc.terminate()
            try:
                _server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                _server_proc.kill()
        binary = _exe_path()
        args = [str(binary), "--model", model_path, "--mmproj", projector_path,
                "--host", "127.0.0.1", "--port", str(SERVER_PORT),
                "--ctx-size", "8192", "--threads", str(DECODE_THREADS), "--threads-batch", str(BATCH_THREADS),
                "--batch-size", "512", "--ubatch-size", "256", "--parallel", str(PARALLEL_REQUESTS)]
        # Never persist user image payloads or stream output to log files.
        _server_proc = subprocess.Popen(args, stdin=subprocess.DEVNULL,
                                        stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
        deadline = time.monotonic() + START_TIMEOUT
        while time.monotonic() < deadline:
            if _server_proc.poll() is not None:
                raise RuntimeError("QWEN3_VL_SERVER_EXITED")
            if _healthy():
                return
            time.sleep(1)
        _server_proc.terminate()
        raise RuntimeError("QWEN3_VL_SERVER_START_TIMEOUT")


class LocalQwen3VL:
    """OpenAI-shaped adapter for a loopback-only official llama-server."""

    def __init__(self, model_path: str, projector_path: str):
        _ensure_running(model_path, projector_path)

    def create_chat_completion(self, *, messages, max_tokens, temperature, stream):
        if not stream:
            raise ValueError("QWEN3_VL_STREAM_REQUIRED")
        payload = json.dumps({
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": True,
        }, separators=(",", ":")).encode("utf-8")
        request = urllib.request.Request(
            SERVER_URL + "/v1/chat/completions", data=payload, method="POST",
            headers={"Content-Type": "application/json", "Accept": "text/event-stream"}
        )
        def events():
            # stream remains closeable by caller's generator .close()
            with urllib.request.urlopen(request, timeout=600) as response:
                for raw in response:
                    if not raw.startswith(b"data: "):
                        continue
                    part = raw[6:].strip()
                    if part == b"[DONE]":
                        break
                    if not part:
                        continue
                    try:
                        item = json.loads(part)
                    except (ValueError, UnicodeDecodeError):
                        continue
                    if isinstance(item, dict):
                        yield item
        return events()


def load(model_path: str, projector_path: str) -> LocalQwen3VL:
    return LocalQwen3VL(model_path, projector_path)
