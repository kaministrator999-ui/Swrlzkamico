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


# Exercise real image parsing, not just a JPEG magic-byte stub.
import io
from PIL import Image
jpeg_buffer = io.BytesIO()
Image.new("RGB", (16, 16), "white").save(jpeg_buffer, format="JPEG")
jpeg = jpeg_buffer.getvalue()
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

# Real image preprocessing must bound the pixels supplied to the CPU projector.
assert vision.MODEL_INPUT_SIDE == 384
assert vision.MAX_IMAGE_BYTES == 8 * 1024 * 1024
assert vision.MAX_BODY_BYTES > 4 * vision.MAX_IMAGE_BYTES // 3
source_image = Image.new("RGB", (1024, 768), "purple")
source_bytes = io.BytesIO()
source_image.save(source_bytes, format="PNG")
encoded_image = "data:image/png;base64," + base64.b64encode(source_bytes.getvalue()).decode("ascii")
assert vision._validated_image(encoded_image) == encoded_image
assert vision._source_image_metadata(encoded_image) == {
    "sourceWidth": 1024, "sourceHeight": 768,
    "sourceBytes": len(source_bytes.getvalue()),
    "originalBytesPreserved": True,
}
prepared = vision._prepare_image(encoded_image)
with Image.open(io.BytesIO(base64.b64decode(prepared.partition(",")[2]))) as downsized:
    assert downsized.size == (384, 288), downsized.size

# The server must accept real source pixels larger than its old 2 MB cap,
# without rewriting JPEG/PNG/WebP payloads at ingress.
import os
noise_image = Image.frombytes("RGB", (1024, 1024), os.urandom(1024*1024*3))
noise_buffer=io.BytesIO()
noise_image.save(noise_buffer, format="PNG")
noise_data=noise_buffer.getvalue()
assert 2_000_000 < len(noise_data) < vision.MAX_IMAGE_BYTES
noise_url="data:image/png;base64,"+base64.b64encode(noise_data).decode("ascii")
assert vision._validated_image(noise_url)==noise_url
assert vision._source_image_metadata(noise_url)["sourceBytes"]==len(noise_data)
assert base64.b64decode(noise_url.partition(",")[2])==noise_data

