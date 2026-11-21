"""Exercise the exact Forge validation and correction source without a live editor."""
from __future__ import annotations

import argparse
import ast
import json
import math
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, patch


LOFT_CODE = "FORGE_INVALID_LOFT_PROFILE"
LOFT = {
    "op": "mesh.add", "kind": "loft", "name": "Bent stem",
    "path": [[0, 0, 0], [0.2, 0.5, 0], [0.1, 1, 0]],
    "radii": [0.2, 0.1, 0.00025], "segments": 16,
    "color": "#407653", "material": "matte", "scale": [1, 1, 1],
}
LATHE = {"op": "mesh.add", "kind": "lathe", "profile": [[0, 0], [1, 1]]}
SPHERE = {"op": "mesh.add", "kind": "sphere", "name": "Stem base"}
REQUEST = "Create an editable bent stem model in Model Atelier."
OBSERVATION = "The reference shows a bent stem with a narrow end."


def load_module(root, name):
    source = root / f"{name}.py"
    loaded = ModuleType(name)
    exec(compile(source.read_bytes(), str(source), "exec"), vars(loaded))
    return loaded


def check_geometry(before, after):
    cases = [
        ({"path": None}, "path", "point-format"),
        ({"path": [[0, 0], [2, 1]]}, "path", "point-format"),
        ({"path": [[0, 0, 0], [math.nan, 0, 0]]}, "path", "point-format"),
        ({"path": [[0, 0, 0], [101, 0, 0]]}, "path", "point-format"),
        ({"path": [[0, 0, 0], [0, 0, 0]]}, "path", "adjacent-spacing"),
        ({"path": [[0, 0, 0], [1e-7, 0, 0]]}, "path", "adjacent-spacing"),
        ({"radii": None}, "radii", "count-mismatch"),
        ({"radii": [0.2, 0.1]}, "radii", "count-mismatch"),
        ({"radii": [0.2, 0.1, 0]}, "radii", "radius-range"),
        ({"radii": [0.2, 0.1, 0.000249]}, "radii", "radius-range"),
        ({"radii": [0.2, 0.1, 5.001]}, "radii", "radius-range"),
        ({"radii": [0.2, 0.1, True]}, "radii", "radius-range"),
    ]
    for fields, field, reason in cases:
        operation = {**LOFT, **fields}
        assert before.validate_geometry(operation) == after.validate_geometry(operation) == LOFT_CODE
        issue = after.loft_profile_issue(operation)
        assert issue["field"] == field and issue["reason"] == reason, (fields, issue)
        assert isinstance(issue["requirement"], str) and issue["requirement"].strip(), issue

    for operation, expected in (
        (LOFT, None),
        ({**LOFT, "path": [[-100, 0, 0], [100, 1, 0], [-100, 0, 0]],
          "radii": [5, 0.1, 0.00025], "segments": 64}, None),
        ({**LOFT, "segments": 65}, "FORGE_INVALID_MESH_SEGMENTS"),
        ({**LOFT, "profile": LATHE["profile"]}, "FORGE_UNSUPPORTED_SHAPE_FIELD"),
        ({**LATHE, "profile": [[0, 0], [0, 1]]}, "FORGE_INVALID_LATHE_PROFILE"),
        ({**LATHE, "arcStart": 7}, "FORGE_INVALID_LATHE_ARC"),
        ({**SPHERE, "path": LOFT["path"]}, "FORGE_UNSUPPORTED_SHAPE_FIELD"),
        (LATHE, None),
        (SPHERE, None),
    ):
        assert before.validate_geometry(operation) == after.validate_geometry(operation) == expected
        if operation["kind"] == "loft":
            assert after.loft_profile_issue(operation) is None


def run_planner(root, geometry, first, replacement):
    staged = Mock(return_value={})
    register = Mock(side_effect=AssertionError("An unapproved plan cannot register a native batch."))
    receipts = Mock(side_effect=AssertionError("An unapproved plan cannot wait for native receipts."))
    summary = {
        "projectId": "test-project", "epoch": 1, "mode": "edit", "workspace": "model-atelier",
        "meshes": [], "meshTools": {
            "schema": geometry.SCHEMA, "kinds": list(geometry.MESH_KINDS),
            "maxOperations": geometry.MAX_OPERATIONS,
        },
    }
    context = SimpleNamespace(project_id=summary["projectId"], model_context=lambda: summary)
    dependencies = {
        "forge_mesh_tools_v2": geometry,
        "brain_forge": SimpleNamespace(
            classify_forge_intent=lambda *_: {"disposition": "mutation"},
            current_command_text=lambda prompt: prompt, inspection_text=Mock(),
            native_plan_system=lambda *_, **__: "Plan the requested mesh.",
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
            create_batch=register, wait_batch=receipts, revalidate=lambda *_, **__: None,
            create_design_proposal=staged, claim_design_proposal=Mock(),
        ),
    }
    submissions = []

    def infer(messages, _max_tokens):
        staged.assert_not_called()
        submissions.append(json.loads(messages[1]["content"]))
        next_loft = first if len(submissions) == 1 else replacement
        return json.dumps({"disposition": "apply", "operations": [SPHERE, next_loft]}), {"finishReason": "stop"}

    with patch.dict(sys.modules, dependencies):
        actions = load_module(root, "forge_chat_actions")
        events = list(actions.generate_events({"prompt": REQUEST, "verifiedForgeImage": {
            "question": REQUEST, "observation": OBSERVATION,
        }}, context, generate_plan=infer))
        grammar = actions.native_plan_response_format(summary)
    register.assert_not_called()
    receipts.assert_not_called()
    return submissions, events, staged, context, grammar


