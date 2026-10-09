"""Opt-in routing integration test. Stubs online and programming dependencies for isolation."""
from __future__ import annotations

import os
import sys
import types
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

brain=types.ModuleType("brain_programming")
brain.programming_intent=lambda prompt, history, pins, state: {
    "codingTask": "function" in prompt.lower(), "contentMode": "none",
}
sys.modules["brain_programming"]=brain

online=types.ModuleType("online_tools")
online.classify_online_request=lambda prompt, history, intent, location: {
    "requested": False, "reason": "no-external-evidence-request",
}
online.stream_online_request=lambda *args: iter(())
online.online_camera=lambda result: result
sys.modules["online_tools"]=online

from model_router import dispatch  # noqa: E402


def assert_route(prompt, model_id, enabled, expected_tier=None, expected_model=None):
    received=[]
    def generate(payload):
        received.append(payload)
        yield {"type": "DELTA", "text": "probe"}
        yield {"type": "COMPLETED", "phase": "COMPLETE"}
    with patch.dict(os.environ, {"SWRLZ_ADAPTIVE_EFFORT": "1" if enabled else "0"}):
        events=list(dispatch(
            model_id,
            {"prompt": prompt, "history": [], "pinnedContext": []},
            generate, generate, generate, generate,
        ))
    effort=[e for e in events if e.get("type")=="TASK_EFFORT_PLAN"]
    assert len(received)==1, events
    assert received[0].get("selectedModelId")== (expected_model or model_id), events
    if not enabled:
        assert not effort and "taskEffortPlan" not in received[0], events
    else:
        assert len(effort)==1, events
        assert received[0]["taskEffortPlan"]==effort[0]["plan"]
        assert effort[0]["plan"]["tier"]==expected_tier, effort[0]
        assert effort[0]["plan"]["automaticToolPermission"] is False
    assert sum(e.get("type")=="DELTA" for e in events)==1
    return events


assert_route("Hello", "700m", False)
assert_route("Hello", "700m", True, 1)
assert_route("Explain what a function does", "700m", True, 2, "coder")
heavy=assert_route("Deploy this update to our production server", "700m", True, 5)
plan=next(e["plan"] for e in heavy if e.get("type")=="TASK_EFFORT_PLAN")
assert plan["requiresAuthorization"] and plan["verification"]=="independent-gate"
assert_route("Fix this function but preserve existing behavior", "700m", True, 3, "coder")
print("TASK_EFFORT_ROUTER_V182_PASS enabled, disabled, coder-route, critical-safety")
