"""Offline adapter contract tests; no HF model download or hardware mutation."""
from __future__ import annotations

import importlib.util
import io
import json
from pathlib import Path
from unittest.mock import patch


MODULE = Path(__file__).with_name("hf_chat_qwen35_9b_runtime.py")
spec = importlib.util.spec_from_file_location("candidate_qwen35", MODULE)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


class FakeResponse:
    def __init__(self, payload):
        self.body = io.BytesIO(payload)
    def __enter__(self):
        return self.body
    def __exit__(self, exc_type, exc, tb):
        self.body.close()


def test_tokenize():
    recorded = []
    def post(path, payload, timeout=600):
        recorded.append((path, payload, timeout))
        return FakeResponse(json.dumps({"tokens": [3, 4, 5]}).encode())
    with patch.object(runtime, "_post", post):
        actual = runtime.SingleQwen35().tokenize("hello".encode("utf-8"))
    assert actual == [3, 4, 5]
    assert recorded[0][0] == "/tokenize"
    assert recorded[0][1]["content"] == "hello"
    assert recorded[0][1]["add_special"] is False


def test_stream_and_format():
    collected = []
    body = (b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n'
            b'data: {"choices":[{"delta":{"content":" there"}}]}\n\n'
            b'data: [DONE]\n\n')
    def post(path, payload, timeout=600):
        collected.append((path, payload))
        return FakeResponse(body)
    with patch.object(runtime, "_post", post):
        result = list(runtime.SingleQwen35().create_chat_completion(
            messages=[{"role": "user", "content": "hi"}], max_tokens=10,
            temperature=0.25, stream=True,
            response_format={"type": "json_object"}))
    assert len(result) == 2
    assert result[0]["choices"][0]["delta"]["content"] == "Hello"
    assert collected[0][0] == "/v1/chat/completions"
    assert collected[0][1]["chat_template_kwargs"] == {"enable_thinking": False}
    assert collected[0][1]["response_format"] == {"type": "json_object"}


def test_singleton_and_asset_guards():
    original_instance, original_cache = runtime._instance, dict(runtime._file_cache)
    try:
        sentinel = runtime.SingleQwen35()
        runtime._instance = sentinel
        runtime._file_cache = {
            runtime.MODEL_FILE: "/tmp/qwen35-test.gguf",
            runtime.PROJECTOR_FILE: "/tmp/qwen35-projector-test.gguf",
        }
        with patch.object(runtime, "_healthy", return_value=True):
            assert runtime.load() is sentinel
            assert runtime.load() is sentinel
            try:
                runtime.load("/tmp/wrong.gguf")
            except RuntimeError as exc:
                assert "MODEL_PATH_MISMATCH" in str(exc)
            else:
                raise AssertionError("Foreign model path accepted")
    finally:
        runtime._instance = original_instance
        runtime._file_cache = original_cache


if __name__ == "__main__":
    test_tokenize()
    test_stream_and_format()
    test_singleton_and_asset_guards()
    print("QWEN35_RUNTIME_ADAPTER_TESTS_PASS", json.dumps({
        "model": runtime.MODEL_REPO,
        "revision": runtime.MODEL_REVISION,
        "cpuThreads": runtime.DECODE_THREADS,
        "context": runtime.CONTEXT_TOKENS,
        "api": "local-only",
    }))