def check_retry(before_root, after_root, before, after):
    wrong_count = {**LOFT, "radii": [0.1]}
    submissions, events, staged, context, old_grammar = run_planner(before_root, before, wrong_count, LOFT)
    assert len(submissions) == 2 and "typedValidationDetail" not in submissions[1]
    assert events[-1]["forgeStatus"] == "DESIGN_PREVIEW"
    staged.assert_called_once_with(context, [SPHERE, LOFT])

    for broken, field, reason in (
        (wrong_count, "radii", "count-mismatch"),
        ({**LOFT, "radii": [0.2, 0.1, 0]}, "radii", "radius-range"),
        ({**LOFT, "path": [[0, 0, 0], [0, 0, 0], [0.1, 1, 0]]}, "path", "adjacent-spacing"),
    ):
        submissions, events, staged, context, grammar = run_planner(after_root, after, broken, LOFT)
        assert grammar == old_grammar
        assert len(submissions) == 2 and "typedValidationDetail" not in submissions[0]
        correction = submissions[1]
        assert correction["currentUserRequest"] == REQUEST and correction["referenceImageEvidence"] == OBSERVATION
        assert correction["invalidProposedPlan"]["operations"] == [SPHERE, broken]
        assert correction["typedValidationFailure"] == LOFT_CODE
        detail = correction["typedValidationDetail"]
        assert detail["operationIndex"] == 2 and detail["field"] == field and detail["reason"] == reason, detail
        assert detail["requirement"] == after.loft_profile_issue(broken)["requirement"]
        assert [event.get("phase") for event in events].count("FORGE_REPAIRING") == 1
        assert events[-1]["forgeStatus"] == "DESIGN_PREVIEW"
        staged.assert_called_once_with(context, [SPHERE, LOFT])

    submissions, events, staged, _, _ = run_planner(after_root, after, wrong_count, wrong_count)
    assert len(submissions) == 2
    staged.assert_not_called()
    assert events[-1]["type"] == "FAILED" and events[-1]["code"] == LOFT_CODE
    assert "typedValidationDetail" not in events[-1]


def check_vision(before_root, after_root):
    before = before_root / "chat_vision.py"
    after = after_root / "chat_vision.py"
    if not before.is_file() and not after.is_file():
        return
    generate_calls = []
    for path, expected in ((before, 224), (after, 384)):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        budget = next(
            node for node in tree.body
            if isinstance(node, ast.Assign)
            and any(ast.unparse(target) == "MAX_VISION_OUTPUT_TOKENS" for target in node.targets)
        )
        assert ast.literal_eval(budget.value) == expected
        inference = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "_ask_vision_local"
        )
        analysis_levels = [
            ast.unparse(node) for node in ast.walk(inference)
            if isinstance(node, ast.Assign)
            and any(ast.unparse(target) == "analysis_levels" for target in node.targets)
        ]
        assert analysis_levels == ["analysis_levels = 1"]
        calls = [
            ast.unparse(node) for node in ast.walk(inference)
            if isinstance(node, ast.Call) and ast.unparse(node.func) == "generate"
        ]
        assert calls.count("generate(image, prompt, MAX_VISION_OUTPUT_TOKENS)") == 1
        generate_calls.append(calls)
        assert any(ast.unparse(node) == "image = image_url" for node in ast.walk(inference)
                   if isinstance(node, ast.Assign))
    assert generate_calls[0] == generate_calls[1]
    assert "Use compact complete sentences about the visible details most relevant to the question." in source
    print("FORGE_VISION_BUDGET_PASS: bounded 384-token pass preserves original-image input")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    args = parser.parse_args()
    before = load_module(args.before, "forge_mesh_tools_v2")
    after = load_module(args.after, "forge_mesh_tools_v2")
    check_geometry(before, after)
    check_retry(args.before, args.after, before, after)
    check_vision(args.before, args.after)
    print("FORGE_LOFT_REPAIR_PASS: precise bounded correction, unchanged geometry validation and preview gate")
