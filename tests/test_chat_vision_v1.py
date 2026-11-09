"""Offline no-paid-provider contract tests for §C self-hosted image understanding."""
from __future__ import annotations

import base64
import importlib.util
import json
import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


# Exercise transport, region inference, and explicit level comparisons using
# the single active Qwen3-VL vision route, with mocked model responses.
SOURCE = Path(__file__).resolve().parents[1] / "hf_space" / "chat_vision.py"
# The vision module loads the layout helper alongside the Space runtime.
sys.path.insert(0, str(SOURCE.parent))
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
assert vision.MODEL_REPO == "Qwen/Qwen3-VL-4B-Instruct-GGUF"
assert len(vision.MODEL_REVISION) == 40
assert vision.MODEL_FILE == "Qwen3VL-4B-Instruct-Q4_K_M.gguf"
assert vision.PROJECTOR_FILE == "mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf"

# Space metadata must fetch exactly the pinned local CPU vision assets at build
# time, not on the first user image upload. Keep the runtime revision identical.
space_readme = (SOURCE.parent / "README.md").read_text(encoding="utf-8")
preload = (
    'Qwen/Qwen3-VL-4B-Instruct-GGUF '
    'Qwen3VL-4B-Instruct-Q4_K_M.gguf,'
    'mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf '
    + vision.MODEL_REVISION
)
assert 'preload_from_hub:' in space_readme
assert preload in space_readme
assert space_readme.count('preload_from_hub:') == 1

# Real image preprocessing must bound the pixels supplied to the CPU projector.
assert vision.MODEL_INPUT_SIDE == 768
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
    assert downsized.size == (768, 576), downsized.size

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
assert fake_model.calls[0]["max_tokens"] == vision.MAX_VISION_OUTPUT_TOKENS == 224
assert fake_model.calls[0]["stream"] is True
visual_prompt = fake_model.calls[0]["messages"][0]["content"][0]["text"]
assert "multi-view sheet" in visual_prompt
assert "concrete" in visual_prompt
assert "never generalize a pose or held object to" in visual_prompt
assert "Detail-only, palette and overhead panels" in visual_prompt
assert "clothing, objects" in visual_prompt
assert "Only read clearly legible text" in visual_prompt
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
assert detail_dimensions == [(768, 576), (768, 576)], detail_dimensions
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
assert study_pixels==[(768,576),(768,576),(768,576)],study_pixels
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
    # Resource observations are from shared cgroup, not model-owned RAM/CPU.
    usage = done["resourceUsage"]
    assert usage["schema"] == "swrlz-response-resource-usage-v1"
    assert usage["scope"] == "shared-cgroup-v2"
    assert usage["isolatedModelAttribution"] is False
    assert usage["routeId"] == "qwen3-vl-4b"
    assert usage["outcome"] == "COMPLETE"
    assert "memoryPeakSampledBytes" in usage["observed"]
    # Only the actual account and matching completed vision handoff may attach
    # those readings to a saved user/assistant message.
    handoff_prompt = "Describe this image." + vision.VISION_START + done["description"] + vision.VISION_END
    receipt = vision.vision_job_resource_receipt("google:test",job_id,handoff_prompt)
    assert receipt is not None and receipt["usage"]["routeId"] == "qwen3-vl-4b"
    assert vision.vision_job_resource_receipt("google:other",job_id,handoff_prompt) is None
    assert vision.vision_job_resource_receipt("google:test","0"*32,handoff_prompt) is None
    assert vision.vision_job_resource_receipt("google:test",job_id,handoff_prompt+"tampered") is None
    # Status reflects only server-read original dimensions, never a guessed
    # pixel size or a fabricated verified visual recognition score.
    assert done["done"] is True
    assert done["elapsedSeconds"] >= done["phaseElapsedSeconds"] >= 0
    assert isinstance(done["elapsedSeconds"], float)
    assert isinstance(done["phaseElapsedSeconds"], float)
    # Each explicit Send gets its own ID. Retries of that Send reuse the
    # accepted completed job; a new Send never replays stale completed text.
    first_payload = {"image": valid, "question": "Fresh resend",
                     "visionRequestId": "vision-fresh-0001"}
    first = client.post("/api/lalm_station/vision", json=first_payload)
    assert first.status_code == 202 and first.json()["resumedExistingJob"] is False
    first_id = first.json()["jobId"]
    assert poll_done(first_id)["phase"] == "COMPLETE"
    calls_after_first = len(fake_model.calls)
    retry = client.post("/api/lalm_station/vision", json=first_payload)
    assert retry.status_code == 202
    assert retry.json()["jobId"] == first_id
    assert retry.json()["resumedExistingJob"] is True
    assert retry.json()["done"] is True
    assert len(fake_model.calls) == calls_after_first, "retry may not rerun inference"
    second_payload = dict(first_payload, visionRequestId="vision-fresh-0002")
    second = client.post("/api/lalm_station/vision", json=second_payload)
    assert second.status_code == 202
    assert second.json()["resumedExistingJob"] is False
    assert second.json()["jobId"] != first_id
    assert poll_done(second.json()["jobId"])["phase"] == "COMPLETE"
    assert len(fake_model.calls) == calls_after_first + 1, "new Send must rerun local inference"
    # Older clients without per-send IDs must not silently replay a completed
    # request just because image, prompt and analysis level match.
    legacy = client.post("/api/lalm_station/vision", json={"image": valid, "question": "Simple"})
    assert legacy.status_code == 202
    assert legacy.json()["jobId"] != job_id
    assert legacy.json()["resumedExistingJob"] is False
    assert poll_done(legacy.json()["jobId"])["phase"] == "COMPLETE"

