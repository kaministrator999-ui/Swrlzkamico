"""Single resident Qwen3.5-9B CPU model for §C's text, code and vision routes.

This is a candidate. Source branches alone do not change the live Space.
The only network download is pinned open weights from the Hugging Face Hub,
and all inference stays on a loopback-only llama.cpp server.
"""
from __future__ import annotations

import hashlib
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

from huggingface_hub import hf_hub_download

MODEL_REPO = "twoody/Qwen3.5-9B-GGUF"
MODEL_REVISION = "b647a5938c8cf40d1c3553ddd9bf2892895f0110"
MODEL_FILE = "Qwen3.5-9B-Q4_K_M.gguf"
PROJECTOR_FILE = "mmproj-F16.gguf"
MODEL_LABEL = "Qwen3.5-9B Q4_K_M · single resident model"
MODEL_CHECKPOINT = f"{MODEL_REPO}@{MODEL_REVISION}/{MODEL_FILE}"
EXPECTED_FILES = {
    MODEL_FILE: (5780090688, "8c4cc24f54473f3d4e080d4ec7fd2a40d0bbec0f94f3c807cd62694905357d54"),
    PROJECTOR_FILE: (918165888, "2f7ce3652232b91c2220fad23f5b62d110f67e84bd5ed33a7d2bea82f8ee1d26"),
}
LLAMA_CPP_COMMIT = "7fe450e19305b828c199d602c23a8337aaa1f03b"  # tag b11146, Qwen3.5 capable
UPSTREAM_URL = "https://github.com/ggml-org/llama.cpp.git"
SERVER_PORT = 16947
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"
CONTEXT_TOKENS = 8192
START_TIMEOUT_SECONDS = 360
PARALLEL_REQUESTS = 1

_guard = threading.RLock()
_build_lock = threading.RLock()
_server_process = None
_instance = None
_warmed = False
_file_cache: dict[str, str] = {}


def _cpu_threads() -> int:
    """Use only CPUs actually available to this Space, not host CPU count."""
    try:
        affinity = len(os.sched_getaffinity(0))
    except (OSError, AttributeError):
        affinity = os.cpu_count() or 1
    capacity = max(1, min(16, int(affinity)))
    # Visible CPU quota is authoritative if affinity exposes more host cores.
    try:
        quota, period = Path("/sys/fs/cgroup/cpu.max").read_text().split()[:2]
        if quota != "max" and int(period) > 0:
            capacity = min(capacity, max(1, int(int(quota) / int(period))))
    except (ValueError, OSError, IndexError):
        pass
    return capacity


CPU_CAPACITY = _cpu_threads()
# Balanced profile: decode is memory-bandwidth-sensitive, prefill parallelizes.
# swrlz-qwen35-cpu-v2; safe on 2-vCPU fallback and available 16-core cgroups.
DECODE_THREADS = min(10, CPU_CAPACITY)
BATCH_THREADS = min(16, CPU_CAPACITY)


def _verified_asset(filename: str) -> str:
    if filename in _file_cache:
        return _file_cache[filename]
    if filename not in EXPECTED_FILES:
        raise ValueError("QWEN35_ASSET_NOT_ALLOWLISTED")
    options = {"repo_id": MODEL_REPO, "revision": MODEL_REVISION, "filename": filename}
    try:
        path = hf_hub_download(**options, local_files_only=True)
    except Exception:
        path = hf_hub_download(**options)
    expected_bytes, expected_sha = EXPECTED_FILES[filename]
    candidate = Path(path)
    if candidate.stat().st_size != expected_bytes:
        raise RuntimeError("QWEN35_ASSET_SIZE_MISMATCH: " + filename)
    digest = hashlib.sha256()
    with candidate.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    if digest.hexdigest() != expected_sha:
        raise RuntimeError("QWEN35_ASSET_SHA256_MISMATCH: " + filename)
    _file_cache[filename] = str(candidate)
    return str(candidate)


