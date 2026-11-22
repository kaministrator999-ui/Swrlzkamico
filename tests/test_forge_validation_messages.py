"""Check user-visible terminal plan feedback without an account or live editor."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch


LOFT_CODE = "FORGE_INVALID_LOFT_PROFILE"
SCOPE_CODE = "FORGE_UNREQUESTED_NATIVE_ACTION"
GENERIC = "Check that the Chat panel is connected"
CASES = (
    ("point-format", "the curve path is invalid"),
    ("adjacent-spacing", "consecutive path points are too close together"),
    ("count-mismatch", "the number of thickness values does not match the path points"),
    ("radius-range", "one or more thickness values are invalid"),
    ("private fixture diagnostic", "the curve profile is invalid"),
    (None, "the curve profile is invalid"),
)
LOFT = {"op": "mesh.add", "kind": "loft", "name": "private fixture mesh"}
NATIVE_REMOVE = {"op": "mesh.remove", "id": "example-mesh"}
VALID = {"op": "mesh.add", "kind": "sphere", "name": "Example part"}
OTHER = {"op": "unsupported-fixture-operation"}


def run_planner(root, candidates, *, reason=None):
    stage = Mock(return_value={})
    register = Mock(side_effect=AssertionError("A preview must not register a native batch."))
    wait = Mock(side_effect=AssertionError("A preview must not wait for native receipts."))
    summary = {"projectId": "fixture-project", "epoch": 1, "mode": "edit",
               "workspace": "model-atelier", "meshes": [{"id": "example-mesh"}]}
    context = SimpleNamespace(project_id=summary["projectId"], model_context=lambda: summary)
    kinds = ("sphere", "box", "cone", "cylinder", "loft", "lathe")
    diagnostic = {"field": "radii", "reason": reason, "requirement": "private fixture requirement"}
    inference_calls = []
    dependencies = {
        "forge_mesh_tools_v2": SimpleNamespace(
            MAX_OPERATIONS=64, MESH_KINDS=kinds, LEGACY_KINDS=kinds[:4],
            GEOMETRY_FIELDS=frozenset({"path", "radii", "profile", "segments", "arcStart", "arcLength"}),
            FRAME_VIEWS=("front", "three"), mesh_tools=lambda _: {"schema": "fixture-capability"},
            operation_limit=lambda _: 64, validate_geometry=lambda op: LOFT_CODE if op == LOFT else None,
            loft_profile_issue=lambda _: diagnostic if reason else None,
        ),
        "brain_forge": SimpleNamespace(
            classify_forge_intent=lambda *_: {"disposition": "mutation"}, current_command_text=lambda prompt: prompt,
            inspection_text=Mock(), native_plan_system=lambda *_, **__: "Plan the requested mesh.",
            requests_new_project=lambda _: False, _literal=str,
        ),
        "forge_workspace_insights_v1": SimpleNamespace(build_insight=Mock()),
        "progress_timeline_v238": SimpleNamespace(forge_failure_fields=lambda code, _: {"code": code}),
        "forge_design_preview_v1": SimpleNamespace(
            wants_preview=lambda _: False, should_preview=lambda *_: True,
            build_preview=lambda *_: ("Review the design.", {}), approval_id=lambda _: None,
        ),
        "forge_studio_commands_v1": SimpleNamespace(
            STUDIO_SCHEMA={}, STUDIO_LABELS={}, PARTICLE_PRESETS=(),
            validate_studio_operation=Mock(), StudioCommandError=ValueError,
        ),
        "forge_embed": SimpleNamespace(
            create_batch=register, wait_batch=wait, revalidate=lambda *_, **__: None,
            create_design_proposal=stage, claim_design_proposal=Mock(),
        ),
    }

    def infer(messages, _budget):
        candidate = candidates[len(inference_calls)]
        inference_calls.append(json.loads(messages[1]["content"]))
        if isinstance(candidate, Exception):
            raise candidate
        return json.dumps({"disposition": "apply", "operations": [candidate]}), {"finishReason": "stop"}

    source = root / "forge_chat_actions.py"
    actions = ModuleType("forge_chat_actions")
    with patch.dict(sys.modules, dependencies):
        exec(compile(source.read_bytes(), str(source), "exec"), vars(actions))
        events = list(actions.generate_events({"prompt": "Create a small editable shape."}, context, generate_plan=infer))
    register.assert_not_called()
    wait.assert_not_called()
    return events, inference_calls, stage


def failed(result, code, attempts):
    events, calls, stage = result
    assert len(calls) == attempts, calls
    assert [event.get("phase") for event in events].count("FORGE_REPAIRING") == attempts - 1
    stage.assert_not_called()
    assert all(event["type"] not in {"FORGE_BATCH_READY", "WIDGET", "COMPLETED"} for event in events)
    assert events[-1] == {"type": "FAILED", "phase": "FORGE_FAILED", "code": code,
                          "reason": events[-2]["text"], "forgeStatus": "FAILED"}, events
    assert events[-2]["type"] == "DELTA"
    assert "private fixture" not in events[-1]["reason"]
    return events[-1]["reason"]


def verify(before, after):
    for reason, text in CASES:
        old = run_planner(before, [LOFT, LOFT], reason=reason)
        new = run_planner(after, [LOFT, LOFT], reason=reason)
        assert GENERIC in failed(old, LOFT_CODE, 2)
        message = failed(new, LOFT_CODE, 2)
        assert text in message and "No editor changes were sent." in message
        assert "retry one curved part at a time" in message and GENERIC not in message
        assert old[1] == new[1], "The two model attempts must receive identical inputs."

    assert GENERIC in failed(run_planner(before, [NATIVE_REMOVE, NATIVE_REMOVE]), SCOPE_CODE, 2)
    message = failed(run_planner(after, [NATIVE_REMOVE, NATIVE_REMOVE]), SCOPE_CODE, 2)
    assert "outside your request" in message and "No editor changes were sent." in message
    assert "which part to change" in message and GENERIC not in message

    for candidates, code, attempts in (([OTHER, OTHER], "FORGE_NATIVE_OPERATION_NOT_ALLOWED", 2),
                                       ([TimeoutError("private fixture timeout")], "FORGE_REQUEST_UNAVAILABLE", 1)):
        old = failed(run_planner(before, candidates), code, attempts)
        assert failed(run_planner(after, candidates), code, attempts) == old

    old, *_ = run_planner(before, [LOFT, VALID], reason="count-mismatch")
    new, calls, stage = run_planner(after, [LOFT, VALID], reason="count-mismatch")
    assert len(calls) == 2 and new == old
    assert new[-1]["forgeStatus"] == "DESIGN_PREVIEW"
    stage.assert_called_once()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    verify(args.before, args.after)
    print("FORGE_VALIDATION_MESSAGES_PASS: actionable failures precede all writes; successful and transport paths unchanged")