assert client.post("/api/lalm_station/vision", json={"image": "invalid"}).status_code == 400
for bad in (0,4,"3",True):
    invalid_response=client.post("/api/lalm_station/vision",
        json={"image":valid,"question":"test","analysisLevels":bad})
    assert invalid_response.status_code==400,invalid_response.text
for invalid_nonce in ("x", "has spaces in it", "z" * 129, 17):
    invalid_response = client.post("/api/lalm_station/vision", json={
        "image": valid, "question": "test", "visionRequestId": invalid_nonce})
    assert invalid_response.status_code == 400
    assert invalid_response.json()["code"] == "VISION_REQUEST_ID_INVALID"
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
    now = 100.0 + vision.WATCH_LEASE_SECONDS + 10.0
    active = {"phase": "QUEUED", "id": "a" * 32,
              "lastPolledAt": 100.0, "cancelEvent": threading.Event()}
    watched = {"phase": "ANALYZING", "id": "b" * 32,
               "lastPolledAt": now - 5.0, "cancelEvent": threading.Event()}
    vision._jobs["a" * 32] = active
    vision._jobs["b" * 32] = watched
    vision._cancel_unwatched_jobs(now)
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
    isinstance(node, ast.FunctionDef) and node.name in {"_ground_vision_handoff", "_direct_vision_description", "_format_direct_vision_report", "_omit_unverifiable_turnaround_claims", "_conflicting_staff_handedness"}
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
assert direct_response.startswith("## Image analysis\n\n")
assert observed in direct_response
assert direct_response.count(observed) == 1, "Never regenerate or invent description"
assert "not independently verified" in direct_response
# Real old Qwen descriptions keep one readable final answer; the raw model
# appendix stays in the saved user message and its export.
legacy = ("Character reference · local model observation (accuracy unverified)\n\n"
          "Subject and views: One hooded character in multiple views.\n"
          "Shape and proportions: Large hood and compact body.\n"
          "Materials and markings: Purple robe, gold trim.\n"
          "\nFocused image details (unverified source-crop observations):\n"
          "- Upper-left crop: Large hood and compact body.")
legacy_answer = direct({"prompt": question + vision.VISION_START + legacy + vision.VISION_END})
assert legacy_answer.startswith("## Image analysis")
assert "### Shape & proportions" in legacy_answer
assert "### Materials & markings" in legacy_answer
assert "Upper-left crop" not in legacy_answer
assert legacy_answer.count("Large hood and compact body.") == 1