def _server_executable() -> str:
    configured = os.environ.get("SWRLZ_QWEN35_LLAMA_SERVER", "").strip()
    if configured:
        p = Path(configured)
        if not p.is_file() or not os.access(p, os.X_OK):
            raise RuntimeError("QWEN35_SERVER_BINARY_INVALID")
        return str(p)
    root = Path(tempfile.gettempdir()) / ("swrlz-qwen35-llama-" + LLAMA_CPP_COMMIT[:12])
    binary = root / "build" / "bin" / "llama-server"
    if binary.is_file() and os.access(binary, os.X_OK):
        return str(binary)
    with _build_lock:
        if binary.is_file() and os.access(binary, os.X_OK):
            return str(binary)
        for command in ("git", "cmake", "c++"):
            if shutil.which(command) is None:
                raise RuntimeError("QWEN35_BUILD_TOOL_MISSING: " + command)
        root.mkdir(parents=True, exist_ok=True)
        if not (root / ".git").exists():
            subprocess.run(["git", "init", str(root)], check=True, timeout=45,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["git", "-C", str(root), "remote", "add", "origin", UPSTREAM_URL],
                           check=True, timeout=45, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(root), "fetch", "--depth=1", "origin", LLAMA_CPP_COMMIT],
                       check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(root), "checkout", "--detach", LLAMA_CPP_COMMIT],
                       check=True, timeout=45, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        actual = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"],
                                         text=True, timeout=10).strip()
        if actual != LLAMA_CPP_COMMIT:
            raise RuntimeError("QWEN35_LLAMA_SOURCE_MISMATCH")
        subprocess.run([
            "cmake", "-S", str(root), "-B", str(root / "build"),
            "-DCMAKE_BUILD_TYPE=Release", "-DLLAMA_BUILD_SERVER=ON",
            "-DLLAMA_BUILD_TESTS=OFF", "-DLLAMA_BUILD_EXAMPLES=OFF",
            "-DLLAMA_CURL=OFF", "-DGGML_NATIVE=OFF",
        ], check=True, timeout=180, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["cmake", "--build", str(root / "build"), "--target",
                        "llama-server", "--parallel", str(DECODE_THREADS)],
                       check=True, timeout=1200, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if not binary.is_file():
            raise RuntimeError("QWEN35_SERVER_BINARY_NOT_BUILT")
    return str(binary)


def _post(path: str, payload: dict, timeout: int = 600):
    request = urllib.request.Request(
        SERVER_URL + path, data=json.dumps(payload, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    return urllib.request.urlopen(request, timeout=timeout)


def _healthy() -> bool:
    try:
        with urllib.request.urlopen(SERVER_URL + "/health", timeout=3) as response:
            return json.load(response).get("status") in {"ok", "ready"}
    except (OSError, ValueError, urllib.error.HTTPError):
        return False


def _launch(model_path: str, projector_path: str) -> None:
    global _server_process
    if _server_process is not None and _server_process.poll() is None and _healthy():
        return
    binary = _server_executable()
    args = [
        binary, "--model", model_path, "--mmproj", projector_path,
        "--host", "127.0.0.1", "--port", str(SERVER_PORT),
        "--ctx-size", str(CONTEXT_TOKENS), "--threads", str(DECODE_THREADS),
        "--threads-batch", str(BATCH_THREADS), "--batch-size", "512",
        "--ubatch-size", "256", "--parallel", str(PARALLEL_REQUESTS),
        "--jinja",
    ]
    if _server_process is not None and _server_process.poll() is None:
        _server_process.terminate()
        try:
            _server_process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            _server_process.kill()
    _server_process = subprocess.Popen(args, stdin=subprocess.DEVNULL,
                                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    deadline = time.monotonic() + START_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        if _server_process.poll() is not None:
            raise RuntimeError("QWEN35_SERVER_EXITED_ON_LOAD")
        if _healthy():
            return
        time.sleep(1)
    _server_process.terminate()
    raise RuntimeError("QWEN35_SERVER_STARTUP_TIMEOUT")


class SingleQwen35:
    def tokenize(self, text: bytes, add_bos: bool = False):
        content = text.decode("utf-8", errors="strict")
        with _post("/tokenize", {"content": content, "add_special": bool(add_bos)}, timeout=60) as response:
            data = json.load(response)
        tokens = data.get("tokens")
        if not isinstance(tokens, list):
            raise RuntimeError("QWEN35_TOKEN_COUNT_UNAVAILABLE")
        return tokens

    def create_chat_completion(self, *, messages, max_tokens, temperature, stream=True, **kwargs):
        if not stream:
            raise ValueError("QWEN35_STREAM_REQUIRED")
        payload = {
            "messages": messages, "max_tokens": int(max_tokens),
            "temperature": float(temperature), "stream": True,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        # Preserve structured JSON contracts where the existing coder requests them.
        for key in ("response_format", "top_p", "top_k", "stop"):
            if key in kwargs:
                payload[key] = kwargs[key]
        def events():
            with _post("/v1/chat/completions", payload, timeout=900) as response:
                for raw in response:
                    if not raw.startswith(b"data:"):
                        continue
                    content = raw.split(b":", 1)[1].strip()
                    if content == b"[DONE]":
                        break
                    if content:
                        value = json.loads(content)
                        if value.get("error"):
                            raise RuntimeError("QWEN35_INFERENCE_ERROR")
                        yield value
        return events()


def load(model_path: str | None = None, projector_path: str | None = None):
    """Start one verified resident process, shared by all model routes."""
    global _instance
    with _guard:
        actual_model = _verified_asset(MODEL_FILE)
        actual_projector = _verified_asset(PROJECTOR_FILE)
        if model_path and Path(model_path).resolve() != Path(actual_model).resolve():
            raise RuntimeError("QWEN35_MODEL_PATH_MISMATCH")
        if projector_path and Path(projector_path).resolve() != Path(actual_projector).resolve():
            raise RuntimeError("QWEN35_PROJECTOR_PATH_MISMATCH")
        if _instance is None or not _healthy():
            _launch(actual_model, actual_projector)
            _instance = SingleQwen35()
        return _instance


def warmup():
    """Verify actual tokenization and generation before reporting ready."""
    global _warmed
    _warmed = False
    model = load()
    if not model.tokenize(b"ready", add_bos=False):
        raise RuntimeError("QWEN35_TOKENIZER_NOT_READY")
    response = list(model.create_chat_completion(
        messages=[{"role": "user", "content": "Reply OK."}],
        max_tokens=8, temperature=0.0, stream=True))
    if not any(event.get("choices") for event in response):
        raise RuntimeError("QWEN35_INFERENCE_NOT_READY")
    _warmed = True
    return {"model": MODEL_LABEL, "ready": True, "threads": DECODE_THREADS,
            "batchThreads": BATCH_THREADS, "context": CONTEXT_TOKENS,
            "cpuCapacity": CPU_CAPACITY, "profile": "swrlz-qwen35-cpu-v2"}


def ready() -> bool:
    """Read-only readiness after one verified warm decode, not model-download status."""
    return _warmed and _instance is not None and _healthy()
