"""Offline no-paid-provider contract tests for §C self-hosted image understanding."""
from __future__ import annotations

import base64
import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


SOURCE = Path(__file__).resolve().parents[1] / "hf_space" / "chat_vision.py"
spec = importlib.util.spec_from_file_location("swrlz_chat_vision_test", SOURCE)
assert spec and spec.loader
vision = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vision)


def expect_invalid(value: object, expected: str) -> None:
    try:
        vision._validated_image(value)
    except ValueError as exc:
        assert str(exc) == expected, (str(exc), expected)
    else:
        raise AssertionError("Expected rejection " + expected)


jpeg = b"\xff\xd8\xff" + b"\0" * 20
valid = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode("ascii")
assert vision._validated_image(valid) == valid
expect_invalid("data:image/svg+xml;base64," + base64.b64encode(jpeg).decode(), "IMAGE_FORMAT_INVALID")
expect_invalid("data:image/jpeg;base64,?", "IMAGE_FORMAT_INVALID")
expect_invalid("data:image/jpeg;base64," + base64.b64encode(b"not-jpeg").decode(), "IMAGE_FORMAT_INVALID")
expect_invalid("data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff" + b"\0" * vision.MAX_IMAGE_BYTES).decode(), "IMAGE_TOO_LARGE")

source = SOURCE.read_text(encoding="utf-8")
assert "SWRLZ_VISION_API_KEY" not in source
assert "router.huggingface.co" not in source
assert "urllib.request" not in source
assert vision.MODEL_REPO == "ggml-org/SmolVLM-256M-Instruct-GGUF"
assert len(vision.MODEL_REVISION) == 40
assert vision.MODEL_FILE == "SmolVLM-256M-Instruct-Q8_0.gguf"
assert vision.PROJECTOR_FILE == "mmproj-SmolVLM-256M-Instruct-Q8_0.gguf"

# Space metadata must fetch exactly the pinned local CPU vision assets at build
# time, not on the first user image upload. Keep the runtime revision identical.
space_readme = (SOURCE.parent / "README.md").read_text(encoding="utf-8")
preload = (
    'ggml-org/SmolVLM-256M-Instruct-GGUF '
    'SmolVLM-256M-Instruct-Q8_0.gguf,'
    'mmproj-SmolVLM-256M-Instruct-Q8_0.gguf '
    + vision.MODEL_REVISION
)
assert 'preload_from_hub:' in space_readme
assert preload in space_readme
assert space_readme.count('preload_from_hub:') == 1

class FakeModel:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return {"choices": [{"message": {"content": "A white dog on grass."}}]}

fake_model = FakeModel()
with patch.object(vision, "_prepare_image", lambda image: image), patch.object(vision, "_load_local_model", lambda: fake_model):
    answer = vision._ask_vision_local(valid, "What is shown?")
assert answer == "A white dog on grass."
assert len(fake_model.calls) == 1
assert fake_model.calls[0]["messages"][0]["content"][1]["image_url"]["url"] == valid
assert fake_model.calls[0]["max_tokens"] <= 112

vision._inference_lock.acquire()
try:
    try:
        vision._ask_vision_local(valid, "Busy?")
    except vision.VisionBusy:
        pass
    else:
        raise AssertionError("Overlapping vision requests were not rejected")
finally:
    vision._inference_lock.release()

app = FastAPI()
vision.install(app, lambda _: None)
client = TestClient(app)
with patch.object(vision, "_ask_vision_local", lambda image, question: "A local visual description."):
    response = client.post("/api/lalm_station/vision", json={"image": valid, "question": "What is shown?"})
    assert response.status_code == 200, response.text
    assert response.json() == {
        "ok": True,
        "description": "A local visual description.",
        "imageStored": False,
        "backend": "local-cpu",
    }
assert client.post("/api/lalm_station/vision", json={"image": "invalid"}).status_code == 400
assert client.post("/api/lalm_station/vision", data="oops", headers={"Content-Type": "text/plain"}).status_code == 415

unauthenticated = FastAPI()
vision.install(unauthenticated, lambda _: (_ for _ in ()).throw(PermissionError()))
assert TestClient(unauthenticated).post("/api/lalm_station/vision", json={"image": valid}).status_code == 401

with patch.object(vision, "_ask_vision_local", side_effect=vision.VisionBusy()):
    assert client.post("/api/lalm_station/vision", json={"image": valid}).status_code == 429
with patch.object(vision, "_ask_vision_local", side_effect=RuntimeError("private source pixels")):
    response = client.post("/api/lalm_station/vision", json={"image": valid})
    assert response.status_code == 503
    assert "private source pixels" not in response.text

print("Chat vision local CPU: authenticated boundaries, no paid provider, concurrency and mocked inference PASS")