# Regression from an actual Little Crystal Mage turnaround observation:
# visually unverifiable categorical negatives and cross-view absolutes must
# not be polished into false certainty by the final presentation layer.
problematic_vision = (
    "Character reference · local model observation (accuracy unverified)\n\n"
    "Subject and views: Front, left side, right side, back, and top views of "
    "a single character, Little Crystal Mage.\n"
    "Silhouette and anatomy: Pale skin, silver-white braided hair, purple eyes. "
    "Standing posture with arms at sides or holding staff. "
    "No occlusion in any view; all limbs and head are visible.\n"
    "Clothing and surface detail: Deep purple hooded robe with gold embroidery. "
    "Belt with pouch. Brown boots. No buckles or hidden construction.\n"
    "Props and small features: Staff topped with glowing purple crystal. "
    "Braids are visible in all views. No leaf emblems or leaf motifs on the staff.\n"
    "Visibility limits: Back view shows only the back of the robe and staff; "
    "no occlusion of the character's face or limbs. "
    "Top view shows only the head and shoulders; no occlusion of the staff or hands.\n"
    "\nFocused image details (unverified source-crop observations):\n"
    "- Upper-left figure detail: Two identical figures in purple robes."
)
problematic_result = direct({
    "prompt": "What do you see in this image?" +
              vision.VISION_START + problematic_vision + vision.VISION_END
})
assert problematic_result.startswith("## Image analysis")
for unsafe in (
    "No occlusion", "no occlusion", "all limbs and head are visible",
    "No buckles", "No leaf emblems", "Braids are visible in all views",
    "Two identical figures"
):
    assert unsafe not in problematic_result, unsafe
for preserved in (
    "Little Crystal Mage", "silver-white braided hair", "Deep purple hooded robe",
    "Staff topped with glowing purple crystal",
    "Back view shows only the back of the robe"
):
    assert preserved in problematic_result, preserved
assert problematic_vision.count("No occlusion") == 1, "raw observation remains untouched"

# Captured improved-but-verbose mage caption: report the final answer once,
# remove raw crop confusion and verbatim cross-section repetitions while
# retaining view-specific information. These are presentation regressions,
# not evidence that Qwen correctly identified original image pixels.
newer_mage_observation = (
    "Character reference · local model observation (accuracy unverified)\n\n"
    "Subject and views: One character shown in five views: front, left side, "
    "right side, back, and top. All views depict the same character and props.\n"
    "Silhouette and anatomy: Silver-white hair in two braids. The back view "
    "shows the full cape and a staff. The top view shows the hood's shape "
    "and the staff's position.\n"
    "Clothing and surface detail: Purple robe with gold trim. Brown boots "
    "with fur lining.\n"
    "Props and small features: Staff topped with glowing purple crystal. "
    "The staff is visible in all views. Brown satchel hangs at the hip. "
    "The top view shows the hood's shape and the staff's position.\n"
    "Visibility limits: The back view does not show the face; the top view "
    "shows only the hood, not the whole body.\n"
    "\nFocused image details (unverified source-crop observations):\n"
    "- Upper-left figure detail: Two identical chibi figures."
)
formatted_newer=direct({"prompt":"What do you see in this image?" +
                        vision.VISION_START + newer_mage_observation +
                        vision.VISION_END})
assert formatted_newer.count("The top view shows the hood's shape and the staff's position.") == 1
assert "The staff is visible in all views" not in formatted_newer
assert "Two identical chibi figures" not in formatted_newer
assert "Brown satchel hangs at the hip" in formatted_newer
assert "The back view does not show the face" in formatted_newer
assert "not independently verified" in formatted_newer

# Captured screenshot case: both left/right staff hands were guessed in one
# turnaround, boots appeared in anatomy and clothing, and illustrations
# were described as verified 3D geometry. The formatter may abstain from
# these unsupported details, but must preserve the useful core features.
redundant_mage = (
    "Character reference · local model observation (accuracy unverified)\n\n"
    "Subject and views: Five views — front, left side, right side, back, and top — "
    "show Little Crystal Mage in a consistent outfit.\n"
    "Silhouette and anatomy: Pale skin and white braids. Limbs are short. "
    "Feet are clad in brown boots with fur trim at top.\n"
    "Clothing and surface detail: Purple hooded robe with gold trim. "
    "Robe has layered geometry with visible folds and creases. "
    "Boots are brown with fur trim at top. No buckles or hidden fastenings.\n"
    "Props and small features: Staff with purple crystal. "
    "Staff is held by right hand in front view, left hand in side views. "
    "Pouch attaches to belt.\n"
    "Visibility limits: Top view shows the hood and staff. "
    "No occlusion is implied for the staff or other features.\n"
    "\nFocused image details (unverified source-crop observations):\n"
    "- Upper-left figure detail: Two identical figures with staves. "
    "Right side view shows left hand gripping a staff."
)
cleaned_mage = direct({"prompt":"What do you see in this image?" +
                       vision.VISION_START + redundant_mage + vision.VISION_END})