# Cropping a large original must focus on actual inner source pixels, not
# upscale the previous whole-sheet 768px or 384px preview.
source_large=Image.new("RGB",(2048,1536),"blue")
source_large.paste(Image.new("RGB",(1024,768),"red"),(512,384))
large_buffer=io.BytesIO()
source_large.save(large_buffer,format="PNG")
large_url="data:image/png;base64,"+base64.b64encode(large_buffer.getvalue()).decode("ascii")
whole=vision._prepare_image(large_url,max_side=768)
focus=vision._prepare_image(large_url,max_side=768,focus_center=True)
with Image.open(io.BytesIO(base64.b64decode(whole.partition(",")[2]))) as im:
    assert im.size==(768,576)
    assert im.getpixel((0,im.height//2))[2] > 160, "Whole-sheet edge should be blue"
with Image.open(io.BytesIO(base64.b64decode(focus.partition(",")[2]))) as im:
    assert im.size==(768,576)
    assert im.getpixel((0,im.height//2))[0] > 160, "Native center crop edge should be red"
assert focus!=whole

# A build-time cache hit must NOT incur a Hub network metadata request.
from huggingface_hub.errors import LocalEntryNotFoundError
with patch("huggingface_hub.hf_hub_download", return_value="/cached/model") as download:
    assert vision._cached_asset(vision.MODEL_FILE) == "/cached/model"
    assert download.call_count == 1
    assert download.call_args.kwargs["local_files_only"] is True
with patch("huggingface_hub.hf_hub_download", side_effect=[
        LocalEntryNotFoundError("not preloaded"), "/downloaded/model"]) as download:
    assert vision._cached_asset(vision.MODEL_FILE) == "/downloaded/model"
    assert download.call_count == 2
    assert download.call_args_list[0].kwargs["local_files_only"] is True
    assert "local_files_only" not in download.call_args_list[1].kwargs

class FakeModel:
    def __init__(self):
        self.calls = []

    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return iter([{"choices": [{"delta": {"content": "A white dog on grass."}}]}])

fake_model = FakeModel()
with patch.object(vision, "_load_local_model", return_value=fake_model) as loader:
    assert vision.prewarm_local_model() is fake_model
    loader.assert_called_once()
recorded_phases = []
with patch.object(vision, "_prepare_image", lambda image: image), \
     patch.object(vision, "_source_image_metadata", return_value={"sourceWidth":1,"sourceHeight":1,"sourceBytes":len(jpeg),"originalBytesPreserved":True}), \
     patch.object(vision, "_load_local_model", lambda: fake_model):
    answer = vision._ask_vision_local(
        valid, "What is shown?",
        report_phase=lambda phase, **fields: recorded_phases.append((phase, fields)),
    )
assert answer == "A white dog on grass."
assert any(phase=="ANALYZING" and fields.get("inferenceStage")=="PREFILL" and
           fields.get("activeLevel")==1 for phase,fields in recorded_phases)
assert any(phase == "ANALYZING" and fields.get("inferenceStage") == "DECODING" and
           fields.get("firstChunkSeconds") >= 0 for phase, fields in recorded_phases)
assert len(fake_model.calls) == 1
assert fake_model.calls[0]["messages"][0]["content"][1]["image_url"]["url"] == valid
assert fake_model.calls[0]["max_tokens"] == vision.MAX_VISION_OUTPUT_TOKENS == 88
assert fake_model.calls[0]["stream"] is True
visual_prompt = fake_model.calls[0]["messages"][0]["content"][0]["text"]
assert "multi-view character sheet" in visual_prompt
assert "distinctive colors" in visual_prompt
assert "held objects" in visual_prompt
assert "only clearly legible labels" in visual_prompt
assert "Question: What is shown?" in visual_prompt

# The actual exported turnaround attempts were too generic even when Chat
# faithfully relayed them. The gate tests *observations*, not image identities.
for generic in (
    "Character turnaround page with various views of character.",
    "Character turnaround page with various pictures and text.",
    "The image is a character turnaround. It includes various views of the character, including front view, left side view, right side view, back view, top view, and details about the color palette.",
):
    assert vision._needs_detail_retry(generic), generic
assert not vision._needs_detail_retry(
    "Character turnaround of a mage in a purple hood, gold boots and a crystal staff."
)
assert not vision._needs_detail_retry("A white dog on grass.")
assert not vision._needs_detail_retry("A red car parked beside a building.")
assert vision._needs_detail_retry("Image with various objects.")
assert vision._needs_detail_retry("An image of some shapes.")

# A generic first pass must use the *original* retained resolution for one
# extra inference, not attempt to upscale the already-downsampled 384px JPEG.
class DetailFakeModel:
    def __init__(self):
        self.calls = []
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        result = ("Character turnaround page with various views of character."
                  if len(self.calls) == 1 else
                  "A small mage with a purple hood, golden trim and a crystal staff, shown from multiple angles.")
        return iter([{"choices": [{"delta": {"content": result}}]}])

detail_model = DetailFakeModel()
detail_phases = []
with patch.object(vision, "_load_local_model", return_value=detail_model):
    refined = vision._ask_vision_local(encoded_image, "What do you see in this picture?",
        report_phase=lambda phase, **fields: detail_phases.append((phase, fields)))
assert "purple hood" in refined and "crystal staff" in refined
assert len(detail_model.calls) == 2
assert [call["max_tokens"] for call in detail_model.calls] == [
    vision.MAX_VISION_OUTPUT_TOKENS, vision.DETAIL_RETRY_TOKENS]
detail_dimensions = []
for call in detail_model.calls:
    url = call["messages"][0]["content"][1]["image_url"]["url"]
    with Image.open(io.BytesIO(base64.b64decode(url.partition(",")[2]))) as im:
        detail_dimensions.append(im.size)
assert detail_dimensions == [(384, 288), (640, 480)], detail_dimensions
assert any(phase=="ANALYZING" and fields.get("inferenceStage")=="DETAIL_RETRY" and
           fields.get("detailRetryReason")=="GENERIC_CHARACTER_SHEET" and
           fields.get("activeLevel")==2 for phase,fields in detail_phases)
assert any(fields.get("inferenceStage") == "DETAIL_DECODING" for _, fields in detail_phases)

class RetryFailureModel:
    def __init__(self):
        self.calls = 0
    def create_chat_completion(self, **kwargs):
        self.calls += 1
        if self.calls > 1:
            raise RuntimeError("detail model failed")
        return iter([{"choices": [{"delta": {"content":
            "Character turnaround page with various views of character."}}]}])

retry_failure = RetryFailureModel()
with patch.object(vision, "_load_local_model", return_value=retry_failure):
    coarse = vision._ask_vision_local(encoded_image, "What do you see?")
assert coarse == "Character turnaround page with various views of character."
assert retry_failure.calls == 2

# Never invoke optional retry when original inference was already descriptive.
class SpecificFakeModel:
    def __init__(self):
        self.calls = []
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        return iter([{"choices": [{"delta": {"content":
            "Character turnaround of a mage in a purple hood and gold boots holding a crystal staff."}}]}])

specific_model = SpecificFakeModel()
with patch.object(vision, "_load_local_model", return_value=specific_model):
    detailed_first = vision._ask_vision_local(encoded_image, "What is shown?")
assert "purple hood" in detailed_first
assert len(specific_model.calls) == 1

# Explicit level study runs L1/L2/L3, even when L1 is descriptive.
# It preserves exact source text and actual per-level durations, not a claim
# that a descriptor-keyword score establishes pixel accuracy.
class ThreeLevelModel:
    def __init__(self):
        self.calls=[]
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        sample=[
            "A purple mage in gold boots holding a crystal staff.",
            "Character turnaround of a purple-hooded mage holding a violet crystal staff.",
            "Multi-view character design: purple hood, gold trim, brown boots and a crystal staff.",
        ][len(self.calls)-1]
        return iter([{"choices":[{"delta":{"content":sample}}]}])

study_model=ThreeLevelModel()
study_phases=[]
with patch.object(vision,"_load_local_model",return_value=study_model):
    study=vision._ask_vision_local(encoded_image,"What do you see in this picture?",
        analysis_levels=3,
        report_phase=lambda phase,**fields: study_phases.append((phase,fields)))
assert len(study_model.calls)==3
assert "Level 1" in study and "Level 2" in study and "Level 3" in study
assert "raw model outputs" in study and "accuracy unverified" in study
assert "Original source received: 1024 × 768px" in study
assert "center-source-crop-if-large" in study
assert "A purple mage in gold boots" in study
assert "gold trim, brown boots" in study
assert [x["max_tokens"] for x in study_model.calls]==[
    vision.MAX_VISION_OUTPUT_TOKENS,vision.DETAIL_RETRY_TOKENS,vision.LEVEL3_TOKENS]
study_pixels=[]
for call in study_model.calls:
    url=call["messages"][0]["content"][1]["image_url"]["url"]
    with Image.open(io.BytesIO(base64.b64decode(url.partition(",")[2]))) as im:
        study_pixels.append(im.size)
assert study_pixels==[(384,288),(640,480),(768,576)],study_pixels
last_records=[fields["levelRecords"] for phase,fields in study_phases if fields.get("levelRecords")]
assert len(last_records[-1])==3
assert last_records[-1][0]["description"]=="A purple mage in gold boots holding a crystal staff."
assert last_records[-1][2]["inputMaxSide"]==768
assert all(x["elapsedSeconds"]>=0 for x in last_records[-1])
assert any(f.get("inferenceStage")=="LEVEL3_PREFILL" for _,f in study_phases)
assert any(f.get("inferenceStage")=="LEVEL3_DECODING" for _,f in study_phases)
assert any(f.get("inferenceStage")=="LEVEL3_RETRY" for _,f in study_phases)

# Explicit L1 disables automatic retry even for an uninformative caption.
one_level_model=DetailFakeModel()
with patch.object(vision,"_load_local_model",return_value=one_level_model):
    only_fast=vision._ask_vision_local(encoded_image,"Describe image",analysis_levels=1)
assert len(one_level_model.calls)==1
assert only_fast=="Character turnaround page with various views of character."
for invalid in (0,4,"3",True):
    try:
        vision._ask_vision_local(encoded_image,"test",analysis_levels=invalid)
    except ValueError as exc:
        assert str(exc)=="VISION_LEVEL_INVALID"
    else:
        raise AssertionError("Invalid analysis level should be rejected")

# Cooperative cancellation during the optional pass cannot be converted into
# apparent success by the fallback error handler.
class CancelDuringDetail:
    def __init__(self, stop):
        self.calls = 0
        self.stop = stop
    def create_chat_completion(self, **kwargs):
        self.calls += 1
        if self.calls == 1:
            return iter([{"choices": [{"delta": {"content":
                "Character turnaround page with various pictures and text."}}]}])
        self.stop.set()
        return iter([{"choices": [{"delta": {"content": "A purple hood."}}]}])

stop_detail = threading.Event()
cancel_detail_model = CancelDuringDetail(stop_detail)
with patch.object(vision, "_load_local_model", return_value=cancel_detail_model):
    try:
        vision._ask_vision_local(encoded_image, "Describe this image",
                                 should_cancel=stop_detail.is_set)
    except vision.VisionCancelled:
        pass
    else:
        raise AssertionError("Cancelled detail retry must remain cancelled")
assert cancel_detail_model.calls == 2
assert not vision._inference_lock.locked(), "Cancelled retry must release CPU lock"

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
    assert done["inferenceStage"] == "DECODING", done
    assert done["firstChunkSeconds"] >= 0, done
    assert done["description"] == "A white dog on grass."
    assert done["requestedLevels"] == 2
    assert done["completedLevels"] == 1
    assert len(done["levelRecords"]) == 1
    assert done["levelRecords"][0]["level"] == 1
    assert done["selectedLevel"] == 1
    assert done["sourceWidth"] == 16 and done["sourceHeight"] == 16
    assert done["sourceBytes"] == len(jpeg)
    assert done["originalBytesPreserved"] is True
    # Status reflects only server-read original dimensions, never a guessed
    # pixel size or a fabricated verified visual recognition score.
    assert done["done"] is True
    assert done["elapsedSeconds"] >= done["phaseElapsedSeconds"] >= 0
    assert isinstance(done["elapsedSeconds"], float)
    assert isinstance(done["phaseElapsedSeconds"], float)

assert client.post("/api/lalm_station/vision", json={"image": "invalid"}).status_code == 400
for bad in (0,4,"3",True):
    invalid_response=client.post("/api/lalm_station/vision",
        json={"image":valid,"question":"test","analysisLevels":bad})
    assert invalid_response.status_code==400,invalid_response.text
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
        def pieces():
            if "Question: First" in user_prompt or "User question: First" in user_prompt:
                started.set()
                if not release.wait(timeout=3):
                    raise RuntimeError("test worker never released")
            yield {"choices": [{"delta": {"content": "The image contains a small mage."}}]}
        return pieces()


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

# Cancellation must free a queued request before it acquires the model lock,
# and should stop streaming generation between chunks, never release the lock
# before native inference really returns.
cancel_started = threading.Event()
allow_next_chunk = threading.Event()


class CancellableModel:
    def create_chat_completion(self, **kwargs):
        def chunks():
            cancel_started.set()
            yield {"choices": [{"delta": {"content": "partial"}}]}
            if not allow_next_chunk.wait(timeout=3):
                raise RuntimeError("test did not release token generation")
            yield {"choices": [{"delta": {"content": " that must not be saved"}}]}
        return chunks()


with patch.object(vision, "_prepare_image", lambda x: x), patch.object(vision, "_load_local_model", lambda: CancellableModel()):
    running = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Cancel running"})
    assert running.status_code == 202
    cancelled_id = running.json()["jobId"]
    assert cancel_started.wait(timeout=2)
    other_cancel = TestClient(other_user).post("/api/lalm_station/vision/cancel", json={"jobId": cancelled_id})
    assert other_cancel.status_code == 404, other_cancel.text
    assert TestClient(unauthenticated).post("/api/lalm_station/vision/cancel", json={"jobId": cancelled_id}).status_code == 401
    stopped = client.post("/api/lalm_station/vision/cancel", json={"jobId": cancelled_id})
    assert stopped.status_code == 200 and stopped.json()["cancelRequested"] is True
    allow_next_chunk.set()
    cancelled = poll_done(cancelled_id)
    assert cancelled["phase"] == "CANCELLED" and cancelled["done"] is True
    assert cancelled["ok"] is False
    assert "description" not in cancelled
    resumed = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Cancel running"})
    assert resumed.status_code == 202
    assert resumed.json()["jobId"] != cancelled_id
    assert poll_done(resumed.json()["jobId"])["phase"] == "COMPLETE"

# An unwatched request triggers a cooperative cancellation flag. A poll on a
# genuinely live request keeps its lease current, so the queue does not evict it.
with vision._jobs_lock:
    active = {"phase": "QUEUED", "id": "a" * 32,
              "lastPolledAt": 100.0, "cancelEvent": threading.Event()}
    watched = {"phase": "ANALYZING", "id": "b" * 32,
               "lastPolledAt": 205.0, "cancelEvent": threading.Event()}
    vision._jobs["a" * 32] = active
    vision._jobs["b" * 32] = watched
    vision._cancel_unwatched_jobs(205.0)
    assert active["cancelEvent"].is_set()
    assert not watched["cancelEvent"].is_set()
    vision._jobs.pop("a" * 32)
    vision._jobs.pop("b" * 32)


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
    isinstance(node, ast.FunctionDef) and node.name in {"_ground_vision_handoff", "_direct_vision_description"}
    or isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id in {"_VISION_START","_VISION_END"} for target in node.targets)
)]
namespace = {"Any": typing.Any, "re": __import__("re")}
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
direct = namespace["_direct_vision_description"]
assert direct(input_payload) is not None  # This is an intentional direct image-description question.
direct_user = "What do you see in this picture?" + vision.VISION_START + observed + vision.VISION_END
direct_response = direct({"prompt": direct_user, "history": []})
assert isinstance(direct_response, str)
assert "Local image analyzer's description" in direct_response
assert direct_response.endswith(observed)
assert direct_response.count(observed) == 1, "Never regenerate or invent description"
assert direct({"prompt": "Describe this image" + vision.VISION_START + observed + vision.VISION_END}) is not None
assert direct({"prompt": "What do you see in this image?" + vision.VISION_START + observed + vision.VISION_END}) is not None
assert direct({"prompt": "Please describe this image!" + vision.VISION_START + observed + vision.VISION_END}) is not None
assert direct({"prompt": "What do you see in this picture?\nPlease identify tiny text" + vision.VISION_START + observed + vision.VISION_END}) is None
assert direct({"prompt": "How should I model this?" + vision.VISION_START + observed + vision.VISION_END}) is None
assert direct({"prompt": "What do you see in this picture?" + vision.VISION_START + vision.VISION_END}) is None
assert direct({"prompt": "What do you see in this picture?"}) is None
assert "VISION_DESCRIPTION_DIRECT" in router_source
assert 'direct_vision = _direct_vision_description(payload)' in router_source
assert "payload=_ground_vision_handoff(_apply_personality(payload))" in router_source

station_source = (SOURCE.parent / "station.py").read_text(encoding="utf-8")
assert "from chat_vision import export_threads_with_vision_handoffs" in station_source
assert '"threads":export_threads_with_vision_handoffs(_ordered_native_threads(snapshot["threads"]))' in station_source
assert '"Cache-Control":"no-store"' in station_source

# A watcher resuming after a pause renews its own lease before pruning
# other abandoned jobs. This guards browser auto-resync after mobile sleep.
station_source = (SOURCE.parent / "chat_vision.py").read_text(encoding="utf-8")
assert station_source.index('job["lastPolledAt"] = now', station_source.index("def vision_status(")) < station_source.index('_cancel_unwatched_jobs(now)', station_source.index("def vision_status("))

# Dense wide reference sheets need real source-pixel crops focused on the
# figure band, not four full-height strips containing unrelated footer panels.
from PIL import ImageDraw
reference = Image.new("RGB", (1448, 1086), "white")
painter = ImageDraw.Draw(reference)
for index in range(4):
    left = 32 + index * 360
    painter.rectangle((left, 170, left + 160, 670),
                      fill="#7040ba", outline="#202020", width=12)
    painter.line((left + 25, 200, left + 140, 625),
                 fill="#e5b744", width=14)
# Palette below figures must not occupy each character-focused crop.
painter.rectangle((0, 950, 1447, 1085), fill="#11aa22")
buffer = io.BytesIO()
reference.save(buffer, format="PNG")
reference_encoded = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
regions = vision._detail_regions(reference_encoded, "Character page with various features.")
assert [label for label, _ in regions] == [
    "Far-left detail", "Center-left detail",
    "Center-right detail", "Far-right detail",
]
for label, encoded in regions:
    with Image.open(io.BytesIO(base64.b64decode(encoded.partition(",")[2]))) as cropped:
        assert cropped.height <= 740, (label, cropped.size)
        assert cropped.width <= 768, (label, cropped.size)
assert vision._detail_regions(valid, "Red background") == []

print("Chat vision local CPU: authenticated boundaries, no paid provider, concurrency and mocked inference and export handoff PASS")
