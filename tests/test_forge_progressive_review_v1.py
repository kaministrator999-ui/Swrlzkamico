"""Source-bound §C Analyze Workspace progressive stream acceptance tests."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sys

before, after = map(Path, sys.argv[1:3])
sys.path.insert(0, str(after))
from forge_progressive_review_v1 import stream_insight
from forge_workspace_insights_v1 import build_insight

legacy = (before / "model_router.py").read_text("utf8")
router = (after / "model_router.py").read_text("utf8")
assert "from forge_progressive_review_v1 import stream_insight" not in legacy
assert router.count("from forge_progressive_review_v1 import stream_insight") == 1
assert 'native_intent.get("disposition") == "read"' in router
assert "yield from stream_insight(forge_context.model_context(), command," in router
assert "yield from generate_events(native_payload,forge_context,forge_embed.create_batch,forge_embed.wait_batch)" in router
assert (after / "forge_workspace_insights_v1.py").read_bytes() == (before / "forge_workspace_insights_v1.py").read_bytes()
summary = {
    "project": {"name": "Glitch Dragon"},
    "workspace": "model-atelier", "mode": "edit", "dirty": True,
    "totalMeshes": 11, "selectedId": "part-1",
    "activeLevel": {"name": "First Floor"},
    "meshes": [
        {"id": "part-1", "name": "Wing", "kind": "loft",
         "position": [0,1,0], "rotation": [0,0,0], "scale": [1,1,1], "material": "metal", "color": "#aabbcc"},
        {"id": "part-2", "name": "Wing", "kind": "loft",
         "position": [0,1,0], "rotation": [0,0,0], "scale": [1,1,1], "material": "metal", "color": "#aabbcc"},
        {"id": "part-3", "name": "Tail", "kind": "sphere",
         "position": [1,1,0], "rotation": [0,0,0], "scale": [1,1,1]},
    ],
}
calls = []
def fake_model(payload):
    calls.append(payload)
    yield {"type": "STATUS", "phase": "LOADING"}
    yield {"type": "DELTA", "text": "My assessment: review the wing geometry. "}
    yield {"type": "DELTA", "text": "Matching origins alone do not prove a collision."}
    yield {"type": "COMPLETE"}
tokens = {"forgeHostToken": "DO_NOT_SEND", "hostId": "HOST_DO_NOT_SEND",
          "profileId": "default", "_cancelCheck": lambda: False}
events = list(stream_insight(summary, "Analyze current model in viewport",
                             model_generate=fake_model, source_payload=tokens))
assert events[0]["phase"] == "FORGE_REVIEW_OPEN"
assert events[1]["type"] == "DELTA" and "Glitch Dragon" in events[1]["text"]
assert any("First Floor" in e.get("text", "") for e in events)
assert any("loft" in e.get("text", "") and "scale" in e.get("text", "") for e in events)
assert any(e.get("phase") == "FORGE_REVIEW_PATTERNS" for e in events)
assert any(e.get("phase") == "FORGE_REVIEW_SYNTHESIS" for e in events)
assert any("not verified bugs" in e.get("text", "") for e in events)
assert len([e for e in events if e["type"] == "WIDGET"]) == 1
assert len([e for e in events if e["type"] == "COMPLETED"]) == 1
assert events[-1]["type"] == "COMPLETED"
assert len(calls) == 1
assert "DO_NOT_SEND" not in str(calls[0])
assert "hostId" not in calls[0]
assert calls[0]["nativeEditorEvidence"]["sampled"] == 3
assert calls[0]["nativeEditorEvidence"]["total"] == 11
assert "not a viewport image" in calls[0]["prompt"].lower()
assert all(e["type"] != "FORGE_BATCH_READY" for e in events)
assert any("My assessment: review the wing" in e.get("text", "") for e in events)
assert events.index(next(e for e in events if e.get("phase") == "FORGE_REVIEW_OPEN")) < len(events)-4
widget = next(e["widget"] for e in events if e["type"] == "WIDGET")
assert widget == build_insight(summary, "Analyze current model in viewport")[1]
for g in (None, lambda payload: iter(({"type":"FAILED","reason":"offline"},))):
    result = list(stream_insight(summary, model_generate=g))
    assert result[-1]["type"] == "COMPLETED"
    assert any("My assessment:" in e.get("text","") for e in result)
    assert not any(e["type"] == "FAILED" for e in result)
no_select = dict(summary, selectedId=None)
result = list(stream_insight(no_select))
assert any("Nothing is currently selected" in e.get("text","") for e in result)
assert not any("selected object is" in e.get("text","") for e in result)
scene = dict(summary, workspace="scene", actors=[
    {"id":"a","name":"Tree","type":"bush","position":[0,0,0]}], totalActors=1, selectedId="a")
result = list(stream_insight(scene))
assert "Scene workspace" in result[1]["text"]
assert len([e for e in result if e["type"] == "WIDGET"]) == 1
print("FORGE_PROGRESSIVE_REVIEW_PASS: early source-backed deltas, model synthesis, fallback, no write/visual claim")