assert "Staff with purple crystal." in cleaned_mage
assert "right hand in front" not in cleaned_mage
assert "left hand in side" not in cleaned_mage
assert "No occlusion is implied" not in cleaned_mage
assert "No buckles or hidden fastenings" not in cleaned_mage
assert "layered geometry" not in cleaned_mage
assert "appears layered, with folds and creases" in cleaned_mage
assert cleaned_mage.lower().count("boots") == 1, cleaned_mage
assert "Two identical figures" not in cleaned_mage
assert "not independently verified" in cleaned_mage
assert "Feet are clad" in redundant_mage, "source handoff must remain unchanged"

# New real mage report: a richer satchel/hood detail belongs in the final
# reply, but basic belt/hair/eye inventory must not be repeated across sections.
latest_mage = (
    "Character reference · local model observation (accuracy unverified)\n\n"
    "Subject and views: Front, left side, right side, back, and top views of "
    "a single Little Crystal Mage.\n"
    "Silhouette and anatomy: Silver-white hair in two braids; purple eyes; "
    "wears a hooded robe with cape; stands on two legs; holds a staff in the "
    "right hand; left hand rests on a satchel in front view; back view "
    "shows full cape and staff beside the figure; top view shows hood "
    "shape and staff position.\n"
    "Clothing and surface detail: Purple hooded robe with gold trim; "
    "star, moon, leaf and magic symbols; fur-lined boots; belt with buckle; "
    "satchel with leaf emblem; robe has layered geometry with visible "
    "seams and folds.\n"
    "Props and small features: Staff topped with glowing purple crystal; "
    "satchel with brown leather and leaf emblem; belt with buckle; "
    "hood with star and moon motifs; hair in two braids; eyes purple; "
    "no other visible accessories.\n"
    "Visibility limits: Back view shows the robe and staff; "
    "top view shows hood and staff; no occlusion is implied for all views; "
    "no hidden parts are visible.\n"
    "\nFocused image details (unverified source-crop observations):\n"
    "- Upper-left figure detail: Two identical figures in purple robes; "
    "right side view shows left hand gripping a staff."
)
latest_report = direct({"prompt": "What do you see in this image?" +
                        vision.VISION_START + latest_mage + vision.VISION_END})
assert latest_report.count("belt with buckle") == 1, latest_report
assert latest_report.count("hair in two braids") == 1, latest_report
assert "eyes purple" not in latest_report
assert "satchel with brown leather and leaf emblem" in latest_report
assert "holds a staff in the right hand" not in latest_report
assert "top view shows hood shape and staff position" in latest_report
assert "hood with star and moon motifs" in latest_report, "do not discard unique location-specific details"
assert "no occlusion is implied" not in latest_report
assert "layered geometry" not in latest_report
assert "Two identical figures" not in latest_report
assert "belt with buckle" in latest_mage, "raw text is untouched"



assert "not independently verified" in problematic_result

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

# Genuine multi-panel image layout is discovered from original pixels, not
# from the words "Little Crystal Mage" or hardcoded five equal-width columns.
from PIL import ImageDraw
from vision_sheet_layout import discover_view_panels

sheet = Image.new("RGB", (1448, 1086), "white")
sheet_paint = ImageDraw.Draw(sheet)
for index in range(5):
    left = 42 + index * 280
    sheet_paint.rectangle((left, 165, left + 170, 690),
                          fill="#7040ba", outline="#26103c", width=8)
    sheet_paint.ellipse((left + 30, 190, left + 140, 330), fill="#e9d6af")
    sheet_paint.rectangle((left + 60, 390, left + 115, 650), fill="#7253a9")
