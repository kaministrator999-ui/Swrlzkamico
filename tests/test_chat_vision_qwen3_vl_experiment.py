"""Offline Qwen3-VL route checks; no Space mutation or model downloads."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1] / "hf_space"
SOURCE = ROOT / "chat_vision.py"


def _vision(variant):
    # The real Space exposes hf_space as its module root. Reproduce that
    # import context for isolated source loading without permanently editing sys.path.
    with patch.dict(os.environ, {"SWRLZ_VISION_MODEL": variant}), \
         patch.object(sys, "path", [str(ROOT), *sys.path]):
        spec = importlib.util.spec_from_file_location("swrlz_qwen3_vision_test", SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def test_qwen_is_the_only_vision_engine_and_ignores_stale_settings():
    # Historical environment settings cannot select a retired model.
    for old_value in ("smolvlm-500m", "Qwen/Qwen2.5-VL-3B-Instruct",
                      "unrecognized-legacy-setting", "qwen3-vl-4b"):
        vision = _vision(old_value)
        assert vision.VISION_MODEL_VARIANT == "qwen3-vl-4b"
        assert vision.MODEL_REPO == "Qwen/Qwen3-VL-4B-Instruct-GGUF"
        assert vision.MODEL_INPUT_SIDE == 768
        assert vision.MAX_VISION_OUTPUT_TOKENS == 224
        assert vision.WATCH_LEASE_SECONDS == 20 * 60
    source = SOURCE.read_text(encoding="utf-8")
    assert "MTMDChatHandler" not in source
    assert "ggml-org/SmolVLM" not in source
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    preload = readme.split("---", 2)[1]
    assert "Qwen3VL-4B-Instruct-Q4_K_M.gguf" in preload
    assert "SmolVLM" not in preload


def test_qwen_trial_config_pinned():
    vision = _vision("qwen3-vl-4b")
    assert vision.MODEL_REPO == "Qwen/Qwen3-VL-4B-Instruct-GGUF"
    assert vision.MODEL_REVISION == "1cd86afb9a95c410a6038ab3b40d8b578c892266"
    assert vision.MODEL_FILE == "Qwen3VL-4B-Instruct-Q4_K_M.gguf"
    assert vision.PROJECTOR_FILE == "mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf"
    assert vision.MODEL_INPUT_SIDE == 768
    assert vision.MAX_VISION_OUTPUT_TOKENS == 224


def test_trial_loads_separate_process_without_overwriting_llama_cpp():
    vision = _vision("qwen3-vl-4b")
    calls = []
    sentinel = object()
    fake_backend = types.ModuleType("qwen3vl_local_server")
    fake_backend.load = lambda model, projector: (calls.append((model, projector)), sentinel)[1]
    with patch.dict(sys.modules, {"qwen3vl_local_server": fake_backend}):
        with patch.object(vision, "_cached_asset", side_effect=lambda name: "/cache/" + name):
            assert vision._load_local_model() is sentinel
    assert calls == [("/cache/" + vision.MODEL_FILE, "/cache/" + vision.PROJECTOR_FILE)]


def test_qwen_prewarms_once_on_space_startup_without_ui_status():
    # Source-only guard: importing app.py would start costly HF runtime setup.
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert '("vision",prewarm_local_model)' in app
    assert 'threading.Thread(target=_warm_backends,daemon=True' in app
    assert "QWEN3_VL_LOAD_ON_FIRST_IMAGE" not in app
    assert "HF_WARMUP_DEFERRED" not in app
    assert '("700m",large_load)' in app
    # Vision model cache is shared by startup prewarm and subsequent images.
    source = SOURCE.read_text(encoding="utf-8")
    assert "_model = instance" in source
    assert "if _model is not None:" in source
    assert "with _inference_lock:" in source


def test_qwen_server_is_local_and_source_revision_immutable():
    import sys
    sys.path.insert(0, str(ROOT))
    import qwen3vl_local_server as server
    assert server.LLAMA_CPP_COMMIT == "fd27b2034905f8dadd8bd6d2cc44595f4929d391"
    assert server.SERVER_URL.startswith("http://127.0.0.1:")
    assert "https://github.com/ggml-org/llama.cpp.git" == server.UPSTREAM_URL


def test_qwen_server_sse_yields_real_choices_not_synthetic_output():
    import sys
    sys.path.insert(0, str(ROOT))
    import qwen3vl_local_server as server

    class FakeHTTP:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def __iter__(self):
            return iter([
                b'data: {"choices":[{"delta":{"content":"rock"}}]}\n',
                b'data: {"choices":[{"delta":{"content":" hand"}}]}\n',
                b'data: [DONE]\n'
            ])

    with patch.object(server.urllib.request, "urlopen", return_value=FakeHTTP()):
        adapter = object.__new__(server.LocalQwen3VL)
        events = list(adapter.create_chat_completion(
            messages=[{"role":"user","content":"test"}], max_tokens=8,
            temperature=0.1, stream=True
        ))
    assert [chunk["choices"][0]["delta"]["content"] for chunk in events] == ["rock", " hand"]


if __name__ == "__main__":
    for name, obj in sorted(globals().items()):
        if name.startswith("test_") and callable(obj):
            obj()
    print("Qwen3-VL isolated source/adapter tests: PASS")
