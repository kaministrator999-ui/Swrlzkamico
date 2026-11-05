"""Offline no-paid-provider contract tests for §C self-hosted image understanding."""
from __future__ import annotations

import base64
import importlib.util
import json
import threading
import time
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
assert fake_model.calls[0]["max_tokens"] <= 192
visual_prompt = fake_model.calls[0]["messages"][0]["content"][0]["text"]
assert "different viewpoints" in visual_prompt
assert "not a transformation" in visual_prompt
assert "title or view labels" in visual_prompt
assert "Do not invent evolution" in visual_prompt

# Async job contract: the POST acknowledges immediately, status exposes real
# worker stages, duplicate submissions resume the same job, and one other image
# can wait for CPU. A third distinct upload is bounded rather than piling up.
app = FastAPI()
vision.install(app, lambda _: "google:test")
client = TestClient(app)


def poll_done(job_id):
    for _ in range(200):
        r = client.get("/api/lalm_station/vision/status", params={"jobId": job_id})
        assert r.status_code == 200, r.text
        payload = r.json()
        if payload["done"]:
            return payload
        time.sleep(.02)
    raise AssertionError("Mocked image job did not finish")


with patch.object(vision, "_prepare_image", lambda x: x), patch.object(vision, "_load_local_model", lambda: fake_model):
    response = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Simple"})
    assert response.status_code == 202, response.text
    job_id = response.json()["jobId"]
    assert len(job_id) == 32
    done = poll_done(job_id)
    assert done["phase"] == "COMPLETE", done
    assert done["description"] == "A white dog on grass."
    assert done["done"] is True
    assert done["elapsedSeconds"] >= done["phaseElapsedSeconds"] >= 0
    assert isinstance(done["elapsedSeconds"], float)
    assert isinstance(done["phaseElapsedSeconds"], float)

assert client.post("/api/lalm_station/vision", json={"image": "invalid"}).status_code == 400
assert client.post("/api/lalm_station/vision", data="oops", headers={"Content-Type": "text/plain"}).status_code == 415
assert client.get("/api/lalm_station/vision/status", params={"jobId": "invalid"}).status_code == 400
assert client.get("/api/lalm_station/vision/status", params={"jobId": "a"*32}).status_code == 404

unauthenticated = FastAPI()
vision.install(unauthenticated, lambda _: (_ for _ in ()).throw(PermissionError()))
assert TestClient(unauthenticated).post("/api/lalm_station/vision", json={"image": valid}).status_code == 401
assert TestClient(unauthenticated).get("/api/lalm_station/vision/status", params={"jobId": job_id}).status_code == 401
other_user = FastAPI()
vision.install(other_user, lambda _: "google:other")
assert TestClient(other_user).get("/api/lalm_station/vision/status", params={"jobId": job_id}).status_code == 404

started = threading.Event()
release = threading.Event()


class SlowFakeModel:
    def create_chat_completion(self, **kwargs):
        user_prompt = kwargs["messages"][0]["content"][0]["text"]
        if "Question: First" in user_prompt or "User question: First" in user_prompt:
            started.set()
            if not release.wait(timeout=3):
                raise RuntimeError("test worker never released")
        return {"choices": [{"message": {"content": "The image contains a small mage."}}]}


with patch.object(vision, "_prepare_image", lambda x: x), patch.object(vision, "_load_local_model", lambda: SlowFakeModel()):
    first = client.post("/api/lalm_station/vision", json={"image": valid, "question": "First"})
    assert first.status_code == 202
    assert started.wait(timeout=2)
    first_id = first.json()["jobId"]
    again = client.post("/api/lalm_station/vision", json={"image": valid, "question": "First"})
    assert again.status_code == 202 and again.json()["jobId"] == first_id
    second = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Second"})
    assert second.status_code == 202
    second_id = second.json()["jobId"]
    queued = client.get("/api/lalm_station/vision/status", params={"jobId": second_id}).json()
    assert queued["phase"] == "QUEUED", queued
    assert queued["elapsedSeconds"] >= queued["phaseElapsedSeconds"] >= 0
    time.sleep(.07)
    queued_later = client.get("/api/lalm_station/vision/status", params={"jobId": second_id}).json()
    assert queued_later["elapsedSeconds"] >= queued["elapsedSeconds"]
    assert queued_later["phaseElapsedSeconds"] >= queued["phaseElapsedSeconds"]
    third = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Third"})
    assert third.status_code == 429
    assert third.json()["code"] == "VISION_QUEUE_FULL"
    release.set()
    assert poll_done(first_id)["phase"] == "COMPLETE"
    assert poll_done(second_id)["phase"] == "COMPLETE"