sheet_paint.rectangle((50, 934, 1390, 1036), fill="#6e3e86")
source_b = io.BytesIO()
sheet.save(source_b, format="PNG")
sheet_url = "data:image/png;base64," + base64.b64encode(source_b.getvalue()).decode("ascii")
panel_layout = discover_view_panels(sheet)
assert [name for name, _ in panel_layout] == [
    "View panel 1", "View panel 2", "View panel 3",
    "View panel 4", "View panel 5", "Supporting reference panels"
], panel_layout
assert all(0 <= x0 < x1 <= 1448 and 0 <= y0 < y1 <= 1086
           for _, (x0, y0, x1, y1) in panel_layout)
assert panel_layout[-1][1][1] > panel_layout[0][1][1], "Supporting row must be below figures"
planned = vision._detail_regions(sheet_url, "Character turnaround of one character in five views.",
                                  with_boxes=True)
assert [name for name, _, _ in planned] == [name for name, _ in panel_layout]
assert all(url.startswith("data:image/jpeg;base64,") for _, url, _ in planned)
assert len({tuple(box) for _, _, box in planned}) == 6

class PanelModel:
    def __init__(self):
        self.calls = []
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        prompt = kwargs["messages"][0]["content"][0]["text"]
        if "Unverified source-crop notes" in prompt:
            observation = ("Subject and views: One illustrated character in several labeled views.\n"
                           "View comparisons: Back and top are different source views.\n"
                           "Materials and markings: A purple cloak with gold decoration.\n"
                           "Props and contact: A staff appears in the character views.")
        elif "Supporting reference panels" in prompt:
            observation = "A bottom panel contains color samples and decorative reference shapes."
        elif "Source region View panel" in prompt:
            observation = "One figure occupies this view with a dark purple cloak and gold trim."
        else:
            observation = "Character turnaround of a purple-cloaked person shown in multiple views."
        return iter([{"choices": [{"delta": {"content": observation}}]}])

panel_model = PanelModel()
panel_phases = []
with patch.object(vision, "_load_local_model", return_value=panel_model):
    panel_answer = vision._ask_vision_local(
        sheet_url, "What do you see in this image?",
        report_phase=lambda phase, **fields: panel_phases.append((phase, fields)),
    )
assert len(panel_model.calls) == 8, "whole overview + five panels + reference row + whole-image synthesis"
assert panel_answer.startswith("Character reference · local model observation")
assert any(f.get("requestedRegions") == 6 for _, f in panel_phases)
panel_records = [f["spatialRegionRecords"] for _, f in panel_phases
                 if f.get("spatialRegionRecords")]
assert len(panel_records[-1]) == 6
assert [record["regionKind"] for record in panel_records[-1]] == ["view"] * 5 + ["support"]
assert [record["viewPanelIndex"] for record in panel_records[-1]] == [1, 2, 3, 4, 5, None]
last_instructions = panel_model.calls[-1]["messages"][0]["content"][0]["text"]
assert "View panel 5" in last_instructions
assert "Supporting reference panels" in last_instructions
assert "POSITIONAL labels" in last_instructions
# Changing the number of panels should not force a 5-view result.
three = Image.new("RGB", (1200, 880), "white")
three_paint = ImageDraw.Draw(three)
for index in range(3):
    x = 60 + 390 * index
    three_paint.rectangle((x, 160, x + 230, 650), fill="#5f34a3")
assert len(discover_view_panels(three)) == 3
assert discover_view_panels(Image.new("RGB", (1200, 900), "white")) == []

# The older fallback still handles art with no clear separate whitespace
# between figures, using selective closeups rather than invented panels.

reference = Image.new("RGB", (1448, 1086), "white")
painter = ImageDraw.Draw(reference)
for index in range(4):
    left = 32 + index * 360
    painter.rectangle((left, 170, left + 160, 670),
                      fill="#7040ba", outline="#202020", width=12)
    painter.line((left + 25, 200, left + 140, 625),
                 fill="#e5b744", width=14)
# A continuous overlaid band defeats panel separation: exercise fallback.
painter.rectangle((30, 350, 1410, 475), fill="#7040ba")
# Palette below figures must not occupy each character-focused crop.
painter.rectangle((0, 950, 1447, 1085), fill="#11aa22")
buffer = io.BytesIO()
reference.save(buffer, format="PNG")
reference_encoded = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode("ascii")
regions = vision._detail_regions(reference_encoded, "Character page with various features.")
assert [label for label, _ in regions] == ["Upper-left figure detail"]
refined_regions = vision._detail_regions(
    reference_encoded,
    "Character turnaround: braided white hair, a purple hood, golden robe trim, staff and embroidery.")
