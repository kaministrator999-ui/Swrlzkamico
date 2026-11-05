"""Offline, bounded image-preprocessing and provider-wire tests for §C."""
from __future__ import annotations

import base64
import importlib.util
import json
import os
from pathlib import Path
from unittest.mock import patch


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
valid = "data:image/jpeg;base64," + base64.b64encode(jpeg).decode()
assert vision._validated_image(valid) == valid
expect_invalid("data:image/svg+xml;base64," + base64.b64encode(jpeg).decode(), "IMAGE_FORMAT_INVALID")
expect_invalid("data:image/jpeg;base64,?", "IMAGE_FORMAT_INVALID")
expect_invalid("data:image/jpeg;base64," + base64.b64encode(b"not-jpeg").decode(), "IMAGE_FORMAT_INVALID")
expect_invalid("data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff" + b"\0" * vision.MAX_IMAGE_BYTES).decode(), "IMAGE_TOO_LARGE")

with patch.dict(os.environ, {
    "SWRLZ_VISION_API_URL": "https://example.test/v1/chat/completions",
    "SWRLZ_VISION_MODEL": "vision-test-model",
    "SWRLZ_VISION_API_KEY": "test-only-token",
}):
    endpoint, model, token = vision._vision_config()
    assert endpoint == "https://example.test/v1/chat/completions"
    assert model == "vision-test-model"
    assert token == "test-only-token"

    class FakeResponse:
        def __enter__(self):
            return self
        def __exit__(self, *_):
            return False
        def read(self, _):
            return json.dumps({"choices": [{"message": {"content": "A grounded visual description."}}]}).encode()

    observed = []

    def fake_urlopen(request, timeout):
        assert timeout == 35
        assert request.get_method() == "POST"
        assert request.get_header("Authorization") == "Bearer test-only-token"
        payload = json.loads(request.data)
        observed.append(payload)
        return FakeResponse()

    with patch.object(vision.urllib.request, "urlopen", fake_urlopen):
        description = vision._ask_vision(endpoint, model, token, valid, "What is shown?")
    assert description == "A grounded visual description."
    assert len(observed) == 1
    assert observed[0]["model"] == model
    assert observed[0]["messages"][0]["content"][1]["image_url"]["url"] == valid

with patch.dict(os.environ, {
    "SWRLZ_VISION_API_URL": "http://insecure.test/v1/chat/completions",
    "SWRLZ_VISION_MODEL": "vision-test-model",
    "SWRLZ_VISION_API_KEY": "test-only-token",
}):
    try:
        vision._vision_config()
    except ValueError as exc:
        assert str(exc) == "VISION_ENDPOINT_INVALID"
    else:
        raise AssertionError("Non-HTTPS vision endpoint accepted")

print("Chat vision: size, format, HTTPS and mocked provider POST PASS")