with patch.object(vision, "_ask_vision_local", side_effect=RuntimeError("secret image bytes")):
    failed = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Error case"})
    assert failed.status_code == 202
    result = poll_done(failed.json()["jobId"])
    assert result["phase"] == "FAILED" and result["ok"] is False
    assert "secret image bytes" not in json.dumps(result)

assert "router.huggingface.co" not in source
assert "SWRLZ_VISION_API_KEY" not in source

# Parse exactly what the text-only Chat model received. The existing side-menu
# download is owned by Station and returns saved threads, not private pixels.
question = "What do you see in this picture?"
observed = "Title: Character Turnaround.\nMultiple views of the same purple-hooded mage."
saved = question + vision.VISION_START + observed + vision.VISION_END
user_message = {"id": "u1", "role": "user", "text": saved, "meta": {"requestId": "r1"}}
unrelated = {"id": "u2", "role": "user", "text": "No image here."}
assistant = {"id": "a1", "role": "assistant", "text": "A summary."}
threads = [{"id": "t1", "messages": [user_message, unrelated, assistant]}]
exported = vision.export_threads_with_vision_handoffs(threads)
analysis = exported[0]["messages"][0]["visionAnalysis"]
assert analysis == {
    "schema": "swrlz-vision-handoff-export-v1",
    "questionSentToChatModel": question,
    "descriptionSentToChatModel": observed,
    "source": "parsed-from-saved-user-message",
    "isVerifiedVisionModelReceipt": False,
    "imagePixelsIncluded": False,
}
assert exported[0]["messages"][0]["text"] == saved
assert "visionAnalysis" not in threads[0]["messages"][0], "Export must not change durable state"
assert "visionAnalysis" not in exported[0]["messages"][1]
assert "visionAnalysis" not in exported[0]["messages"][2]
assert vision.vision_handoff_from_message({"role": "user", "text": question + vision.VISION_START + vision.VISION_END}) is None
assert vision.vision_handoff_from_message({"role": "user", "text": saved + " extra"}) is None
assert vision.vision_handoff_from_message({"role": "assistant", "text": saved}) is None
assert vision.vision_handoff_from_message({"role": "user", "text": question + vision.VISION_START + "x"*6001 + vision.VISION_END}) is None
# Marker-shaped user text is labeled as a parser result, NOT an independently
# verified inference receipt. The same parser works for older image chats.
assert analysis["isVerifiedVisionModelReceipt"] is False

# Grounding is added to the inference-only copy after classification; neither
# the export nor the stored prompt is rewritten by the second model's policy.
import ast
import typing
router_source = (SOURCE.parent / "model_router.py").read_text(encoding="utf-8")
tree = ast.parse(router_source)
selected = [node for node in tree.body if isinstance(node, (ast.Assign, ast.FunctionDef)) and (
    isinstance(node, ast.FunctionDef) and node.name == "_ground_vision_handoff"
    or isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in {"_VISION_START","_VISION_END"} for target in node.targets)
)]
namespace = {"Any": typing.Any}
exec(compile(ast.Module(body=selected, type_ignores=[]), "<vision-grounding>", "exec"), namespace)
ground = namespace["_ground_vision_handoff"]
unchanged = {"prompt": "Hello", "history": []}
assert ground(unchanged) is unchanged
input_payload = {"prompt": saved, "history": []}
grounded = ground(input_payload)
assert grounded is not input_payload
assert grounded["prompt"].endswith(saved)
assert "NOT transformation stages" in grounded["prompt"]
assert "FALLIBLE textual description" in grounded["prompt"]
assert input_payload["prompt"] == saved
assert "payload=_ground_vision_handoff(_apply_personality(payload))" in router_source

station_source = (SOURCE.parent / "station.py").read_text(encoding="utf-8")
assert "from chat_vision import export_threads_with_vision_handoffs" in station_source
assert '"threads":export_threads_with_vision_handoffs(_ordered_native_threads(snapshot["threads"]))' in station_source
assert '"Cache-Control":"no-store"' in station_source

print("Chat vision local CPU: authenticated boundaries, no paid provider, concurrency and mocked inference and export handoff PASS")