assert [label for label, _ in refined_regions] == [
    "Upper-left figure detail", "Central outfit and prop detail",
], "Only useful source-image face and costume close-ups, not four whole views"
boxed_regions = vision._detail_regions(
    reference_encoded, "A purple hood, braided hair, gold trim and a staff.",
    with_boxes=True)
assert len(boxed_regions) == 2
for label, encoded, box in boxed_regions:
    assert label and encoded.startswith("data:image/jpeg;base64,")
    assert len(box) == 4 and all(0 <= n <= 1 for n in box)
    assert box[0] < box[2] and box[1] < box[3], "source region, not invented object boundary"
text_regions = vision._detail_regions(
    reference_encoded, "Braided hair and a gold-trimmed robe.",
    "Read the small labels and examine the details.")
assert len(text_regions) <= 2 and text_regions[0][0] == "Lower label detail"
for label, encoded in regions:
    with Image.open(io.BytesIO(base64.b64decode(encoded.partition(",")[2]))) as cropped:
        assert cropped.height <= 768, (label, cropped.size)
        assert cropped.width <= 768, (label, cropped.size)
assert vision._detail_regions(valid, "Red background") == []

# A 0/0/0 study must never imply that Level 1 won on accuracy.
class ZeroDescriptorStudyModel:
    def __init__(self):
        self.calls = 0
    def create_chat_completion(self, **kwargs):
        captions = [
            "Character page with various features.",
            "A character has different views.",
            "A character turnaround poster.",
        ]
        text = captions[self.calls]
        self.calls += 1
        return iter([{"choices": [{"delta": {"content": text}}]}])
zero_model = ZeroDescriptorStudyModel()
with patch.object(vision, "_load_local_model", return_value=zero_model):
    zero_study = vision._ask_vision_local(valid, "What do you see?", analysis_levels=3)
assert zero_model.calls == 3
assert "All level captions returned 0 tracked descriptors" in zero_study
assert "Level 1 remains the fallback, not a quality winner" in zero_study

# The whole-image integration pass must use BOTH actual pixels and
# accumulated region observations. A generic final caption must not replace
# already-specific raw crops, and simple images must not incur this pass.
class JointVisionModel:
    def __init__(self, generic_final=False):
        self.calls = []
        self.generic_final = generic_final
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        captions = [
            "Character turnaround with braided white hair, purple hood, gold robe trim and crystal staff.",
            "Purple hood with golden stitching and a crystal staff.",
            "Purple cape with a moon symbol on the back.",
            ("A character with various features." if self.generic_final
             else "Subject and views: A mage appears in a character turnaround.\n"
                  "Silhouette and anatomy: A small figure with braided hair.\n"
                  "Clothing and surface detail: A purple hood and gold-trimmed cloak with moon markings.\n"
                  "Props and small features: A crystal staff."),
        ]
        return iter([{"choices": [{"delta": {"content": captions[len(self.calls)-1]}}]}])
joint_model = JointVisionModel()
joint_phases = []
with patch.object(vision, "_load_local_model", return_value=joint_model):
    joined = vision._ask_vision_local(
        reference_encoded, "Describe the visible mage.",
        report_phase=lambda phase, **fields: joint_phases.append((phase, fields)),
    )
assert len(joint_model.calls) == 4, "one overview, two targeted crops, one synthesis"
assert joined.startswith("Character reference · local model observation")
assert "purple hood" in joined and "gold-trimmed cloak" in joined
assert "Upper-left figure detail" in joined
assert "Character turnaround with braided white hair" not in joined, "no duplicated raw overview"
assert vision.RAW_CROP_MARKER in joined, "original crop notes remain inspectable in the saved user handoff"
direct_joined = direct({"prompt": "What do you see in this image?" +
                        vision.VISION_START + joined + vision.VISION_END})
