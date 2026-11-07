"""Offline configuration and mocked-loader checks; no model download or paid inference."""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
import sys
import types
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "hf_space" / "chat_vision.py"


def _vision(variant):
    with patch.dict(os.environ, {"SWRLZ_VISION_MODEL": variant}):
        spec = importlib.util.spec_from_file_location("swrlz_qwen3_vision_test", SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    return module


def test_current_smolvlm_default_preserved():
    vision = _vision("smolvlm-500m")
    assert vision.VISION_MODEL_VARIANT == "smolvlm-500m"
    assert vision.MODEL_REPO == "ggml-org/SmolVLM-500M-Instruct-GGUF"
    assert vision.MODEL_INPUT_SIDE == 384
    assert vision.MAX_VISION_OUTPUT_TOKENS == 88


def test_qwen_config_pins_matching_weights_and_projector():
    vision = _vision("qwen3-vl-4b")
    assert vision.MODEL_REPO == "Qwen/Qwen3-VL-4B-Instruct-GGUF"
    assert vision.MODEL_REVISION == "1cd86afb9a95c410a6038ab3b40d8b578c892266"
    assert vision.MODEL_FILE == "Qwen3VL-4B-Instruct-Q4_K_M.gguf"
    assert vision.PROJECTOR_FILE == "mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf"
    assert vision.MODEL_INPUT_SIDE == 768
    assert vision.MAX_VISION_OUTPUT_TOKENS == 224


def test_qwen_loader_uses_compatible_handler_and_matching_projector():
    vision = _vision("qwen3-vl-4b")
    observed = {}

    class FakeHandler:
        def __init__(self, **kwargs):
            observed["handler"] = kwargs

    class FakeLlama:
        def __init__(self, **kwargs):
            observed["llama"] = kwargs

    fake_cpp = types.ModuleType("llama_cpp")
    fake_cpp.Llama = FakeLlama
    fake_multimodal = types.ModuleType("llama_cpp.llama_multimodal")
    fake_multimodal.Qwen3VLChatHandler = FakeHandler
    with patch.dict(sys.modules, {"llama_cpp": fake_cpp,
                                  "llama_cpp.llama_multimodal": fake_multimodal}):
        with patch.object(vision, "_cached_asset", side_effect=lambda filename: "/test/" + filename):
            instance = vision._load_local_model()
    assert isinstance(instance, FakeLlama)
    assert observed["handler"]["mmproj_path"].endswith(vision.PROJECTOR_FILE)
    assert observed["handler"]["force_reasoning"] is False
    assert observed["handler"]["image_min_tokens"] == 1024
    assert observed["handler"]["use_gpu"] is False
    assert observed["llama"]["model_path"].endswith(vision.MODEL_FILE)
    assert observed["llama"]["n_ctx"] == 10240
    assert observed["llama"]["n_gpu_layers"] == 0


def test_unsupported_runtime_fails_before_downloading_weights():
    vision = _vision("qwen3-vl-4b")
    fake_cpp = types.ModuleType("llama_cpp")
    fake_cpp.Llama = object
    # A plain 0.3.35-style distribution without Qwen3VLChatHandler
    # must not download 3GB of weights and then quietly use the wrong handler.
    with patch.dict(sys.modules, {"llama_cpp": fake_cpp}):
        sys.modules.pop("llama_cpp.llama_multimodal", None)
        with patch.object(vision, "_cached_asset", side_effect=AssertionError("download attempted")):
            try:
                vision._load_local_model()
            except RuntimeError as exc:
                assert "QWEN3_VL_BACKEND_UNAVAILABLE" in str(exc)
            else:
                raise AssertionError("incompatible runtime was accepted")