assert "### Subject & views" in direct_joined
assert "Upper-left figure detail" not in direct_joined, "no second raw-crop text dump in §C reply"
assert vision.RAW_CROP_MARKER not in direct_joined
final_prompt = joint_model.calls[-1]["messages"][0]["content"]
assert final_prompt[1]["type"] == "image_url", "the integration must see the source image"
assert final_prompt[1]["image_url"]["url"] == (
    joint_model.calls[0]["messages"][0]["content"][1]["image_url"]["url"]
), "final synthesis must reuse the complete 768px overview, not downsize again"
assert "Whole scene:" in final_prompt[0]["text"]
assert "Central outfit and prop detail" in final_prompt[0]["text"]
assert "View comparisons:" in final_prompt[0]["text"]
assert "visible belt buckle cannot" in final_prompt[0]["text"]
assert "110 to 175 information-dense words" in final_prompt[0]["text"]
assert "No props, hand-held objects" in final_prompt[0]["text"]
assert "only when clearly" in final_prompt[0]["text"]
assert "different crop" in final_prompt[0]["text"]
assert "Do NOT narrate what each view fails to show" in final_prompt[0]["text"]
assert any(f.get("inferenceStage") == "FUSION_PREFILL" for _, f in joint_phases)
assert any(f.get("integratedSelected") is True for _, f in joint_phases)
assert joint_model.calls[-1]["max_tokens"] == 384
assert any(fields.get("referenceProgress") is True and fields.get("requestedRegions") == 2
           for _, fields in joint_phases), "show overview before crops finish"
assert any(fields.get("completedRegions") == 1 for _, fields in joint_phases)
assert any(fields.get("completedRegions") == 2 for _, fields in joint_phases)
assert any(fields.get("integratedObservation") for _, fields in joint_phases)
# The pipeline emits real intermediate results, not fictional consistency stages.
assert all(fields.get("inferenceStage") not in ("CONTRADICTION_CHECK", "CONSISTENCY_CHECK")
           for _, fields in joint_phases)
# A short coherent full-image interpretation must win over four verbose
# crop observations; total keyword count across crops is not scene accuracy.
class CompactFusionModel:
    def __init__(self):
        self.calls = []
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        texts = [
            "Character turnaround: braided white hair, a purple hood, gold robe trim and a crystal staff.",
            "A purple hood, gold trim, boots, violet gems and white hair.",
            "A purple cape, moon motifs, gold ornaments and lavender gloves.",
            "The same character wears a purple hood and carries a crystal staff across several views.",
        ]
        return iter([{"choices":[{"delta":{"content":texts[len(self.calls)-1]}}]}])
compact_model = CompactFusionModel()
compact_phases = []
with patch.object(vision, "_load_local_model", return_value=compact_model):
    compact = vision._ask_vision_local(
        reference_encoded, "Describe the same character across views.",
        report_phase=lambda phase, **fields: compact_phases.append(fields))
assert len(compact_model.calls) == 4
assert compact.startswith("Character reference · local model observation")
assert "same character wears a purple hood" in compact
assert any(x.get("integratedSelected") is True for x in compact_phases)


weaker_model = JointVisionModel(generic_final=True)
weaker_phases = []
with patch.object(vision, "_load_local_model", return_value=weaker_model):
    retained = vision._ask_vision_local(
        reference_encoded, "Describe the visible mage.",
        report_phase=lambda phase, **fields: weaker_phases.append((phase, fields)),
    )
assert "Purple hood with golden stitching and a crystal staff" in retained
assert not retained.startswith("Character reference · local model observation")
assert any(f.get("integratedSelected") is False for _, f in weaker_phases)

# Regression: an informative third crop must NOT overwrite the previously
# accumulated zero-keyword crop observations. An unselected whole-scene
# synthesis remains visible with its real, unverified model text.
class PriorCropRetentionModel:
    def __init__(self):
        self.calls = []
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        captions = [
            "Character turnaround with braided hair, purple hood and gold-trimmed robe.",
            "A character drawing in one panel.",
            "A girl wearing a purple coat.",
            "A character page with various features.",
        ]
        return iter([{"choices": [{"delta": {
            "content": captions[len(self.calls) - 1],
        }}]}])

retention_model = PriorCropRetentionModel()
retention_phases = []
with patch.object(vision, "_load_local_model", return_value=retention_model):
    retained_crops = vision._ask_vision_local(
        reference_encoded,
        "Describe the character turnaround.",
        report_phase=lambda phase, **fields: retention_phases.append((phase, fields)),
    )
assert len(retention_model.calls) == 4, "whole image, two targeted crops, final synthesis"
for caption in [
    "A character drawing in one panel.",
    "A girl wearing a purple coat.",
]:
    assert caption in retained_crops, ("Earlier crop was erased", caption)
assert retained_crops.index("A character drawing in one panel.") < retained_crops.index("A girl wearing a purple coat.")
assert "Whole-image synthesis (too generic to select" in retained_crops
assert any(fields.get("integratedOutcome") == "NOT_SELECTED" for _, fields in retention_phases)
assert any(fields.get("integratedSelected") is False for _, fields in retention_phases)

# The vision model's vague opening caption must not decide whether a bright,
# detailed, wide reference page gets figure-sized crops or two giant halves.
# Earlier code routed this exact shape to Left-side/Right-side detail whenever
# the small model omitted "turnaround" from its caption.
generic_regions = vision._detail_regions(
    reference_encoded, "An illustration with different colors.", "What is this?"
)
assert [label for label, _ in generic_regions] == [
    "Upper-left figure detail",
], "Wide reference pages get selective close-ups, not forced four-view passes"
assert vision._detail_regions(valid, "An illustration.") == [], "Blank image stays fast"

# A model identity receipt is issued AFTER a successful local model load and
# is returned via real progress events; it is not invented by the browser.
identity_model = JointVisionModel()
identity_events = []
with patch.object(vision, "_load_local_model", return_value=identity_model):
    vision._ask_vision_local(
        reference_encoded, "Describe the reference sheet.",
        report_phase=lambda phase, **fields: identity_events.append((phase, fields)),
    )
identities = [
    fields for phase, fields in identity_events
    if fields.get("visionModelLoaded") is True
]
assert identities
assert identities[-1]["activeVisionModel"] == vision.MODEL_REPO
assert identities[-1]["activeVisionRevision"] == vision.MODEL_REVISION
assert identities[-1]["activeVisionProjector"] == vision.PROJECTOR_FILE

# Regression for a detailed crop paragraph that previously ended mid-word
# at the decoder's 128-token limit. Only a real finish_reason="length"
# should flag truncation; other finish reasons must not be mislabeled.
class RegionFinishModel:
    def __init__(self):
        self.calls = []
    def create_chat_completion(self, **kwargs):
        self.calls.append(kwargs)
        index = len(self.calls)
        if index == 1:
            response = "Character turnaround with braided hair, purple hood and gold-trimmed robe."
        elif index == 3:
            response = "A purple hooded mage holds a staff and has a crescent"
        elif index == 4:
            response = "A mage in a purple coat holding a staff."
        else:
            response = "Purple cloak, gold trim, crystal staff."
        yield {"choices": [{"delta": {"content": response}}]}
        yield {"choices": [{"delta": {},
                            "finish_reason": "length" if index == 3 else "stop"}]}

finish_model = RegionFinishModel()
finish_stages = []
with patch.object(vision, "_load_local_model", return_value=finish_model):
    limited = vision._ask_vision_local(
        reference_encoded, "Describe the mage.",
        report_phase=lambda phase, **fields: finish_stages.append((phase, fields)),
    )
assert len(finish_model.calls) == 4
assert "at 128-token limit; description may be incomplete" in limited
assert "crescent" in limited
crop_snapshots = [
    f["spatialRegionRecords"] for _, f in finish_stages
    if "spatialRegionRecords" in f
]
assert crop_snapshots
assert sum(bool(item.get("tokenLimitReached")) for item in crop_snapshots[-1]) == 1
assert crop_snapshots[-1][1]["finishReason"] == "length"
assert all(record["coordinateSpace"] == "exif-corrected-source-normalized"
           and len(record["sourceBox"]) == 4 for record in crop_snapshots[-1])
assert all("at most 55 words" in call["messages"][0]["content"][0]["text"]
           for call in finish_model.calls[1:3])
assert not crop_snapshots[-1][0]["tokenLimitReached"]

print("Chat vision local CPU: authenticated boundaries, no paid provider, concurrency and mocked inference and export handoff PASS")
